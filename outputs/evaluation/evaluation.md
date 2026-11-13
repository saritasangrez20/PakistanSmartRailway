# AI automation evaluation

Backend: **retrieval**, run 2026-11-13T08:57:19+00:00

## AI Trust Score

| Metric | Result |
|---|---|
| Correct recommendations | 74 |
| Incorrect recommendations | 11 |
| Total | 85 |
| **Trust Score (accuracy)** | **74/85 = 87.1%** |
| Recall of the A2/A3 manual mapping | 50.0% |
| F1 | 63.5% |
| Hallucinated IDs rejected by guardrail | 0 |
| Suggestions flagged for priority human review | 60.9% |
| Suggestions verified by a human so far | 0.0% |

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
| OT (IEC 62443 / SP 800-82) | 14 | 9 | 64.3 | 9 | 4 | 44.4 |
| PISF 2026 | 23 | 22 | 95.7 | 4 | 4 | 100.0 |

Gap analysis agreement with the human reference mapping: 122 of 235 requirements get the same status (51.9%).

Full error list: `outputs/evaluation/errors.csv`.
