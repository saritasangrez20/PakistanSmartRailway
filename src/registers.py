"""Load the master registers and check that every ID chain links correctly.

Chain checked: Asset -> Risk -> Control -> Compliance requirement -> Evidence,
plus the audit findings and data inventory that hang off it.

Run:  python run.py validate
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

from .config import (ASSESSMENTS, CONTROL_STATUSES, COMPLIANCE_WEIGHTS, OUTPUTS, READINESS_CREDIT,
                     REGISTERS, rating_for, split_ids)

REGISTER_FILES = {
    "assets": "assets.csv",
    "data_inventory": "data_inventory.csv",
    "risks": "risks.csv",
    "controls": "controls.csv",
    "compliance": "compliance.csv",
    "evidence": "evidence.csv",
    "audit_findings": "audit_findings.csv",
}

ID_PATTERNS = {
    "assets": ("asset_id", r"AST-\d{2}"),
    "data_inventory": ("data_id", r"DATA-\d{2}"),
    "risks": ("risk_id", r"R-\d{2}"),
    "controls": ("control_id", r"CTL-\d{2}"),
    "compliance": ("req_id", r"CMP-\d{2}"),
    "evidence": ("evidence_id", r"EV-\d{3}"),
    "audit_findings": ("finding_id", r"(AUD|PIR)-\d{2}"),
}

CLASSIFICATIONS = ("Public", "Internal", "Confidential", "Restricted", "Critical")


@dataclass
class Issue:
    severity: str  # ERROR breaks the chain, WARNING needs a look
    register: str
    record: str
    message: str


def load_registers() -> dict[str, pd.DataFrame]:
    regs = {name: pd.read_csv(REGISTERS / file, dtype=str, keep_default_na=False)
            for name, file in REGISTER_FILES.items()}
    regs["maturity"] = pd.read_csv(ASSESSMENTS / "maturity.csv", dtype=str, keep_default_na=False)
    regs["readiness"] = pd.read_csv(ASSESSMENTS / "readiness.csv", dtype=str, keep_default_na=False)
    for col in ("likelihood", "impact", "inherent_score", "target_likelihood", "target_impact", "target_score"):
        regs["risks"][col] = regs["risks"][col].astype(int)
    for col in ("criticality", "rto_minutes", "rpo_minutes"):
        regs["assets"][col] = regs["assets"][col].astype(int)
    regs["maturity"]["score"] = regs["maturity"]["score"].astype(float)
    return regs


def validate(regs: dict[str, pd.DataFrame]) -> list[Issue]:
    issues: list[Issue] = []

    def err(reg, rec, msg):
        issues.append(Issue("ERROR", reg, rec, msg))

    def warn(reg, rec, msg):
        issues.append(Issue("WARNING", reg, rec, msg))

    # 1. IDs: well formed and unique
    for name, (col, pattern) in ID_PATTERNS.items():
        ids = regs[name][col]
        for value in ids:
            if not re.fullmatch(pattern, value):
                err(name, value, f"{col} does not match {pattern}")
        for dup in ids[ids.duplicated()].unique():
            err(name, dup, f"duplicate {col}")

    asset_ids = set(regs["assets"].asset_id)
    risk_ids = set(regs["risks"].risk_id)
    control_ids = set(regs["controls"].control_id)

    # 2. Assets
    for _, a in regs["assets"].iterrows():
        if not 1 <= a.criticality <= 5:
            err("assets", a.asset_id, "criticality must be 1 to 5")
        if a.classification not in CLASSIFICATIONS:
            err("assets", a.asset_id, f"unknown classification {a.classification}")
        if a.rpo_minutes > a.rto_minutes:
            warn("assets", a.asset_id, "RPO is longer than RTO")
        if a.criticality == 5 and a.rto_minutes > 480:
            warn("assets", a.asset_id, "criticality 5 asset with an RTO over 8 hrs")

    # 3. Data inventory
    for _, d in regs["data_inventory"].iterrows():
        for aid in [d.primary_asset] + split_ids(d.other_assets):
            if aid not in asset_ids:
                err("data_inventory", d.data_id, f"unknown asset {aid}")
        if d.classification not in CLASSIFICATIONS:
            err("data_inventory", d.data_id, f"unknown classification {d.classification}")
    for _, a in regs["assets"].iterrows():
        held = regs["data_inventory"][regs["data_inventory"].primary_asset == a.asset_id]
        order = {c: i for i, c in enumerate(CLASSIFICATIONS)}
        if len(held) and held.classification.map(order).max() > order[a.classification]:
            warn("assets", a.asset_id, "holds data classified higher than the asset itself")

    # 4. Risks
    risks_by_control: dict[str, set[str]] = {}
    for _, r in regs["risks"].iterrows():
        for aid in split_ids(r.asset_ids):
            if aid not in asset_ids:
                err("risks", r.risk_id, f"unknown asset {aid}")
        for field in ("likelihood", "impact", "target_likelihood", "target_impact"):
            if not 1 <= r[field] <= 5:
                err("risks", r.risk_id, f"{field} must be 1 to 5")
        if r.inherent_score != r.likelihood * r.impact:
            err("risks", r.risk_id, f"inherent score {r.inherent_score} is not L x I = {r.likelihood * r.impact}")
        if not 1 <= r.inherent_score <= 25:
            err("risks", r.risk_id, f"inherent score {r.inherent_score} is outside 1 to 25")
        elif r.inherent_rating != rating_for(r.inherent_score):
            err("risks", r.risk_id, f"rating {r.inherent_rating} does not match the band for {r.inherent_score}")
        if r.target_score != r.target_likelihood * r.target_impact:
            err("risks", r.risk_id, "target score is not target L x target I")
        if not 1 <= r.target_score <= 25:
            err("risks", r.risk_id, f"target score {r.target_score} is outside 1 to 25")
        elif r.target_rating != rating_for(r.target_score):
            err("risks", r.risk_id, "target rating does not match its band")
        if r.target_score > r.inherent_score:
            err("risks", r.risk_id, "target residual score is higher than the inherent score")
        linked = split_ids(r.control_ids)
        for cid in linked:
            if cid not in control_ids:
                err("risks", r.risk_id, f"unknown control {cid}")
            risks_by_control.setdefault(cid, set()).add(r.risk_id)
        if r.inherent_rating in ("High", "Critical"):
            if r.treatment == "Accept" or not linked:
                err("risks", r.risk_id, f"{r.inherent_rating} risk has no mitigating control")
        if r.treatment == "Accept" and r.target_score != r.inherent_score:
            err("risks", r.risk_id, "accepted risk should keep its inherent score as residual")

    # 5. Controls (and the two way link with risks)
    domains = set(regs["compliance"].domain)
    for _, c in regs["controls"].iterrows():
        if c.status not in CONTROL_STATUSES:
            err("controls", c.control_id, f"unknown status {c.status}")
        if c.domain not in domains:
            err("controls", c.control_id, f"domain '{c.domain}' is not a compliance register domain")
        listed = set(split_ids(c.risk_ids))
        for rid in listed - risk_ids:
            err("controls", c.control_id, f"unknown risk {rid}")
        back = risks_by_control.get(c.control_id, set())
        for rid in listed - back:
            err("controls", c.control_id, f"lists {rid} but {rid} does not list this control")
        for rid in back - listed:
            err("controls", c.control_id, f"{rid} lists this control but the control does not list {rid}")
        if not listed:
            warn("controls", c.control_id, "control is not linked to any risk")
        if not c.framework_refs.strip():
            err("controls", c.control_id, "no framework reference")

    # 6. Compliance register
    for _, q in regs["compliance"].iterrows():
        if q.applicable == "Y":
            if q.rating not in COMPLIANCE_WEIGHTS:
                err("compliance", q.req_id, f"unknown rating {q.rating}")
            elif float(q.weight) != COMPLIANCE_WEIGHTS[q.rating]:
                err("compliance", q.req_id, "weight does not match its rating")
            for cid in split_ids(q.linked_controls):
                if cid not in control_ids:
                    err("compliance", q.req_id, f"unknown control {cid}")
            if not split_ids(q.linked_controls) and q.domain != "Risk management":
                warn("compliance", q.req_id, f"{q.domain} / {q.framework} has no linked control")
        elif q.rating != "N/A":
            err("compliance", q.req_id, "not applicable cell must be rated N/A")

    # 7. Evidence: every control needs at least one evidence item
    ev = regs["evidence"]
    for _, e in ev.iterrows():
        if e.control_id and e.control_id not in control_ids:
            err("evidence", e.evidence_id, f"unknown control {e.control_id}")
    for _, c in regs["controls"].iterrows():
        items = ev[ev.control_id == c.control_id]
        if items.empty:
            err("controls", c.control_id, "no evidence item in the evidence register")
        elif c.status == "Implemented" and (items.availability != "Available").any():
            err("evidence", c.control_id, "control is Implemented but some evidence is not available")

    # 8. Audit findings
    finding_ids = set(regs["audit_findings"].finding_id)
    for _, f in regs["audit_findings"].iterrows():
        if f.control_id not in control_ids:
            err("audit_findings", f.finding_id, f"unknown control {f.control_id}")
    for _, e in ev.iterrows():
        if e.audit_ref and e.audit_ref not in finding_ids:
            err("evidence", e.evidence_id, f"unknown audit reference {e.audit_ref}")

    # 9. Assessments
    for _, m in regs["maturity"].iterrows():
        if not 0 <= m.score <= 5:
            err("maturity", m.capability, "score must be 0 to 5")
    for _, r in regs["readiness"].iterrows():
        if r.status not in READINESS_CREDIT:
            err("readiness", r.item_id, f"status must be Y, P or N, got {r.status}")

    return issues


def write_report(issues: list[Issue], regs: dict[str, pd.DataFrame]) -> str:
    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]
    lines = ["# Register validation report", ""]
    lines.append("| Register | Records |")
    lines.append("|---|---|")
    for name in REGISTER_FILES:
        lines.append(f"| {name} | {len(regs[name])} |")
    lines += ["", f"**Result: {'PASS' if not errors else 'FAIL'}**, "
              f"{len(errors)} errors, {len(warnings)} warnings", ""]
    for title, group in (("Errors", errors), ("Warnings", warnings)):
        if group:
            lines += [f"## {title}", "", "| Register | Record | Message |", "|---|---|---|"]
            lines += [f"| {i.register} | {i.record} | {i.message} |" for i in group]
            lines.append("")
    text = "\n".join(lines)
    OUTPUTS.mkdir(exist_ok=True)
    (OUTPUTS / "validation_report.md").write_text(text, encoding="utf-8")
    return text


def main() -> int:
    regs = load_registers()
    issues = validate(regs)
    write_report(issues, regs)
    errors = [i for i in issues if i.severity == "ERROR"]
    for i in issues:
        print(f"{i.severity:7} {i.register}:{i.record}  {i.message}")
    print(f"\nValidation {'PASSED' if not errors else 'FAILED'}: {len(errors)} errors, "
          f"{len(issues) - len(errors)} warnings. Report: outputs/validation_report.md")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
