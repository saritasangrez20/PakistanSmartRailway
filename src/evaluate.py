"""Evaluate the AI mapper: AI Trust Score, recall, error lists and Automation Gain.

Ground truth: data/ground_truth/reference_mapping.csv
    source A2 / A3   the mapping the group made by hand in the assignments (primary set)
    source Reviewer  further mappings a human reviewer accepts as correct (acceptable set)

Comparison is at the level each framework was mapped by hand (match_key): ISO 27001 and CIS
controls, IEC 62443 SRs, NIST CSF and AI RMF functions, PISF domains.

Metrics
    Trust Score (accuracy) = correct recommendations / total recommendations x 100
                             (correct = in the acceptable set; this is precision)
    Recall (primary)       = primary mappings the AI found / all primary mappings x 100
    Automation Gain        = (manual minutes - AI assisted minutes) / manual minutes x 100
                             AI assisted minutes = measured runtime + human review time

Run:  python run.py evaluate
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .ai_mapper.catalog import load_catalog
from .ai_mapper.mapper import MAPPING_DIR, default_mapping_path, mapping_path
from .config import ASSESSMENTS, GROUND_TRUTH, OUTPUTS

EVAL_DIR = OUTPUTS / "evaluation"


def pct(a: float, b: float) -> float:
    return round(a / b * 100, 1) if b else 0.0


def score_mapping(mapping: pd.DataFrame, reference: pd.DataFrame) -> dict:
    fam = load_catalog().drop_duplicates("match_key").set_index("match_key").family
    predicted = set(zip(mapping.control_id, mapping.match_key))
    acceptable = set(zip(reference.control_id, reference.match_key))
    primary_ref = reference[reference.source != "Reviewer"]
    primary = set(zip(primary_ref.control_id, primary_ref.match_key))

    correct = predicted & acceptable
    incorrect = predicted - acceptable
    found_primary = predicted & primary
    precision = pct(len(correct), len(predicted))
    recall = pct(len(found_primary), len(primary))
    f1 = round(2 * precision * recall / (precision + recall), 1) if precision + recall else 0.0

    per_family = []
    for family in sorted(set(fam)):
        p = {x for x in predicted if fam.get(x[1]) == family}
        a = {x for x in acceptable if fam.get(x[1]) == family}
        g = {x for x in primary if fam.get(x[1]) == family}
        per_family.append({"family": family, "recommended": len(p), "correct": len(p & a),
                           "trust_score_pct": pct(len(p & a), len(p)),
                           "primary": len(g), "primary_found": len(p & g), "recall_pct": pct(len(p & g), len(g))})

    errors = ([{"type": "False positive (not in acceptable set)", "control_id": c, "match_key": k}
               for c, k in sorted(incorrect)] +
              [{"type": "False negative (A2/A3 mapping missed)", "control_id": c, "match_key": k}
               for c, k in sorted(primary - predicted)])
    return {"recommended": len(predicted), "correct": len(correct), "incorrect": len(incorrect),
            "trust_score_pct": precision, "primary_total": len(primary), "primary_found": len(found_primary),
            "recall_primary_pct": recall, "f1_pct": f1, "per_family": per_family, "errors": errors}


def gap_agreement() -> dict | None:
    ai, ref = OUTPUTS / "gap" / "requirement_status.csv", OUTPUTS / "gap" / "reference" / "requirement_status.csv"
    if not (ai.exists() and ref.exists()):
        return None
    a = pd.read_csv(ai).set_index("req_id").compliance_status
    r = pd.read_csv(ref).set_index("req_id").compliance_status
    both = a.index.intersection(r.index)
    agree = int((a[both] == r[both]).sum())
    return {"requirements": len(both), "same_status": agree, "agreement_pct": pct(agree, len(both))}


def automation_gain(log: dict, controls: int) -> dict:
    base = json.loads((ASSESSMENTS / "automation_baseline.json").read_text(encoding="utf-8"))
    m, a = base["manual"], base["ai_assisted"]
    manual = m["mapping_minutes_per_control"] * controls + m["gap_analysis_minutes"]
    runtime_min = log["runtime_seconds"] / 60
    review = a["review_minutes_per_control"] * controls
    ai_total = runtime_min + review
    return {"manual_minutes": round(manual, 1), "ai_runtime_minutes": round(runtime_min, 2),
            "human_review_minutes": round(review, 1), "ai_assisted_minutes": round(ai_total, 1),
            "automation_gain_pct": pct(manual - ai_total, manual),
            "manual_measured": m.get("measured", False), "review_measured": a.get("measured", False)}


def evaluate(path: Path) -> dict:
    mapping = pd.read_csv(path, dtype=str, keep_default_na=False)
    reference = pd.read_csv(GROUND_TRUTH / "reference_mapping.csv", dtype=str)
    backend = path.stem.replace("ai_mapping_", "")
    log = json.loads((MAPPING_DIR / f"run_log_{backend}.json").read_text(encoding="utf-8"))
    scores = score_mapping(mapping, reference)
    reviewed = mapping[mapping.human_decision != ""]
    gain = automation_gain(log, log["controls"])
    summary = {
        "process": "Control mapping and gap analysis",
        "backend": backend, "model": log.get("model"), "run_at": log["run_at"],
        "controls": log["controls"], "suggestions": len(mapping),
        "trust_score_pct": scores["trust_score_pct"], "correct": scores["correct"],
        "incorrect": scores["incorrect"], "total": scores["recommended"],
        "recall_primary_pct": scores["recall_primary_pct"], "f1_pct": scores["f1_pct"],
        "hallucinated_ids_rejected": log["rejected_ids_total"], "parse_failures": log["parse_failures"],
        "injection_flagged_controls": len(log["injection_flagged_controls"]),
        "flagged_for_priority_review_pct": pct((mapping.review_priority != "Normal").sum(), len(mapping)),
        "human_verified_pct": pct(len(reviewed), len(mapping)),
        "human_rejected": int((reviewed.human_decision.str.lower() == "reject").sum()),
        "human_accepted": int((reviewed.human_decision.str.lower() == "accept").sum()),
        "human_trust_score_pct": pct((reviewed.human_decision.str.lower() == "accept").sum(), len(reviewed)),
        **gain,
        "human_approval": "Required",
    }
    return {"summary": summary, "per_family": scores["per_family"], "errors": scores["errors"],
            "gap_agreement": gap_agreement()}


def to_markdown(result: dict, comparison: list[dict]) -> str:
    s = result["summary"]
    est = "" if s["manual_measured"] else " (manual time is an ESTIMATE: replace it in data/assessments/automation_baseline.json)"
    lines = ["# AI automation evaluation", "",
             f"Backend: **{s['backend']}**" + (f", model `{s['model']}`" if s["model"] else "") + f", run {s['run_at']}", "",
             "## AI Trust Score", "",
             "| Metric | Result |", "|---|---|",
             f"| Correct recommendations | {s['correct']} |",
             f"| Incorrect recommendations | {s['incorrect']} |",
             f"| Total | {s['total']} |",
             f"| **Trust Score (accuracy)** | **{s['correct']}/{s['total']} = {s['trust_score_pct']}%** |",
             f"| Recall of the A2/A3 manual mapping | {s['recall_primary_pct']}% |",
             f"| F1 | {s['f1_pct']}% |",
             f"| Hallucinated IDs rejected by guardrail | {s['hallucinated_ids_rejected']} |",
             f"| Suggestions flagged for priority human review | {s['flagged_for_priority_review_pct']}% |",
             f"| Suggestions verified by a human so far | {s['human_verified_pct']}% |",
             f"| Human review: accepted / reviewed | {s['human_accepted']}/{s['human_accepted'] + s['human_rejected']} "
             f"= {s['human_trust_score_pct']}% |", "",
             "## Automation Gain" + est, "",
             "| | Minutes |", "|---|---|",
             f"| Manual mapping and gap analysis | {s['manual_minutes']} |",
             f"| AI runtime (measured) | {s['ai_runtime_minutes']} |",
             f"| Human review of AI output | {s['human_review_minutes']} |",
             f"| AI assisted total | {s['ai_assisted_minutes']} |",
             f"| **Automation Gain** | **{s['automation_gain_pct']}%** |", "",
             "## By framework", "",
             "| Framework | Recommended | Correct | Trust % | A2/A3 mappings | Found | Recall % |",
             "|---|---|---|---|---|---|---|"]
    lines += [f"| {f['family']} | {f['recommended']} | {f['correct']} | {f['trust_score_pct']} | {f['primary']} | "
              f"{f['primary_found']} | {f['recall_pct']} |" for f in result["per_family"]]
    if result["gap_agreement"]:
        g = result["gap_agreement"]
        lines += ["", f"Gap analysis agreement with the human reference mapping: {g['same_status']} of "
                  f"{g['requirements']} requirements get the same status ({g['agreement_pct']}%)."]
    if len(comparison) > 1:
        lines += ["", "## Backend comparison", "", "| Backend | Trust % | Recall % | F1 % | Runtime (s) |", "|---|---|---|---|---|"]
        lines += [f"| {c['backend']} | {c['trust_score_pct']} | {c['recall_primary_pct']} | {c['f1_pct']} | "
                  f"{c['runtime_seconds']} |" for c in comparison]
    lines += ["", "Full error list: `outputs/evaluation/errors.csv`."]
    return "\n".join(lines) + "\n"


def main(mapping_path: str | None = None) -> dict:
    path = Path(mapping_path) if mapping_path else default_mapping_path()
    result = evaluate(path)
    comparison = []
    for backend in ("retrieval", "ollama"):
        p = globals()["mapping_path"](backend)
        if p.exists():
            r = evaluate(p)["summary"]
            log = json.loads((MAPPING_DIR / f"run_log_{backend}.json").read_text(encoding="utf-8"))
            comparison.append({"backend": backend, "trust_score_pct": r["trust_score_pct"],
                               "recall_primary_pct": r["recall_primary_pct"], "f1_pct": r["f1_pct"],
                               "runtime_seconds": log["runtime_seconds"]})
    result["backend_comparison"] = comparison
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    (EVAL_DIR / "evaluation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    pd.DataFrame(result["errors"]).to_csv(EVAL_DIR / "errors.csv", index=False)
    text = to_markdown(result, comparison)
    (EVAL_DIR / "evaluation.md").write_text(text, encoding="utf-8")
    print(text)
    return result
