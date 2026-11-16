# Design and Implementation of an Enterprise Information Assurance, GRC and AI-Assisted Cybersecurity Program

## Pakistan Smart Railways (PSR)

**CY3003 Information Assurance, Final Project**

Group 07

| Name | Roll number |
|---|---|
| Amna Ali | 23i-2067 |
| Sarita Sangrez | 23i-2088 |
| Subhan Umer | 23i-2054 |

## 0. How to read this report

Every number in this report is calculated, not estimated. All five master registers live in
`data/registers/` as CSV files. `scoring.py` reads them and produces `outputs/metrics.md`, the scored
risk register and the dashboard. Nothing is typed in twice. If a control status changes in the
register, the control effectiveness figure, the residual risk, the compliance percentage and the
dashboard all move together.

Between them the registers carry 15 assets, 13 data sets, 17 risks, 25 controls, 78 compliance cells, 68 evidence
items and 14 audit rows. Validation checks every ID link in the chain Asset to Risk to Control
to Requirement to Evidence before any scoring runs. Right now it reports zero errors and zero warnings.

PSR is hypothetical. We built it for this course and carried it unchanged through Assignments 1 to 4.
Where those assignments disagreed with each other, one value was chosen and applied everywhere.
Those corrections are listed in `docs/decisions.md` and summarised in section 20.

## 1. Organisation architecture

### 1.1 Profile

Pakistan Smart Railways is a nationwide railway operator running passenger and freight services on a
digital infrastructure. Tickets are sold online, trains are scheduled, tracked, signalled and controlled, track and rolling
stock are monitored, and the fleet is maintained in-house.

| Category | Scale |
|---|---|
| Railway network | Nationwide |
| Stations | approximately 100 |
| Trains | 150+ including freight |
| Employees | approximately 15,000 |
| Daily passengers | approximately 250,000 |
| Control centres | 3 |
| Data centres | Primary plus a Disaster Recovery site |
| Maintenance facilities | Multiple regional |
| Cloud | Hybrid |
| IoT devices | Thousands |
| Third parties | Payment, cloud, telecom, maintenance and technology vendors |

Five technology domains sit inside that. IT runs business and administrative systems. OT runs train
control, signalling and interlocking. Hybrid cloud carries scalable applications and data services. IoT covers track, rolling stock and station sensing. AI drives predictive maintenance and
operational decision support.

### 1.2 Zone architecture

```
                         ┌──────────────── INTERNET / PUBLIC ─────────────────┐
                         │  Passengers · Mobile app · Web portal · Vendors    │
                         └────────────────────────┬───────────────────────────┘
                                                  │  TLS, WAF, API gateway
  ╔══════════════════════ CLOUD ZONE ═════════════╧═══════════════════════════╗
  ║  AST-09 Hybrid cloud   AST-10 App & portal   AST-13 Email (SaaS)          ║
  ║  Payment token store · Object storage · Replication target                ║
  ╚═══════════════════════════════╤═══════════════════════════════════════════╝
                                  │  Site-to-site VPN, brokered access
  ╔══════════════════════ IT ZONE ╧═══════════════════════════════════════════╗
  ║  AST-03 E-ticketing   AST-04 Passenger master DB   AST-12 Crew scheduling ║
  ║  AST-06 SOC / SIEM    AST-05 Enterprise network & fibre backbone          ║
  ║  AST-15 DR data centre            3 control centres                       ║
  ╚═══════════════════════════════╤═══════════════════════════════════════════╝
                                  │  ◄── CTL-01 default-deny boundary, CTL-02 PAM jump host
  ╔══════════════════════ OT / IoT ZONE ══════════════════════════════════════╗
  ║  AST-01 Centralized Train Control    AST-02 Signalling & interlocking     ║
  ║  AST-08 Track & rolling stock sensors  AST-11 Fare collection & gates     ║
  ║  AST-14 Station CCTV                  ~100 stations                       ║
  ╚═══════════════════════════════╤═══════════════════════════════════════════╝
                                  │  one-way telemetry feed
  ╔══════════════════════ AI ZONE ╧═══════════════════════════════════════════╗
  ║  AST-07 Predictive maintenance engine · Model registry · Training data    ║
  ╚═══════════════════════════════════════════════════════════════════════════╝
```

One boundary matters more than all the rest, and that's the one between IT and OT. Section 16 maps it onto the Purdue
model. Today that boundary is physically present but rule-wise it is open, which is finding AUD-01.

## 2. Governance structure

### 2.1 Roles

| Role | Responsibility |
|---|---|
| Board of Directors | Strategic oversight and governance |
| CEO | Overall management and accountability |
| Risk Committee | Oversees major organisational and cybersecurity risks |
| Board Audit Committee | Receives Internal Audit reporting |
| CIO | IT infrastructure, applications and digital systems |
| CISO | Cybersecurity, security risk and security operations |
| COO | Railway operations |
| Risk Management | Identifies, assesses and monitors risk |
| Compliance | Ensures requirements and policies are applied |
| Internal Audit | Independently evaluates controls and compliance |
| IT Department | Enterprise IT infrastructure |
| OT/Engineering | Signalling, train control and operational systems |
| SOC | Monitors security events, supports detection and response |
| Business owners | Named owner for every major system |

### 2.2 Reporting lines

```
                    Board of Directors
                    ├── Board Audit Committee ──── Internal Audit
                    └── Risk Committee
                            │
                           CEO
            ┌───────────────┼───────────────┬──────────────┐
           CIO            CISO             COO         Compliance
            │               │               │
      IT Department    SOC · Risk Mgmt   OT/Engineering
```

Assignment 1 had the CISO reporting through the CIO. We corrected that here. The CISO now reports to
the CEO with a dotted line to the Risk Committee, and Internal Audit reports to the Board Audit Committee, not into management.

Independence is the reason. A CISO who reports to the CIO is asking the person responsible for
delivery to fund the person responsible for saying delivery is unsafe. Those two jobs pull in
opposite directions. Same logic applies to Internal Audit. An auditor who reports to the people
being audited cannot raise a finding against them, which is why the maturity score for Audit is held
at 3 and not 4 despite the audit plan itself being sound.

### 2.3 Three lines of defence

| Line | Who at PSR | What they own |
|---|---|---|
| First | IT Department, OT/Engineering, Passenger Services, business owners | Operate the controls and own the risk |
| Second | CISO, Risk Management, Compliance | Set policy, challenge the first line, maintain the registers |
| Third | Internal Audit | Independent assurance to the Board Audit Committee |

The SOC sits in the first line operationally and reports to the CISO. Deliberately so. Detection
is an operational activity, and keeping it under the CISO is what gives the second line its own telemetry instead of only the first line's word.

## 3. Security policy set

Governance scored 2 out of 5 because the structure exists but the policy set is not formalised. The
structure below closes that. Each policy names the controls it mandates, so a policy cannot drift
away from what is actually implemented.

### 3.1 Hierarchy

```
POLICY      what must be true, approved by the Board, reviewed annually
   ↓
STANDARD    the measurable rule, approved by the CISO
   ↓
GUIDELINE   recommended practice, not mandatory
   ↓
PROCEDURE   the step-by-step, owned by the operating team
```

### 3.2 The policy set

| Policy | Mandates | Standards beneath it | Owner |
|---|---|---|---|
| Information Security Policy | The whole control register | Classification, acceptable use | CISO |
| Access Control Policy | CTL-07, CTL-08, CTL-09, CTL-10 | MFA standard, PAM standard, JML standard, recertification standard | CISO |
| OT and Safety Systems Policy | CTL-01, CTL-02, CTL-03, CTL-04, CTL-05 | Segmentation standard, OT remote access standard, OT patching standard | OT/Engineering |
| Data Protection and Privacy Policy | CTL-10, CTL-14, CTL-15 | Encryption standard, retention standard, DLP standard | CISO |
| Business Continuity Policy | CTL-18, CTL-19, CTL-25 | Backup standard, restore test standard, exercise standard | CIO |
| Incident Management Policy | CTL-24, CTL-25 | Logging standard, severity and escalation standard | CISO |
| Third-Party Security Policy | CTL-02, CTL-23 | Vendor security annex, notification SLA standard | CISO / Procurement |
| AI Governance Policy | CTL-06, CTL-20, CTL-21 | Model approval standard, drift monitoring standard | Maintenance / Data & AI |
| Cloud Security Policy | CTL-16 | Secure baseline standard, configuration drift standard | CIO |
| Application Security Policy | CTL-11, CTL-12, CTL-13 | Secure development standard, API authorisation standard | CIO |

### 3.3 Worked example

Policies are useless if you can't trace them to something testable. This is the full chain for one
requirement.

| Level | Statement |
|---|---|
| Policy | All remote access to operational technology is controlled and time-limited |
| Standard | Vendor access is brokered through a PAM jump host, is approved per session, carries MFA, and expires within 8 hours |
| Guideline | Prefer screen-recorded sessions for safety-relevant work |
| Procedure | PSR-PRC-014: raise a change ticket, approver checks the possession window, operator checks out the credential, session is recorded, credential rotates on check-in |
| Control | CTL-02 Controlled OT remote access |
| Evidence | PAM session recordings, checkout logs, approval tickets |
| Audit test | Sample 20 vendor sessions, confirm each has an approval, an expiry and a recording |
| Finding | PIR-01, Critical. Standing vendor account with no expiry was the entry point in the Assignment 3 incident |

## 4. Asset inventory

Criticality runs 1 to 5. Classification follows the highest class of data the asset holds, which is
why the mobile app (AST-10) is Restricted and not Public. Yes, it serves public timetables, but it also handles bookings and payment tokens.

| ID | Asset | Owner | Type | Domain | Crit | Classification |
|---|---|---|---|---|---|---|
| AST-01 | Centralized Train Control System | COO / OT | OT System | OT | 5 | Critical |
| AST-02 | Digital Signalling & Interlocking | OT/Engineering | OT System | OT | 5 | Critical |
| AST-03 | Passenger E-Ticketing & Reservation | Passenger Services / CIO | Application | IT | 5 | Restricted |
| AST-04 | Passenger Master Database | CISO / Data Owner | Data | IT | 5 | Restricted |
| AST-05 | Enterprise Network & Fibre Backbone | IT Department | Network | IT/OT | 5 | Confidential |
| AST-06 | SOC and SIEM | CISO | Cybersecurity | IT | 5 | Confidential |
| AST-07 | AI Predictive Maintenance Engine | Maintenance / Data & AI | AI/ML | AI | 5 | Critical |
| AST-08 | IoT Track & Rolling Stock Sensors | OT/Engineering | IoT | IoT | 4 | Critical |
| AST-09 | Enterprise Hybrid Cloud | IT Department | Cloud | Cloud | 4 | Restricted |
| AST-10 | Mobile App & Web Portal | Passenger Services / IT | Application | IT | 4 | Restricted |
| AST-11 | Automated Fare Collection & Gates | Passenger Services / OT | OT/IoT | OT/IoT | 4 | Restricted |
| AST-12 | Crew Scheduling & Rostering | COO / Operations | Application | IT | 4 | Confidential |
| AST-13 | Enterprise Email & Communications | IT Department | Cloud | Cloud | 3 | Internal |
| AST-14 | Station CCTV & Video Analytics | Physical Security | Physical / IoT | IoT | 3 | Confidential |
| AST-15 | Disaster Recovery Data Centre | CIO / IT Department | Infrastructure | IT | 5 | Restricted |

Seven assets carry criticality 5. Four of them are either OT or feed OT, which is what makes the IT
to OT boundary the single most important control in the programme.

## 5. Data inventory and data flow

### 5.1 Classification scheme

| Class | Meaning | Controls required |
|---|---|---|
| Public | Published deliberately | Integrity only |
| Internal | Staff-only, low harm if leaked | Access control |
| Confidential | Business harm if leaked | Access control plus encryption |
| Restricted | Regulatory or personal data | Encryption, IAM, MFA, DLP, monitoring |
| Critical | Safety-relevant, harm to life | All of the above plus integrity verification and offline backup |

### 5.2 Inventory

| ID | Data set | Class | Primary asset | Owner | Priority |
|---|---|---|---|---|---|
| DATA-01 | Timetables, fares, station information | Public | AST-10 | Passenger Services | Integrity |
| DATA-02 | Staff email and directory | Internal | AST-13 | IT Department | Confidentiality |
| DATA-03 | Crew work schedules and rosters | Confidential | AST-12 | Railway Operations | Availability |
| DATA-04 | Vendor contracts and register | Confidential | AST-09 | CISO / Procurement | Confidentiality |
| DATA-05 | CCTV footage | Confidential | AST-14 | Physical Security | Confidentiality |
| DATA-06 | SIEM logs and audit reports | Confidential | AST-06 | CISO | Integrity |
| DATA-07 | Passenger identity, contact, travel | Restricted | AST-04 | Passenger Services / Data Owner | Confidentiality |
| DATA-08 | Booking records | Restricted | AST-03 | Passenger Services | Confidentiality |
| DATA-09 | Payment tokens | Restricted | AST-03 | Passenger Services | Confidentiality |
| DATA-10 | Movement authorities and train control | Critical | AST-01 | OT/Engineering | Integrity and availability |
| DATA-11 | Signalling and interlocking logic | Critical | AST-02 | OT/Engineering | Integrity and availability |
| DATA-12 | Safety-relevant sensor telemetry | Critical | AST-08 | OT/Engineering | Integrity |
| DATA-13 | Predictive maintenance model and inputs | Critical | AST-07 | Maintenance / Data & AI | Integrity |

Of the five Critical data sets, four are judged on integrity rather than confidentiality. Nobody's harmed if a movement authority leaks. People die if one is altered. Which inverts the usual ordering of the CIA triad, and it is why OT controls in section 16 are built around command authentication and not encryption.

### 5.3 Passenger data flow

```
Passenger ──► Mobile app / portal (AST-10) ──► API gateway ──► E-ticketing (AST-03)
                     │  TLS 1.3                   │ CTL-11 authz        │
                     │                            │ CTL-13 token        │
                     ▼                            ▼                     ▼
              Payment provider            Passenger master DB (AST-04)  Booking records
              (tokenised, CTL-14)          CTL-10 RBAC · CTL-14 encrypt  DATA-08
                                           CTL-15 DAM  ◄── GAP
                                                   │
                                                   ├──► Hybrid cloud (AST-09) replication
                                                   └──► DR data centre (AST-15)
```

### 5.4 Safety telemetry flow

```
Track & rolling stock sensors (AST-08) ──► OT collector ──► one-way feed ──► AI engine (AST-07)
         DATA-12                            CTL-05 ◄GAP      CTL-06 ◄GAP      DATA-13
                                            device identity   telemetry validation
                                                                      │
                                                     maintenance recommendation
                                                                      │
                                                      human planner ──┴──► work order
```

That one-way feed is the design decision worth defending. The AI engine reads OT telemetry and never
writes back to it. So a poisoned model can produce a wrong maintenance recommendation, which
a human planner reviews, but it cannot issue a command to a train. CTL-05 and CTL-06 are both Gaps,
so today the telemetry entering that pipe is neither authenticated nor validated. Hence risk R-11.

## 6. Risk register and risk calculations

### 6.1 Scales

Risk is Likelihood times Impact, both scored 1 to 5, giving 1 to 25.

| Band | Score | Meaning |
|---|---|---|
| Critical | 16 to 25 | Treat immediately, Board visibility |
| High | 10 to 15 | Treat within the current cycle |
| Medium | 5 to 9 | Treat or formally accept |
| Low | 1 to 4 | Accept and review annually |

### 6.2 Register

| ID | Risk | L | I | Inherent | Rating | Treatment | Controls |
|---|---|---|---|---|---|---|---|
| R-01 | Compromise of the centralized train control system | 3 | 5 | 15 | High | Mitigate | CTL-01, CTL-02, CTL-07 |
| R-02 | Manipulation of signalling and interlocking | 2 | 5 | 10 | High | Mitigate | CTL-01, CTL-04 |
| R-03 | Unpatched legacy and end-of-life OT | 4 | 5 | 20 | Critical | Mitigate | CTL-01, CTL-03, CTL-17 |
| R-04 | IoT sensor spoofing and tampering | 3 | 4 | 12 | High | Mitigate | CTL-05, CTL-06 |
| R-05 | Ransomware on ticketing and reservations | 4 | 5 | 20 | Critical | Mitigate | CTL-07, CTL-17, CTL-18, CTL-24, CTL-25 |
| R-06 | Broken access control in app and portal APIs | 4 | 4 | 16 | Critical | Mitigate | CTL-11, CTL-12 |
| R-07 | Fare fraud at smart gates | 4 | 3 | 12 | High | Mitigate | CTL-12, CTL-13 |
| R-08 | Loss of crew scheduling data | 2 | 3 | 6 | Medium | Accept | — |
| R-09 | Mass exfiltration of passenger data | 4 | 5 | 20 | Critical | Mitigate | CTL-07, CTL-08, CTL-10, CTL-14, CTL-15 |
| R-10 | Cloud misconfiguration | 4 | 4 | 16 | Critical | Mitigate | CTL-07, CTL-14, CTL-16 |
| R-11 | AI model poisoning and drift | 2 | 5 | 10 | High | Mitigate | CTL-06, CTL-20, CTL-21 |
| R-12 | Backups and DR site not recoverable | 3 | 5 | 15 | High | Mitigate | CTL-18, CTL-19, CTL-25 |
| R-13 | Insecure CCTV and video infrastructure | 4 | 2 | 8 | Medium | Accept | — |
| R-14 | Phishing and business email compromise | 5 | 3 | 15 | High | Mitigate | CTL-07, CTL-22 |
| R-15 | Privileged insider misuse and stale accounts | 3 | 5 | 15 | High | Mitigate | CTL-07, CTL-08, CTL-09 |
| R-16 | Third party and supply chain compromise | 3 | 4 | 12 | High | Transfer / Mitigate | CTL-02, CTL-23 |
| R-17 | SOC and SIEM blind spots | 3 | 4 | 12 | High | Mitigate | CTL-24, CTL-25 |

Five Critical, ten High, two Medium. Average inherent score 13.76 out of 25.

### 6.3 Why the scores are what they are

Some of these deserve explaining, because the number on its own does not argue for itself.

**R-03 at 4 x 5 = 20.** Likelihood 4 because legacy OT on a railway is not patched on a monthly
cycle. Patching a signalling controller means taking a possession, and possessions are scheduled
around train services, not around Patch Tuesday. End-of-life equipment stays in service for years
after the vendor stops shipping fixes. Impact 5 because the asset is safety-relevant.

**R-14 at 5 x 3 = 15.** Likelihood 5 is the only 5 in the register. With 15,000 employees, somebody
clicks. That isn't pessimism, it's arithmetic. Impact is held at 3 because email is Internal, so a
compromised mailbox is a foothold and not a safety event on its own. What makes it matter is the foothold, and that's captured by R-15 and R-09 downstream.

**R-02 at 2 x 5 = 10.** Likelihood only 2, which looks low for something this serious. Signalling
and interlocking are air-gapped by design and run proprietary protocols, so reaching them takes a
deliberate multi-stage intrusion rather than a commodity attack. Impact is 5 and cannot be anything
else. Manipulate an interlocking and you get a collision.

**R-08 and R-13 accepted.** Both are Medium and both sit inside appetite. Crew scheduling data has a
manual fallback, which is a paper roster, so losing it is disruptive and not dangerous. CCTV is
Confidential and the cameras do not reach OT. Accepting is a decision and not an oversight, and both
are reviewed annually by the Risk Committee.

### 6.4 Risk appetite

| Domain | Appetite | Tolerance |
|---|---|---|
| Safety and OT | None. No Critical or High risk may be accepted | Zero |
| Passenger data | Low | No Restricted data risk above Medium may be accepted |
| Service availability | Moderate | Ticketing may run degraded with manual fallback |
| Fare revenue | Moderate | Known fraud loss up to the cost of the control |
| Corporate IT | Moderate | Medium risks may be accepted with annual review |

Our register respects this. Neither accepted risk touches safety, OT or Restricted data.

## 7. Risk treatment and residual risk

### 7.1 Treatment strategies used

| Strategy | Where PSR used it | Why |
|---|---|---|
| Avoid | Not used | No risk could be removed by withdrawing a service that passengers depend on |
| Mitigate | 15 of 17 risks | The default where a control can reduce likelihood or impact |
| Transfer | R-16, partly | Vendor security annex and liability clauses transfer some supply chain exposure, and cyber insurance covers part of the ransomware loss. The safety consequence cannot be transferred |
| Accept | R-08, R-13 | Medium, within appetite, reviewed annually |

Transfer deserves a caveat. You can insure the cost of a ticketing outage. You can't insure a derailment, and no contract clause makes the regulator or the travelling public whole. So R-16 is
marked Transfer / Mitigate, and the mitigating half (CTL-02, CTL-23) is the part that is actually
load-bearing.

### 7.2 How residual risk is calculated

Target residual risk is set per risk, with a written rationale, and impact only falls where a
control genuinely limits damage. Backups cut impact. Awareness training does not.

Current residual risk is computed, not asserted:

```
credit  = average(control status credit)    Implemented 1.0, Partial 0.5, Gap 0.0
current_L = round(L - (L - target_L) x credit)
current_I = round(I - (I - target_I) x credit)
current   = current_L x current_I
```

Risks only move from inherent towards target in proportion to how much of their control set is
actually in place. That's the honest version. A control that's planned but not built earns zero.

### 7.3 Residual position

| ID | Inherent | Credit | Current | Target | Movement |
|---|---|---|---|---|---|
| R-01 | 15 | 0.33 | 15 | 10 | none yet |
| R-02 | 10 | 0.25 | 10 | 5 | none yet |
| R-03 | 20 | 0.50 | 15 | 10 | Critical to High |
| R-04 | 12 | 0.00 | 12 | 6 | none |
| R-05 | 20 | 0.50 | 15 | 8 | Critical to High |
| R-06 | 16 | 0.25 | 16 | 8 | none yet |
| R-07 | 12 | 0.25 | 12 | 6 | none yet |
| R-08 | 6 | — | 6 | 6 | accepted |
| R-09 | 20 | 0.50 | 15 | 10 | Critical to High |
| R-10 | 16 | 0.33 | 12 | 8 | Critical to High |
| R-11 | 10 | 0.00 | 10 | 5 | none |
| R-12 | 15 | 0.33 | 10 | 5 | High, score down 5 |
| R-13 | 8 | — | 8 | 8 | accepted |
| R-14 | 15 | 0.75 | 8 | 8 | High to Medium, at target |
| R-15 | 15 | 0.33 | 15 | 8 | none yet |
| R-16 | 12 | 0.00 | 12 | 6 | none |
| R-17 | 12 | 0.25 | 12 | 6 | none yet |

Average inherent 13.76, current 11.94, target after the full treatment plan 7.24. So PSR has taken
13.2% off its risk so far, against 47.4% planned.

Some risks have moved nowhere at all, because every control attached to them is a Gap. R-04, R-11
and R-16 are the clearest examples. R-14 is the only risk already at target, and that is because
both its controls (CTL-07 Partial, CTL-22 Implemented) are the furthest along in the register.

Read as a whole, the table says something uncomfortable and it's true. PSR's risk reduction so far has
come almost entirely from controls that were easy to buy. Controls that would move the Critical risks are the ones nobody has built.

## 8. Framework selection and control matrix

### 8.1 Selection

No single framework covers a railway that runs IT, OT, cloud, IoT and AI at once. Each one is used
for the job it is actually good at.

| Requirement | Framework | What it does here |
|---|---|---|
| Governance alignment | COBIT 2019 | Aligns cybersecurity investment with PSR strategy |
| ISMS | ISO/IEC 27001:2022 | Builds the management system and the Statement of Applicability |
| Cybersecurity programme | NIST CSF 2.0 | Operates the programme across Govern, Identify, Protect, Detect, Respond, Recover |
| System authorisation | NIST RMF | Assesses and authorises high-risk systems |
| Technical baseline | CIS Controls v8 | Implements baseline technical safeguards |
| OT | IEC 62443 | Secures the industrial control systems |
| OT operations | NIST SP 800-82 | Guides how OT controls are actually applied |
| Zone architecture | Purdue Model | Segments IT from OT |
| AI | NIST AI RMF | Governs the predictive maintenance model |
| Cloud compliance | Policy-as-Code | Automates configuration compliance |
| National alignment | PISF 2026 | Aligns to the Pakistan national framework |

Seven of these carry requirement catalogues in `data/frameworks/`, 235 requirements in total: ISO
27001 Annex A (93), IEC 62443 and SP 800-82 (57), NIST CSF 2.0 (22), NIST AI RMF (19), CIS v8 (18),
COBIT 2019 subset (13) and PISF 2026 (13).

One honest caveat. The PISF 2026 catalogue is a placeholder at domain level, one requirement per
compliance domain, because the official clause text was not available. Every PISF figure in this
report should be read with that in mind. Replacing that one file and rerunning the pipeline is a
ten-minute job once the document is published.

### 8.2 Control matrix

Status is the Assignment 2 baseline. Control type uses the standard classification: Administrative,
Technical or Physical by nature, and Preventive, Detective, Corrective or Compensating by purpose.

| ID | Control | Domain | Type | Framework refs | Status | Owner |
|---|---|---|---|---|---|---|
| CTL-01 | IT/OT network segmentation | Network | Technical / Preventive | IEC 62443-3-3 SR 5.1, CIS 12, SP 800-82 | Partial | OT/Engineering |
| CTL-02 | Controlled OT remote access | IAM | Technical / Preventive | IEC 62443-2-4, ISO A.5.15 | Gap | CISO |
| CTL-03 | OT asset inventory and legacy exceptions | Asset mgmt | Administrative / Detective | IEC 62443-2-1, CIS 1, SP 800-82 | Partial | OT/Engineering |
| CTL-04 | Signalling command authentication | OT safety | Technical / Preventive | IEC 62443-3-3 SR 3.1, CSF Detect | Gap | OT/Engineering |
| CTL-05 | IoT device authentication | OT safety | Technical / Preventive | IEC 62443-3-3 SR 1.1, CIS 4 | Gap | OT/Engineering |
| CTL-06 | Sensor telemetry validation | AI governance | Technical / Detective | NIST AI RMF MAP, IEC 62443-3-3 | Gap | Maintenance / Data & AI |
| CTL-07 | Multi-factor authentication | IAM | Technical / Preventive | ISO A.8.5, CIS 6, PISF | Partial | CISO |
| CTL-08 | Privileged access management | IAM | Technical / Preventive | ISO A.8.2, CIS 5 | Partial | CISO |
| CTL-09 | Joiner-mover-leaver and recertification | IAM | Administrative / Detective | ISO A.5.18, COBIT | Gap | CIO |
| CTL-10 | RBAC on passenger master database | Data protection | Technical / Preventive | ISO A.5.15, CIS 3 | **Implemented** | Passenger Services |
| CTL-11 | API security | AppSec | Technical / Preventive | ISO A.8.26, CIS 16 | Partial | CIO |
| CTL-12 | Application and API security testing | AppSec | Technical / Detective | ISO A.8.29, CIS 16 | Gap | CIO |
| CTL-13 | Ticket token and fare validation | AppSec | Technical / Preventive | ISO A.8.26, CIS 13 | Partial | Passenger Services |
| CTL-14 | Encryption of passenger data | Data protection | Technical / Preventive | ISO A.8.24, PISF | Partial | CISO |
| CTL-15 | Database activity monitoring | Logging | Technical / Detective | ISO A.8.16, CIS 8 | Gap | CISO |
| CTL-16 | Secure cloud configuration | Cloud | Technical / Preventive | CIS 4, CIS 5, CSF Protect | Gap | CIO |
| CTL-17 | Vulnerability management and patching | OT safety | Technical / Corrective | ISO A.8.8, CIS 7 | Partial | CIO |
| CTL-18 | Immutable and isolated backups | BC/DR | Technical / Corrective | ISO A.8.13, CIS 11, PISF | **Implemented** | CIO |
| CTL-19 | Restore testing and DR failover | BC/DR | Administrative / Detective | ISO A.5.30, CSF Recover | Gap | CIO |
| CTL-20 | AI governance | AI governance | Administrative / Preventive | NIST AI RMF GOVERN, MAP | Gap | Maintenance / Data & AI |
| CTL-21 | Model drift monitoring with human review | AI governance | Technical / Detective | NIST AI RMF MEASURE, MANAGE | Gap | Maintenance / Data & AI |
| CTL-22 | Email security and awareness | Governance | Administrative / Preventive | CIS 9, CIS 14, ISO A.6.3 | **Implemented** | CISO |
| CTL-23 | Vendor security requirements | Supply chain | Administrative / Preventive | ISO A.5.19 to A.5.21, PISF | Gap | CISO / Procurement |
| CTL-24 | Minimum logging standard and SIEM coverage | Logging | Technical / Detective | ISO A.8.15, CIS 8, CSF Detect | Partial | CISO |
| CTL-25 | Incident and recovery exercise programme | BC/DR | Administrative / Corrective | ISO A.5.24, A.5.30, CIS 17 | Gap | CISO |

Three Implemented, nine Partial, thirteen Gap.

### 8.3 Control effectiveness

```
CE = Effective controls / Applicable controls x 100 = 3 / 25 = 12.0%
```

Only Implemented controls count as effective. Counting Partial as half gives 30.0%, and both numbers
are reported everywhere so neither can be quoted alone.

12% is the headline and it is the honest one. Half a control does not half stop an attacker. The Assignment 3 incident is the proof: CTL-07 was Partial, MFA was enforced on cloud and
IT admin accounts but not on OT vendor paths, and the attacker walked in through the half that was
missing.

Four of the thirteen Gaps sit on Critical risks and are therefore the critical control gaps:
CTL-12, CTL-15, CTL-16 and CTL-25.

### 8.4 PISF 2026 mapping

| PISF domain | PSR controls | Rating |
|---|---|---|
| PISF-GOV Governance | CTL-22 | Partially compliant |
| PISF-AST Asset management | CTL-03, CTL-05 | Weak |
| PISF-RSK Risk management | Risk register and treatment plan | Compliant |
| PISF-IAM Identity and access | CTL-07, CTL-08, CTL-09, CTL-10, CTL-11, CTL-16 | Partially compliant |
| PISF-NET Network security | CTL-01 | Partially compliant |
| PISF-OT Operational technology | CTL-01, CTL-02, CTL-03, CTL-04, CTL-05 | Weak |
| PISF-APP Application security | CTL-11, CTL-12, CTL-13 | Weak |
| PISF-DAT Data protection | CTL-10, CTL-14, CTL-15 | Partially compliant |
| PISF-CLD Cloud security | CTL-16 | Weak |
| PISF-LOG Logging and monitoring | CTL-06, CTL-15, CTL-24 | Partially compliant |
| PISF-BDR Backup and recovery | CTL-18, CTL-19, CTL-25 | Partially compliant |
| PISF-TPR Third-party risk | CTL-02, CTL-23 | Non-compliant |
| PISF-AIG AI governance | CTL-06, CTL-20, CTL-21 | Non-compliant |

PISF alignment overall is 38.5%.

## 9. Compliance assessment and gap analysis

### 9.1 Method

Compliance is scored as a heat map, 13 domains across 6 frameworks, 78 cells. Eighteen cells are Not Applicable, leaving
60. Each applicable cell is weighted:

| Rating | Weight |
|---|---|
| Compliant | 1.0 |
| Partially compliant | 0.5 |
| Weak | 0.25 |
| Non-compliant | 0.0 |

```
Compliance = Satisfied requirements / Applicable requirements x 100
           = 22.75 / 60 = 37.9%
```

Of the 60 applicable cells: 2 Compliant, 31 Partially compliant, 21 Weak, 6 Non-compliant.

### 9.2 By framework

| Framework | Compliance |
|---|---|
| ISO 27001 | 44.2% |
| NIST CSF | 42.3% |
| CIS Controls | 38.9% |
| PISF 2026 | 38.5% |
| IEC 62443 / SP 800-82 | 27.8% |
| NIST AI RMF | 16.7% |

### 9.3 By domain

| Domain | Compliance |
|---|---|
| Risk management | 65.0% |
| Network security and segmentation | 50.0% |
| Data protection and privacy | 50.0% |
| Asset management | 45.0% |
| Identity and access management | 45.0% |
| Logging, monitoring and detection | 45.0% |
| Backup and disaster recovery | 40.0% |
| Application and API security | 37.5% |
| Governance and policy | 35.0% |
| OT and safety systems | 25.0% |
| Cloud security | 25.0% |
| Third-party and supply chain | 15.0% |
| AI governance | 6.2% |

Risk management at 65% is the strongest domain and that is not a coincidence. PSR has been working on it for four assignments straight. AI governance at 6.2% is the weakest, and the AI
engine is already in production making maintenance decisions on safety-relevant assets.

### 9.4 Requirement-level gap analysis

Mapping all 25 controls against all 235 requirements produces 52 requirement gaps, ranked by the
inherent risk each one leaves open.

| Framework | Requirements | Addressed | Coverage |
|---|---|---|---|
| PISF 2026 | 13 | 11 | 84.6% |
| CIS Controls | 18 | 15 | 83.3% |
| NIST CSF | 22 | 8 | 36.4% |
| COBIT | 13 | 4 | 30.8% |
| ISO 27001 | 93 | 19 | 20.4% |
| OT (IEC 62443 / SP 800-82) | 57 | 7 | 12.3% |
| NIST AI RMF | 19 | 2 | 10.5% |

Top gaps by the risk behind them:

| Gap | Requirement | Status | Controls | Max risk |
|---|---|---|---|---|
| GAP-001 | CIS 17 Incident Response Management | Gap | CTL-25 | 20 |
| GAP-002 | ISO A.5.30 ICT readiness for business continuity | Gap | CTL-19, CTL-25 | 20 |
| GAP-003 | CIS 1 Inventory and Control of Enterprise Assets | Partial | CTL-03, CTL-05 | 20 |
| GAP-005 | CIS 7 Continuous Vulnerability Management | Partial | CTL-17 | 20 |
| GAP-006 | CIS 8 Audit Log Management | Partial | CTL-04, CTL-15, CTL-24 | 20 |
| GAP-008 | IEC 62443-3-3 SR 5.1 Network segmentation | Partial | CTL-01 | 20 |
| GAP-011 | ISO A.5.18 Access rights | Partial | CTL-02, CTL-08, CTL-09 | 20 |
| GAP-012 | ISO A.5.34 Privacy and protection of PII | Partial | CTL-14 | 20 |
| GAP-013 | ISO A.8.2 Privileged access rights | Partial | CTL-02, CTL-08, CTL-16 | 20 |
| GAP-014 | ISO A.8.5 Secure authentication | Partial | CTL-02, CTL-05, CTL-07 | 20 |

OT coverage at 12.3% looks alarming until you read the catalogue. IEC 62443-3-3 has 57 system
requirements and PSR has five OT controls, so low coverage is arithmetic and not negligence.
Read properly, it says OT needs its own control programme, not that the existing five are bad.

Requirements no control addresses are listed in `outputs/gap/not_addressed.csv`. Most are physical,
HR or secure-development controls that fall outside the 25 in the register. They belong in the Statement of Applicability discussion and should not be counted as failures.

## 10. Audit plan and findings

### 10.1 Plan

Each test starts at a requirement, names the control meant to satisfy it, pulls the evidence that
control produces, examines that evidence, and records a finding with a recommendation wherever the
evidence does not hold. Evidence is graded by how much it can be trusted:

| Evidence type | Confidence |
|---|---|
| System-generated log or export | Highest |
| Configuration extract | High |
| Screenshot | Medium |
| Signed document | Medium |
| Verbal assertion | Lowest, never sufficient alone |

Five testing methods are used: inquiry, observation, inspection, re-performance and automated
testing. Inquiry alone never closes a test.

### 10.2 Findings

Seven findings came from the Assignment 2 audit plan and seven from the Assignment 3 post-incident
review. Thirteen findings plus one observation.

| ID | Sev | Control | Finding |
|---|---|---|---|
| AUD-01 | High | CTL-01 | Physical segmentation exists but firewall rules are very liberal |
| AUD-02 | High | CTL-07 | MFA enforced for cloud and IT admin, not for OT or vendor remote access |
| AUD-03 | Medium | CTL-10 | RBAC correct, but manual offboarding left two transferred staff with old rights |
| AUD-04 | Observation | CTL-18 | Backups immutable and isolated, recoverability never timed |
| AUD-05 | High | CTL-20 | No AI governance; model in production without inventory or approval |
| AUD-06 | High | CTL-23 | Vendor contracts purely commercial, no security assessment or notification SLA |
| AUD-07 | High | CTL-24 | IT and cloud logging reaches the SIEM; OT and legacy do not |
| PIR-01 | Critical | CTL-02 | Standing vendor account, no exploit needed, no expiry |
| PIR-02 | High | CTL-07 | Attacker used the MFA gap already recorded in AUD-02 |
| PIR-03 | Critical | CTL-09 | Domain admin account of a 2024 leaver still enabled |
| PIR-04 | High | CTL-19 | Full restore took 61 hrs against an 8 hr RTO |
| PIR-05 | Critical | CTL-15 | 1.9 TB left the passenger database over four days with no alert |
| PIR-06 | High | CTL-01 | Any/any maintenance rules stayed open after the possession ended |
| PIR-07 | High | CTL-25 | The incident response plan had never been exercised |

Three Critical, nine High, one Medium, one observation.

### 10.3 What the findings actually say

Audit and incident agree with each other, and that's the finding behind the findings. PIR-02
is AUD-02. PIR-06 is AUD-01. The audit told PSR where it would be attacked, in writing, before it
was attacked there. Nothing was done in between.

CTL-18 is the counter-example worth holding on to. Backups were genuinely immutable and genuinely
isolated from production credentials, which is why the ransomware did not reach them, which is why
PSR recovered at all. The observation against it was that recoverability was never timed. That
observation then became PIR-04 when the restore took 61 hours.

An observation isn't a finding. This one became a finding because nobody acted on it.

## 11. IAM architecture

### 11.1 Pipeline

```
User ──► Identity ──► Authentication ──► Authorization ──► Least privilege ──► Monitoring
         HR source     MFA (CTL-07)      RBAC (CTL-10)     PAM (CTL-08)       SIEM (CTL-24)
         JML (CTL-09)  vendor via PAM    ABAC for OT       recertification    DAM (CTL-15)
           ◄GAP          (CTL-02) ◄GAP                     (CTL-09) ◄GAP        ◄GAP
```

Four of the six stages have a Gap in them. Two of them work: authentication for IT and cloud, and RBAC on the passenger database.

### 11.2 Access control models and where each is used

| Model | Used for | Why that model |
|---|---|---|
| MAC | Signalling and interlocking logic (DATA-11) | Safety classification is fixed by the system, not by an owner. No user can reclassify it |
| RBAC | Passenger data, ticketing, crew scheduling | Stable job functions, high user count, easy to recertify |
| ABAC | OT remote access, maintenance possessions | The decision depends on time, location and work order, not just who you are |
| DAC | Not used for Restricted or Critical data | Owner-granted access cannot be recertified reliably at 15,000 staff |

### 11.3 Role to permission matrix

| Role | Train control (AST-01) | Signalling (AST-02) | Passenger DB (AST-04) | Ticketing (AST-03) | SIEM (AST-06) | AI engine (AST-07) |
|---|---|---|---|---|---|---|
| Train Controller | Read / Execute | Read | — | — | — | — |
| Signalling Engineer | Read | Read / Write* | — | — | — | — |
| Station Supervisor | Read | — | — | Read | — | — |
| Booking Agent | — | — | Read (masked) | Read / Write | — | — |
| Data Analyst | — | — | Read (pseudonymised) | Read | — | Read |
| SOC Analyst | Read (logs) | Read (logs) | Read (logs) | Read (logs) | Read / Write | Read (logs) |
| Maintenance Vendor | — | — | — | — | — | — |
| ML Engineer | — | — | — | — | — | Read / Write* |
| DBA | — | — | Admin* | Admin* | — | — |

`*` requires PAM checkout with MFA and an approved change ticket.

Notice that the vendor row is empty. That's on purpose. Vendors get no standing permission at all. Everything a vendor
can do is granted per session through the ABAC rule below and expires with it.

### 11.4 ABAC policy for OT vendor access

```
RULE  ot_vendor_session
IF    Subject.role        = maintenance_vendor
AND   Subject.mfa         = true
AND   Resource.zone       = OT
AND   Action              = remote_session
AND   Environment.path    = pam_jump_host
AND   Environment.time    IN approved_possession_window
AND   Environment.src_net = vendor_vpn
AND   Context.change_ticket = approved
THEN  GRANT (max 8 hours, session recorded, credential rotates on check-in)
ELSE  DENY
WHY   PIR-01: a standing vendor account with no expiry was the entry point
```

Three further rules follow the same shape:

```
RULE  deny_standing_ot_access
IF    Resource.zone = OT AND Subject.access_type = standing
THEN  DENY
WHY   no permanent credential may exist in the OT zone

RULE  bulk_passenger_read
IF    Resource.data_class = Restricted AND Action.row_count > 1000
THEN  DENY unless Context.approval = data_owner
WHY   PIR-05: 1.9 TB left the passenger database unnoticed

RULE  dormant_account
IF    Subject.last_login > 90 days
THEN  DENY and disable
WHY   PIR-03: a 2024 leaver's domain admin account was still enabled
```

### 11.5 Access review

Quarterly for Restricted and Critical, annually for everything else, and the business owner signs,
not IT.

| Review | Scope | Reviewer | Frequency | Evidence |
|---|---|---|---|---|
| Privileged accounts | All PAM-vaulted accounts | CISO | Monthly | PAM checkout report |
| Restricted data access | AST-03, AST-04, AST-09 | Data owner | Quarterly | RBAC extract with sign-off |
| OT access | AST-01, AST-02, AST-08, AST-11 | OT/Engineering lead | Quarterly | Jump host account list |
| Vendor accounts | All third-party identities | Procurement and CISO | Quarterly | Vendor register reconciliation |
| Dormant accounts | Enterprise-wide | IT Department | Monthly | Accounts with no login in 90 days |
| General staff | All other systems | Line manager | Annually | Recertification report |

Sample review table:

| Account | Role | System | Last login | Owner decision | Action |
|---|---|---|---|---|---|
| svc_vendor_maint01 | Vendor service | AST-01 | 11 days | Revoke | Replaced by ABAC session grant |
| a.khan_adm | Domain admin | Enterprise | 612 days | Revoke | Leaver 2024, disabled |
| s.iqbal | Booking agent | AST-03 | 2 days | Retain | — |
| r.malik | Signalling engineer | AST-02 | 4 days | Retain | — |
| d.hussain | Transferred to Finance | AST-04 | 38 days | Revoke | Transfer, rights not removed (AUD-03) |

IAM readiness is 4 of 10 checks, so 40%.

## 12. Data protection architecture

### 12.1 Encryption

| State | Control | Status |
|---|---|---|
| At rest | AES-256 on AST-03, AST-04, AST-09, AST-15; keys in an HSM, never in the same database | Partial |
| In transit | TLS 1.3 externally, mutual TLS between application and database, IPsec on the OT boundary | Partial |
| In use | Not implemented. Confidential computing is a roadmap item for the payment token path | Gap |

Key management is the part most often skipped. Keys sit in an HSM, rotate annually, and the database
administrator role cannot read them. A DBA with full table access and no key access cannot decrypt
what they can select, which is the control that makes CTL-14 worth anything.

### 12.2 Privacy

| Principle | How PSR applies it |
|---|---|
| Lawful basis | Contract for booking, legal obligation for identity verification |
| Minimisation | Analysts receive pseudonymised data, booking agents see masked CNIC digits |
| Purpose limitation | Travel history may not be used to train the maintenance model |
| Retention | Booking records 7 years for tax, CCTV 30 days, SIEM logs 1 year |
| Subject rights | Access, correction and erasure through Passenger Services, 30 days |
| Breach notification | Regulator and affected passengers, with a criminal referral to the NCCIA under PECA 2016 |
| Cross-border | Passenger data stays in-country. Cloud regions are pinned and contractually fixed |

### 12.3 Architecture

```
                        ┌─── Classification (DATA-01 to DATA-13) ───┐
                        │                                           │
    Public ──► integrity only          Restricted ──► CTL-10 RBAC
    Internal ──► access control                      CTL-14 encryption at rest + in transit
    Confidential ──► + encryption                    CTL-15 database activity monitoring ◄GAP
                                                     DLP on email, USB, cloud upload ◄GAP
                                       Critical ──► + integrity verification
                                                     + offline immutable backup (CTL-18)
```

What's missing is detection. CTL-14 is Partial so most Restricted data is encrypted, but CTL-15
is a Gap, so nothing watches the queries. PIR-05 is exactly that shape: 1.9 TB left over four days
through a legitimate authenticated session. Encryption at rest doesn't stop an attacker who has logged in. Only monitoring does.

Residual privacy risk after the planned controls is R-09 at 10 out of 25, down from 20. It does not
reach Low, and that is deliberate. Any system holding 250,000 passengers' identity data every day carries irreducible exposure.

## 13. BIA, RTO/RPO and DR architecture

### 13.1 Business impact analysis

| Asset | 1 hr | 4 hrs | 24 hrs | 72 hrs | Impact type |
|---|---|---|---|---|---|
| AST-01 Train control | Services halt nationwide | Safety fallback only | Network shutdown | National disruption | Safety, regulatory |
| AST-02 Signalling | Local manual working | Regional stop | Nationwide stop | National disruption | Safety |
| AST-03 E-ticketing | Counter fallback | Revenue loss, queues | Material revenue loss | Reputational, regulatory | Financial, reputational |
| AST-04 Passenger DB | Bookings degraded | Bookings fail | Full stop on digital sales | Regulatory exposure | Regulatory, reputational |
| AST-06 SOC/SIEM | Blind to attack | Detection lost | Compliance breach | Compounded risk | Security |
| AST-07 AI engine | Planning degraded | Manual scheduling | Maintenance backlog | Reliability falls | Operational |
| AST-08 IoT sensors | Condition monitoring lost | Manual inspection | Safety margin falls | Possessions forced | Safety, operational |
| AST-11 Fare gates | Open gates, revenue leak | Manual checking | Revenue loss | Reputational | Financial |
| AST-15 DR site | No effect until needed | No effect | Recovery capability lost | Catastrophic if primary fails | Resilience |

### 13.2 RTO and RPO

| Asset | RTO | RPO | Why |
|---|---|---|---|
| AST-01 Train control | 15 min | 1 min | Safety-critical, nationwide service halt |
| AST-02 Signalling | 15 min | 1 min | Safety-critical, interlocking state must be exact |
| AST-05 Network backbone | 30 min | 5 min | Everything else depends on it |
| AST-06 SOC/SIEM | 30 min | 5 min | Blind time is attacker time |
| AST-15 DR data centre | 30 min | 5 min | Must be ready when the primary is not |
| AST-04 Passenger DB | 1 hr | 5 min | Booking integrity, regulatory exposure |
| AST-08 IoT sensors | 1 hr | 5 min | Safety margin depends on current readings |
| AST-09 Hybrid cloud | 1 hr | 5 min | Hosts applications and replication |
| AST-11 Fare collection | 1 hr | 5 min | Revenue leak, manual fallback exists |
| AST-12 Crew scheduling | 1 hr | 15 min | Paper roster fallback |
| AST-13 Email | 1 hr | 15 min | Coordination, not operations |
| AST-14 CCTV | 1 hr | 5 min | Investigation and station security |
| AST-07 AI engine | 2 hrs | 15 min | Advisory, humans can plan manually |
| AST-10 Mobile app | 2 hrs | 10 min | Counter and web fallback |
| AST-03 E-ticketing | 8 hrs | 15 min | Manual counter ticketing covers the gap |

AST-03 at 8 hours is the corrected value. The Assignment 3 BC/DR table said 2 hours and the incident
narrative assumed 8. Eight is the defensible one, because manual counter ticketing genuinely works
at all 100 stations for most of a day, and promising a 2 hour recovery that was never tested is
worse than promising 8 and meeting it.

### 13.3 DR architecture

```
   PRIMARY DATA CENTRE                    DISASTER RECOVERY SITE (AST-15)
   ┌────────────────────┐   continuous    ┌────────────────────┐
   │ AST-01 · AST-02    │ ─ replication ─►│ warm standby        │
   │ AST-03 · AST-04    │                 │ RTO 30 min          │
   │ AST-06 · AST-12    │                 │ RPO 5 min           │
   └─────────┬──────────┘                 └────────────────────┘
             │
             ├──► HYBRID CLOUD (AST-09) ── object replication, pinned in-country
             │
             └──► IMMUTABLE BACKUP (CTL-18)
                  offline, isolated from production credentials
                  3 copies · 2 media · 1 offline
```

CTL-18 is the control that saved PSR in the Assignment 3 incident. Backups were immutable and the
credentials that could have deleted them were not reachable from the ticketing domain. The
ransomware encrypted production and could not touch the backups.

What it did not do was make recovery fast. BC/DR readiness is 6 of 10, and the four failures are all
on the same theme: no BIA signed off, restores never timed, failover never exercised, RTO never met
in a test. PSR can recover. What PSR can't say is how long recovery takes, and PIR-04 is what happens when
you find out during the incident. 61 hours against an 8 hour objective, 53 hours over.

## 14. Incident response and SOC architecture

### 14.1 Severity and escalation

| Severity | Definition | Escalation | Target response |
|---|---|---|---|
| SEV-1 | Safety impact or OT compromise | CISO, COO, CEO, Board, regulator | Immediate |
| SEV-2 | Restricted data breach or service-wide outage | CISO, CIO, Risk Committee | 30 min |
| SEV-3 | Single system compromise, contained | CISO, system owner | 2 hrs |
| SEV-4 | Policy violation, no confirmed compromise | SOC lead | Next working day |

### 14.2 Roles

| Role | Held by | Responsibility |
|---|---|---|
| Incident Commander | CISO | Declares severity, owns the decision log |
| Technical Lead | SOC Lead | Containment and eradication |
| OT Safety Authority | OT/Engineering | Sole authority to return control systems to service |
| Communications | Corporate Affairs | Passenger and media statements |
| Legal and Regulatory | Compliance | NCCIA referral, regulator notification |
| Business Continuity | CIO | Manual fallback, recovery sequencing |
| Scribe | SOC analyst on duty | Timeline for the post-incident review |

The OT Safety Authority holding sole return-to-service authority is the load-bearing clause. A
security incident on a railway can be declared technically contained while the physical system is
still unsafe. Only engineering can make that call.

### 14.3 SOC / SIEM / SOAR architecture

```
   LOG SOURCES                        PLATFORM                      RESPONSE
   ───────────                        ────────                      ────────
   IT endpoints      ─┐
   Cloud (AST-09)    ─┤
   Identity / PAM    ─┼──►  SIEM (AST-06)  ──► Correlation ──►  Analyst triage
   Application/API   ─┤      CTL-24 Partial     use cases          │
   Database (DAM)    ─┤          ▲                                 ├─► SOAR playbooks ◄GAP
     ◄GAP CTL-15      │          │                                 │   isolate host
   OT / IoT  ◄GAP ───┘          │                                 │   revoke session
   Legacy    ◄GAP                │                                 │   disable account
                                 │                                 │
                          Threat intelligence                      └─► Incident Commander
```

CTL-24 is Partial and the Gap is specific. IT and cloud endpoint logs reach the SIEM. OT, IoT,
legacy systems and database activity do not. Hence AUD-07 and PIR-05. Six days inside the environment, four of them spent moving 1.9 TB, all of it through the half of
the estate the SIEM cannot see.

### 14.4 Incident scenario: ransomware on ticketing

| When | What | Phase | Links |
|---|---|---|---|
| Day -11, 21:10 | Maintenance vendor remote account used from an unusual location | Pre-incident | R-16, CTL-02, CTL-07 |
| Day -10, 04:55 | Dormant 2024 domain administrator account picked up | Pre-incident | R-15, CTL-09 |
| Day -6 to -2 | 1.9 TB staged in the cloud and moved out | Undetected | R-09, CTL-15 |
| Day -4, 02:30 | East-west probing against the OT gateway over leftover any/any rules | Undetected | R-01, CTL-01 |
| Day 0, 01:50 | Ransomware deployed across the ticketing platform | Impact | R-05 |
| Day 0, 02:40 | Passenger Services escalates failed bookings and API errors | Detection | CTL-24 |
| Day 0, 03:05 | Station supervisor at Lahore reports a ransom note | Detection | — |
| Day 0, 03:12 | SOC opens the incident, CISO takes command | Detection | AST-06 |
| Day 0, 03:30 to 09:00 | Ticketing cluster isolated, vendor tunnels terminated | Containment | CTL-01, CTL-02 |
| Day 0, 06:00 | Online sales suspended, manual counter ticketing at all 100 stations | Containment | R-07 accepted |
| Day 0 to 1 | Scope settled, OT confirmed not reached, no signalling impact | Analysis | R-01, R-02 |
| Day 1 to 3 | Rebuild from known-good images, 34 dormant privileged accounts disabled, vendor access moved behind the PAM jump host | Eradication | CTL-02, CTL-09 |
| Day 1, +19 h | Live and forward reservations restored, online sales read-only | Recovery | CTL-18 |
| Day 2 | Affected passengers notified, criminal referral to the NCCIA under PECA 2016 | Containment | R-09 |
| Day 3, +61 h | Full ticketing dataset restored | Recovery | CTL-19 |
| Day 4 | Online and app sales stable, counter reconciliation begins | Recovery | — |
| Day 14 | Incident closed after seven days of clean telemetry | Recovery | — |
| Day 21 | Post-incident review, seven findings raised | Lessons learned | CTL-25 |

Two things are worth drawing out. Detection came from a business user noticing failed bookings, not
from the SIEM, and the attacker had been inside for eleven days by then. And OT was never reached,
which was partly CTL-01 and partly luck, since the probing at Day -4 went through boundary rules
that should not have been open.

Incident readiness is 5 of 11 checks, so 45.5%.

## 15. Cloud security

### 15.1 Shared responsibility

| Layer | Provider | PSR |
|---|---|---|
| Physical and facility | ✔ | |
| Hypervisor and host | ✔ | |
| Network infrastructure | ✔ | |
| Guest OS and patching | | ✔ |
| Network configuration and security groups | | ✔ CTL-16 |
| Identity and access | | ✔ CTL-07, CTL-08 |
| Application code | | ✔ CTL-11, CTL-12 |
| Data and classification | | ✔ CTL-10, CTL-14 |
| Encryption keys | | ✔ |
| Logging and monitoring | shared | ✔ CTL-24 |
| Backup and recovery | shared | ✔ CTL-18, CTL-19 |

Every row PSR owns that is currently a Gap is a cloud risk: CTL-16, CTL-12, CTL-15. R-10 is rated
Critical at 16 for that reason.

### 15.2 Cloud risks

| Risk | Control | Status |
|---|---|---|
| Misconfigured storage exposed publicly | CTL-16 secure baseline, policy-as-code checks | Gap |
| Over-permissive IAM roles | CTL-08 PAM, quarterly review | Partial |
| No MFA on cloud admin | CTL-07 | Partial, enforced here |
| Unencrypted data at rest | CTL-14 | Partial |
| Data leaving the country | Region pinning, contractual | In place |
| Configuration drift | Policy-as-code in the pipeline | Gap |

### 15.3 Policy-as-code

Cloud compliance is checked in the deployment pipeline, so nothing waits for an audit to surface.

```
RULE  no_public_storage
IF    resource.type = storage_bucket
AND   resource.public_access = true
THEN  DENY
WHY   passenger data must never be reachable without authentication

RULE  encryption_required
IF    resource.stores_data_class IN (Restricted, Critical)
AND   resource.encryption = false
THEN  DENY
WHY   CTL-14, ISO 27001 A.8.24

RULE  mfa_on_admin
IF    principal.role = admin AND principal.mfa = false
THEN  DENY
WHY   AUD-02, PIR-02

RULE  region_pinned
IF    resource.region NOT IN (approved_in_country_regions)
THEN  DENY
WHY   passenger data sovereignty
```

## 16. IoT and OT security

### 16.1 Purdue model

| Level | What sits there at PSR | Controls |
|---|---|---|
| Level 5 Enterprise | AST-13 email, corporate IT | CTL-22 |
| Level 4 Business | AST-03 ticketing, AST-12 crew scheduling, AST-09 cloud | CTL-11, CTL-14, CTL-16 |
| **DMZ** | PAM jump host, one-way telemetry feed, patch staging | **CTL-01, CTL-02** |
| Level 3 Operations | 3 control centres, AST-06 SOC, historian | CTL-03, CTL-24 |
| Level 2 Supervisory | AST-01 train control, SCADA/HMI | CTL-01, CTL-04, CTL-07 |
| Level 1 Control | AST-02 signalling and interlocking controllers | CTL-04 |
| Level 0 Process | AST-08 track and rolling stock sensors, points, signals | CTL-05, CTL-06 |

The DMZ row is where the programme lives or dies. Every control that would stop an attacker moving
from Level 4 to Level 2 sits in that one row, and both of those controls are incomplete. CTL-01 is
Partial and CTL-02 is a Gap.

### 16.2 IEC 62443 security levels

| Zone | Target SL | Current | Why |
|---|---|---|---|
| Signalling and interlocking (L1) | SL 3 | SL 1 | Protection against deliberate attack with moderate resources is required for safety |
| Train control (L2) | SL 3 | SL 1 | Nationwide service impact |
| IoT sensing (L0) | SL 2 | SL 0 | No device identity at all today |
| Fare collection | SL 2 | SL 1 | Financial, not safety |
| Enterprise IT | SL 1 | SL 1 | Covered by CIS and ISO instead |

### 16.3 IoT lifecycle

| Stage | Control | Status |
|---|---|---|
| Procurement | Security requirements in the vendor annex (CTL-23) | Gap |
| Onboarding | Unique device identity, no default credentials (CTL-05) | Gap |
| Operation | Telemetry validation before use (CTL-06) | Gap |
| Maintenance | Signed firmware, staged through the DMZ | Gap |
| Decommission | Credential revocation and inventory removal (CTL-03) | Partial |

Thousands of devices with no unique identity, and that's the honest summary. R-04 at 12 reflects it, and it
has not moved at all because both of its controls are Gaps.

### 16.4 Supply chain

| Vendor type | Access | Risk | Control |
|---|---|---|---|
| OT maintenance | Remote to Level 2 | R-16, R-01 | CTL-02 ABAC session, CTL-23 |
| Cloud provider | Infrastructure | R-10 | Shared responsibility, region pinning |
| Payment provider | Tokenised, no card data held | R-09 reduced | Tokenisation, PCI DSS on their side |
| Telecom | Network transit | R-17 | Encryption in transit |
| Technology vendors | Software supply | R-16 | CTL-23, signed artefacts |

Supply chain compliance is 15%, the second weakest domain, and PIR-01 shows what that buys you. The
entry point in the incident was a vendor account, not an exploit. No vulnerability was used. They just logged in.

## 17. Quantum readiness

PSR is not migrating to post-quantum cryptography this year. This section is here to work out which systems will need it and which can wait, because "harvest now, decrypt later" makes the
decision about data lifetime rather than about today's threat.

| System | Current crypto | Data lifetime | Priority | Migration |
|---|---|---|---|---|
| Signed OT firmware (AST-02, AST-08) | RSA/ECDSA signatures | 15 to 25 years in service | **Highest** | ML-DSA. Signature forgery on safety firmware is the worst case, and equipment outlives the crypto |
| PKI and certificate authority | RSA 2048 | 10 years | High | Hybrid certificates first, then ML-DSA |
| Backups (CTL-18) | AES-256 at rest | 7 years retention | High | AES-256 is quantum-resistant enough. Protect the key exchange, not the cipher |
| Passenger data at rest (AST-04) | AES-256 | 7 years | Medium | Same reasoning |
| TLS on the portal and app | ECDHE key exchange | Session only | Medium | ML-KEM hybrid when the provider supports it |
| VPN and OT boundary (CTL-01) | IKEv2 with DH groups | Session, but long-lived tunnels | Medium | ML-KEM hybrid |
| Payment tokens | Provider-managed | Short | Low | Follows the payment provider |

That ordering is deliberate and not the obvious one. Most PQC plans start with TLS because it's visible. For a railway, signed firmware comes first, because a signalling controller installed in
2026 is still in the track in 2046, and whoever can forge its update signature then can push
whatever they want to it.

## 18. AI automation

### 18.1 What was automated and why

Mapping 25 controls to 235 requirements across 7 frameworks by hand is slow and inconsistent. The
Assignment 2 control matrix mapped each control to only 2 or 3 requirements, and PISF, COBIT and
NIST CSF were covered unevenly. Redoing it every time a control changes is not realistic.

So the automation is control mapping and requirement-level gap analysis.

### 18.2 How it works

```
controls.csv ──► TF-IDF retrieval ──► 5 candidates per framework ──► local LLM
                                                                     (Ollama, qwen2.5:7b, temp 0, seed 42)
                                           │
                                    JSON: req_id, confidence, rationale
                                           │
                                    ┌──────▼───────┐
                                    │  GUARDRAILS  │
                                    │ shortlist check · ID repair
                                    │ injection scan · localhost only
                                    └──────┬───────┘
                                           ▼
                            ai_mapping_ollama.csv (human_decision blank)
                                           │
                                 human reviewer accepts / rejects
                                           ▼
                            gap analysis ──► 52 ranked gaps
```

Everything runs locally. `assert_local_endpoint` refuses any non-localhost URL, so control data never
leaves the machine. Data leakage is controlled in code here, not in a policy document.

### 18.3 Results

| Metric | Result |
|---|---|
| Suggestions produced | 139 across 25 controls |
| Trust Score (full reference) | 123 / 139 = 88.5% |
| Trust Score (frozen reference) | 111 / 139 = 79.9% |
| Recall of the A2/A3 manual mapping | 72.6% |
| Accepted by reviewers | 121 / 139 = 87.1% |
| Invented IDs blocked by the guardrail | 2 |
| Real IDs in the wrong format, repaired | 10 |
| Parse failures | 0 |
| Manual effort | 650 min |
| AI-assisted effort | 185.3 min (46.3 runtime + 139 review) |
| **Automation Gain** | **71.5%** |
| No-LLM retrieval baseline | 90.6% trust, 50.0% recall |

Per framework, the model is strongest on CIS (96.4% trust, 83.3% recall) and weakest on COBIT
(53.8% trust) and OT (44.4% recall). Human review is mandatory there, not advisory.

### 18.4 Two numbers, not one

The Trust Score is reported twice on purpose.

While reviewing the output, reviewers added 15 pairs to the reference mapping that they judged
correct. Twelve of those 15 were pairs the model itself had suggested. Grading a run against a
reference its own output has extended inflates the score. Excluding those rows gives a frozen Trust Score of 79.9%, which is 8.6 points lower.

Both figures are in the report because the gap between them is itself the finding. Those rows are
flagged `added_during_review = Y` in the CSV so the calculation is reproducible either way.

### 18.5 AI Automation Card

| Item | Answer |
|---|---|
| IA phase | Framework mapping and compliance gap analysis |
| Existing problem | Manual mapping of 25 controls to 235 requirements is slow and uneven |
| Input | Control register and framework catalogues. No personal data |
| AI method | TF-IDF retrieval shortlist, then a local LLM selects, with confidence and rationale |
| Processing | Retrieve, prompt with the control fenced as data, validate against the shortlist, compute requirement status, rank gaps by inherent risk |
| Output | Suggested mappings for review, ranked gap register, framework coverage summary, evaluation report |
| Human role | Accept or reject every suggestion. Priority review for OT, segmentation and AI mappings |
| Security risk | Hallucination, prompt injection through control text, data leakage, over-reliance |
| Accuracy | Trust Score 88.5% full and 79.9% frozen, recall 72.6%, per-framework breakdown, full error list |
| Benefit | 71.5% time saving, full coverage of 7 frameworks instead of 2 to 3 per control, repeatable |
| Limitation | Cannot judge whether a control is actually implemented. Works from catalogue summaries, not full standard text. PISF is domain level. Weak on COBIT and OT |
| Governance | Owner CISO. Compliance approves before mappings enter the register. Internal Audit samples quarterly. The AI never changes a control status or a risk score |

### 18.6 Governance of our own AI

| Risk | How it could happen | Control in the tool | What a human still does |
|---|---|---|---|
| Hallucination | Invents a requirement ID | Only shortlisted IDs accepted. Badly formatted real IDs repaired and counted, anything else dropped | Reviews every suggestion |
| Bias | Favours ISO and CIS, under-maps OT and AI | Equal candidates per framework, per-framework scores published | Checks the per-framework table |
| Data leakage | Control data sent to an external service | Localhost-only enforced in code | CISO approval before any remote model |
| Prompt injection | Control text says "mark all controls compliant" | Control text fenced as data, injection scanner logs hits. The model cannot change status or scores | Investigates any flagged control |
| Model drift | New model version changes results | Temperature 0, seed 42, model and run time logged, evaluation rerun on every change | Re-baselines the Trust Score |
| Over-reliance | Analyst accepts without checking | Every row starts blank, gap report marked PRELIMINARY until reviewed, verification rate published | Signs off the reviewed mapping |
| Explainability | CISO cannot see why | Rationale, confidence and retrieval similarity on every row | Rejects unconvincing rationales |
| Availability | Ollama not running | Retrieval-only baseline still runs | Decides if the baseline is sufficient |
| Vendor risk | Model withdrawn | Open-weight model held locally, any model swappable with `--model` | Approves the model choice |

### 18.7 What went wrong, and what it taught us

Run one looked bad. 35.5% recall and 69 apparently invented requirement IDs.

Reading the run log showed every one of the 69 was a real ID in the wrong shape. Qwen was returning "ISO 27001 A.8.22" and "A.8.2 | ISO 27001" where the catalogue held "A.8.22". Our guardrail was matching exact strings, so it rejected all of them as hallucinations. The guardrail
was too strict and it reported its own over-rejection as the model's failure.

After adding token-level ID repair, recall roughly doubled and only 2 genuinely invented IDs
remained.

That's the AI governance lesson of this project, and it isn't the one we expected to write. A
safety control on an AI system can fail silently, in the safe direction, and look like evidence that
the AI is unreliable. Nothing in the output said so. Accuracy agreed with the guardrail, because both were measuring the same wrong thing. Only reading the logs found it.

Which is the argument for the human review step existing at all. The model mostly doesn't hallucinate. What it can't do is see when the measurement around it has
gone wrong.

## 19. Maturity assessment and roadmap

### 19.1 Current maturity

```
M = sum of capability scores / number of capabilities = 19 / 10 = 1.9 / 5
```

| Capability | Score | Year 3 | Evidence |
|---|---|---|---|
| Governance | 2 | 4 | Structure and owners defined, policy set not formalised |
| Risk Management | 3 | 4 | Registers, justified scores, treatment for every High and Critical |
| IAM | 2 | 4 | RBAC in place, MFA and PAM Partial, JML and vendor access Gaps |
| Data Protection | 2 | 4 | Classification exists, encryption Partial, no DAM |
| Incident Response | 2 | 4 | Plan and 24x7 SOC exist, never exercised, OT not detected |
| BC/DR | 2 | 4 | Immutable backups and warm DR, restores never timed |
| AI Governance | 1 | 3 | Model in production with no inventory, approval or drift monitoring |
| OT Security | 1 | 3 | Weak against every applicable framework |
| Supply Chain | 1 | 3 | Contracts purely commercial, no security annex |
| Audit | 3 | 4 | Full audit chain and tracked findings, no independent committee yet |

Band: 1.5 or above is Developing. **PSR is DEVELOPING at 1.9, target 3.7 by Year 3.**

Only three capabilities score 1. All three are where the Critical risks live.

### 19.2 Readiness

| Area | Score |
|---|---|
| IAM | 4 / 10 = 40.0% |
| BC/DR | 6 / 10 = 60.0% |
| Incident response | 5 / 11 = 45.5% |
| AI governance | 4.5 / 12 = **3.75 / 10** |

```
AI Readiness = Obtained / Maximum x 10 = 4.5 / 12 x 10 = 3.75
```

### 19.3 Three-year roadmap

**Year 1, Foundation.** Stop the bleeding the audit already found.

| Action | Control | Closes | Maturity effect |
|---|---|---|---|
| MFA everywhere including OT and vendor paths | CTL-07 | AUD-02, PIR-02 | IAM 2 to 3 |
| Brokered, time-bound vendor access through PAM | CTL-02 | PIR-01 | OT 1 to 2 |
| Default-deny IT/OT boundary with expiring exceptions | CTL-01 | AUD-01, PIR-06 | OT 2 to 3 |
| JML automation and quarterly recertification | CTL-09 | PIR-03 | IAM 3 |
| Database activity monitoring | CTL-15 | PIR-05 | Data protection 2 to 3 |
| First tabletop and timed restore drill | CTL-25, CTL-19 | PIR-04, PIR-07 | BC/DR 2 to 3, IR 2 to 3 |
| Formalise the policy set | section 3 | Governance gap | Governance 2 to 3 |
| Vendor security annex in all contracts | CTL-23 | AUD-06 | Supply chain 1 to 2 |

**Year 2, Integration.** Make the controls talk to each other.

| Action | Control | Effect |
|---|---|---|
| OT and IoT log sources into the SIEM | CTL-24 | Closes AUD-07, IR detection |
| SOAR playbooks for isolate, revoke, disable | CTL-24 | IR 3 to 4 |
| AI inventory, model registry, approved datasets | CTL-20 | AI governance 1 to 2 |
| Drift monitoring with human review | CTL-21 | AI governance 2 |
| IoT device identity rollout | CTL-05 | OT 3, closes R-04 |
| Telemetry validation before AI use | CTL-06 | Closes R-11 path |
| Policy-as-code in the cloud pipeline | CTL-16 | Cloud 25% upward |
| SAST and DAST in the release pipeline | CTL-12 | Closes R-06 |
| Internal Audit reporting to the Board Audit Committee | section 2 | Audit 3 to 4 |

**Year 3, Optimisation.** Prove it, continuously.

| Action | Effect |
|---|---|
| Continuous control monitoring against the registers | Evidence availability from 25% to above 80% |
| Signalling command authentication (CTL-04) at IEC 62443 SL 3 | OT 3 |
| PQC migration begins with signed OT firmware | Quantum readiness |
| Annual independent audit and red team | Audit 4 |
| Automated evidence collection feeding the dashboard | Maturity 3.7 |

### 19.4 Top five recommendations

Ranked by the inherent risk exposure each one would reduce. Calculated, not chosen.

| # | Control | Action | Risks | Owner |
|---|---|---|---|---|
| 1 | CTL-07 | Extend MFA to OT jump hosts and vendor remote access, no exceptions | R-01, R-05, R-09, R-10, R-14, R-15 | CISO |
| 2 | CTL-25 | First tabletop and restore drill within the first quarter | R-05, R-12, R-17 | CISO |
| 3 | CTL-12 | Mandatory SAST/DAST in the pipeline plus an annual penetration test | R-06, R-07 | CIO |
| 4 | CTL-02 | Remove standing vendor access, time-bound checkout through PAM with MFA | R-01, R-16 | CISO |
| 5 | CTL-01 | Default-deny between IT and OT, every exception owned and expiring | R-01, R-02, R-03 | OT/Engineering |

## 20. Final assurance position

### 20.1 The dashboard

Our one-page CISO Executive Dashboard is `outputs/ciso_dashboard.pdf`, generated from the registers
by `dashboard.py`. It's reproduced on the next page. The HTML beside it holds the same page plus the
registers underneath it, so clicking a heat map cell or a control opens the rows the figure was
calculated from. Printing it gives back the same single page.

| Measure | Result |
|---|---|
| Overall IA status | **DEVELOPING** |
| Governance maturity | 1.9 / 5, Year 3 target 3.7 |
| Overall risk score | 11.9 / 25 current, 13.8 inherent, 7.2 target |
| High / Critical risks | 14 of 17 |
| Control effectiveness | 12.0% (30.0% weighted) |
| Compliance | 37.9% |
| Audit findings | 13 (3 Critical, 9 High, 1 Medium) |
| Critical control gaps | 4: CTL-12, CTL-15, CTL-16, CTL-25 |
| IAM readiness | 40.0% |
| BC/DR readiness | 60.0% |
| Incident readiness | 45.5% |
| AI governance readiness | 3.75 / 10 |
| Evidence available | 25.0% of 68 items |
| AI automation impact | 71.5% time saving at 88.5% trust (79.9% frozen) |

Top five risks now: R-06 broken API access control (16), R-03 legacy OT (15), R-05 ticketing
ransomware (15), R-09 passenger data exfiltration (15), R-01 train control compromise (15).

### 20.2 Corrections carried from Assignments 1 to 3

| # | Issue | Decision |
|---|---|---|
| 1 | AST-03 RTO was 2 hrs in the A3 table and 8 hrs in the A3 incident | 8 hrs |
| 2 | A3 called R-05 one of four Critical risks | There are five: R-03, R-05, R-06, R-09, R-10 |
| 3 | A3 said the scenario was built from OT and SCADA rows | It is ransomware on e-ticketing, R-05 |
| 4 | AST-08 missing from the A3 RTO/RPO table | RTO 1 hr, RPO 5 mins |
| 5 | A2 Section E had the Audit Plan heading twice | Second version kept |

### 20.3 What the numbers say

PSR adopted technology faster than it secured it.

Evidence for that sits in the shape of the scores rather than their level. Risk management sits at
3 and governance documentation is in reasonable order, because those are the activities that produce
paper. OT security, AI governance and supply chain all sit at 1, and all three hold Critical risks.
PSR knows what's wrong. Everything is written down carefully. What hasn't happened is building the controls.

The Assignment 3 incident is the same statement in operational form. Each gap the attacker used was
already in the registers before the attack. PIR-01 was a known standing vendor account. PIR-02 was
AUD-02, written down and unactioned. PIR-03 was a dormant admin account that CTL-09 would have
caught. PIR-05 was the database monitoring gap. Not one of them was a surprise.

Control effectiveness at 12% against compliance at 37.9% is the gap between having a programme on
paper and having one running. Evidence availability at 25% is the same gap measured a third way.

Recovery is where the programme earned something back. CTL-18 was one of only three Implemented
controls, it was implemented properly, and it is the reason the ransomware did not become permanent
data loss. One well-built control did more than twenty planned ones.

Hence a Year 1 roadmap that is short rather than ambitious. Eight actions, all of
them already named in a finding, none of them novel. Doing those eight moves maturity from 1.9 to
roughly 2.8 and takes the Critical risk count from five to two, without a single new technology
being introduced.
