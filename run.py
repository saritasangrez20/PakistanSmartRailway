"""Single entry point for the PSR project pipeline.

Examples
    python run.py validate
    python run.py score
    python run.py map --backend ollama --model qwen2.5:7b
    python run.py gaps
    python run.py evaluate
    python run.py dashboard
    python run.py all --backend ollama
"""
from __future__ import annotations

import argparse
import sys


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PSR Information Assurance pipeline")
    parser.add_argument("step", choices=["validate", "score", "map", "gaps", "evaluate", "dashboard", "all"])
    parser.add_argument("--backend", choices=["ollama", "retrieval"], default="ollama",
                        help="AI mapper backend: local Ollama LLM, or retrieval only (no LLM)")
    parser.add_argument("--model", default=None, help="Ollama model name, default from OLLAMA_MODEL or qwen2.5:7b")
    parser.add_argument("--ollama-url", default=None, help="Ollama URL, default http://localhost:11434")
    parser.add_argument("--mapping", default=None,
                        help="gaps/evaluate: mapping CSV to use (default: the latest AI mapping)")
    parser.add_argument("--approved-only", action="store_true",
                        help="gaps: only use mappings a human marked as accept")
    parser.add_argument("--no-pdf", action="store_true", help="dashboard: skip the PDF export")
    args = parser.parse_args(argv)

    steps = ["validate", "score", "map", "gaps", "evaluate", "dashboard"] if args.step == "all" else [args.step]

    for step in steps:
        print(f"\n=== {step} ===")
        if step == "validate":
            from src import registers
            if registers.main() != 0:
                print("Fix the register errors before continuing.")
                return 1
        elif step == "score":
            from src import scoring
            scoring.main()
        elif step == "map":
            from src.ai_mapper import mapper
            mapper.main(backend=args.backend, model=args.model, base_url=args.ollama_url)
        elif step == "gaps":
            from src.ai_mapper import gap_analysis
            gap_analysis.main(mapping_path=args.mapping, approved_only=args.approved_only)
        elif step == "evaluate":
            from src import evaluate
            from src import scoring
            evaluate.main(mapping_path=args.mapping)
            scoring.main(quiet=True)  # refresh metrics with the AI KPIs
        elif step == "dashboard":
            from src import dashboard
            dashboard.main(pdf=not args.no_pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
