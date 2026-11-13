"""Load framework catalogs and turn controls and requirements into text for retrieval and prompting."""
from __future__ import annotations

import re

import pandas as pd

from ..config import FRAMEWORKS, REGISTERS

# Framework families: SP 800-82 sits with IEC 62443 because A2 assessed them as one OT column.
FAMILY = {
    "ISO 27001": "ISO 27001",
    "CIS Controls": "CIS Controls",
    "NIST CSF": "NIST CSF",
    "IEC 62443": "OT (IEC 62443 / SP 800-82)",
    "NIST SP 800-82": "OT (IEC 62443 / SP 800-82)",
    "NIST AI RMF": "NIST AI RMF",
    "COBIT": "COBIT",
    "PISF 2026": "PISF 2026",
}

# Expand common abbreviations so word based retrieval can match them.
SYNONYMS = {
    r"\bmfa\b": "mfa multi-factor authentication secure authentication",
    r"\bpam\b": "pam privileged access management privileged access rights",
    r"\brbac\b": "rbac role based access control",
    r"\bjml\b": "joiner mover leaver access rights",
    r"\bsiem\b": "siem security monitoring logging",
    r"\bsoc\b": "soc security operations monitoring",
    r"\bdr\b": "disaster recovery continuity",
    r"\bapi(s)?\b": "api application",
    r"\bot\b": "ot operational technology industrial control system",
    r"\bit/ot\b": "it ot operational technology network zones",
    r"\biot\b": "iot devices sensors",
    r"\bai\b": "ai artificial intelligence",
    r"\bsast\b": "sast static application security testing",
    r"\bdast\b": "dast dynamic application security testing",
    r"\bscada\b": "scada industrial control system",
    r"\bvendor(s)?\b": "vendor supplier service provider third party",
    r"\bcontract(s)?\b": "contract agreement",
    r"\bbackup(s)?\b": "backup backups data recovery",
    r"\brestor(e|ation)\b": "restore recovery testing continuity",
    r"\bencryption\b": "encryption cryptography",
    r"\bdrift\b": "drift monitoring model performance over time",
    r"\bsegmentation\b": "segmentation segregation of networks zones",
    r"\bpatch(ing)?\b": "patching vulnerability management",
    r"\bphishing\b": "phishing email awareness",
}


def expand(text: str) -> str:
    out = text.lower()
    for pattern, extra in SYNONYMS.items():
        if re.search(pattern, out):
            out += " " + extra
    return out


def load_catalog() -> pd.DataFrame:
    frames = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in sorted(FRAMEWORKS.glob("*.csv"))]
    cat = pd.concat(frames, ignore_index=True)
    cat["family"] = cat.framework.map(FAMILY)
    if cat.family.isna().any():
        raise ValueError(f"unknown framework in catalogs: {set(cat[cat.family.isna()].framework)}")
    cat["text"] = cat.apply(lambda r: f"{r.title}. {r.description}. {r.group}", axis=1)
    return cat


def load_controls() -> pd.DataFrame:
    ctl = pd.read_csv(REGISTERS / "controls.csv", dtype=str, keep_default_na=False)
    ctl["text"] = ctl.apply(lambda r: f"{r.control_name}. {r.description}. Domain: {r.domain}. "
                                      f"Evidence: {r.evidence_required}.", axis=1)
    return ctl
