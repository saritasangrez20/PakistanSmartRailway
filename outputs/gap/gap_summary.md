# Requirement level gap analysis

Mapping used: `outputs/mapping/ai_mapping_ollama.csv`

| Framework | Requirements | Addressed | Satisfied | Partial | Gap | Not addressed | Coverage % | Compliance of addressed % |
|---|---|---|---|---|---|---|---|---|
| CIS Controls | 18 | 15 | 5 | 6 | 4 | 3 | 83.3 | 53.3 |
| COBIT | 13 | 4 | 1 | 0 | 3 | 9 | 30.8 | 25.0 |
| OT (IEC 62443 / SP 800-82) | 57 | 7 | 0 | 3 | 4 | 50 | 12.3 | 21.4 |
| ISO 27001 | 93 | 19 | 4 | 8 | 7 | 74 | 20.4 | 42.1 |
| NIST AI RMF | 19 | 2 | 0 | 0 | 2 | 17 | 10.5 | 0.0 |
| NIST CSF | 22 | 8 | 2 | 4 | 2 | 14 | 36.4 | 50.0 |
| PISF 2026 | 13 | 11 | 2 | 6 | 3 | 2 | 84.6 | 45.5 |

## Top 15 gaps by risk exposure (52 in total)

| Gap | Framework | Requirement | Status | Controls | Max inherent risk |
|---|---|---|---|---|---|
| GAP-001 | CIS Controls | CIS 17 Incident Response Management | Gap (control planned) | CTL-25 | 20 |
| GAP-002 | ISO 27001 | A.5.30 ICT readiness for business continuity | Gap (control planned) | CTL-19;CTL-25 | 20 |
| GAP-003 | CIS Controls | CIS 1 Inventory and Control of Enterprise Assets | Partially satisfied | CTL-03;CTL-05 | 20 |
| GAP-004 | CIS Controls | CIS 2 Inventory and Control of Software Assets | Partially satisfied | CTL-03 | 20 |
| GAP-005 | CIS Controls | CIS 7 Continuous Vulnerability Management | Partially satisfied | CTL-17 | 20 |
| GAP-006 | CIS Controls | CIS 8 Audit Log Management | Partially satisfied | CTL-04;CTL-15;CTL-24 | 20 |
| GAP-007 | CIS Controls | CIS 12 Network Infrastructure Management | Partially satisfied | CTL-01 | 20 |
| GAP-008 | IEC 62443 | 62443-3-3 SR 5.1 Network segmentation | Partially satisfied | CTL-01 | 20 |
| GAP-009 | IEC 62443 | 62443-2-1 Security program requirements for IACS asset owners | Partially satisfied | CTL-03;CTL-17 | 20 |
| GAP-010 | NIST SP 800-82 | SP800-82 OT controls Applying security controls to OT | Partially satisfied | CTL-17 | 20 |
| GAP-011 | ISO 27001 | A.5.18 Access rights | Partially satisfied | CTL-02;CTL-08;CTL-09 | 20 |
| GAP-012 | ISO 27001 | A.5.34 Privacy and protection of PII | Partially satisfied | CTL-14 | 20 |
| GAP-013 | ISO 27001 | A.8.2 Privileged access rights | Partially satisfied | CTL-02;CTL-08;CTL-16 | 20 |
| GAP-014 | ISO 27001 | A.8.5 Secure authentication | Partially satisfied | CTL-02;CTL-05;CTL-07 | 20 |
| GAP-015 | ISO 27001 | A.8.15 Logging | Partially satisfied | CTL-06;CTL-15;CTL-24 | 20 |

Requirements no control addresses are listed in `not_addressed.csv`. Most are physical, HR or development controls outside the 25 controls in the register; review them for the Statement of Applicability rather than treating them all as gaps.
