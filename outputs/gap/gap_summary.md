# Requirement level gap analysis

Mapping used: `outputs/mapping/ai_mapping_ollama.csv`

| Framework | Requirements | Addressed | Satisfied | Partial | Gap | Not addressed | Coverage % | Compliance of addressed % |
|---|---|---|---|---|---|---|---|---|
| CIS Controls | 18 | 14 | 4 | 6 | 4 | 4 | 77.8 | 50.0 |
| COBIT | 13 | 2 | 0 | 0 | 2 | 11 | 15.4 | 0.0 |
| OT (IEC 62443 / SP 800-82) | 57 | 6 | 0 | 2 | 4 | 51 | 10.5 | 16.7 |
| ISO 27001 | 93 | 4 | 0 | 2 | 2 | 89 | 4.3 | 25.0 |
| NIST AI RMF | 19 | 0 | 0 | 0 | 0 | 19 | 0.0 | 0.0 |
| NIST CSF | 22 | 1 | 0 | 0 | 1 | 21 | 4.5 | 0.0 |
| PISF 2026 | 13 | 9 | 2 | 4 | 3 | 4 | 69.2 | 44.4 |

## Top 15 gaps by risk exposure (30 in total)

| Gap | Framework | Requirement | Status | Controls | Max inherent risk |
|---|---|---|---|---|---|
| GAP-001 | CIS Controls | CIS 17 Incident Response Management | Gap (control planned) | CTL-25 | 20 |
| GAP-002 | CIS Controls | CIS 1 Inventory and Control of Enterprise Assets | Partially satisfied | CTL-03;CTL-05 | 20 |
| GAP-003 | CIS Controls | CIS 7 Continuous Vulnerability Management | Partially satisfied | CTL-17 | 20 |
| GAP-004 | CIS Controls | CIS 8 Audit Log Management | Partially satisfied | CTL-04;CTL-24 | 20 |
| GAP-005 | CIS Controls | CIS 12 Network Infrastructure Management | Partially satisfied | CTL-01 | 20 |
| GAP-006 | CIS Controls | CIS 13 Network Monitoring and Defense | Partially satisfied | CTL-01 | 20 |
| GAP-007 | IEC 62443 | 62443-2-1 Security program requirements for IACS asset owners | Partially satisfied | CTL-03;CTL-17 | 20 |
| GAP-008 | NIST SP 800-82 | SP800-82 OT controls Applying security controls to OT | Partially satisfied | CTL-17 | 20 |
| GAP-009 | ISO 27001 | A.8.2 Privileged access rights | Partially satisfied | CTL-07 | 20 |
| GAP-010 | ISO 27001 | A.8.5 Secure authentication | Partially satisfied | CTL-07 | 20 |
| GAP-011 | PISF 2026 | PISF-AST Asset management | Partially satisfied | CTL-03;CTL-05 | 20 |
| GAP-012 | PISF 2026 | PISF-NET Network security and segmentation | Partially satisfied | CTL-01 | 20 |
| GAP-013 | PISF 2026 | PISF-OT OT and safety systems | Partially satisfied | CTL-01;CTL-04;CTL-05;CTL-17 | 20 |
| GAP-014 | PISF 2026 | PISF-LOG Logging, monitoring and detection | Partially satisfied | CTL-04;CTL-13;CTL-24 | 20 |
| GAP-015 | CIS Controls | CIS 4 Secure Configuration of Enterprise Assets and Software | Gap (control planned) | CTL-05;CTL-16 | 16 |

Requirements no control addresses are listed in `not_addressed.csv`. Most are physical, HR or development controls outside the 25 controls in the register; review them for the Statement of Applicability rather than treating them all as gaps.
