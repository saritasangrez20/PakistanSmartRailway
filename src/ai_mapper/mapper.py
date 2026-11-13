"""AI control mapper: maps every PSR control (CTL-01..) to framework requirements.

Pipeline per control
    1. Retrieval shortlists the closest requirements in each framework family (offline, TF-IDF).
    2. Backend 'ollama': a local LLM picks the requirements the control really satisfies, with a
       confidence and a one line rationale. Guardrails drop any ID that was not shortlisted.
       Backend 'retrieval': a fixed similarity rule picks them instead (no LLM, baseline).
    3. Every suggestion is written for human review (human_decision column). Earlier decisions
       are kept when the mapper is re-run.

Outputs (outputs/mapping/)
    ai_mapping_<backend>.csv   one row per suggested control to requirement mapping
    run_log_<backend>.json     timing, model, rejected IDs, injection flags (for evaluation)

Run:  python run.py map --backend ollama        (or --backend retrieval)
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import pandas as pd

from ..config import OUTPUTS
from .catalog import load_catalog, load_controls
from .guardrails import extract_json, scan_for_injection, validate_mappings
from .llm import OllamaClient
from .prompts import SYSTEM_PROMPT, build_user_prompt
from .retrieval import Retriever

MAPPING_DIR = OUTPUTS / "mapping"
SAFETY_DOMAINS = {"OT and safety systems", "Network security and segmentation", "AI governance"}
REVIEW_COLUMNS = ["human_decision", "reviewer", "review_note"]


def mapping_path(backend: str):
    return MAPPING_DIR / f"ai_mapping_{backend}.csv"


def default_mapping_path():
    """The mapping gaps/evaluate use when none is given: the LLM run if it exists, else the baseline."""
    for backend in ("ollama", "retrieval"):
        if mapping_path(backend).exists():
            return mapping_path(backend)
    raise FileNotFoundError("No mapping yet. Run: python run.py map --backend ollama (or retrieval)")


def review_priority(confidence: float, domain: str) -> str:
    if domain in SAFETY_DOMAINS:
        return "High (safety-relevant domain)"
    if confidence < 0.6:
        return "High (low confidence)"
    return "Normal"


def run(backend: str = "ollama", model: str | None = None, base_url: str | None = None,
        per_family: int = 5, client=None) -> tuple[pd.DataFrame, dict]:
    catalog = load_catalog()
    controls = load_controls()
    retriever = Retriever(catalog, controls)
    by_id = catalog.set_index("req_id")

    if backend == "ollama":
        client = client or OllamaClient(model=model, base_url=base_url)
        client.check()

    rows, log_controls = [], []
    started = time.perf_counter()
    for _, ctl in controls.iterrows():
        cands = retriever.candidates(ctl.text, per_family=per_family)
        flags = scan_for_injection(ctl.text)
        entry = {"control_id": ctl.control_id, "candidates": len(cands), "injection_flags": flags,
                 "rejected_ids": [], "parse_error": None, "seconds": 0.0}

        if backend == "retrieval":
            chosen = Retriever.select(cands)
            picks = [{"req_id": r.req_id, "confidence": round(min(1.0, r.similarity * 2.5), 3),
                      "rationale": f"Text similarity {r.similarity:.2f}"} for r in chosen.itertuples()]
        else:
            prompt = build_user_prompt(ctl, cands)
            picks = []
            for attempt in range(2):  # one retry if the reply is not valid JSON
                reply, seconds = client.chat(SYSTEM_PROMPT, prompt)
                entry["seconds"] += round(seconds, 2)
                try:
                    picks, rejected = validate_mappings(extract_json(reply), set(cands.req_id))
                    entry["rejected_ids"] = rejected
                    entry["parse_error"] = None
                    break
                except (ValueError, json.JSONDecodeError) as exc:
                    entry["parse_error"] = str(exc)
            print(f"  {ctl.control_id}: {len(picks)} mappings, {len(entry['rejected_ids'])} rejected, "
                  f"{entry['seconds']:.1f}s")

        sim = dict(zip(cands.req_id, cands.similarity))
        for p in picks:
            req = by_id.loc[p["req_id"]]
            rows.append({
                "control_id": ctl.control_id, "control_name": ctl.control_name, "control_status": ctl.status,
                "family": req.family, "framework": req.framework, "req_id": p["req_id"],
                "match_key": req.match_key, "title": req.title, "confidence": p["confidence"],
                "similarity": sim.get(p["req_id"], 0.0), "rationale": p["rationale"],
                "method": backend if backend == "retrieval" else f"ollama:{client.model}",
                "review_priority": review_priority(p["confidence"], ctl.domain),
                "human_decision": "", "reviewer": "", "review_note": "",
            })
        entry["mappings"] = len(picks)
        log_controls.append(entry)

    runtime = time.perf_counter() - started
    mapping = pd.DataFrame(rows)
    log = {
        "backend": backend,
        "model": client.model if backend == "ollama" else None,
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runtime_seconds": round(runtime, 2),
        "controls": len(controls),
        "mappings": len(mapping),
        "rejected_ids_total": sum(len(c["rejected_ids"]) for c in log_controls),
        "parse_failures": sum(1 for c in log_controls if c["parse_error"]),
        "injection_flagged_controls": [c["control_id"] for c in log_controls if c["injection_flags"]],
        "per_control": log_controls,
    }
    return mapping, log


def keep_previous_decisions(mapping: pd.DataFrame, path) -> pd.DataFrame:
    """Carry human review decisions over from an earlier run of the same backend."""
    if not path.exists() or mapping.empty:
        return mapping
    old = pd.read_csv(path, dtype=str, keep_default_na=False)
    if not set(REVIEW_COLUMNS) <= set(old.columns):
        return mapping
    old = old[old.human_decision != ""][["control_id", "req_id"] + REVIEW_COLUMNS]
    merged = mapping.drop(columns=REVIEW_COLUMNS).merge(old, on=["control_id", "req_id"], how="left")
    return merged.fillna({c: "" for c in REVIEW_COLUMNS})


def main(backend: str = "ollama", model: str | None = None, base_url: str | None = None) -> pd.DataFrame:
    mapping, log = run(backend=backend, model=model, base_url=base_url)
    MAPPING_DIR.mkdir(parents=True, exist_ok=True)
    path = mapping_path(backend)
    mapping = keep_previous_decisions(mapping, path)
    mapping.to_csv(path, index=False)
    (MAPPING_DIR / f"run_log_{backend}.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"{log['mappings']} mappings for {log['controls']} controls in {log['runtime_seconds']}s "
          f"({log['rejected_ids_total']} hallucinated IDs rejected, {log['parse_failures']} parse failures)")
    print(f"Written: {path.relative_to(OUTPUTS.parent)}. Review it: fill human_decision with accept or reject.")
    return mapping
