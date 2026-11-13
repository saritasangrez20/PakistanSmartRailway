"""Guardrails around the LLM, one per AI governance risk the project brief lists.

  Hallucination     -> validate_mappings drops any requirement ID that was not in the shortlist
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


def validate_mappings(payload: dict, allowed_ids: set[str]) -> tuple[list[dict], list[str]]:
    """Return (clean mappings, rejected IDs). Keeps only shortlisted IDs, clamps confidence."""
    clean, rejected, seen = [], [], set()
    items = payload.get("mappings", []) if isinstance(payload, dict) else []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("req_id", "")).strip()
        if rid not in allowed_ids:
            rejected.append(rid)
            continue
        if rid in seen:
            continue
        seen.add(rid)
        try:
            conf = float(item.get("confidence", 0.5))
        except (TypeError, ValueError):
            conf = 0.5
        clean.append({"req_id": rid, "confidence": min(max(conf, 0.0), 1.0),
                      "rationale": str(item.get("rationale", "")).strip()[:300]})
    return clean, rejected
