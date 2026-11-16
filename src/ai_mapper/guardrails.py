"""Guardrails around the LLM, one per AI governance risk the project brief lists.

  Hallucination     -> validate_mappings drops any requirement ID that was not in the shortlist;
                       real IDs in the wrong format are repaired first (resolve_id) and counted
  Prompt injection  -> scan_for_injection flags instruction-like text inside control data, and the
                       prompt fences data in tags and tells the model to treat it as data only
  Data leakage      -> assert_local_endpoint refuses to send register data to a non-local host
  Over-reliance     -> every row carries human_decision, and gap analysis can be limited to
                       human-approved rows (--approved-only)
"""
from __future__ import annotations

import json
import re
from urllib.parse import urlparse

INJECTION_PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|rules)",
    r"disregard (the )?(system|previous) (prompt|instructions)",
    r"you are now",
    r"system prompt",
    r"mark (this|all) (control|requirements?) as (compliant|implemented|satisfied)",
    r"</?(system|assistant|instructions?)>",
    r"respond only with",
]

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}


def scan_for_injection(text: str) -> list[str]:
    hits = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            hits.append(pattern)
    return hits


def assert_local_endpoint(url: str, allow_remote: bool = False) -> None:
    host = urlparse(url).hostname or ""
    if host not in LOCAL_HOSTS and not allow_remote:
        raise PermissionError(
            f"Refusing to send PSR register data to {host}. The AI mapper only talks to a local "
            "Ollama server so confidential control data never leaves the machine. "
            "Set allow_remote=True only with CISO approval.")


def extract_json(text: str) -> dict:
    """Parse the model reply, tolerating code fences or text around the JSON object."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("no JSON object in model output")
    return json.loads(match.group(0))


def resolve_id(raw: str, allowed_ids: set[str]) -> str | None:
    """Match a model supplied ID to a shortlisted ID, tolerating formatting noise.

    Small models often return real IDs in the wrong shape, for example "ISO 27001 A.8.22",
    "A.8.2 | ISO 27001" or "PISF 2026 PISF-BDR". Those are repaired to the shortlisted ID.
    The match is on whole tokens (so "A.8.2" never matches inside "A.8.22") and the longest
    shortlisted ID found wins. Anything that matches no shortlisted ID is still rejected.
    """
    raw = " ".join(str(raw).split())
    if raw in allowed_ids:
        return raw
    # also accept IEC IDs given without the part prefix, e.g. "SR 5.1" for "62443-3-3 SR 5.1"
    aliases = {}
    for aid in allowed_ids:
        aliases[aid] = aid
        if aid.startswith("62443-3-3 "):
            aliases[aid.removeprefix("62443-3-3 ")] = aid
        if aid.startswith("CIS "):
            aliases["CIS Control " + aid.removeprefix("CIS ")] = aid
    hits = []
    for alias, aid in aliases.items():
        pattern = r"(?<![\w.])" + re.escape(alias) + r"(?!\w)(?!\.\d)"
        if re.search(pattern, raw, flags=re.IGNORECASE):
            hits.append((len(alias), aid))
    if not hits:
        return None
    hits.sort(reverse=True)
    best = [aid for length, aid in hits if length == hits[0][0]]
    return best[0] if len(set(best)) == 1 else None


def validate_mappings(payload: dict, allowed_ids: set[str]) -> tuple[list[dict], list[str], list[dict]]:
    """Return (clean mappings, rejected IDs, repaired IDs).

    Keeps only shortlisted IDs, repairs IDs that are shortlisted but badly formatted, clamps confidence.
    """
    clean, rejected, repaired, seen = [], [], [], set()
    items = payload.get("mappings", []) if isinstance(payload, dict) else []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        raw = str(item.get("req_id", "")).strip()
        rid = resolve_id(raw, allowed_ids)
        if rid is None:
            rejected.append(raw)
            continue
        if rid != raw:
            repaired.append({"raw": raw, "resolved": rid})
        if rid in seen:
            continue
        seen.add(rid)
        try:
            conf = float(item.get("confidence", 0.5))
        except (TypeError, ValueError):
            conf = 0.5
        clean.append({"req_id": rid, "confidence": min(max(conf, 0.0), 1.0),
                      "rationale": str(item.get("rationale", "")).strip()[:300]})
    return clean, rejected, repaired
