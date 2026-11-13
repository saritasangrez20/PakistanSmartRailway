"""Requirement level gap analysis built on a control to requirement mapping.

For every requirement in the framework catalogs:
    best status of the controls mapped to it  ->  compliance status
        Implemented  -> Satisfied           (1.0)
        Partial      -> Partially satisfied (0.5)
        Gap          -> Gap, control planned (0.0)
        no control   -> Not addressed       (0.0)  candidate for the Statement of Applicability review

The gap register lists every Partial and Gap requirement, ranked by the highest inherent risk
score among the risks its controls treat, so the worst exposure comes first.

Run:  python run.py gaps                     (uses the AI mapping, flagged PRELIMINARY until reviewed)
      python run.py gaps --approved-only     (only rows a human marked accept)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import GROUND_TRUTH, OUTPUTS, REGISTERS, STATUS_CREDIT, split_ids
from .catalog import load_catalog
from .mapper import default_mapping_path

GAP_DIR = OUTPUTS / "gap"
STATUS_LABEL = {"Implemented": "Satisfied", "Partial": "Partially satisfied", "Gap": "Gap (control planned)"}
STATUS_RANK = {"Implemented": 2, "Partial": 1, "Gap": 0}


def reference_as_mapping() -> pd.DataFrame:
    """Turn the reference mapping (match keys) into requirement rows so it can be analysed the same way."""
    ref = pd.read_csv(GROUND_TRUTH / "reference_mapping.csv", dtype=str)
    cat = load_catalog()[["req_id", "match_key", "framework", "family", "title"]]
    rows = ref.merge(cat.drop(columns="framework"), on="match_key", how="left")
    # function level keys (e.g. CSF DETECT) cover several categories; keep one row per category
    return rows.assign(human_decision="accept")


def analyse(mapping: pd.DataFrame, approved_only: bool = False) -> dict[str, pd.DataFrame]:
    controls = pd.read_csv(REGISTERS / "controls.csv", dtype=str, keep_default_na=False)
    risks = pd.read_csv(REGISTERS / "risks.csv", dtype=str, keep_default_na=False)
    status = dict(zip(controls.control_id, controls.status))
    ctl_risks = {c.control_id: split_ids(c.risk_ids) for c in controls.itertuples()}
    inherent = dict(zip(risks.risk_id, risks.inherent_score.astype(int)))

    used = mapping.copy()
    if approved_only:
        used = used[used.human_decision.str.lower() == "accept"]
    used = used[used.human_decision.str.lower() != "reject"]

    catalog = load_catalog()
    rows = []
    for req in catalog.itertuples():
        mapped = sorted(set(used[used.req_id == req.req_id].control_id))
        if mapped:
            best = max((status[c] for c in mapped), key=STATUS_RANK.get)
            label, score = STATUS_LABEL[best], STATUS_CREDIT[best]
            linked = sorted({r for c in mapped for r in ctl_risks[c]})
            exposure = max((inherent[r] for r in linked), default=0)
        else:
            label, score, linked, exposure = "Not addressed", 0.0, [], 0
        rows.append({"family": req.family, "framework": req.framework, "req_id": req.req_id,
                     "title": req.title, "mapped_controls": ";".join(mapped),
                     "control_statuses": ";".join(status[c] for c in mapped),
                     "compliance_status": label, "score": score,
                     "linked_risks": ";".join(linked), "max_inherent_risk": exposure})
    status_df = pd.DataFrame(rows)

    summary = []
    for family, g in status_df.groupby("family", sort=False):
        addressed = g[g.compliance_status != "Not addressed"]
        summary.append({
            "family": family, "requirements": len(g), "addressed": len(addressed),
            "satisfied": int((g.compliance_status == "Satisfied").sum()),
            "partial": int((g.compliance_status == "Partially satisfied").sum()),
            "gap": int((g.compliance_status == "Gap (control planned)").sum()),
            "not_addressed": int((g.compliance_status == "Not addressed").sum()),
            "coverage_pct": round(len(addressed) / len(g) * 100, 1),
            "compliance_of_addressed_pct": round(addressed.score.mean() * 100, 1) if len(addressed) else 0.0,
        })
    summary_df = pd.DataFrame(summary)

    gaps = status_df[status_df.compliance_status.isin(["Partially satisfied", "Gap (control planned)"])]
    gaps = gaps.sort_values(["max_inherent_risk", "score"], ascending=[False, True]).reset_index(drop=True)
    gaps.insert(0, "gap_id", [f"GAP-{i:03d}" for i in range(1, len(gaps) + 1)])
    not_addressed = status_df[status_df.compliance_status == "Not addressed"]
    return {"status": status_df, "summary": summary_df, "gaps": gaps, "not_addressed": not_addressed}


def write(result: dict, out_dir: Path, source: str, preliminary: bool) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    result["status"].to_csv(out_dir / "requirement_status.csv", index=False)
    result["summary"].to_csv(out_dir / "framework_summary.csv", index=False)
    result["gaps"].to_csv(out_dir / "gap_register.csv", index=False)
    result["not_addressed"].to_csv(out_dir / "not_addressed.csv", index=False)
    s, g = result["summary"], result["gaps"]
    lines = ["# Requirement level gap analysis", "",
             f"Mapping used: `{source}`", ""]
    if preliminary:
        lines += ["> **PRELIMINARY**: built on AI suggestions that a human has not yet approved. "
                  "Review the mapping file and rerun with `--approved-only` before relying on it.", ""]
    lines += ["| Framework | Requirements | Addressed | Satisfied | Partial | Gap | Not addressed | "
              "Coverage % | Compliance of addressed % |", "|---|---|---|---|---|---|---|---|---|"]
    for r in s.itertuples():
        lines.append(f"| {r.family} | {r.requirements} | {r.addressed} | {r.satisfied} | {r.partial} | {r.gap} | "
                     f"{r.not_addressed} | {r.coverage_pct} | {r.compliance_of_addressed_pct} |")
    lines += ["", f"## Top 15 gaps by risk exposure ({len(g)} in total)", "",
              "| Gap | Framework | Requirement | Status | Controls | Max inherent risk |", "|---|---|---|---|---|---|"]
    for r in g.head(15).itertuples():
        lines.append(f"| {r.gap_id} | {r.framework} | {r.req_id} {r.title} | {r.compliance_status} | "
                     f"{r.mapped_controls} | {r.max_inherent_risk} |")
    lines += ["", "Requirements no control addresses are listed in `not_addressed.csv`. Most are physical, "
              "HR or development controls outside the 25 controls in the register; review them for the "
              "Statement of Applicability rather than treating them all as gaps."]
    (out_dir / "gap_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(mapping_path: str | None = None, approved_only: bool = False) -> dict:
    path = Path(mapping_path) if mapping_path else default_mapping_path()
    mapping = pd.read_csv(path, dtype=str, keep_default_na=False)
    reviewed = (mapping.human_decision != "").all() if len(mapping) else False
    result = analyse(mapping, approved_only=approved_only)
    write(result, GAP_DIR, str(path.relative_to(OUTPUTS.parent)) if path.is_absolute() else str(path),
          preliminary=not (approved_only or reviewed))
    # Same analysis on the human reference mapping, so evaluation can compare the two
    ref = analyse(reference_as_mapping())
    write(ref, GAP_DIR / "reference", "data/ground_truth/reference_mapping.csv", preliminary=False)
    print(result["summary"].to_string(index=False))
    print(f"{len(result['gaps'])} gaps. Written: outputs/gap/ (and outputs/gap/reference/ for the human baseline)")
    return result
