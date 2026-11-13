# AI automation evaluation

Backend: **ollama**, model `qwen2.5:7b`, run 2026-11-13T16:22:08+00:00

## AI Trust Score

| Metric | Result |
|---|---|
| Correct recommendations | 123 |
| Incorrect recommendations | 16 |
| Total | 139 |
| **Trust Score (accuracy)** | **123/139 = 88.5%** |
| Recall of the A2/A3 manual mapping | 72.6% |
| F1 | 79.8% |
| Real IDs in the wrong format, repaired by guardrail | 10 |
| Invented IDs rejected by guardrail | 2 |
| Suggestions flagged for priority human review | 29.5% |
| Suggestions verified by a human so far | 100.0% |
| Human review: accepted / reviewed | 121/139 = 87.1% |

## Automation Gain

| | Minutes |
|---|---|
| Manual mapping and gap analysis | 650 |
| AI runtime (measured) | 46.27 |
| Human review of AI output | 75 |
| AI assisted total | 121.3 |
| **Automation Gain** | **81.3%** |

## By framework

| Framework | Recommended | Correct | Trust % | A2/A3 mappings | Found | Recall % |
|---|---|---|---|---|---|---|
| CIS Controls | 28 | 27 | 96.4 | 18 | 15 | 83.3 |
| COBIT | 13 | 7 | 53.8 | 1 | 1 | 100.0 |
| ISO 27001 | 31 | 29 | 93.5 | 20 | 14 | 70.0 |
| NIST AI RMF | 5 | 3 | 60.0 | 5 | 3 | 60.0 |
| NIST CSF | 22 | 19 | 86.4 | 5 | 4 | 80.0 |
| OT (IEC 62443 / SP 800-82) | 8 | 8 | 100.0 | 9 | 4 | 44.4 |
| PISF 2026 | 32 | 30 | 93.8 | 4 | 4 | 100.0 |

Gap analysis agreement with the human reference mapping: 133 of 235 requirements get the same status (56.6%).

## Backend comparison

| Backend | Trust % | Recall % | F1 % | Runtime (s) |
|---|---|---|---|---|
| retrieval | 90.6 | 50.0 | 64.4 | 0.12 |
| ollama | 88.5 | 72.6 | 79.8 | 2776.15 |

Full error list: `outputs/evaluation/errors.csv`.
