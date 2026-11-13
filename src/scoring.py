"""Course scoring system: turns the registers into the real numbers for the report and dashboard.

Formulas (from the project brief)
    Risk                 = Likelihood x Impact
    Control effectiveness = Effective controls / Applicable controls x 100
    Compliance           = Satisfied requirements / Applicable requirements x 100
    Governance maturity  = sum of capability scores / number of capabilities
    AI readiness         = Obtained score / Maximum score x 10
    Automation gain      = (Manual time - AI time) / Manual time x 100   (see evaluate.py)

Project rules (fixed so every number can be traced)
    * A control counts as effective only when its status is Implemented. Partial is reported
      separately as the weighted figure, never as the headline.
    * Current residual risk moves each risk from inherent towards its target residual in proportion
      to how much of its control set is in place today (Implemented 1, Partial 0.5, Gap 0):
          current = inherent - (inherent - target) x average credit, rounded half up, per L and I.
    * Readiness checklists score Y = 1, P = 0.5, N = 0.

Run:  python run.py score
"""
from __future__ import annotations

import json
import math

import pandas as pd

from .config import (COMPLIANCE_WEIGHTS, MATURITY_BANDS, OUTPUTS, READINESS_CREDIT, STATUS_CREDIT,
                     rating_for, split_ids)
from .registers import load_registers


def round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


def control_credit(control_ids: list[str], status: dict[str, str]) -> float:
    if not control_ids:
        return 0.0
    return sum(STATUS_CREDIT[status[c]] for c in control_ids) / len(control_ids)


def score_risks(regs) -> pd.DataFrame:
    status = dict(zip(regs["controls"].control_id, regs["controls"].status))
    rows = []
    for _, r in regs["risks"].iterrows():
        ctl = split_ids(r.control_ids)
        credit = control_credit(ctl, status)
        cur_l = round_half_up(r.likelihood - (r.likelihood - r.target_likelihood) * credit)
        cur_i = round_half_up(r.impact - (r.impact - r.target_impact) * credit)
        rows.append({
            "risk_id": r.risk_id, "risk_title": r.risk_title, "risk_scenario": r.risk_scenario, "risk_owner": r.risk_owner,
            "treatment": r.treatment, "control_ids": r.control_ids,
            "likelihood": r.likelihood, "impact": r.impact,
            "inherent_score": r.inherent_score, "inherent_rating": r.inherent_rating,
            "control_credit": round(credit, 3),
            "current_likelihood": cur_l, "current_impact": cur_i,
            "current_score": cur_l * cur_i, "current_rating": rating_for(cur_l * cur_i),
            "target_likelihood": r.target_likelihood, "target_impact": r.target_impact,
            "target_score": r.target_score, "target_rating": r.target_rating,
        })
    return pd.DataFrame(rows)


def compute(regs=None) -> dict:
    regs = regs or load_registers()
    risks = score_risks(regs)
    controls = regs["controls"]
    status = dict(zip(controls.control_id, controls.status))
    rating_order = ["Critical", "High", "Medium", "Low"]

    # Risk
    risk = {
        "total_risks": len(risks),
        "inherent_by_rating": {k: int((risks.inherent_rating == k).sum()) for k in rating_order},
        "current_by_rating": {k: int((risks.current_rating == k).sum()) for k in rating_order},
        "target_by_rating": {k: int((risks.target_rating == k).sum()) for k in rating_order},
        "high_critical_inherent": int(risks.inherent_rating.isin(["High", "Critical"]).sum()),
        "high_critical_current": int(risks.current_rating.isin(["High", "Critical"]).sum()),
        "critical_inherent": int((risks.inherent_rating == "Critical").sum()),
        "avg_inherent": round(risks.inherent_score.mean(), 2),
        "avg_current": round(risks.current_score.mean(), 2),
        "avg_target": round(risks.target_score.mean(), 2),
        "risk_reduction_to_date_pct": round((1 - risks.current_score.sum() / risks.inherent_score.sum()) * 100, 1),
        "risk_reduction_planned_pct": round((1 - risks.target_score.sum() / risks.inherent_score.sum()) * 100, 1),
    }
    top = risks.sort_values(["current_score", "inherent_score", "impact"], ascending=False).head(5)
    risk["top5"] = [{"risk_id": r.risk_id, "title": r.risk_title, "inherent": int(r.inherent_score),
                     "current": int(r.current_score), "rating": r.current_rating} for r in top.itertuples()]

    # Controls
    n = len(controls)
    counts = {s: int((controls.status == s).sum()) for s in ("Implemented", "Partial", "Gap")}
    weighted = sum(STATUS_CREDIT[s] * c for s, c in counts.items())
    critical_risks = set(risks[risks.inherent_rating == "Critical"].risk_id)
    critical_gaps = [c.control_id for c in controls.itertuples()
                     if c.status == "Gap" and set(split_ids(c.risk_ids)) & critical_risks]
    ctl = {
        "total_controls": n, "by_status": counts,
        "effectiveness_pct": round(counts["Implemented"] / n * 100, 1),
        "effectiveness_weighted_pct": round(weighted / n * 100, 1),
        "critical_control_gaps": len(critical_gaps), "critical_control_gap_ids": critical_gaps,
        "all_gap_ids": list(controls[controls.status == "Gap"].control_id),
    }

    # Recommendations: controls not yet implemented, ranked by the inherent risk they would reduce
    inherent = dict(zip(risks.risk_id, risks.inherent_score))
    recs = []
    for c in controls.itertuples():
        if c.status == "Implemented":
            continue
        exposure = sum(inherent[r] for r in split_ids(c.risk_ids))
        recs.append({"control_id": c.control_id, "control": c.control_name, "status": c.status,
                     "action": c.planned_action, "owner": c.owner, "risks": c.risk_ids,
                     "priority_score": round(exposure * (1 - STATUS_CREDIT[c.status]), 1)})
    recs.sort(key=lambda x: x["priority_score"], reverse=True)

    # Compliance (A2 heat map, domain x framework)
    comp = regs["compliance"]
    app = comp[comp.applicable == "Y"]
    satisfied = app.rating.map(COMPLIANCE_WEIGHTS).sum()
    by_fw = {}
    for fw, g in app.groupby("framework", sort=False):
        by_fw[fw] = round(g.rating.map(COMPLIANCE_WEIGHTS).sum() / len(g) * 100, 1)
    by_domain = {}
    for d, g in app.groupby("domain", sort=False):
        by_domain[d] = round(g.rating.map(COMPLIANCE_WEIGHTS).sum() / len(g) * 100, 1)
    compliance = {"satisfied": float(satisfied), "applicable": len(app),
                  "compliance_pct": round(satisfied / len(app) * 100, 1),
                  "by_rating": {k: int((app.rating == k).sum()) for k in COMPLIANCE_WEIGHTS},
                  "by_framework_pct": by_fw, "by_domain_pct": by_domain}

    # Maturity
    mat = regs["maturity"]
    m = round(mat.score.sum() / len(mat), 2)
    band = next(name for floor, name in MATURITY_BANDS if m >= floor)
    maturity = {"score": m, "status": band, "target_year3": round(mat.target_year3.astype(float).mean(), 2),
                "by_capability": dict(zip(mat.capability, mat.score.astype(float)))}

    # Readiness
    rd = regs["readiness"]
    readiness = {}
    for area, g in rd.groupby("area"):
        got = g.status.map(READINESS_CREDIT).sum()
        readiness[area] = {"obtained": float(got), "maximum": len(g), "pct": round(got / len(g) * 100, 1)}
    readiness["AI"]["score_out_of_10"] = round(readiness["AI"]["obtained"] / readiness["AI"]["maximum"] * 10, 2)

    # Audit
    af = regs["audit_findings"]
    findings = af[af.severity != "Observation"]
    audit = {"findings": len(findings), "observations": int((af.severity == "Observation").sum()),
             "by_severity": {k: int((findings.severity == k).sum()) for k in ("Critical", "High", "Medium", "Low")},
             "open": int((findings.status == "Open").sum())}

    # Evidence
    ev = regs["evidence"]
    evidence = {"items": len(ev), "by_availability": ev.availability.value_counts().to_dict(),
                "available_pct": round((ev.availability == "Available").mean() * 100, 1),
                "audited_items": int((ev.audited == "Y").sum())}

    metrics = {"organisation": "Pakistan Smart Railways (PSR)", "risk": risk, "controls": ctl,
               "recommendations": recs[:5], "compliance": compliance, "maturity": maturity,
               "readiness": readiness, "audit": audit, "evidence": evidence}

    # AI automation KPIs, if the evaluation step has run
    eval_path = OUTPUTS / "evaluation" / "evaluation.json"
    if eval_path.exists():
        metrics["ai_automation"] = json.loads(eval_path.read_text(encoding="utf-8"))["summary"]
    return metrics, risks


def to_markdown(m: dict) -> str:
    r, c, cp, mt, rd = m["risk"], m["controls"], m["compliance"], m["maturity"], m["readiness"]
    lines = ["# PSR metrics (generated by scoring.py)", "",
             "## Risk", "",
             f"* Risks: {r['total_risks']}; inherent Critical {r['inherent_by_rating']['Critical']}, "
             f"High {r['inherent_by_rating']['High']}, Medium {r['inherent_by_rating']['Medium']}",
             f"* High/Critical risks: {r['high_critical_inherent']} inherent, {r['high_critical_current']} current",
             f"* Average risk score: inherent {r['avg_inherent']}/25, current {r['avg_current']}/25, "
             f"target {r['avg_target']}/25",
             f"* Risk reduced so far: {r['risk_reduction_to_date_pct']}%; planned: {r['risk_reduction_planned_pct']}%",
             "", "## Controls", "",
             f"* {c['total_controls']} controls: {c['by_status']}",
             f"* Control effectiveness: {c['effectiveness_pct']}% (weighted with Partial = 0.5: "
             f"{c['effectiveness_weighted_pct']}%)",
             f"* Critical control gaps: {c['critical_control_gaps']} ({', '.join(c['critical_control_gap_ids'])})",
             "", "## Compliance", "",
             f"* Compliance: {cp['satisfied']} / {cp['applicable']} = {cp['compliance_pct']}%",
             *[f"  * {k}: {v}%" for k, v in cp["by_framework_pct"].items()],
             "", "## Maturity and readiness", "",
             f"* Governance maturity: {mt['score']}/5 ({mt['status']}); Year 3 target {mt['target_year3']}/5",
             f"* IAM readiness {rd['IAM']['pct']}%, BC/DR readiness {rd['BCDR']['pct']}%, "
             f"incident readiness {rd['IR']['pct']}%",
             f"* AI governance readiness: {rd['AI']['score_out_of_10']}/10",
             "", "## Audit and evidence", "",
             f"* Audit findings: {m['audit']['findings']} {m['audit']['by_severity']} plus "
             f"{m['audit']['observations']} observation(s)",
             f"* Evidence items: {m['evidence']['items']}, available {m['evidence']['available_pct']}%",
             "", "## Top 5 risks (by current residual score)", ""]
    lines += [f"{i}. {t['risk_id']} {t['title']} (inherent {t['inherent']}, current {t['current']})"
              for i, t in enumerate(r["top5"], 1)]
    lines += ["", "## Top 5 recommendations (by risk exposure they address)", ""]
    lines += [f"{i}. {x['control_id']} {x['control']}: {x['action']}" for i, x in enumerate(m["recommendations"], 1)]
    if "ai_automation" in m:
        a = m["ai_automation"]
        lines += ["", "## AI automation", "",
                  f"* Trust score (accuracy): {a['trust_score_pct']}%",
                  f"* Automation gain: {a['automation_gain_pct']}%"]
    return "\n".join(lines) + "\n"


def main(quiet: bool = False) -> dict:
    metrics, risks = compute()
    OUTPUTS.mkdir(exist_ok=True)
    (OUTPUTS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (OUTPUTS / "metrics.md").write_text(to_markdown(metrics), encoding="utf-8")
    risks.to_csv(OUTPUTS / "risk_register_scored.csv", index=False)
    if not quiet:
        print(to_markdown(metrics))
        print("Written: outputs/metrics.json, outputs/metrics.md, outputs/risk_register_scored.csv")
    return metrics


if __name__ == "__main__":
    main()
