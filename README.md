# Pakistan Smart Railways (PSR): Information Assurance, GRC and AI automation

**New to the project? Start with [docs/HANDOVER.md](docs/HANDOVER.md)** (what is done, results, and the to do list).

Final project for CY3003 Information Assurance. PSR is a hypothetical smart railway (IT, OT, cloud, IoT
and AI) carried through Assignments 1 to 3. This repository holds the five master registers, the code
that turns them into the course metrics, the AI automation (control mapping and gap analysis on a local
Ollama LLM), its evaluation, and the one page CISO dashboard.

## Quick start (VS Code, Windows)

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
python run.py all --backend retrieval
```

That last command runs everything without an LLM and writes all outputs to `outputs/`. On macOS or
Linux activate with `source .venv/bin/activate` instead.

## Running the AI mapper on Ollama

1. Install Ollama from ollama.com, then pull a model (about 4.7 GB):

```bash
ollama pull qwen2.5:7b
```

2. Make sure Ollama is running (the desktop app starts it; otherwise run `ollama serve`).
3. Run the pipeline with the LLM backend:

```bash
python run.py all --backend ollama
```

A different model can be used with `--model llama3.1:8b` or the `OLLAMA_MODEL` variable. The mapper
only talks to a server on localhost, so register data never leaves the machine.

4. Review the AI output: open `outputs/mapping/ai_mapping_ollama.csv` and fill `human_decision` with
   `accept` or `reject` (plus `reviewer`). Then rerun the gap analysis on approved rows only:

```bash
python run.py gaps --approved-only
```

```bash
python run.py evaluate
```

```bash
python run.py dashboard
```

5. Time yourselves doing a manual mapping of a few controls and put the real minutes in
   `data/assessments/automation_baseline.json` (set `measured` to true). Until then the Automation
   Gain uses an estimate and the reports say so.

## Pipeline steps

| Step | Command | Output |
|---|---|---|
| 1. Validate registers | `python run.py validate` | `outputs/validation_report.md` (fails on any broken ID link) |
| 2. Score | `python run.py score` | `outputs/metrics.md`, `metrics.json`, `risk_register_scored.csv` |
| 3. AI mapping | `python run.py map --backend ollama` | `outputs/mapping/ai_mapping_<backend>.csv`, run log |
| 4. Gap analysis | `python run.py gaps` | `outputs/gap/` (status per requirement, gap register, summary) |
| 5. Evaluate | `python run.py evaluate` | `outputs/evaluation/evaluation.md`, `errors.csv` |
| 6. Dashboard | `python run.py dashboard` | `outputs/ciso_dashboard.html` and `.pdf` |

Tests: `python -m pytest -q` (includes a fake Ollama server, so the LLM path is tested without a model).

## Repository layout

```
data/
  registers/      the master registers
    assets.csv            Asset Register (15 assets, with classification and RTO/RPO)
    data_inventory.csv    Data inventory (13 data sets)
    risks.csv             Risk Register (17 risks, inherent and target residual)
    controls.csv          Control Register (CTL-01 to CTL-25)
    compliance.csv        Compliance Register (A2 heat map, 13 domains x 6 frameworks)
    evidence.csv          Evidence Register (68 items)
    audit_findings.csv    Audit findings (A2 audit plan and A3 post-incident review)
  assessments/    maturity scores, readiness checklists, automation time baseline
  frameworks/     requirement catalogs: ISO 27001, CIS v8, NIST CSF 2.0, IEC 62443 / SP 800-82,
                  NIST AI RMF, COBIT 2019, PISF 2026 (placeholder)
  ground_truth/   reference mapping used to grade the AI
src/
  registers.py    load and validate the registers
  scoring.py      course formulas (risk, CE, compliance, maturity, readiness)
  ai_mapper/      retrieval, Ollama client, prompts, guardrails, mapper, gap analysis
  evaluate.py     Trust Score, recall, Automation Gain
  dashboard.py    CISO dashboard
docs/             decisions log, AI Automation Card, AI governance of our own AI
outputs/          everything generated (safe to delete and regenerate)
scripts/          catalog builder
```

## Scoring rules used everywhere

| Measure | Formula |
|---|---|
| Risk | Likelihood x Impact (1 to 25); Critical 16+, High 10 to 15, Medium 5 to 9, Low 1 to 4 |
| Current residual risk | inherent minus (inherent minus target) x share of its controls in place (Implemented 1, Partial 0.5, Gap 0), per L and I, rounded half up |
| Control effectiveness | Implemented controls / all controls x 100 (weighted figure with Partial = 0.5 shown alongside) |
| Compliance | weighted satisfied cells / applicable cells x 100 (A2 weights: 1, 0.5, 0.25, 0) |
| Governance maturity | sum of 10 capability scores / 10; status band: 1.5+ Developing, 2.5+ Defined, 3.5+ Managed |
| Readiness | checklist items Y = 1, P = 0.5, N = 0; AI readiness = obtained / maximum x 10 |
| AI Trust Score | correct AI recommendations / total AI recommendations x 100 |
| Automation Gain | (manual minutes minus AI assisted minutes) / manual minutes x 100 |

See `docs/decisions.md` for every correction and assumption made while building the registers.
