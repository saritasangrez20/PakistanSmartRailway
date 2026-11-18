---
title: "PSR Final Project: Demo Preparation"
subtitle: "CY3003 Information Assurance · Group 07 · Amna Ali, Sarita Sangrez, Subhan Umer"
---

# 1. Everything we have done and found

## The project in one sentence

We took Pakistan Smart Railways (PSR) from Assignments 1 to 3 and turned it into a working assurance programme: all the data sits in linked registers, code calculates every score, a local AI maps our controls to 7 security frameworks, and a dashboard shows the CISO where PSR stands.

## Step 1: The five master registers (the foundation)

Everything from A1 to A3 was moved into linked CSV files:

| Register | Contents |
|---|---|
| Assets | 15 assets (train control, signalling, ticketing, passenger database, cloud, AI engine and others) with classification and RTO/RPO |
| Risks | 17 risks with likelihood × impact, plus residual risk (new) |
| Controls | 25 controls (CTL-01 to CTL-25), each Implemented, Partial or Gap |
| Compliance | 60 framework × domain ratings from the A2 heat map |
| Evidence | 68 evidence items, plus 13 audit findings and a data inventory of 13 data sets |

Every item has an ID, and a validation script checks that every link holds: asset > risk > control > requirement > evidence > audit finding. It currently reports 0 errors.

**Corrections made to the assignments:**

* AST-03 (e-ticketing) RTO is 8 hrs
* There are 5 Critical risks, not 4 (R-03, R-05, R-06, R-09, R-10)
* The A3 scenario is ransomware on ticketing (R-05)
* AST-08 (IoT sensors) now has an RTO of 1 hr and RPO of 5 mins
* Governance fix: the CISO now reports to the CEO, not the CIO, and Internal Audit reports to a Board Audit Committee. Both changes are for independence.

## Step 2: PSR's security findings

| Measure | Result | Meaning |
|---|---|---|
| Overall status | **DEVELOPING**, maturity 1.9 / 5 | Basics exist; most security is not built or proven |
| Risks | 5 Critical, 10 High, 2 Medium | Serious exposure in OT, passenger data and ransomware |
| Average risk | 13.8 at the start, **11.9 now**, 7.2 after the plan | Today's controls cut risk 13%; the full plan cuts it 47% |
| Control effectiveness | **12%** (3 of 25 implemented) | Most controls are Partial or missing |
| Compliance | **37.9%** | AI governance (16.7%) and OT (27.8%) are the weakest frameworks |
| Audit findings | 13 (3 Critical), all open | |
| Evidence available | 25% | Most controls could not be proven to an auditor |
| Readiness | BC/DR 60%, incident response 45.5%, IAM 40%, AI governance 3.75 / 10 | |

**Key finding:** *PSR adopted technology faster than it secured it.* The weakest areas (OT, AI governance and supply chain, all scoring 1 out of 5) hold the Critical risks. In the A3 ransomware incident, every gap the attacker used was already recorded in our registers before the attack: the standing vendor account, the partial MFA, the dormant admin account and the missing database monitoring. PSR knew what was wrong but had not built the controls. Backups (CTL-18) were the one control that worked, and they are the reason the ransomware did not become permanent data loss.

**Top 5 recommendations** (ranked by the code, by the risk each would reduce):

1. CTL-07 MFA everywhere, including OT and vendor access
2. CTL-25 Incident and recovery exercise programme
3. CTL-12 Application and API security testing
4. CTL-02 Brokered, time-limited vendor access
5. CTL-01 Default-deny IT/OT segmentation

## Step 3: The AI automation

**The task:** map 25 controls to 235 requirements across ISO 27001, CIS, NIST CSF, IEC 62443, NIST AI RMF, COBIT and PISF 2026, then find the gaps. By hand this takes about 11 hours.

**How it works:**

1. Search shortlists the 5 best requirements per framework
2. A local LLM (qwen2.5:7b on Ollama) picks the real matches
3. A safety check blocks any ID that was not on the shortlist
4. A human reviews every suggestion

The model runs locally, so confidential data never leaves the machine.

**What happened:**

1. **First run:** it looked poor. Recall was 35.5% and the log reported "69 invented IDs".
2. **Investigation:** the logs showed all 69 were real requirements in the wrong format (for example `ISO 27001 A.8.22` instead of `A.8.22`). Our safety check was too strict and was throwing away correct answers.
3. **Fix and second run:** badly formatted IDs are repaired and anything else is still blocked. Only **2 truly invented IDs** remained.
4. **Review:** Sarita, Subhan and Amna reviewed all 139 suggestions and accepted 121.

**Final results:**

| Metric | Result |
|---|---|
| Trust Score (accuracy) | **88.5%** (123 / 139) |
| Trust Score on the frozen answer key | **79.9%** (111 / 139) |
| Recall of our A2 manual mapping | **72.6%** |
| Automation Gain | **71.5%** (650 min by hand against 185 min with AI and review) |
| No-LLM search baseline | 90.6% accurate but only 50% recall, so the LLM finds far more |
| Weak spots | COBIT (vague suggestions, 53.8% trust) and OT (misses specialist requirements, 44.4% recall) |

**Subhan's two corrections, and why they matter:**

1. **Frozen Trust Score.** During review we added 15 rows to the answer key, and 12 of them were the AI's own suggestions. Grading the AI against an answer key it helped write flatters it. Excluding those rows gives 79.9%. Both figures are reported, and the difference is a finding in itself.
2. **Review time per suggestion, not per control.** 139 suggestions at 1 minute each lowers the Automation Gain from 81% to an honest 71.5%. F1 was also removed, because precision and recall are measured against different answer sets.

**AI governance lessons:**

* A safety control on an AI can fail silently: ours made the AI look worse than it was
* An evaluation can be inflated without anyone noticing: the answer key problem
* Only reading the logs and evaluating honestly caught both, which is why a human approves every AI output

## Step 4: The report and the dashboard

**Final report** (`docs/FINAL_REPORT.md`, plus `.docx` and `.pdf`), 20 sections covering every deliverable in the brief, including:

* Architecture, governance (with the reporting fix) and three lines of defence
* The policy set, data flows, residual risk and the PISF mapping
* IAM with ABAC and an access review, data protection, BIA and DR
* The IR plan and SOC / SIEM / SOAR design
* Cloud shared responsibility, the OT Purdue model, quantum readiness (signed OT firmware moves to post-quantum signatures first)
* The AI section and a 3-year roadmap

**Interactive dashboard** (`outputs/ciso_dashboard.html`):

* An executive view plus 8 drill-down tabs
* A 5 × 5 heat map with Inherent, Current and Target tabs; clicking a cell filters the risks
* A detail drawer that walks asset > risk > control > evidence > audit finding
* Searchable registers, AI accuracy per framework, and dark mode
* The executive view prints as a one-page PDF

# 2. Work division

| Member | Owns | Dashboard tabs | Time |
|---|---|---|---|
| **Sarita** | Organisation, assets and data, risk register, residual risk, corrections to A1 to A3 | Executive view · Assets & data · Risk register | 0:00 to 2:00 |
| **Amna** | Control matrix, compliance assessment, audit plan and findings, evidence and readiness | Controls · Compliance · Audit & evidence | 2:00 to 4:00 |
| **Subhan** | AI automation and its evaluation, gap analysis, maturity and roadmap, report and dashboard | AI automation · Framework gaps · Maturity & roadmap | 4:00 to 6:00 |

The order follows the story: what PSR has and what can go wrong, then what PSR is doing about it and how well, then how we automated the analysis and where PSR goes next.

**Setup before starting:** open `outputs\ciso_dashboard.html` in Chrome or Edge, press F11 for full screen, choose light mode (button at the top right). Use the left sidebar to move between tabs. The speaker drives the mouse, or one person clicks while the speaker talks.

# 3. Demo script

## Sarita (0:00 to 2:00)

### Executive view (0:00 to 0:35)

**Show:** the top of the page, with the 12 measure cards.

> "We built an information assurance programme for Pakistan Smart Railways, a railway running IT, OT, cloud, IoT and AI systems. Every number on this dashboard is calculated by our code from five linked registers; nothing is typed in by hand. The headline: PSR is DEVELOPING, with governance maturity 1.9 out of 5. The average risk is 11.9 out of 25, and 14 of our 17 risks are still High or Critical."

### Assets & data (0:35 to 1:00)

**Click:** "Assets & data" in the sidebar. Point at "Assets by zone", then scroll to the asset inventory.

> "PSR protects 15 assets across IT, OT, cloud, IoT and AI, and 13 data sets. The most critical are the train control system and signalling, with a 15-minute recovery time objective. We also corrected the earlier assignments, for example setting e-ticketing's RTO to 8 hours."

### Risk register (1:00 to 2:00)

**Click:** "Risk register".

1. Point at the heat map on the **Inherent** tab, then click **Current**, then **Target**
2. Scroll to the register and click the **R-05** row. The drawer opens
3. Click **CTL-18** inside the drawer, then **Close**

> "We have 17 risks, 5 of them Critical. Watch the heat map: inherent, then current, then target. The average falls from 13.8 to 11.9 today, and to 7.2 once our plan is done. Every risk can be traced end to end. This is R-05, ransomware on ticketing: here's its score, the controls treating it, the assets exposed and the audit findings. Following CTL-18, the backups: it's implemented, the evidence is available, and it's the reason the ransomware in Assignment 3 didn't become permanent data loss. Amna will show how well the controls are working."

## Amna (2:00 to 4:00)

### Controls (2:00 to 2:45)

**Click:** "Controls". Point at "Status mix", then "The four that cannot wait", then "Implementation by domain".

> "PSR has 25 controls, but only 3 are fully implemented. Control effectiveness is therefore 12%, or 30% if partial controls count as half. These four are Gap controls sitting on Critical risks, so they can't wait: application and API security testing, database activity monitoring, secure cloud configuration, and an incident exercise programme. By domain, AI governance, cloud and supply chain are at 0%."

### Compliance (2:45 to 3:20)

**Click:** "Compliance". Point at "By domain", which is sorted weakest first.

> "We assessed compliance against ISO 27001, NIST CSF, CIS, IEC 62443, NIST AI RMF and PISF 2026. PSR scores 37.9%. The weakest domains are AI governance at 6% and supply chain at 15%; the strongest is risk management at 65%. So PSR documents risk well, but it hasn't built the controls in its most dangerous areas."

### Audit & evidence (3:20 to 4:00)

**Click:** "Audit & evidence". Point at "Findings by severity", "Evidence availability" and "Readiness checklists".

> "Our audit plan and the Assignment 3 incident review produced 13 findings, 3 of them Critical, and all are still open. Only 25% of the evidence for our controls is available, so most controls couldn't be proven to an auditor today. Readiness: BC/DR 60%, incident response 45.5%, IAM 40%, AI governance 3.75 out of 10. Every gap the attacker used in Assignment 3 was already in these findings. Subhan will show how we used AI to speed up this analysis."

## Subhan (4:00 to 6:00)

### AI automation (4:00 to 5:05)

**Click:** "AI automation". Point at the summary cards, then the "Where the model is reliable" table, then "Against a no-LLM baseline".

> "Mapping 25 controls to 235 framework requirements takes about 11 hours by hand. We used a local LLM on Ollama, so confidential data never leaves the machine, and each of us reviewed every one of its 139 suggestions. It's 88.5% accurate. We also report a stricter 79.9%, because some reference answers were added during review, and grading the AI against answers it helped write would flatter it. It finds 73% of our manual mappings and cuts effort by 71.5%. Search alone is slightly more precise but finds only half as much, so the LLM earns its place on recall. It's weak on COBIT and OT, which is why human review is mandatory. Our biggest lesson: the first run reported 69 invented IDs, but the logs showed they were real IDs in the wrong format. Our own safety check was too strict. After the fix, only 2 were truly invented."

### Framework gaps (5:05 to 5:25)

**Click:** "Framework gaps". Point at "Coverage by framework", then the top of the gap register.

> "The AI mapping produces this gap analysis: 52 requirement gaps, ranked by the risk behind them. NIST AI RMF and OT have the lowest coverage, and they sit over the most dangerous risks."

### Maturity & roadmap (5:25 to 6:00)

**Click:** "Maturity & roadmap". Point at the capability bars, then Years 1, 2 and 3.

> "Maturity is 1.9 today, with a target of 3.7. Our roadmap follows the data. Year 1 fixes the Gap controls sitting on Critical risks. Year 2 closes the remaining gaps. Year 3 brings the partial controls up to fully implemented. Our conclusion: PSR adopted technology faster than it secured it, and this roadmap closes that gap. Thank you."

# 4. Rehearsal checklist

* [ ] Pull the latest version on the presenting laptop (`git checkout main`, `git restore outputs/`, `git pull`)
* [ ] Rehearse with a timer. If you run long, cut Assets & data for Sarita, Compliance for Amna, or Framework gaps for Subhan; each can shrink to one sentence
* [ ] Practise the R-05 > CTL-18 click path; it is the strongest moment of the demo
* [ ] Close the drawer before switching tabs
* [ ] If a heat map cell click filters the register, press **Clear** to reset it
* [ ] Backup: if the HTML misbehaves, open `outputs\ciso_dashboard.pdf`, the executive view on one page
* [ ] Everyone knows the headline numbers: **1.9 / 5, 11.9 / 25, 12%, 37.9%, 13 findings, 88.5% / 79.9%, 72.6%, 71.5%**

# 5. Likely questions, and who answers

| Question | Who | Short answer |
|---|---|---|
| How is current risk calculated? | Sarita | It moves from inherent towards target in proportion to how many of its controls are in place (Implemented 1, Partial 0.5, Gap 0). |
| Why did you change the governance structure? | Sarita | Independence: a CISO under the CIO and an auditor under management cannot challenge the people they report to. |
| Why 12% effectiveness but 37.9% compliance? | Amna | Effectiveness counts only fully implemented controls; compliance gives partial credit. The gap is "on paper versus actually running". |
| Why are all the findings still open? | Amna | They are current-state findings; closing them is Year 1 of the roadmap. |
| Why two Trust Scores? | Subhan | 15 reference answers were added during review, 12 of them the AI's own. 79.9% excludes them, so it is the honest accuracy. |
| Can the AI decide compliance? | Subhan | No. It only proposes mappings; status, scores and approvals stay with people. |
| Why a local LLM? | Subhan | Data leakage: control and gap data is confidential, and Ollama keeps it on our machine. |
| What would you improve? | Subhan | A bigger model or one prompt per framework (to fix COBIT and OT), the official PISF 2026 clauses, and continuous evidence collection. |
