# Project handover: what is done and what is left

## 1. What the project is

Final project for CY3003 Information Assurance: an Information Assurance, GRC and AI automation programme
for **Pakistan Smart Railways (PSR)**, the hypothetical smart railway from Assignments 1 to 3.

The brief asks for three things on top of the assignments:
1. Five master registers kept in sync (asset, risk, control, compliance, evidence)
2. One AI automation of an IA task, with its accuracy, time saving, risks and human oversight
3. A one page CISO Executive Dashboard with real calculated numbers

All three are done. What is left is mostly **writing the final report**.

## 2. What is done

| Part | Where | What it is |
|---|---|---|
| Master registers | `data/registers/` | Assets (15), data inventory (13), risks (17, with residual risk), controls (CTL-01 to CTL-25), compliance (A2 heat map), evidence (68 items), audit findings (13 + 1 observation) |
| Validation | `python run.py validate` | Checks every Asset > Risk > Control > Requirement > Evidence link. Currently 0 errors |
| Scoring | `outputs/metrics.md` | Every course formula: risk, residual risk, control effectiveness, compliance, maturity, readiness |
| Framework catalogs | `data/frameworks/` | ISO 27001, CIS v8, NIST CSF 2.0, IEC 62443 / SP 800-82, NIST AI RMF, COBIT, PISF 2026 (235 requirements) |
| AI automation | `src/ai_mapper/`, `outputs/mapping/` | Local LLM (Ollama, qwen2.5:7b) maps controls to framework requirements; every suggestion reviewed by Sarita, Subhan and Amna |
| Gap analysis | `outputs/gap/gap_summary.md` | 52 requirement gaps ranked by the risk behind them |
| AI evaluation | `outputs/evaluation/evaluation.md` | Trust Score, recall, Automation Gain, comparison with a no-LLM baseline |
| CISO dashboard | `outputs/ciso_dashboard.pdf` | One page, all numbers calculated |
| AI Automation Card | `docs/ai_automation_card.md` | The 12 item card the brief asks for (ready to paste) |
| AI governance of our own AI | `docs/ai_governance.md` | The 9 AI risks from the brief, with our controls and who is accountable (ready to paste) |
| Decisions log | `docs/decisions.md` | Every correction to A1 to A3 and every assumption (read before the viva) |

### Corrections made to the assignments (use these values everywhere in the report)

1. AST-03 (e-ticketing) RTO is **8 hrs** (the A3 table said 2 hrs; the A3 incident needs 8)
2. There are **5 Critical risks**: R-03, R-05, R-06, R-09, R-10 (A3 said four)
3. The A3 scenario is **ransomware on e-ticketing (R-05)**, not built from the OT/SCADA rows
4. AST-08 (IoT sensors) gets RTO **1 hr**, RPO **5 mins** (missing from A3)
5. Remove the duplicated "Audit Plan" heading and intro in A2 Section E

## 3. The results

### PSR security position

| Measure | Result |
|---|---|
| Overall IA status | **DEVELOPING** (governance maturity 1.9 / 5, Year 3 target 3.7) |
| Risks | 17: 5 Critical, 10 High, 2 Medium |
| Average risk score | 13.8 inherent, **11.9 current**, 7.2 after planned controls |
| High / Critical risks today | 14 of 17 |
| Control effectiveness | **12%** (3 of 25 implemented); 30% if Partial counts as half |
| Compliance | **37.9%** (22.75 / 60, A2 heat map) |
| Audit findings | 13 (3 Critical, 9 High, 1 Medium) |
| Critical control gaps | 4: CTL-12, CTL-15, CTL-16, CTL-25 |
| Readiness | IAM 40%, BC/DR 60%, Incident 45.5%, AI governance 3.75 / 10 |
| Evidence available | 25% of 68 items |

**Top 5 risks now:** R-06 API access control (16), R-03 legacy OT (15), R-05 ticketing ransomware (15),
R-09 passenger data exfiltration (15), R-01 train control compromise (15).

**Top 5 recommendations:** CTL-07 MFA everywhere, CTL-25 exercise programme, CTL-12 app/API security
testing, CTL-02 brokered vendor access, CTL-01 default-deny IT/OT segmentation.

**Message for the report:** PSR adopted technology faster than it secured it. The weakest areas
(OT, AI, vendors) hold the most dangerous risks, and the A3 incident used exactly the gaps already recorded.

### AI automation results

| Metric | Result |
|---|---|
| Task | Map 25 controls to 235 requirements in 7 frameworks, then find gaps |
| Trust Score (accuracy) | **123 / 139 = 88.5%** |
| Accepted by reviewers | 121 / 139 = 87.1% |
| Recall of our A2/A3 manual mapping | **72.6%** |
| Automation Gain | **81.3%** (650 min by hand, 121 min with AI and review) |
| Truly invented IDs (blocked) | 2 |
| Badly formatted real IDs (repaired) | 10 |
| No-LLM search baseline | 90.6% trust but only 50% recall, so the LLM is worth using |

**The story to tell:** the first run looked poor (35.5% recall, "69 invented IDs"). Reading the logs
showed all 69 were real IDs in the wrong format that our safety check was too strict to accept. After
fixing the check, recall doubled. This is our main AI governance lesson (written up in
`docs/ai_governance.md`): a safety control on an AI can fail silently, and only evaluation and log
review catch it. Weak spots that justify mandatory human review: COBIT (54% trust) and OT (44% recall).

## 4. How to run it

```bash
git clone https://github.com/saritasangrez20/PakistanSmartRailway.git
cd PakistanSmartRailway
git checkout setup/project-skeleton
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
python run.py validate
python run.py score
python run.py dashboard
```

You do **not** need to re-run the AI (`python run.py map`): it takes 46 minutes and the reviewed results
are already committed. Only re-run it if you change `data/registers/controls.csv`. After editing any
register, run `validate`, then `score`, then `dashboard` so the numbers stay in sync.

## 5. What is left (to do)

Every number these sections need is already in `outputs/metrics.md` and the registers. Use them; do not
invent new figures, or the report and dashboard will disagree.

### A. Report sections to write

| # | Section | Source to use | Owner | Done |
|---|---|---|---|---|
| 1 | Organization architecture diagram (IT, OT, cloud, IoT, AI zones; 3 control centres, primary and DR data centres, 100 stations) | A1 Section A, `assets.csv` | | [ ] |
| 2 | Governance structure (fix: CISO should report to CEO or Risk Committee, Internal Audit to a Board Audit Committee) | A1 Section B | | [ ] |
| 3 | Security policy set: policies, standards, guidelines, procedures | `controls.csv` (each policy should cite the controls it mandates) | | [ ] |
| 4 | Data inventory and data flow diagram (passenger > app > ticketing > passenger DB > cloud; sensors > AI engine) | `data_inventory.csv`, A3 classification | | [ ] |
| 5 | Residual risk section | `outputs/risk_register_scored.csv`, `risks.csv` (target_rationale) | | [ ] |
| 6 | PISF 2026 mapping table | `controls.csv` framework_refs, `compliance.csv` PISF column | | [ ] |
| 7 | Compliance assessment and gap analysis | `outputs/metrics.md` (37.9%), `outputs/gap/gap_summary.md` | | [ ] |
| 8 | IAM additions: ABAC rules and a sample access review table | A3 IAM, `readiness.csv` (IAM rows) | | [ ] |
| 9 | Data protection architecture and encryption/privacy assessment | CTL-10, CTL-14, CTL-15, `data_inventory.csv` | | [ ] |
| 10 | BIA table (impact over time per service), RTO/RPO, DR architecture diagram | `assets.csv` (rto/rpo), A3 BC/DR | | [ ] |
| 11 | Incident response plan (roles, severity levels, escalation) and SOC/SIEM/SOAR architecture diagram | A3 incident, `readiness.csv` (IR rows), CTL-24, CTL-15 | | [ ] |
| 12 | Cloud security (shared responsibility matrix), IoT/OT security (Purdue model), supply chain assessment | CTL-16, CTL-05, CTL-01, CTL-23, R-10, R-04, R-16 | | [ ] |
| 13 | Quantum: which systems need PQC migration (TLS, VPN, PKI, payment tokens, signed OT firmware, backups) | CTL-14, `assets.csv` | | [ ] |
| 14 | Maturity assessment and 3-year roadmap (Year 1 Foundation, Year 2 Integration, Year 3 Optimization) | `maturity.csv` (scores and Year 3 targets), top 5 recommendations | | [ ] |
| 15 | AI automation section | `docs/ai_automation_card.md`, `docs/ai_governance.md`, `outputs/evaluation/evaluation.md` | | [ ] |
| 16 | Executive dashboard page | `outputs/ciso_dashboard.pdf` | | [ ] |

### B. Checks before submission

| # | Task | Owner | Done |
|---|---|---|---|
| 1 | Read `docs/decisions.md` and agree with each assumption (or change the register and re-run) | | [ ] |
| 2 | Skim the rows with source `Reviewer` in `data/ground_truth/reference_mapping.csv` and delete any you disagree with, then `python run.py evaluate` and `python run.py dashboard` | | [ ] |
| 3 | If the official PISF 2026 document is available, replace `data/frameworks/pisf_2026.csv` (currently a domain level placeholder) | | [ ] |
| 4 | Make sure every number in the report matches `outputs/metrics.md` and the dashboard | | [ ] |
| 5 | Merge the pull request into `main` when the report is final | | [ ] |
| 6 | Each member can trace one risk end to end for the viva: asset > risk > control > evidence > audit finding > dashboard (for example AST-03 > R-05 > CTL-18 > EV-038 Backup job reports > AUD-04 > top 5 risks on the dashboard) | | [ ] |

## 6. Viva quick answers

* **Where do the numbers come from?** Calculated by `scoring.py` from the registers; formulas are in the README.
* **Why is control effectiveness only 12%?** Only Implemented controls count as effective (3 of 25). Partial counted as half gives 30%.
* **How is residual risk calculated?** Each risk moves from inherent towards its target in proportion to how many of its controls are in place (Implemented 1, Partial 0.5, Gap 0).
* **Why a local LLM?** Control data is confidential; Ollama keeps it on our machine (data leakage control).
* **How do you know the AI is accurate?** Graded against our A2/A3 manual mapping plus reviewer additions; 88.5% trust, 72.6% recall; every suggestion approved by a named reviewer.
* **What went wrong with the AI?** Our guardrail rejected 69 correct IDs because of formatting; we found it in the logs and fixed it. Only 2 truly invented IDs remained.
* **What can't the AI do?** Judge whether a control is actually implemented; it only maps. Weak on COBIT and OT.
