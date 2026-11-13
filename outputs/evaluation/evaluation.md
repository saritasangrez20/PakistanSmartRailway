# AI automation evaluation

Backend: **retrieval**, run 2026-11-13T14:18:39+00:00

## AI Trust Score

| Metric | Result |
|---|---|
| Correct recommendations | 76 |
| Incorrect recommendations | 9 |
| Total | 85 |
| **Trust Score (accuracy)** | **76/85 = 89.4%** |
| Recall of the A2/A3 manual mapping | 50.0% |
| F1 | 64.1% |
| Hallucinated IDs rejected by guardrail | 0 |
| Suggestions flagged for priority human review | 60.9% |
| Suggestions verified by a human so far | 0.0% |
| Human review: accepted / reviewed | 0/0 = 0.0% |

## Automation Gain (manual time is an ESTIMATE: replace it in data/assessments/automation_baseline.json)

| | Minutes |
|---|---|
| Manual mapping and gap analysis | 495 |
| AI runtime (measured) | 0.0 |
| Human review of AI output | 100 |
| AI assisted total | 100.0 |
| **Automation Gain** | **79.8%** |

## By framework

| Framework | Recommended | Correct | Trust % | A2/A3 mappings | Found | Recall % |
|---|---|---|---|---|---|---|
| CIS Controls | 13 | 13 | 100.0 | 18 | 8 | 44.4 |
| COBIT | 4 | 3 | 75.0 | 1 | 0 | 0.0 |
| ISO 27001 | 17 | 16 | 94.1 | 20 | 12 | 60.0 |
| NIST AI RMF | 4 | 2 | 50.0 | 5 | 2 | 40.0 |
| NIST CSF | 10 | 9 | 90.0 | 5 | 1 | 20.0 |
| OT (IEC 62443 / SP 800-82) | 14 | 10 | 71.4 | 9 | 4 | 44.4 |
| PISF 2026 | 23 | 23 | 100.0 | 4 | 4 | 100.0 |

Gap analysis agreement with the human reference mapping: 122 of 235 requirements get the same status (51.9%).

Full error list: `outputs/evaluation/errors.csv`.
