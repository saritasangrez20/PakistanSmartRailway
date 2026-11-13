# AI automation evaluation

Backend: **ollama**, model `qwen2.5:7b`, run 2026-11-13T13:54:08+00:00

## AI Trust Score

| Metric | Result |
|---|---|
| Correct recommendations | 59 |
| Incorrect recommendations | 15 |
| Total | 74 |
| **Trust Score (accuracy)** | **59/74 = 79.7%** |
| Recall of the A2/A3 manual mapping | 35.5% |
| F1 | 49.1% |
| Hallucinated IDs rejected by guardrail | 69 |
| Suggestions flagged for priority human review | 40.5% |
| Suggestions verified by a human so far | 100.0% |
| Human review: accepted / reviewed | 59/74 = 79.7% |

## Automation Gain (manual time is an ESTIMATE: replace it in data/assessments/automation_baseline.json)

| | Minutes |
|---|---|
| Manual mapping and gap analysis | 495 |
| AI runtime (measured) | 46.12 |
| Human review of AI output | 100 |
| AI assisted total | 146.1 |
| **Automation Gain** | **70.5%** |

## By framework

| Framework | Recommended | Correct | Trust % | A2/A3 mappings | Found | Recall % |
|---|---|---|---|---|---|---|
| CIS Controls | 30 | 24 | 80.0 | 18 | 12 | 66.7 |
| COBIT | 6 | 2 | 33.3 | 1 | 1 | 100.0 |
| ISO 27001 | 4 | 4 | 100.0 | 20 | 3 | 15.0 |
| NIST AI RMF | 0 | 0 | 0.0 | 5 | 0 | 0.0 |
| NIST CSF | 3 | 1 | 33.3 | 5 | 1 | 20.0 |
| OT (IEC 62443 / SP 800-82) | 7 | 7 | 100.0 | 9 | 2 | 22.2 |
| PISF 2026 | 24 | 21 | 87.5 | 4 | 3 | 75.0 |

Gap analysis agreement with the human reference mapping: 112 of 235 requirements get the same status (47.7%).

## Backend comparison

| Backend | Trust % | Recall % | F1 % | Runtime (s) |
|---|---|---|---|---|
| retrieval | 89.4 | 50.0 | 64.1 | 0.12 |
| ollama | 79.7 | 35.5 | 49.1 | 2767.01 |

Full error list: `outputs/evaluation/errors.csv`.
