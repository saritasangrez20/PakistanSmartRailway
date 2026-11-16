"""Build the framework requirement catalogs in data/frameworks/.

Titles follow the published structure of each framework. Descriptions are short
summaries written for this project to help retrieval; they are not the official text.
The PISF 2026 catalog is a domain level placeholder (see the note in that file).

Run:  python scripts/build_catalogs.py
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "frameworks"
FIELDS = ["framework", "req_id", "title", "group", "description", "match_key"]


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} requirements")


# ISO/IEC 27001:2022 Annex A
ISO = [
 ("5.1","Policies for information security","Approved information security policy and topic specific policies"),
 ("5.2","Information security roles and responsibilities","Security roles defined and allocated"),
 ("5.3","Segregation of duties","Conflicting duties and responsibilities separated"),
 ("5.4","Management responsibilities","Management requires staff to apply security policy"),
 ("5.5","Contact with authorities","Contact maintained with relevant authorities such as law enforcement"),
 ("5.6","Contact with special interest groups","Contact with security forums and professional groups"),
 ("5.7","Threat intelligence","Collect and analyse threat intelligence"),
 ("5.8","Information security in project management","Security integrated into projects"),
 ("5.9","Inventory of information and other associated assets","Inventory of assets with owners"),
 ("5.10","Acceptable use of information and other associated assets","Rules for acceptable use of assets"),
 ("5.11","Return of assets","Assets returned on termination or change"),
 ("5.12","Classification of information","Information classified by confidentiality integrity availability needs"),
 ("5.13","Labelling of information","Labelling according to classification"),
 ("5.14","Information transfer","Rules for secure information transfer"),
 ("5.15","Access control","Rules for physical and logical access control based on business need such as role based access"),
 ("5.16","Identity management","Full lifecycle of identities managed"),
 ("5.17","Authentication information","Allocation and management of passwords and authentication secrets"),
 ("5.18","Access rights","Access rights provisioned reviewed modified and removed; periodic access review; joiner mover leaver"),
 ("5.19","Information security in supplier relationships","Manage security risks of suppliers and vendors"),
 ("5.20","Addressing information security within supplier agreements","Security requirements and clauses in supplier contracts"),
 ("5.21","Managing information security in the ICT supply chain","Manage risks in the ICT product and service supply chain"),
 ("5.22","Monitoring, review and change management of supplier services","Monitor and review supplier service delivery"),
 ("5.23","Information security for use of cloud services","Acquire use manage and exit cloud services securely"),
 ("5.24","Information security incident management planning and preparation","Incident management plan roles and procedures"),
 ("5.25","Assessment and decision on information security events","Assess events and decide whether they are incidents"),
 ("5.26","Response to information security incidents","Respond to incidents according to procedures"),
 ("5.27","Learning from information security incidents","Use incident knowledge to strengthen controls"),
 ("5.28","Collection of evidence","Collect and preserve evidence about incidents"),
 ("5.29","Information security during disruption","Maintain security during disruption"),
 ("5.30","ICT readiness for business continuity","ICT readiness planned implemented and tested to meet continuity objectives such as RTO; DR exercises"),
 ("5.31","Legal, statutory, regulatory and contractual requirements","Identify and meet legal and contractual requirements"),
 ("5.32","Intellectual property rights","Protect intellectual property rights"),
 ("5.33","Protection of records","Records protected from loss destruction and falsification"),
 ("5.34","Privacy and protection of PII","Protect personally identifiable information and privacy"),
 ("5.35","Independent review of information security","Independent review of the security approach"),
 ("5.36","Compliance with policies, rules and standards for information security","Regular review of compliance with security policies"),
 ("5.37","Documented operating procedures","Operating procedures documented and available"),
 ("6.1","Screening","Background verification of candidates"),
 ("6.2","Terms and conditions of employment","Employment contracts state security responsibilities"),
 ("6.3","Information security awareness, education and training","Security awareness training including phishing awareness"),
 ("6.4","Disciplinary process","Disciplinary process for policy violations"),
 ("6.5","Responsibilities after termination or change of employment","Security duties that remain after leaving"),
 ("6.6","Confidentiality or non-disclosure agreements","Confidentiality agreements in place"),
 ("6.7","Remote working","Security measures for remote working"),
 ("6.8","Information security event reporting","Staff report observed security events"),
 ("7.1","Physical security perimeters","Perimeters protect areas with information and assets"),
 ("7.2","Physical entry","Secure areas protected by entry controls"),
 ("7.3","Securing offices, rooms and facilities","Physical security for offices and facilities"),
 ("7.4","Physical security monitoring","Premises monitored for unauthorised physical access such as CCTV"),
 ("7.5","Protecting against physical and environmental threats","Protection from fire flood and other physical threats"),
 ("7.6","Working in secure areas","Measures for working in secure areas"),
 ("7.7","Clear desk and clear screen","Clear desk and clear screen rules"),
 ("7.8","Equipment siting and protection","Equipment sited securely and protected"),
 ("7.9","Security of assets off-premises","Protect assets outside the premises including field devices"),
 ("7.10","Storage media","Manage storage media through its lifecycle"),
 ("7.11","Supporting utilities","Protect from power failures and utility disruption"),
 ("7.12","Cabling security","Protect power and data cabling"),
 ("7.13","Equipment maintenance","Equipment maintained correctly"),
 ("7.14","Secure disposal or re-use of equipment","Data removed before disposal or reuse"),
 ("8.1","User endpoint devices","Protect information on user endpoint devices"),
 ("8.2","Privileged access rights","Restrict and manage privileged access rights; privileged access management and least privilege"),
 ("8.3","Information access restriction","Restrict access to information according to access policy"),
 ("8.4","Access to source code","Manage access to source code"),
 ("8.5","Secure authentication","Secure authentication technologies such as multi-factor authentication"),
 ("8.6","Capacity management","Monitor and adjust resource capacity"),
 ("8.7","Protection against malware","Protection against malware and ransomware"),
 ("8.8","Management of technical vulnerabilities","Identify vulnerabilities and apply patches"),
 ("8.9","Configuration management","Secure configurations and baselines established monitored and reviewed"),
 ("8.10","Information deletion","Delete information when no longer required"),
 ("8.11","Data masking","Mask data according to access policy"),
 ("8.12","Data leakage prevention","Prevent and detect data leakage and exfiltration"),
 ("8.13","Information backup","Backup copies maintained and tested"),
 ("8.14","Redundancy of information processing facilities","Redundant facilities to meet availability needs"),
 ("8.15","Logging","Logs of activities exceptions and events produced stored and protected"),
 ("8.16","Monitoring activities","Networks systems and applications monitored for anomalous behaviour"),
 ("8.17","Clock synchronization","Clocks synchronised to approved time sources"),
 ("8.18","Use of privileged utility programs","Restrict utilities that can override controls"),
 ("8.19","Installation of software on operational systems","Control software installation on operational systems"),
 ("8.20","Networks security","Networks and network devices secured managed and controlled"),
 ("8.21","Security of network services","Security of network services identified and monitored"),
 ("8.22","Segregation of networks","Groups of systems and services segregated into network zones"),
 ("8.23","Web filtering","Manage access to external websites"),
 ("8.24","Use of cryptography","Rules for cryptography and key management; encryption in transit and at rest"),
 ("8.25","Secure development life cycle","Rules for secure development of software"),
 ("8.26","Application security requirements","Security requirements for applications and APIs identified and approved"),
 ("8.27","Secure system architecture and engineering principles","Principles for engineering secure systems"),
 ("8.28","Secure coding","Secure coding principles applied"),
 ("8.29","Security testing in development and acceptance","Security testing such as penetration testing SAST and DAST before release"),
 ("8.30","Outsourced development","Direct and monitor outsourced development"),
 ("8.31","Separation of development, test and production environments","Separate development test and production"),
 ("8.32","Change management","Changes to systems subject to change management"),
 ("8.33","Test information","Protect information used for testing"),
 ("8.34","Protection of information systems during audit testing","Plan audit tests to minimise disruption"),
]
ISO_GROUP = {"5": "Organizational controls", "6": "People controls", "7": "Physical controls", "8": "Technological controls"}
write("iso27001_2022_annexA.csv", [dict(framework="ISO 27001", req_id=f"A.{i}", title=t, group=ISO_GROUP[i.split('.')[0]],
      description=d, match_key=f"A.{i}") for i, t, d in ISO])

CIS = [
 (1,"Inventory and Control of Enterprise Assets","Inventory and manage all enterprise assets including OT and IoT devices"),
 (2,"Inventory and Control of Software Assets","Inventory and manage software so only authorised software runs"),
 (3,"Data Protection","Processes and technical controls to identify classify handle retain and dispose of data; data access control lists"),
 (4,"Secure Configuration of Enterprise Assets and Software","Secure configuration baselines for devices software and cloud; change default credentials"),
 (5,"Account Management","Manage credentials for user administrator and service accounts; disable dormant accounts"),
 (6,"Access Control Management","Grant and revoke access; MFA for remote and administrative access; role based access"),
 (7,"Continuous Vulnerability Management","Assess and track vulnerabilities and remediate through patching"),
 (8,"Audit Log Management","Collect alert review and retain audit logs; centralised log management"),
 (9,"Email and Web Browser Protections","Protect against threats through email and web browsers; anti-phishing filtering"),
 (10,"Malware Defenses","Prevent or control malware and ransomware"),
 (11,"Data Recovery","Data recovery practices to restore assets to a trusted state; isolated backups and recovery testing"),
 (12,"Network Infrastructure Management","Manage network devices and architecture; network segmentation"),
 (13,"Network Monitoring and Defense","Monitor and defend networks; intrusion detection and traffic filtering between segments"),
 (14,"Security Awareness and Skills Training","Security awareness programme for the workforce"),
 (15,"Service Provider Management","Evaluate and manage service providers that hold sensitive data or access"),
 (16,"Application Software Security","Manage the security lifecycle of in house and acquired software and APIs; security testing"),
 (17,"Incident Response Management","Incident response capability: plans roles communications and exercises"),
 (18,"Penetration Testing","Test the effectiveness and resilience of assets by simulating attacks"),
]
write("cis_controls_v8.csv", [dict(framework="CIS Controls", req_id=f"CIS {n}", title=t, group="CIS Controls v8",
      description=d, match_key=f"CIS {n}") for n, t, d in CIS])

CSF = [
 ("GV.OC","GOVERN","Organizational Context","Mission stakeholders and legal requirements understood"),
 ("GV.RM","GOVERN","Risk Management Strategy","Risk appetite priorities and assumptions established"),
 ("GV.RR","GOVERN","Roles, Responsibilities, and Authorities","Cybersecurity roles and accountability established"),
 ("GV.PO","GOVERN","Policy","Cybersecurity policy established communicated and enforced"),
 ("GV.OV","GOVERN","Oversight","Results of risk management activities used to adjust strategy"),
 ("GV.SC","GOVERN","Cybersecurity Supply Chain Risk Management","Supplier and third party cyber risk managed; contract requirements"),
 ("ID.AM","IDENTIFY","Asset Management","Assets data hardware software and services identified and managed"),
 ("ID.RA","IDENTIFY","Risk Assessment","Cybersecurity risk to the organisation assets and individuals understood"),
 ("ID.IM","IDENTIFY","Improvement","Improvements identified from evaluations tests and exercises"),
 ("PR.AA","PROTECT","Identity Management, Authentication, and Access Control","Access limited to authorised users services and hardware; MFA and least privilege"),
 ("PR.AT","PROTECT","Awareness and Training","Personnel given awareness and training"),
 ("PR.DS","PROTECT","Data Security","Data managed to protect confidentiality integrity and availability; encryption and backups"),
 ("PR.PS","PROTECT","Platform Security","Hardware software and services managed securely; configuration management and patching"),
 ("PR.IR","PROTECT","Technology Infrastructure Resilience","Architecture managed for resilience; network segmentation"),
 ("DE.CM","DETECT","Continuous Monitoring","Assets monitored to find anomalies indicators of compromise and adverse events"),
 ("DE.AE","DETECT","Adverse Event Analysis","Anomalies and indicators analysed to characterise events"),
 ("RS.MA","RESPOND","Incident Management","Responses to detected incidents managed"),
 ("RS.AN","RESPOND","Incident Analysis","Investigations conducted to support response and recovery"),
 ("RS.CO","RESPOND","Incident Response Reporting and Communication","Response coordinated with stakeholders"),
 ("RS.MI","RESPOND","Incident Mitigation","Activities to prevent expansion of an incident"),
 ("RC.RP","RECOVER","Incident Recovery Plan Execution","Restoration activities performed to ensure availability; restore testing"),
 ("RC.CO","RECOVER","Incident Recovery Communication","Restoration activities coordinated with parties"),
]
write("nist_csf_2.csv", [dict(framework="NIST CSF", req_id=i, title=t, group=f, description=d, match_key=f"CSF {f}")
      for i, f, t, d in CSF])

IEC = [
 ("SR 1.1","FR 1 Identification and authentication control","Human user identification and authentication"),
 ("SR 1.2","FR 1 Identification and authentication control","Software process and device identification and authentication"),
 ("SR 1.3","FR 1 Identification and authentication control","Account management"),
 ("SR 1.4","FR 1 Identification and authentication control","Identifier management"),
 ("SR 1.5","FR 1 Identification and authentication control","Authenticator management"),
 ("SR 1.6","FR 1 Identification and authentication control","Wireless access management"),
 ("SR 1.7","FR 1 Identification and authentication control","Strength of password-based authentication"),
 ("SR 1.8","FR 1 Identification and authentication control","Public key infrastructure certificates"),
 ("SR 1.9","FR 1 Identification and authentication control","Strength of public key authentication"),
 ("SR 1.10","FR 1 Identification and authentication control","Authenticator feedback"),
 ("SR 1.11","FR 1 Identification and authentication control","Unsuccessful login attempts"),
 ("SR 1.12","FR 1 Identification and authentication control","System use notification"),
 ("SR 1.13","FR 1 Identification and authentication control","Access via untrusted networks"),
 ("SR 2.1","FR 2 Use control","Authorization enforcement"),
 ("SR 2.2","FR 2 Use control","Wireless use control"),
 ("SR 2.3","FR 2 Use control","Use control for portable and mobile devices"),
 ("SR 2.4","FR 2 Use control","Mobile code"),
 ("SR 2.5","FR 2 Use control","Session lock"),
 ("SR 2.6","FR 2 Use control","Remote session termination"),
 ("SR 2.7","FR 2 Use control","Concurrent session control"),
 ("SR 2.8","FR 2 Use control","Auditable events"),
 ("SR 2.9","FR 2 Use control","Audit storage capacity"),
 ("SR 2.10","FR 2 Use control","Response to audit processing failures"),
 ("SR 2.11","FR 2 Use control","Timestamps"),
 ("SR 2.12","FR 2 Use control","Non-repudiation"),
 ("SR 3.1","FR 3 System integrity","Communication integrity"),
 ("SR 3.2","FR 3 System integrity","Malicious code protection"),
 ("SR 3.3","FR 3 System integrity","Security functionality verification"),
 ("SR 3.4","FR 3 System integrity","Software and information integrity"),
 ("SR 3.5","FR 3 System integrity","Input validation"),
 ("SR 3.6","FR 3 System integrity","Deterministic output"),
 ("SR 3.7","FR 3 System integrity","Error handling"),
 ("SR 3.8","FR 3 System integrity","Session integrity"),
 ("SR 3.9","FR 3 System integrity","Protection of audit information"),
 ("SR 4.1","FR 4 Data confidentiality","Information confidentiality"),
 ("SR 4.2","FR 4 Data confidentiality","Information persistence"),
 ("SR 4.3","FR 4 Data confidentiality","Use of cryptography"),
 ("SR 5.1","FR 5 Restricted data flow","Network segmentation"),
 ("SR 5.2","FR 5 Restricted data flow","Zone boundary protection"),
 ("SR 5.3","FR 5 Restricted data flow","General purpose person-to-person communication restrictions"),
 ("SR 5.4","FR 5 Restricted data flow","Application partitioning"),
 ("SR 6.1","FR 6 Timely response to events","Audit log accessibility"),
 ("SR 6.2","FR 6 Timely response to events","Continuous monitoring"),
 ("SR 7.1","FR 7 Resource availability","Denial of service protection"),
 ("SR 7.2","FR 7 Resource availability","Resource management"),
 ("SR 7.3","FR 7 Resource availability","Control system backup"),
 ("SR 7.4","FR 7 Resource availability","Control system recovery and reconstitution"),
 ("SR 7.5","FR 7 Resource availability","Emergency power"),
 ("SR 7.6","FR 7 Resource availability","Network and security configuration settings"),
 ("SR 7.7","FR 7 Resource availability","Least functionality"),
 ("SR 7.8","FR 7 Resource availability","Control system component inventory"),
]
iec_rows = [dict(framework="IEC 62443", req_id=f"62443-3-3 {i}", title=t, group=g,
                 description=f"OT and industrial control system requirement: {t.lower()}", match_key=f"62443-3-3 {i}")
            for i, g, t in IEC]
iec_rows += [
 dict(framework="IEC 62443", req_id="62443-2-1", title="Security program requirements for IACS asset owners",
      group="Policies and procedures", description="Asset owner cyber security management system for OT: inventory, risk, policies, patching and exceptions",
      match_key="62443-2-1"),
 dict(framework="IEC 62443", req_id="62443-2-4", title="Security program requirements for IACS service providers",
      group="Policies and procedures", description="Requirements for integration and maintenance service providers including vendor remote access",
      match_key="62443-2-4"),
]
SP82 = [
 ("SP800-82 OT program","Establishing an OT cybersecurity program","OT security programme governance roles and policies"),
 ("SP800-82 OT risk","Risk management for OT systems","OT specific risk assessment including safety and availability impacts"),
 ("SP800-82 OT architecture","OT cybersecurity architecture","Defense in depth, network segmentation and zones between IT and OT, boundary protection"),
 ("SP800-82 OT controls","Applying security controls to OT","Access control, patching of legacy systems, monitoring and incident response adapted to OT"),
]
iec_rows += [dict(framework="NIST SP 800-82", req_id=i, title=t, group="NIST SP 800-82 Rev 3", description=d,
                  match_key="SP800-82") for i, t, d in SP82]
write("iec62443_sp800_82.csv", iec_rows)

AIRMF = [
 ("GOVERN 1","GOVERN","Policies, processes, procedures and practices for mapping, measuring and managing AI risk are in place and implemented"),
 ("GOVERN 2","GOVERN","Accountability structures so the right teams are responsible for AI risk"),
 ("GOVERN 3","GOVERN","Workforce diversity, equity, inclusion and accessibility in AI risk decisions"),
 ("GOVERN 4","GOVERN","Organisational culture that considers and communicates AI risk"),
 ("GOVERN 5","GOVERN","Engagement with relevant AI actors and affected stakeholders"),
 ("GOVERN 6","GOVERN","Policies for third party AI software, data and supply chain risk"),
 ("MAP 1","MAP","Context of the AI system established and understood"),
 ("MAP 2","MAP","Categorisation of the AI system"),
 ("MAP 3","MAP","AI capabilities, targeted usage, goals and expected benefits and costs understood"),
 ("MAP 4","MAP","Risks and benefits mapped for all components including third party data and software"),
 ("MAP 5","MAP","Impacts to individuals, groups, organisations and society characterised"),
 ("MEASURE 1","MEASURE","Appropriate methods and metrics identified and applied"),
 ("MEASURE 2","MEASURE","AI systems evaluated for trustworthy characteristics including validity, safety and security"),
 ("MEASURE 3","MEASURE","Mechanisms for tracking identified AI risks over time such as drift"),
 ("MEASURE 4","MEASURE","Feedback about the efficacy of measurement gathered and assessed"),
 ("MANAGE 1","MANAGE","AI risks prioritised, responded to and managed based on assessments"),
 ("MANAGE 2","MANAGE","Strategies to maximise benefits and minimise negative impacts, including human oversight"),
 ("MANAGE 3","MANAGE","AI risks and benefits from third party entities managed"),
 ("MANAGE 4","MANAGE","Risk treatments including response, recovery and monitoring documented and reviewed"),
]
write("nist_ai_rmf.csv", [dict(framework="NIST AI RMF", req_id=i, title=d, group=f, description=f"AI risk management, {f.lower()} function",
      match_key=f"AI RMF {f}") for i, f, d in AIRMF])

COBIT = [
 ("EDM03","Ensured Risk Optimization","Board level direction and monitoring of IT risk"),
 ("APO01","Managed I&T Management Framework","Governance structures roles and policies for IT"),
 ("APO10","Managed Vendors","Manage IT vendors and supplier contracts and performance"),
 ("APO12","Managed Risk","Identify assess and reduce IT related risk"),
 ("APO13","Managed Security","Information security management system"),
 ("BAI09","Managed Assets","Manage IT assets through their lifecycle"),
 ("BAI10","Managed Configuration","Maintain configuration baselines"),
 ("DSS04","Managed Continuity","Business continuity and disaster recovery plans and testing"),
 ("DSS05","Managed Security Services","Protect enterprise information: identity and logical access, user accounts, endpoints, network security and monitoring"),
 ("DSS06","Managed Business Process Controls","Business process controls including roles and segregation of duties"),
 ("MEA01","Managed Performance and Conformance Monitoring","Monitor performance and conformance of IT"),
 ("MEA02","Managed System of Internal Control","Monitor and evaluate internal controls and audit"),
 ("MEA03","Managed Compliance With External Requirements","Ensure compliance with laws regulations and contracts"),
]
write("cobit_2019.csv", [dict(framework="COBIT", req_id=i, title=t, group="COBIT 2019", description=d, match_key=f"COBIT {i}")
      for i, t, d in COBIT])

PISF = [
 ("PISF-GOV","Governance and policy","Information security governance, policies and roles"),
 ("PISF-AST","Asset management","Inventory and ownership of information, IT, OT and IoT assets"),
 ("PISF-RSK","Risk management","Risk assessment and treatment"),
 ("PISF-IAM","Identity and access management","Identity, authentication including multi-factor authentication, privileged access and access reviews"),
 ("PISF-NET","Network security and segmentation","Network protection and segmentation of critical systems"),
 ("PISF-OT","OT and safety systems","Protection of operational technology and critical infrastructure control systems"),
 ("PISF-APP","Application and API security","Secure development and testing of applications and APIs"),
 ("PISF-DAT","Data protection and privacy","Data classification, encryption and protection of personal data"),
 ("PISF-CLD","Cloud security","Secure use and configuration of cloud services"),
 ("PISF-LOG","Logging, monitoring and detection","Security logging, monitoring and incident detection"),
 ("PISF-BDR","Backup and disaster recovery","Backups, business continuity and disaster recovery"),
 ("PISF-TPR","Third-party and supply chain","Security requirements and oversight for vendors and suppliers"),
 ("PISF-AI","AI governance","Governance of artificial intelligence systems"),
]
write("pisf_2026.csv", [dict(framework="PISF 2026", req_id=i, title=t, group="PISF 2026 (domain level placeholder)",
      description=d, match_key=i) for i, t, d in PISF])
