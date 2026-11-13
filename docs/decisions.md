# Decisions and corrections

Where Assignments 1 to 3 disagreed, one option was chosen and applied everywhere.

## Corrections to the assignments

| # | Issue | Decision |
|---|---|---|
| 1 | AST-03 RTO was 2 hrs in the A3 BC/DR table but 8 hrs in the A3 incident (61 hrs actual, 53 hrs over target) | **8 hrs**. The incident arithmetic depends on it, so only the table value changes |
| 2 | A3 called R-05 "one of the four critical risks" | A1 has **five** Critical risks: R-03, R-05, R-06, R-09, R-10 |
| 3 | A3 said the scenario was built from the OT disruption and SCADA compromise rows | The scenario is ransomware on e-ticketing (R-05); the report should describe it that way |
| 4 | AST-08 (IoT sensors) was missing from the A3 RTO/RPO table | Added: **RTO 1 hr, RPO 5 mins**, the same as other operational field systems |
| 5 | A2 Section E had the "Audit Plan" heading and intro twice | Keep the second version only |

## Additions made for the project

| Item | Decision and reason |
|---|---|
| Control statuses | The **A2 statuses are the current baseline**. The A3 lessons learned ("CTL-02 moves from Gap to Implemented" and so on) are recorded as `planned_action`, because the incident was a simulation |
| CTL-25 | New control from the A3 lessons learned (exercise programme), status Gap, linked to R-05, R-12 and R-17 |
| R-08 and R-13 | Medium risks that A2 did not treat. Recorded as **Accept** (within appetite, reviewed annually), so their residual equals their inherent score |
| Target residual risk | Set per risk with a written rationale (`risks.csv`, `target_rationale`). Impact only drops where a control limits the damage (backups, encryption, PAM, validation) |
| R-14 and R-15 assets | A1 listed "all"; the register names the assets with the most exposure |
| Asset classification | Highest class of data the asset holds. A3 listed only AST-10's public pages as Public; the app also handles bookings and payment tokens, so AST-10 is Restricted. AST-05, 09, 11 and 15 were not in A3 and were classified for the project |
| Data inventory | Built from the A3 classification table (13 data sets) |
| Compliance register | One row per A2 heat map cell (78 cells, 60 applicable), giving 22.75 / 60 = 37.9% |
| Evidence register | One row per evidence item in the A2 control matrix, plus 9 programme level documents (A1 to A3). Availability follows control status (Implemented: Available, Partial: Partial, Gap: Not available) |
| Audit findings | 7 from the A2 audit plan (CTL-18 is an observation, not a finding) and 7 from the A3 post-incident review: 13 findings |
| Maturity and readiness | Scored from the registers with the evidence reference beside each score (`data/assessments/`) |

## Framework catalogs

* ISO 27001:2022 Annex A, CIS Controls v8, NIST CSF 2.0 categories, IEC 62443-3-3 SRs (plus 2-1 and
  2-4), NIST SP 800-82, NIST AI RMF categories and a COBIT 2019 subset. Titles follow each framework;
  the descriptions are short summaries written for retrieval, not official text.
* **PISF 2026 is a placeholder at domain level** (one requirement per A2 heat map domain). Replace
  `data/frameworks/pisf_2026.csv` with the official clauses when the document is available, then rerun.

## Reference mapping (ground truth)

`data/ground_truth/reference_mapping.csv` has 244 control to requirement pairs:

* 62 from the group's own work (A2 control matrix, plus CTL-25 from A3): the **primary** set, used for recall
* 182 added as a reviewer: other requirements a control clearly satisfies, used so the AI is not
  marked wrong for a valid mapping A2 did not list. **The group should review these rows**

Matching is done at the level A2 mapped at: ISO and CIS controls, IEC 62443 SRs, NIST CSF and AI RMF
functions, PISF domains. Where A2 wrote only "IEC 62443-3-3" for CTL-06, SR 3.4 and SR 3.5 were used.
