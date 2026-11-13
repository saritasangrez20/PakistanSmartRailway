# Requirement level gap analysis

Mapping used: `data/ground_truth/reference_mapping.csv`

| Framework | Requirements | Addressed | Satisfied | Partial | Gap | Not addressed | Coverage % | Compliance of addressed % |
|---|---|---|---|---|---|---|---|---|
| CIS Controls | 18 | 17 | 6 | 7 | 4 | 1 | 94.4 | 55.9 |
| COBIT | 13 | 5 | 2 | 1 | 2 | 8 | 38.5 | 50.0 |
| OT (IEC 62443 / SP 800-82) | 57 | 33 | 2 | 17 | 14 | 24 | 57.9 | 31.8 |
| ISO 27001 | 93 | 47 | 10 | 20 | 17 | 46 | 50.5 | 42.6 |
| NIST AI RMF | 19 | 19 | 0 | 0 | 19 | 0 | 100.0 | 0.0 |
| NIST CSF | 22 | 22 | 7 | 5 | 10 | 0 | 100.0 | 43.2 |
| PISF 2026 | 13 | 12 | 4 | 5 | 3 | 1 | 92.3 | 54.2 |

## Top 15 gaps by risk exposure (124 in total)

| Gap | Framework | Requirement | Status | Controls | Max inherent risk |
|---|---|---|---|---|---|
| GAP-001 | CIS Controls | CIS 17 Incident Response Management | Gap (control planned) | CTL-25 | 20 |
| GAP-002 | ISO 27001 | A.5.24 Information security incident management planning and preparation | Gap (control planned) | CTL-25 | 20 |
| GAP-003 | ISO 27001 | A.5.26 Response to information security incidents | Gap (control planned) | CTL-25 | 20 |
| GAP-004 | ISO 27001 | A.5.27 Learning from information security incidents | Gap (control planned) | CTL-25 | 20 |
| GAP-005 | ISO 27001 | A.5.29 Information security during disruption | Gap (control planned) | CTL-19;CTL-25 | 20 |
| GAP-006 | ISO 27001 | A.5.30 ICT readiness for business continuity | Gap (control planned) | CTL-19;CTL-25 | 20 |
| GAP-007 | ISO 27001 | A.8.12 Data leakage prevention | Gap (control planned) | CTL-15 | 20 |
| GAP-008 | NIST CSF | RS.MA Incident Management | Gap (control planned) | CTL-25 | 20 |
| GAP-009 | NIST CSF | RS.AN Incident Analysis | Gap (control planned) | CTL-25 | 20 |
| GAP-010 | NIST CSF | RS.CO Incident Response Reporting and Communication | Gap (control planned) | CTL-25 | 20 |
| GAP-011 | NIST CSF | RS.MI Incident Mitigation | Gap (control planned) | CTL-25 | 20 |
| GAP-012 | CIS Controls | CIS 1 Inventory and Control of Enterprise Assets | Partially satisfied | CTL-03;CTL-05 | 20 |
| GAP-013 | CIS Controls | CIS 5 Account Management | Partially satisfied | CTL-05;CTL-08;CTL-09;CTL-16 | 20 |
| GAP-014 | CIS Controls | CIS 7 Continuous Vulnerability Management | Partially satisfied | CTL-12;CTL-17 | 20 |
| GAP-015 | CIS Controls | CIS 8 Audit Log Management | Partially satisfied | CTL-04;CTL-15;CTL-24 | 20 |

Requirements no control addresses are listed in `not_addressed.csv`. Most are physical, HR or development controls outside the 25 controls in the register; review them for the Statement of Applicability rather than treating them all as gaps.
