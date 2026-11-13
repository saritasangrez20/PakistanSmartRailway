"""Minimal client for a local Ollama server (https://ollama.com).

Setup on your machine:
    1. Install Ollama, then:  ollama pull qwen2.5:7b
    2. Ollama runs a server on http://localhost:11434 (start it with `ollama serve` if needed)
"""
from __future__ import annotations

import os
import time

import requests

from .guardrails import assert_local_endpoint

DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"


class OllamaUnavailable(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, model: str | None = None, base_url: str | None = None, timeout: int = 300,
                 allow_remote: bool = False):
        self.model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
        self.base_url = (base_url or os.environ.get("OLLAMA_URL", DEFAULT_URL)).rstrip("/")
        self.timeout = timeout
        assert_local_endpoint(self.base_url, allow_remote=allow_remote)

    def check(self) -> None:
        """Fail early with a clear message if Ollama is not running or the model is missing."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaUnavailable(
                f"Cannot reach Ollama at {self.base_url} ({exc}). Start it with `ollama serve`, "
                "or run the offline baseline with --backend retrieval.") from exc
        names = {m.get("name", "") for m in resp.json().get("models", [])}
        if self.model not in names and f"{self.model}:latest" not in names:
            raise OllamaUnavailable(
                f"Model '{self.model}' is not pulled. Run: ollama pull {self.model}  "
                f"(available: {', '.join(sorted(names)) or 'none'})")

    def chat(self, system: str, user: str) -> tuple[str, float]:
        """Send one chat turn and return (reply text, seconds taken). Temperature 0 for repeatability."""
        body = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0, "seed": 42},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }
        start = time.perf_counter()
        resp = requests.post(f"{self.base_url}/api/chat", json=body, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["message"]["content"], time.perf_counter() - start
