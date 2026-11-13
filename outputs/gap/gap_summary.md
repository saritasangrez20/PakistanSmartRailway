# Requirement level gap analysis

Mapping used: `outputs/mapping/ai_mapping_retrieval.csv`

> **PRELIMINARY**: built on AI suggestions that a human has not yet approved. Review the mapping file and rerun with `--approved-only` before relying on it.

| Framework | Requirements | Addressed | Satisfied | Partial | Gap | Not addressed | Coverage % | Compliance of addressed % |
|---|---|---|---|---|---|---|---|---|
| CIS Controls | 18 | 8 | 3 | 3 | 2 | 10 | 44.4 | 56.2 |
| COBIT | 13 | 3 | 0 | 0 | 3 | 10 | 23.1 | 0.0 |
| OT (IEC 62443 / SP 800-82) | 57 | 9 | 1 | 4 | 4 | 48 | 15.8 | 33.3 |
| ISO 27001 | 93 | 13 | 3 | 5 | 5 | 80 | 14.0 | 42.3 |
| NIST AI RMF | 19 | 2 | 0 | 0 | 2 | 17 | 10.5 | 0.0 |
| NIST CSF | 22 | 8 | 2 | 3 | 3 | 14 | 36.4 | 43.8 |
| PISF 2026 | 13 | 11 | 1 | 7 | 3 | 2 | 84.6 | 40.9 |

## Top 15 gaps by risk exposure (44 in total)

| Gap | Framework | Requirement | Status | Controls | Max inherent risk |
|---|---|---|---|---|---|
| GAP-001 | NIST CSF | RC.RP Incident Recovery Plan Execution | Gap (control planned) | CTL-19;CTL-25 | 20 |
| GAP-002 | NIST CSF | RC.CO Incident Recovery Communication | Gap (control planned) | CTL-19;CTL-25 | 20 |
| GAP-003 | CIS Controls | CIS 7 Continuous Vulnerability Management | Partially satisfied | CTL-17 | 20 |
| GAP-004 | CIS Controls | CIS 12 Network Infrastructure Management | Partially satisfied | CTL-01 | 20 |
| GAP-005 | IEC 62443 | 62443-3-3 SR 1.6 Wireless access management | Partially satisfied | CTL-02;CTL-08 | 20 |
| GAP-006 | IEC 62443 | 62443-3-3 SR 5.1 Network segmentation | Partially satisfied | CTL-01 | 20 |
| GAP-007 | IEC 62443 | 62443-2-1 Security program requirements for IACS asset owners | Partially satisfied | CTL-03;CTL-17 | 20 |
| GAP-008 | NIST SP 800-82 | SP800-82 OT controls Applying security controls to OT | Partially satisfied | CTL-17 | 20 |
| GAP-009 | ISO 27001 | A.8.2 Privileged access rights | Partially satisfied | CTL-02;CTL-08 | 20 |
| GAP-010 | ISO 27001 | A.8.5 Secure authentication | Partially satisfied | CTL-02;CTL-07 | 20 |
| GAP-011 | ISO 27001 | A.8.22 Segregation of networks | Partially satisfied | CTL-01 | 20 |
| GAP-012 | ISO 27001 | A.8.24 Use of cryptography | Partially satisfied | CTL-14 | 20 |
| GAP-013 | NIST CSF | PR.AA Identity Management, Authentication, and Access Control | Partially satisfied | CTL-02;CTL-07 | 20 |
| GAP-014 | NIST CSF | PR.PS Platform Security | Partially satisfied | CTL-17 | 20 |
| GAP-015 | NIST CSF | PR.IR Technology Infrastructure Resilience | Partially satisfied | CTL-01 | 20 |

Requirements no control addresses are listed in `not_addressed.csv`. Most are physical, HR or development controls outside the 25 controls in the register; review them for the Statement of Applicability rather than treating them all as gaps.
