# AI Automation Card: AI assisted control mapping and gap analysis

Figures below are from the latest run in `outputs/evaluation/evaluation.md`. The numbers in brackets
are from the offline retrieval baseline; update them after the Ollama run.

| Item | Answer |
|---|---|
| **IA phase** | Framework mapping and compliance (gap analysis), feeding the control matrix, compliance register and audit plan |
| **Existing problem** | Mapping 25 controls to seven frameworks (235 requirements) by hand is slow and inconsistent: A2 mapped each control to only 2 or 3 requirements, and PISF, COBIT and NIST CSF were covered unevenly. Redoing it after every control change is not realistic |
| **Input** | Control Register (`controls.csv`: name, description, domain, evidence) and framework requirement catalogs (`data/frameworks/`). No personal data |
| **AI method** | Hybrid: TF-IDF retrieval shortlists 5 candidates per framework, then a local LLM on Ollama (`qwen2.5:7b`, temperature 0) selects the requirements each control satisfies, with confidence and a rationale. A retrieval only rule is the no-LLM baseline |
| **Processing** | For each control: retrieve candidates, prompt the LLM with the control fenced as data, validate the JSON reply against the shortlist, then compute requirement status from control status (Implemented: Satisfied, Partial: Partially satisfied, Gap: Gap) and rank gaps by the inherent risk they leave open |
| **Output** | `ai_mapping_ollama.csv` (suggested mappings for review), `gap_register.csv` (ranked gaps), `framework_summary.csv` (coverage and compliance per framework), evaluation report |
| **Human role** | An analyst accepts or rejects every suggestion (`human_decision`). Mappings in safety relevant domains (OT, network segmentation, AI) and low confidence ones are flagged for priority review. Only approved rows feed the final gap analysis (`--approved-only`) |
| **Security risk** | Hallucinated requirements, prompt injection through control text, data leakage to an external AI service, over-reliance. See `ai_governance.md` |
| **Accuracy** | Graded against the reference mapping: AI Trust Score = correct / total recommendations, recall of the A2/A3 manual mapping, per framework scores, error list (baseline: 74/85 = 87.1% trust, 50.0% recall) |
| **Benefit** | Automation Gain = (manual minus AI assisted) / manual x 100 (baseline: 8.2 hrs manual against 1.7 hrs with review = 79.8%, manual time estimated). Also full coverage of all seven frameworks instead of 2 to 3 per control, and a repeatable rerun whenever controls change |
| **Limitation** | Cannot judge whether a control is actually implemented (status comes from the register and audit). Works from short catalog summaries, not the full standard text. PISF 2026 is domain level only. A 7B local model misses some valid mappings and can be overly generous on broad requirements |
| **Governance** | Owner: CISO. The Compliance function approves mappings before they enter the compliance register; Internal Audit samples approved mappings each quarter. The AI never changes a control status or a risk score |
