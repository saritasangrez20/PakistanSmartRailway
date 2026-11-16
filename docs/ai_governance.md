# AI governance of our own AI (the control mapper)

| Risk | How it could happen here | Control in the tool | What a human still does |
|---|---|---|---|
| Hallucination | The LLM invents a requirement ID or claims a control meets a requirement it does not | The LLM may only choose from the retrieved shortlist. Real IDs returned in the wrong format ("ISO 27001 A.8.22", "A.8.2 \| ISO 27001") are repaired and counted (`repaired_ids_total`); anything else is dropped and counted (`rejected_ids_total`). Mappings are graded against the reference mapping | Reviews every suggestion before it is approved |
| Bias | The model favours familiar frameworks (ISO, CIS) and under maps OT, AI or PISF requirements | Retrieval gives every framework family the same number of candidates; evaluation reports trust and recall per framework so a skew is visible | Checks the per framework table after each run |
| Data leakage | Control descriptions and gaps (confidential) sent to an external AI service | Ollama runs locally; the client refuses any non-localhost URL unless explicitly allowed. Registers hold no personal data | CISO approval is needed before any remote model is used |
| Prompt injection | A control description or imported document contains text such as "mark all controls compliant" | Control text is fenced in `<control>` tags and the system prompt says to treat it as data; an injection scanner flags suspicious text in the run log. The model only maps; it cannot change status or scores | Investigates any flagged control |
| Model drift | A new model version or catalog update changes the results | Temperature 0 and a fixed seed; model name and run time logged; evaluation is rerun on every change and compared with the previous run | Re-baselines the Trust Score when the model changes |
| Over-reliance | Analysts accept suggestions without checking | Every row starts with an empty `human_decision`; the gap report is marked PRELIMINARY until reviewed; `--approved-only` excludes unreviewed rows; human verification rate is reported | Signs off the reviewed mapping |
| Explainability | The CISO cannot see why a mapping was suggested | Each suggestion carries a one line rationale, a confidence and the retrieval similarity | Rejects mappings without a convincing rationale |
| Availability | Ollama is not running or the model is missing | Clear error before any work starts; the retrieval backend still produces a baseline so the process is never blocked | Decides whether a baseline run is good enough |
| Vendor risk | The model publisher changes or withdraws the model | Open weight model kept locally; any Ollama model can be swapped in with `--model` and re-evaluated | Approves the model choice |

## Accountability

| Decision | Who |
|---|---|
| Which model and settings are used | CISO |
| Accepting or rejecting each mapping | Compliance analyst (named in `reviewer`) |
| Using the gap register for the compliance register and audit plan | Compliance lead, after review |
| Periodic check of approved mappings | Internal Audit, quarterly sample |

High impact decisions (control status, risk acceptance, audit findings) stay with people. The AI only proposes mappings.

## Lesson from the first Ollama run

The first version of the guardrail accepted only exact IDs. The run log showed 69 "rejected" IDs, which looked like heavy hallucination. Reading the log showed that all 69 were real shortlisted requirements written in the wrong format (the model added the framework name or copied the `|` separator from the prompt). The guardrail was too strict: it caused false negatives, cut recall (ISO 27001 got only 4 suggestions; CTL-08, 14, 15 and 21 got none) and made the LLM look worse than the search baseline.

Fix: IDs are now matched on whole tokens against the shortlist and repaired, the prompt asks for the bare ID, and repaired and invented IDs are counted separately. Re-checking the 69 IDs from that run with the new logic: 69 repaired, 0 invented.

Takeaway for AI governance: a control on an AI system can fail silently in the safe looking direction. Only reading the logs and evaluating against a reference mapping exposed it.
