# AI Automation Card: AI assisted control mapping and gap analysis

Figures below are from the reviewed Ollama run (qwen2.5:7b) in `outputs/evaluation/evaluation.md`.

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
| **Accuracy** | Graded against the reference mapping: AI Trust Score = correct / total recommendations, recall of the A2/A3 manual mapping, per framework scores, error list (result: 123/139 = 88.5% trust, 72.6% recall, F1 79.8%; reviewers accepted 121 of 139 suggestions = 87.1%. The search only baseline reached 90.6% trust but only 50.0% recall) |
| **Benefit** | Automation Gain = (manual minus AI assisted) / manual x 100 (result: 650 min manual against 121.3 min AI assisted, of which 46.3 min AI runtime and 75 min human review = 81.3%, timed by the group). Also full coverage of all seven frameworks instead of 2 to 3 per control, and a repeatable rerun whenever controls change |
| **Limitation** | Cannot judge whether a control is actually implemented (status comes from the register and audit). Works from short catalog summaries, not the full standard text. PISF 2026 is domain level only. A 7B local model still misses about a quarter of the manual mappings (OT recall 44%), suggests overly broad COBIT objectives (53.8% trust on COBIT), and returns real IDs in the wrong format, which the guardrail must repair (10 repaired, 2 invented and blocked) |
| **Governance** | Owner: CISO. The Compliance function approves mappings before they enter the compliance register; Internal Audit samples approved mappings each quarter. The AI never changes a control status or a risk score |
