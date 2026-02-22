"""
Verified certification facts database.

Provides get_cert_facts() — a @tool function that returns accurate, structured
data for 15 certifications. Data reflects 2025/2026 requirements and fees.

Update this file when ISACA, ISC2, or CompTIA change fees or requirements.
"""

from __future__ import annotations

import logging
from typing import Annotated

from agent_framework import tool

logger = logging.getLogger(__name__)

# ── Certification database ────────────────────────────────────────────────────
# Each entry is keyed by the common abbreviation used in the industry.
# All fees in USD. CPE = Continuing Professional Education hours.

CERT_DB: dict[str, dict] = {

    # ── ISACA ─────────────────────────────────────────────────────────────────

    "CISA": {
        "full_name": "Certified Information Systems Auditor",
        "issuer": "ISACA",
        "website": "https://www.isaca.org/credentialing/cisa",
        "category": "IT Audit",
        "experience_required": (
            "5 years of professional IS audit, control, assurance, or security "
            "work experience. Up to 3 years can be substituted: 1 year waived per "
            "year of higher education beyond a 2-year degree (max 3-year waiver). "
            "Note: you may sit the exam before meeting the experience requirement — "
            "you have 5 years from the exam pass date to apply for certification."
        ),
        "exam_questions": 150,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 240,
        "passing_score": "450 on a scale of 200–800",
        "exam_fee_usd": {"isaca_member": 575, "non_member": 760},
        "annual_maintenance_fee_usd": 45,
        "cpe_required": "120 CPE hours every 3 years; minimum 20 CPE per year",
        "domains": [
            "Information System Auditing Process (18%)",
            "Governance and Management of IT (18%)",
            "Information Systems Acquisition, Development, and Implementation (12%)",
            "Information Systems Operations and Business Resilience (26%)",
            "Protection of Information Assets (26%)",
        ],
        "job_roles": ["IT Auditor", "Internal Auditor", "Audit Manager", "Compliance Manager", "Risk Analyst"],
        "ideal_for": (
            "Professionals in IT audit, internal audit, or compliance who audit "
            "information systems and IT controls. Recognized by Big 4 accounting "
            "firms, regulators, and enterprises globally."
        ),
        "notes": (
            "Gold standard for IT audit roles. If you work in IT audit and want one "
            "cert, get CISA. Strong complement with CRISC for risk-focused roles."
        ),
    },

    "CISM": {
        "full_name": "Certified Information Security Manager",
        "issuer": "ISACA",
        "website": "https://www.isaca.org/credentialing/cism",
        "category": "Security Management",
        "experience_required": (
            "5 years of information security work experience, with at least 3 years "
            "in information security management in at least 3 CISM domains. "
            "Substitutions available for education and other certifications."
        ),
        "exam_questions": 150,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 240,
        "passing_score": "450 on a scale of 200–800",
        "exam_fee_usd": {"isaca_member": 575, "non_member": 760},
        "annual_maintenance_fee_usd": 45,
        "cpe_required": "120 CPE hours every 3 years; minimum 20 CPE per year",
        "domains": [
            "Information Security Governance (17%)",
            "Information Security Risk Management (20%)",
            "Information Security Program (33%)",
            "Incident Management (30%)",
        ],
        "job_roles": ["Security Manager", "CISO", "GRC Manager", "Security Director", "IT Risk Manager"],
        "ideal_for": (
            "Security managers and those moving into security management or CISO track. "
            "Strong for GRC and governance-focused positions. Management-focused rather "
            "than hands-on technical."
        ),
        "notes": (
            "CISM is management-focused; CISSP is broader and more technically recognized. "
            "For a CISO track, holding both CISM and CISSP is a powerful combination. "
            "Choose CISSP over CISM if your role requires technical credibility."
        ),
    },

    "CRISC": {
        "full_name": "Certified in Risk and Information Systems Control",
        "issuer": "ISACA",
        "website": "https://www.isaca.org/credentialing/crisc",
        "category": "Risk Management",
        "experience_required": (
            "3 years of cumulative work experience in IT risk management and IS "
            "control, across at least 2 of 4 CRISC domains. Lower bar than CISA/CISM."
        ),
        "exam_questions": 150,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 240,
        "passing_score": "450 on a scale of 200–800",
        "exam_fee_usd": {"isaca_member": 575, "non_member": 760},
        "annual_maintenance_fee_usd": 45,
        "cpe_required": "120 CPE hours every 3 years; minimum 20 CPE per year",
        "domains": [
            "Governance (26%)",
            "IT Risk Assessment (20%)",
            "Risk Response and Reporting (32%)",
            "Information Technology and Security (22%)",
        ],
        "job_roles": ["Risk Manager", "Risk Analyst", "GRC Analyst", "Compliance Manager", "IT Risk Consultant"],
        "ideal_for": (
            "Professionals focused on enterprise IT risk management, risk assessment, "
            "and control implementation. Often held alongside CISA by IT auditors who "
            "want to add formal risk credentials."
        ),
        "notes": (
            "CRISC requires only 3 years of experience — lower bar than CISA (5 years). "
            "Strong complement to CISA. Aligns well with COBIT and NIST frameworks."
        ),
    },

    "CGEIT": {
        "full_name": "Certified in Governance of Enterprise IT",
        "issuer": "ISACA",
        "website": "https://www.isaca.org/credentialing/cgeit",
        "category": "IT Governance",
        "experience_required": (
            "5 years of experience in IT governance, with at least 1 year in a "
            "management, advisory, or governance leadership role."
        ),
        "exam_questions": 150,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 240,
        "passing_score": "450 on a scale of 200–800",
        "exam_fee_usd": {"isaca_member": 575, "non_member": 760},
        "annual_maintenance_fee_usd": 45,
        "cpe_required": "120 CPE hours every 3 years; minimum 20 CPE per year",
        "domains": [
            "Governance of Enterprise IT (40%)",
            "IT Resources (15%)",
            "Benefits Realization (26%)",
            "Risk Optimization (19%)",
        ],
        "job_roles": ["CIO", "IT Director", "Governance Manager", "Enterprise Architect", "Board IT Advisor"],
        "ideal_for": (
            "Senior IT leaders and executives responsible for aligning IT strategy "
            "with business goals. Appropriate for CIOs, VPs of IT, and governance directors."
        ),
        "notes": (
            "Least common ISACA cert. Primarily held by CIOs, VPs, and senior IT governance "
            "roles. Not suitable for early or mid-career professionals — requires executive-level "
            "governance experience."
        ),
    },

    "CSX-P": {
        "full_name": "Cybersecurity Practitioner Certification",
        "issuer": "ISACA",
        "website": "https://www.isaca.org/credentialing/csx-p",
        "category": "Hands-on Cybersecurity",
        "experience_required": (
            "No formal minimum stated; performance-based exam tests practical skills. "
            "Hands-on security experience strongly recommended."
        ),
        "exam_format": "Performance-based lab exam (hands-on tasks, not multiple choice)",
        "exam_duration_minutes": 240,
        "passing_score": "Performance-based pass/fail based on task completion and scoring",
        "exam_fee_usd": {"isaca_member": 499, "non_member": 599},
        "cpe_required": "120 CPE hours every 3 years; minimum 20 CPE per year",
        "domains": [
            "Cybersecurity Operations",
            "Cybersecurity Architecture",
            "Cybersecurity Management",
        ],
        "job_roles": ["Security Analyst", "Security Engineer", "SOC Analyst", "Incident Responder"],
        "ideal_for": (
            "Technical cybersecurity practitioners who want a hands-on, performance-based "
            "cert from ISACA. Unlike other ISACA certs, CSX-P proves practical skills."
        ),
        "notes": (
            "ISACA's answer to performance-based certs like OSCP. Less well-known than CISSP "
            "or OSCP but growing in recognition. Good for practitioners who want ISACA credentials "
            "without multiple-choice-only format."
        ),
    },

    "CDPSE": {
        "full_name": "Certified Data Privacy Solutions Engineer",
        "issuer": "ISACA",
        "website": "https://www.isaca.org/credentialing/cdpse",
        "category": "Data Privacy",
        "experience_required": (
            "3 years of work experience related to privacy governance, privacy architecture, "
            "or data lifecycle management across at least 2 of 3 CDPSE domains."
        ),
        "exam_questions": 120,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 210,
        "passing_score": "450 on a scale of 200–800",
        "exam_fee_usd": {"isaca_member": 575, "non_member": 760},
        "annual_maintenance_fee_usd": 45,
        "cpe_required": "120 CPE hours every 3 years; minimum 20 CPE per year",
        "domains": [
            "Privacy Governance (34%)",
            "Privacy Architecture (36%)",
            "Data Lifecycle (30%)",
        ],
        "job_roles": ["Privacy Engineer", "Data Privacy Manager", "Privacy Architect", "DPO Technical Lead"],
        "ideal_for": (
            "Engineers and architects who design and implement privacy-by-design solutions. "
            "Distinct from pure policy roles — focuses on technical implementation of privacy controls."
        ),
        "notes": (
            "Launched in 2020. Growing relevance with GDPR, CCPA/CPRA, and expanding global "
            "privacy regulations. Particularly relevant in San Diego's biotech and healthcare sectors."
        ),
    },

    # ── ISC2 ──────────────────────────────────────────────────────────────────

    "CISSP": {
        "full_name": "Certified Information Systems Security Professional",
        "issuer": "ISC2",
        "website": "https://www.isc2.org/certifications/cissp",
        "category": "Security Management",
        "experience_required": (
            "5 years of cumulative, paid work experience in at least 2 of 8 CISSP domains. "
            "1 year waived with a 4-year college degree or an approved credential from ISC2's "
            "endorsed list. Those who pass without meeting experience can become an Associate "
            "of ISC2 and have 6 years to earn the experience."
        ),
        "exam_questions": "100–150 (Computerized Adaptive Testing — CAT format)",
        "exam_format": "CAT adaptive exam, computer-based. Linear format for non-English testing.",
        "exam_duration_minutes": 180,
        "passing_score": "700 out of 1000 (scaled score)",
        "exam_fee_usd": {"standard": 749},
        "annual_maintenance_fee_usd": 125,
        "cpe_required": "120 CPE hours every 3 years; minimum 40 CPE per year",
        "domains": [
            "Security and Risk Management (16%)",
            "Asset Security (10%)",
            "Security Architecture and Engineering (13%)",
            "Communication and Network Security (13%)",
            "Identity and Access Management (13%)",
            "Security Assessment and Testing (12%)",
            "Security Operations (13%)",
            "Software Development Security (10%)",
        ],
        "job_roles": ["CISO", "Security Manager", "Security Architect", "Security Consultant", "IT Director"],
        "ideal_for": (
            "Experienced security professionals seeking the most widely recognized senior "
            "security credential globally. Preferred by enterprises, government contractors, "
            "and consulting firms."
        ),
        "notes": (
            "Most widely recognized senior security cert globally. Often described as '10 miles "
            "wide, 1 inch deep' — covers all security domains broadly. Annual maintenance fee "
            "($125) is higher than ISACA certs. CISM is narrower and more governance-focused; "
            "CISSP is broader and more globally portable."
        ),
    },

    "SSCP": {
        "full_name": "Systems Security Certified Practitioner",
        "issuer": "ISC2",
        "website": "https://www.isc2.org/certifications/sscp",
        "category": "Security Practitioner",
        "experience_required": (
            "1 year of cumulative paid work experience in at least 1 of 7 SSCP domains. "
            "Much lower bar than CISSP."
        ),
        "exam_questions": 125,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 180,
        "passing_score": "700 out of 1000",
        "exam_fee_usd": {"standard": 249},
        "annual_maintenance_fee_usd": 125,
        "cpe_required": "60 CPE hours every 3 years",
        "domains": [
            "Security Operations and Administration",
            "Access Controls",
            "Risk Identification, Monitoring, and Analysis",
            "Incident Response and Recovery",
            "Cryptography",
            "Network and Communications Security",
            "Systems and Application Security",
        ],
        "job_roles": ["Security Analyst", "Network Security Engineer", "Systems Administrator", "SOC Analyst"],
        "ideal_for": (
            "Hands-on practitioners with 1+ year of experience who want ISC2 credentials "
            "without the CISSP experience bar. Good for those working toward CISSP."
        ),
        "notes": (
            "Often overlooked but a solid mid-tier cert. Only $249 exam fee. "
            "Good stepping stone toward CISSP. Less well-known than Security+ at the same level."
        ),
    },

    # ── CompTIA ───────────────────────────────────────────────────────────────

    "Security+": {
        "full_name": "CompTIA Security+",
        "issuer": "CompTIA",
        "website": "https://www.comptia.org/certifications/security",
        "category": "Entry-Level Security",
        "experience_required": (
            "No formal prerequisite. CompTIA recommends Network+ and 2 years of IT "
            "experience with a security focus. Most people sit it with 0-2 years experience."
        ),
        "exam_questions": "Up to 90 (multiple choice and performance-based questions)",
        "exam_format": "Multiple choice and performance-based (PBQs), computer-based",
        "exam_duration_minutes": 90,
        "passing_score": "750 on a scale of 100–900",
        "exam_fee_usd": {"standard": 404},
        "renewal_period_years": 3,
        "cpe_required": "50 CEUs every 3 years (or retake the current exam version)",
        "domains": [
            "General Security Concepts (12%)",
            "Threats, Vulnerabilities, and Mitigations (22%)",
            "Security Architecture (18%)",
            "Security Operations (28%)",
            "Security Program Management and Oversight (20%)",
        ],
        "job_roles": ["Junior Security Analyst", "IT Security Specialist", "Network Administrator", "SOC Tier 1"],
        "ideal_for": (
            "Entry-level professionals entering cybersecurity. DoD 8570/8140 approved — "
            "required by many federal and defense employers as a baseline qualification."
        ),
        "notes": (
            "De facto entry-level security cert. The most widely recognized starting cert. "
            "Required by DoD contractors and federal agencies. Best first cert for most people "
            "entering security regardless of background."
        ),
    },

    "CySA+": {
        "full_name": "CompTIA Cybersecurity Analyst",
        "issuer": "CompTIA",
        "website": "https://www.comptia.org/certifications/cybersecurity-analyst",
        "category": "Security Analyst",
        "experience_required": (
            "No formal prerequisite. CompTIA recommends Security+ and 4 years of "
            "hands-on IT or security experience."
        ),
        "exam_questions": "Up to 85 (multiple choice and performance-based)",
        "exam_format": "Multiple choice and performance-based, computer-based",
        "exam_duration_minutes": 165,
        "passing_score": "750 on a scale of 100–900",
        "exam_fee_usd": {"standard": 404},
        "renewal_period_years": 3,
        "cpe_required": "60 CEUs every 3 years (or retake exam)",
        "domains": [
            "Security Operations (33%)",
            "Vulnerability Management (30%)",
            "Incident Response and Management (22%)",
            "Reporting and Communication (15%)",
        ],
        "job_roles": ["Security Analyst", "SOC Analyst Tier 2/3", "Vulnerability Analyst", "Threat Intel Analyst"],
        "ideal_for": (
            "Mid-level analysts advancing beyond Security+. Strong for SOC and blue team roles. "
            "Focuses on detection, analysis, and response — not just concepts."
        ),
        "notes": (
            "Good follow-on to Security+ for analysts. DoD 8570 approved. "
            "Complements SIEM and threat intelligence skills. Pairs well with a SIEM specialization."
        ),
    },

    # ── Offensive Security ────────────────────────────────────────────────────

    "CEH": {
        "full_name": "Certified Ethical Hacker",
        "issuer": "EC-Council",
        "website": "https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/",
        "category": "Ethical Hacking",
        "experience_required": (
            "2 years of information security experience recommended. Must either complete "
            "official EC-Council training or submit an exam eligibility application with proof "
            "of 2 years experience."
        ),
        "exam_questions": 125,
        "exam_format": "Multiple choice, computer-based",
        "exam_duration_minutes": 240,
        "passing_score": "Varies by exam version (approximately 70%)",
        "exam_fee_usd": {"exam_only": 550, "with_official_training": 1899},
        "renewal_period_years": 3,
        "cpe_required": "120 ECE credits every 3 years",
        "job_roles": ["Ethical Hacker", "Penetration Tester (entry)", "Vulnerability Assessor", "Security Consultant"],
        "ideal_for": (
            "Those seeking a recognized ethical hacking cert with a lower barrier than OSCP. "
            "Has value in government and compliance contexts where cert recognition matters."
        ),
        "notes": (
            "Mixed industry reputation — largely theoretical rather than hands-on. "
            "OSCP is strongly preferred by employers for real penetration testing roles. "
            "CEH is easier to obtain and has brand recognition, but practitioners generally "
            "consider it weaker than performance-based alternatives."
        ),
    },

    "OSCP": {
        "full_name": "Offensive Security Certified Professional",
        "issuer": "Offensive Security (OffSec)",
        "website": "https://www.offsec.com/courses/pen-200/",
        "category": "Penetration Testing",
        "experience_required": (
            "No formal prerequisite, but strong Linux fundamentals, basic networking, "
            "and scripting experience are essential. The PWK/PEN-200 course is included "
            "with the exam purchase and must be completed."
        ),
        "exam_format": (
            "24-hour hands-on lab exam — must compromise target machines and submit "
            "a professional penetration test report within 24 additional hours."
        ),
        "exam_fee_usd": {"pen200_course_and_exam": 1499},
        "renewal_period_years": "Does not expire",
        "job_roles": ["Penetration Tester", "Red Team Operator", "Offensive Security Consultant", "Bug Bounty Hunter"],
        "ideal_for": (
            "Those serious about offensive security / penetration testing. "
            "The 24-hour hands-on exam proves real-world exploitation skills."
        ),
        "notes": (
            "Widely considered the gold standard for penetration testing. Does not expire. "
            "Significantly harder than CEH — requires genuine technical ability, not memorization. "
            "If you want to be a pentester, OSCP is the cert to get."
        ),
    },

    # ── SANS / GIAC ───────────────────────────────────────────────────────────

    "GSEC": {
        "full_name": "GIAC Security Essentials",
        "issuer": "GIAC (SANS Institute)",
        "website": "https://www.giac.org/certifications/security-essentials-gsec/",
        "category": "Security Practitioner",
        "experience_required": (
            "No formal prerequisite. SANS SEC401 course strongly recommended but not required. "
            "Proctored open-book exam."
        ),
        "exam_questions": "106–180 questions",
        "exam_format": "Multiple choice, open-book (proctored), computer-based",
        "exam_duration_minutes": 300,
        "passing_score": "73%",
        "exam_fee_usd": {"exam_only": 959, "with_sans_sec401_training": 8000},
        "renewal_period_years": 4,
        "cpe_required": "36 CPE hours every 4 years (or retake exam)",
        "job_roles": ["Security Analyst", "Security Engineer", "Sysadmin (security focus)", "IT Security Generalist"],
        "ideal_for": (
            "Practitioners wanting a well-respected cert that validates broad hands-on "
            "security skills. Open-book format rewards practical knowledge over memorization."
        ),
        "notes": (
            "Highly respected, especially in enterprise and government contexts. "
            "SANS/GIAC certs carry strong credibility. The main barrier is cost — exam alone "
            "is ~$959, SANS training adds ~$7-8K. Check employer tuition assistance programs."
        ),
    },

    # ── Cloud Security ────────────────────────────────────────────────────────

    "AWS Security Specialty": {
        "full_name": "AWS Certified Security – Specialty",
        "issuer": "Amazon Web Services",
        "website": "https://aws.amazon.com/certification/certified-security-specialty/",
        "category": "Cloud Security",
        "experience_required": (
            "Recommended: 5+ years of IT security experience and 2+ years of hands-on "
            "AWS workload security experience."
        ),
        "exam_questions": 65,
        "exam_format": "Multiple choice and multiple response, computer-based",
        "exam_duration_minutes": 170,
        "passing_score": "750 out of 1000 (scaled score)",
        "exam_fee_usd": {"standard": 300},
        "renewal_period_years": 3,
        "domains": [
            "Threat Detection and Incident Response (14%)",
            "Security Logging and Monitoring (18%)",
            "Infrastructure Security (20%)",
            "Identity and Access Management (16%)",
            "Data Protection (18%)",
            "Management and Security Governance (14%)",
        ],
        "job_roles": ["Cloud Security Engineer", "AWS Security Architect", "DevSecOps Engineer", "Cloud Security Analyst"],
        "ideal_for": (
            "Security professionals working primarily in AWS environments. "
            "Essential for cloud security roles at AWS-heavy organizations."
        ),
        "notes": (
            "Most recognized cloud security cert for AWS environments. "
            "Pairs well with CISSP as a cloud specialization. "
            "Relatively affordable at $300 compared to other specialty certs."
        ),
    },

    "Azure Security Technologies": {
        "full_name": "Microsoft Certified: Azure Security Engineer Associate (AZ-500)",
        "issuer": "Microsoft",
        "website": "https://learn.microsoft.com/en-us/credentials/certifications/azure-security-engineer/",
        "category": "Cloud Security",
        "experience_required": (
            "Recommended: hands-on experience implementing Azure security controls and "
            "familiarity with Azure services. AZ-900 Azure Fundamentals is a good starting point."
        ),
        "exam_questions": "40–60 (varies by version)",
        "exam_format": "Multiple choice, case studies, drag-and-drop, computer-based",
        "exam_duration_minutes": 120,
        "passing_score": "700 on a scale of 1–1000",
        "exam_fee_usd": {"standard": 165},
        "renewal_period_years": 1,
        "cpe_required": "Annual free online renewal assessment (no CPE tracking required)",
        "domains": [
            "Manage Identity and Access (25–30%)",
            "Secure Networking (20–25%)",
            "Secure Compute, Storage, and Databases (20–25%)",
            "Manage Security Operations (25–30%)",
        ],
        "job_roles": ["Azure Security Engineer", "Cloud Security Analyst", "DevSecOps Engineer", "Security Architect"],
        "ideal_for": (
            "Security professionals working in Microsoft Azure environments. "
            "Very common requirement at defense contractors and government agencies using Azure."
        ),
        "notes": (
            "Very affordable at $165. Requires annual free renewal exam — shorter shelf life "
            "than other certs but renewal is just a short online assessment. "
            "Essential for Azure security roles. Microsoft Learn provides extensive free prep material."
        ),
    },

    # ── CompTIA (additional) ──────────────────────────────────────────────────

    "A+": {
        "full_name": "CompTIA A+",
        "issuer": "CompTIA",
        "website": "https://www.comptia.org/certifications/a",
        "category": "IT Fundamentals",
        "experience_required": (
            "No formal prerequisites. CompTIA recommends 9–12 months of hands-on lab experience. "
            "Must pass two exams: Core 1 (220-1101) and Core 2 (220-1102)."
        ),
        "exam_questions": "Up to 90 per exam (multiple choice, drag-and-drop, performance-based)",
        "exam_format": "Two separate exams (Core 1 and Core 2), computer-based",
        "exam_duration_minutes": 90,
        "passing_score": "675/900 for Core 1; 700/900 for Core 2",
        "exam_fee_usd": {"per_exam": 246, "both_exams_total": 492},
        "renewal_period_years": 3,
        "cpe_required": "20 CEUs every 3 years (or pass a higher CompTIA exam)",
        "domains": [
            "Core 1: Mobile Devices (15%), Networking (20%), Hardware (25%), Virtualization & Cloud (11%), Troubleshooting (29%)",
            "Core 2: Operating Systems (31%), Security (25%), Software Troubleshooting (22%), Operational Procedures (22%)",
        ],
        "job_roles": ["Help Desk Technician", "Desktop Support Specialist", "Field Service Technician", "IT Support Analyst"],
        "ideal_for": (
            "Individuals entering IT for the first time. The industry-standard entry-level IT credential. "
            "DoD 8570/8140 approved (IAT Level I when paired with a security cert)."
        ),
        "notes": (
            "Most widely recognized entry-level IT cert. Professor Messer's free videos are the best "
            "free study resource. Must pass both Core 1 and Core 2 to earn the certification. "
            "Strong foundation before pursuing Network+ or Security+."
        ),
    },

    "Network+": {
        "full_name": "CompTIA Network+",
        "issuer": "CompTIA",
        "website": "https://www.comptia.org/certifications/network",
        "category": "Networking",
        "experience_required": (
            "No formal prerequisites. CompTIA recommends CompTIA A+ and 9–12 months of networking experience. "
            "Single exam required (N10-009)."
        ),
        "exam_questions": "Up to 90 (multiple choice, drag-and-drop, performance-based)",
        "exam_format": "Single exam (N10-009), computer-based",
        "exam_duration_minutes": 90,
        "passing_score": "720/900",
        "exam_fee_usd": {"standard": 369},
        "renewal_period_years": 3,
        "cpe_required": "30 CEUs every 3 years (or pass a qualifying higher-level CompTIA exam)",
        "domains": [
            "Networking Concepts (23%)",
            "Network Implementation (19%)",
            "Network Operations (17%)",
            "Network Security (20%)",
            "Network Troubleshooting (21%)",
        ],
        "job_roles": ["Network Technician", "Network Administrator", "Systems Administrator", "NOC Analyst", "IT Infrastructure Support"],
        "ideal_for": (
            "IT professionals building on A+ to specialize in networking. DoD 8570/8140 approved. "
            "Natural step before CCNA or Security+."
        ),
        "notes": (
            "Professor Messer's free N10-009 video course is the top free resource. "
            "Vendor-neutral and broadly recognized. Strong stepping stone toward CCNA "
            "(Cisco-specific depth) or Security+ (security specialization)."
        ),
    },

    "PenTest+": {
        "full_name": "CompTIA PenTest+",
        "issuer": "CompTIA",
        "website": "https://www.comptia.org/certifications/pentest",
        "category": "Penetration Testing",
        "experience_required": (
            "No formal prerequisites. CompTIA recommends Network+, Security+, and 3–4 years of "
            "hands-on IT security experience. Single exam (PT0-003)."
        ),
        "exam_questions": "Up to 90 (multiple choice, drag-and-drop, performance-based)",
        "exam_format": "Multiple choice and performance-based, computer-based",
        "exam_duration_minutes": 165,
        "passing_score": "750/900",
        "exam_fee_usd": {"standard": 404},
        "renewal_period_years": 3,
        "cpe_required": "60 CEUs every 3 years (or pass a qualifying exam)",
        "domains": [
            "Engagement Management (18%)",
            "Reconnaissance and Enumeration (21%)",
            "Attacks and Exploits (37%)",
            "Post-Exploitation and Lateral Movement (13%)",
            "Reporting and Communication (11%)",
        ],
        "job_roles": ["Penetration Tester (junior/mid)", "Vulnerability Assessment Analyst", "Security Consultant (offensive)", "Red Team Support"],
        "ideal_for": (
            "Security professionals moving into offensive security. DoD 8570/8140 approved for CSSP roles. "
            "Good stepping stone between Security+ and OSCP."
        ),
        "notes": (
            "PenTest+ covers broader content than OSCP (engagement management, reporting, cloud) "
            "but is less prestigious in the offensive community. OSCP is preferred by practitioners "
            "for hands-on credibility; PenTest+ is better for DoD role compliance requirements."
        ),
    },

    "CASP+": {
        "full_name": "CompTIA Advanced Security Practitioner (CASP+)",
        "issuer": "CompTIA",
        "website": "https://www.comptia.org/certifications/casp",
        "category": "Advanced Security (Technical)",
        "experience_required": (
            "No formal prerequisites. CompTIA recommends 10+ years of IT experience including "
            "5 years of hands-on technical security experience. Single exam (CAS-004)."
        ),
        "exam_questions": "Up to 90 (scenario-driven, multiple choice and performance-based)",
        "exam_format": "Scenario-heavy multiple choice and performance-based, computer-based",
        "exam_duration_minutes": 165,
        "passing_score": "Pass/Fail (compensatory scoring — no numeric score published)",
        "exam_fee_usd": {"standard": 494},
        "renewal_period_years": None,
        "cpe_required": "Perpetual — does not expire; optional CE program participation",
        "domains": [
            "Security Architecture (29%)",
            "Security Operations (30%)",
            "Security Engineering and Cryptography (26%)",
            "Governance, Risk, and Compliance (15%)",
        ],
        "job_roles": ["Senior Security Engineer", "Security Architect", "Principal Security Analyst", "Senior Penetration Tester", "Security Researcher"],
        "ideal_for": (
            "Senior security practitioners who want to stay technical rather than move into management. "
            "DoD IAT Level III and IASAE credential. Does not expire."
        ),
        "notes": (
            "CASP+ is the technical peer to CISSP's management focus. For practitioners who want "
            "CISSP-level recognition without taking on managerial responsibilities, CASP+ is the better fit. "
            "Perpetual certification — no renewal required."
        ),
    },

    # ── Cisco ─────────────────────────────────────────────────────────────────

    "CCNA": {
        "full_name": "Cisco Certified Network Associate",
        "issuer": "Cisco",
        "website": "https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html",
        "category": "Networking",
        "experience_required": (
            "No formal prerequisites. Cisco recommends basic networking understanding. "
            "Single exam (200-301). Cisco-specific — focuses on Cisco IOS and technologies."
        ),
        "exam_questions": "Approximately 100–120 (multiple choice, drag-and-drop, fill-in-blank, simulation)",
        "exam_format": "Multiple choice and simulation questions, computer-based",
        "exam_duration_minutes": 120,
        "passing_score": "Approximately 825/1000 (Cisco does not publish exact passing score)",
        "exam_fee_usd": {"standard": 330},
        "renewal_period_years": 3,
        "cpe_required": "Renew via Cisco CE credits, passing a Professional-level exam, or retaking CCNA",
        "domains": [
            "Network Fundamentals (20%)",
            "Network Access (20%)",
            "IP Connectivity (25%)",
            "IP Services (10%)",
            "Security Fundamentals (15%)",
            "Automation and Programmability (10%)",
        ],
        "job_roles": ["Network Administrator", "Network Technician", "NOC Analyst", "Network Support Engineer", "Junior Network Engineer"],
        "ideal_for": (
            "IT professionals working with Cisco equipment or targeting network engineering careers. "
            "One of the most commonly required certs in networking job postings."
        ),
        "notes": (
            "Jeremy's IT Lab (free on YouTube) is the best free CCNA resource. "
            "Cisco Packet Tracer (free) is essential for hands-on practice. "
            "Boson ExSim-Max is the gold standard for practice exams. "
            "Strong stepping stone to CCNP (Enterprise, Security, or other tracks)."
        ),
    },

    # ── SANS / GIAC (additional) ──────────────────────────────────────────────

    "GCIH": {
        "full_name": "GIAC Certified Incident Handler",
        "issuer": "GIAC (SANS Institute)",
        "website": "https://www.giac.org/certifications/certified-incident-handler-gcih/",
        "category": "Incident Response",
        "experience_required": (
            "No formal prerequisites. GIAC recommends solid networking and OS fundamentals "
            "(Security+ equivalent). Significant security operations experience is strongly advised."
        ),
        "exam_questions": 106,
        "exam_format": "Open-book multiple choice (physical notes allowed, no electronic devices), proctored",
        "exam_duration_minutes": 240,
        "passing_score": "73%",
        "exam_fee_usd": {"exam_only": 959},
        "renewal_period_years": 4,
        "cpe_required": "36 CPE hours every 4 years (or retake exam)",
        "domains": [
            "Incident Handling and Investigation — full IR lifecycle",
            "Computer Crime Investigation and Ethics",
            "Attack Techniques — scanning, enumeration, exploitation, persistence",
            "Malicious Code — malware behavior and analysis basics",
            "Network Investigations — packet and log analysis",
            "Hacker Exploits — web attacks, password attacks, session hijacking",
        ],
        "job_roles": ["Incident Responder", "SOC Analyst (Tier 2/3)", "Threat Analyst", "Cyber Defense Analyst", "Digital Forensics Analyst"],
        "ideal_for": (
            "SOC professionals and incident responders who need to demonstrate both attacker knowledge "
            "and response methodology. DoD 8570/8140 approved for CSSP Incident Responder roles."
        ),
        "notes": (
            "SANS SEC504 is the primary aligned course. Open-book format — building a well-organized "
            "index of notes is the key to success. Exam alone ~$959; SANS training adds ~$7–8K total."
        ),
    },

    "GPEN": {
        "full_name": "GIAC Penetration Tester",
        "issuer": "GIAC (SANS Institute)",
        "website": "https://www.giac.org/certifications/penetration-tester-gpen/",
        "category": "Penetration Testing",
        "experience_required": (
            "No formal prerequisites. Solid networking background (CCNA/Network+ level) and "
            "familiarity with Linux, Windows, and basic scripting are strongly recommended."
        ),
        "exam_questions": "82–115 (varies by version)",
        "exam_format": "Open-book multiple choice (physical printed materials allowed), proctored",
        "exam_duration_minutes": 180,
        "passing_score": "74%",
        "exam_fee_usd": {"exam_only": 959},
        "renewal_period_years": 4,
        "cpe_required": "36 CPE hours every 4 years (or retake exam)",
        "domains": [
            "Penetration Testing Methodology and Planning",
            "Reconnaissance and OSINT",
            "Scanning and Enumeration — Nmap, vulnerability scanning",
            "Exploitation — Metasploit, manual techniques",
            "Password Attacks — cracking, spraying, pass-the-hash",
            "Windows Exploitation and Post-Exploitation",
            "Lateral Movement and Pivoting",
            "Web Application Attack Basics",
            "Reporting and Communications",
        ],
        "job_roles": ["Penetration Tester", "Ethical Hacker", "Vulnerability Assessment Analyst", "Red Team Operator", "Security Consultant (offensive)"],
        "ideal_for": (
            "Penetration testers who prefer a structured methodology credential. Highly respected "
            "in environments where GIAC credentials are recognized (government, defense contractors, enterprise)."
        ),
        "notes": (
            "SANS SEC560 is the primary aligned course. Open-book format — a meticulously organized "
            "index is the key differentiator. OSCP is more hands-on and broadly preferred in offensive "
            "security roles; GPEN is a respected stepping stone or complement. Exam alone ~$959."
        ),
    },

    "GWAPT": {
        "full_name": "GIAC Web Application Penetration Tester",
        "issuer": "GIAC (SANS Institute)",
        "website": "https://www.giac.org/certifications/web-application-penetration-tester-gwapt/",
        "category": "Web Application Security",
        "experience_required": (
            "No formal prerequisites. Experience with web technologies (HTTP, SQL, JavaScript), "
            "Linux, and Burp Suite is strongly recommended. GPEN-level knowledge is a good foundation."
        ),
        "exam_questions": "82–115 (varies by version)",
        "exam_format": "Open-book multiple choice (physical printed materials allowed), proctored",
        "exam_duration_minutes": 180,
        "passing_score": "71%",
        "exam_fee_usd": {"exam_only": 959},
        "renewal_period_years": 4,
        "cpe_required": "36 CPE hours every 4 years (or retake exam)",
        "domains": [
            "Web Application Fundamentals — HTTP, cookies, sessions, same-origin policy",
            "Reconnaissance and Application Mapping",
            "SQL Injection — error-based, blind, time-based",
            "Cross-Site Scripting (XSS) — reflected, stored, DOM-based",
            "Authentication Attacks — credential stuffing, session fixation, JWT attacks",
            "CSRF, IDOR, XXE, Business Logic Flaws, File Upload Vulnerabilities",
            "Burp Suite usage (extensive)",
        ],
        "job_roles": ["Web Application Penetration Tester", "Application Security Analyst", "Bug Bounty Hunter", "AppSec Engineer", "Security Consultant (web)"],
        "ideal_for": (
            "Penetration testers specializing in web application security. Excellent complement to GPEN "
            "for practitioners who handle both network and web application assessments."
        ),
        "notes": (
            "PortSwigger Web Security Academy (free at portswigger.net) is the best free prep resource. "
            "SANS SEC542 is the aligned course. Open-book — build a detailed index organized by attack type. "
            "Strong differentiator for web-focused pentesters alongside GPEN or OSCP."
        ),
    },

    # ── Microsoft (additional) ────────────────────────────────────────────────

    "SC-200": {
        "full_name": "Microsoft Security Operations Analyst Associate",
        "issuer": "Microsoft",
        "website": "https://learn.microsoft.com/en-us/credentials/certifications/security-operations-analyst/",
        "category": "Security Operations (Microsoft)",
        "experience_required": (
            "No formal prerequisites. Microsoft recommends 1+ year of hands-on experience "
            "with Microsoft security products. Familiarity with Azure fundamentals (AZ-900 level) is helpful."
        ),
        "exam_questions": "40–60 (multiple choice, case studies, drag-and-drop)",
        "exam_format": "Multiple choice, case studies, drag-and-drop, computer-based",
        "exam_duration_minutes": 120,
        "passing_score": "700/1000",
        "exam_fee_usd": {"standard": 165},
        "renewal_period_years": 1,
        "cpe_required": "Annual free renewal assessment via Microsoft Learn (no exam fee)",
        "domains": [
            "Mitigate threats using Microsoft Defender XDR (25–30%)",
            "Mitigate threats using Microsoft Defender for Cloud (20–25%)",
            "Mitigate threats using Microsoft Sentinel (50–55%) — KQL, SOAR, threat hunting, incident management",
        ],
        "job_roles": ["SOC Analyst (Microsoft stack)", "Security Operations Engineer", "Threat Hunter (Microsoft)", "Sentinel Engineer", "Cloud Security Analyst"],
        "ideal_for": (
            "SOC analysts and blue team members working in Microsoft security environments "
            "(Sentinel, Defender XDR). Prerequisite for SC-100 Cybersecurity Architect Expert."
        ),
        "notes": (
            "Very affordable at $165 with annual free renewal. KQL (Kusto Query Language) is critical — "
            "practice in Microsoft Sentinel before the exam. John Savill's free YouTube study cram is "
            "the best prep resource. Microsoft Learn provides free, aligned official learning paths."
        ),
    },

    "SC-100": {
        "full_name": "Microsoft Cybersecurity Architect Expert",
        "issuer": "Microsoft",
        "website": "https://learn.microsoft.com/en-us/credentials/certifications/cybersecurity-architect-expert/",
        "category": "Security Architecture (Microsoft)",
        "experience_required": (
            "Formal prerequisite: must hold SC-200, SC-300, or AZ-500 first. "
            "Microsoft recommends 5+ years of security engineering experience including 3 years with Azure."
        ),
        "exam_questions": "40–60 (case studies, scenario-based, multiple choice)",
        "exam_format": "Case studies and scenario-based questions, computer-based",
        "exam_duration_minutes": 120,
        "passing_score": "700/1000",
        "exam_fee_usd": {"standard": 165},
        "renewal_period_years": 1,
        "cpe_required": "Annual free renewal assessment via Microsoft Learn",
        "domains": [
            "Design solutions aligned with security best practices and Zero Trust (20–25%)",
            "Design security operations, identity, and compliance capabilities (25–30%)",
            "Design security solutions for infrastructure — hybrid, multi-cloud, Defender for Cloud (25–30%)",
            "Design security solutions for applications and data — DevSecOps, Microsoft Purview (20–25%)",
        ],
        "job_roles": ["Cybersecurity Architect", "Cloud Security Architect", "Principal Security Engineer", "Security Solutions Architect", "Microsoft Security Practice Lead"],
        "ideal_for": (
            "Senior security architects designing enterprise security across the Microsoft stack. "
            "Expert-level designation signals senior capability; used by Microsoft Partners for client engagements."
        ),
        "notes": (
            "Highest-level Microsoft security certification. Requires SC-200, SC-300, or AZ-500 as prerequisite. "
            "John Savill's free SC-100 study cram (YouTube) is the definitive prep resource. "
            "Microsoft Cybersecurity Reference Architectures (MCRA) whitepaper is essential reading. "
            "$165 exam fee + free annual renewal."
        ),
    },

    # ── TCM Security ──────────────────────────────────────────────────────────

    "PNPT": {
        "full_name": "Practical Network Penetration Tester",
        "issuer": "TCM Security",
        "website": "https://certifications.tcm-sec.com/pnpt/",
        "category": "Penetration Testing",
        "experience_required": (
            "No formal prerequisites. TCM Security strongly recommends completing their "
            "'Practical Ethical Hacking' course by Heath Adams before attempting."
        ),
        "exam_format": (
            "5-day hands-on penetration test of a realistic Active Directory lab environment, "
            "followed by 2 days to write and submit a professional pentest report. "
            "Includes a 15-minute live debrief with TCM Security staff after a passing report."
        ),
        "exam_fee_usd": {"course_and_exam": 399, "retake": 200},
        "renewal_period_years": "Does not expire (lifetime credential as of current policy)",
        "domains": [
            "External reconnaissance and OSINT",
            "External network scanning and enumeration",
            "Active Directory attacks — Kerberoasting, Pass-the-Hash, Pass-the-Ticket",
            "Lateral movement and privilege escalation (Windows and Linux)",
            "Domain compromise and post-exploitation",
            "Professional penetration test report writing",
        ],
        "job_roles": ["Junior Penetration Tester", "Ethical Hacker", "Vulnerability Assessment Analyst", "Entry-level Red Team Operator"],
        "ideal_for": (
            "Entry-to-mid level aspiring penetration testers who want hands-on certification. "
            "Best affordable alternative to OSCP — rigorous, practical, and growing in recognition."
        ),
        "notes": (
            "Only ~$399 vs OSCP's $1,499+ — best value practical pentest cert. Lifetime credential. "
            "Heath Adams' ('The Cyber Mentor') YouTube channel is free prep material. "
            "Excellent OSCP stepping stone — PNPT passers find OSCP significantly more approachable. "
            "Recognition growing, especially at SMBs, MSPs, and startups."
        ),
    },

    # ── IIA ───────────────────────────────────────────────────────────────────

    "CIA": {
        "full_name": "Certified Internal Auditor",
        "issuer": "The Institute of Internal Auditors (IIA)",
        "website": "https://www.theiia.org/en/certifications/cia/",
        "category": "Internal Audit",
        "experience_required": (
            "24 months (2 years) of professional internal auditing experience "
            "(or 12 months with a master's degree). Bachelor's degree required. Three exam parts must be passed."
        ),
        "exam_questions": "Part 1: 125 questions; Part 2: 100 questions; Part 3: 100 questions",
        "exam_format": "Three separate exams (computer-based, multiple choice)",
        "exam_duration_minutes": "Part 1: 150 min; Part 2: 120 min; Part 3: 120 min",
        "passing_score": "600/800 for each part",
        "exam_fee_usd": {"iia_member_per_part": 365, "non_member_per_part": 500},
        "renewal_period_years": 2,
        "cpe_required": "40 CPE credits every 2 years",
        "domains": [
            "Part 1 — Essentials of Internal Auditing: Foundations, Independence, Governance, Risk, Fraud",
            "Part 2 — Practice of Internal Auditing: Managing IA Activity, Planning, Performing, Communicating",
            "Part 3 — Business Knowledge: Business Acumen, Information Security, IT, Financial Management",
        ],
        "job_roles": ["Internal Auditor", "Senior Internal Auditor", "Internal Audit Manager", "Director of Internal Audit", "Chief Audit Executive (CAE)", "GRC Analyst"],
        "ideal_for": (
            "Internal auditors at any career stage. The only globally recognized certification specifically "
            "for internal auditors. Unlike CISA (IT-focused), CIA covers all audit disciplines — financial, "
            "operational, compliance, governance."
        ),
        "notes": (
            "Gold standard for internal audit roles globally. Frequently required for CAE positions. "
            "Pairs powerfully with CISA — CIA for audit methodology credibility, CISA for IT-specific knowledge. "
            "Gleim CIA Review is the most widely recommended self-study system. "
            "IIA SD chapter is active — check for local study groups and CPE events."
        ),
    },

    # ── IAPP Privacy ──────────────────────────────────────────────────────────

    "CIPP/E": {
        "full_name": "Certified Information Privacy Professional/Europe",
        "issuer": "IAPP (International Association of Privacy Professionals)",
        "website": "https://iapp.org/certify/cipp/europe/",
        "category": "Privacy / Data Protection",
        "experience_required": (
            "No formal prerequisites. IAPP recommends some professional experience with privacy "
            "or data protection concepts. Open to anyone."
        ),
        "exam_questions": 90,
        "exam_format": "Closed book, multiple choice, computer-based",
        "exam_duration_minutes": 150,
        "passing_score": "Approximately 300/400 (scaled scoring)",
        "exam_fee_usd": {"standard": 550},
        "renewal_period_years": 2,
        "cpe_required": "20 CPE (Continuing Privacy Education) credits every 2 years",
        "domains": [
            "Introduction to European Data Protection — history, regulatory framework",
            "GDPR — structure, scope, territorial applicability, lawful bases for processing",
            "Data Protection Concepts — personal data, special categories, controllers/processors",
            "Individual Rights — access, rectification, erasure, portability, objection",
            "Security of Processing — Article 32, technical/organizational measures",
            "Accountability and Governance — DPIA, DPO requirements, records of processing",
            "International Data Transfers — adequacy decisions, SCCs, BCRs",
            "Supervisory Authorities — enforcement, fines structure",
        ],
        "job_roles": ["Data Protection Officer (DPO)", "Privacy Manager", "GDPR Consultant", "Compliance Analyst", "Privacy Counsel", "Chief Privacy Officer (CPO)"],
        "ideal_for": (
            "Professionals responsible for GDPR compliance at organizations processing EU personal data. "
            "The baseline qualification for DPO roles across EU member states. "
            "Particularly relevant in San Diego's biotech, healthcare, and global tech sectors."
        ),
        "notes": (
            "Widely regarded as the baseline for DPO roles. Key GDPR numbers: 72-hour breach notification, "
            "fines up to 4% of global annual turnover or €20M (whichever is higher). "
            "IAPP membership (~$250/year) provides study materials. "
            "CIPP/E + CIPP/US is the top combination for global privacy professionals."
        ),
    },

    "CIPP/US": {
        "full_name": "Certified Information Privacy Professional/United States",
        "issuer": "IAPP (International Association of Privacy Professionals)",
        "website": "https://iapp.org/certify/cipp/unitedstates/",
        "category": "Privacy / Data Protection",
        "experience_required": (
            "No formal prerequisites. IAPP recommends professional experience in privacy, law, or "
            "a related field. Open to anyone."
        ),
        "exam_questions": 90,
        "exam_format": "Closed book, multiple choice, computer-based",
        "exam_duration_minutes": 150,
        "passing_score": "Approximately 300/400 (scaled scoring)",
        "exam_fee_usd": {"standard": 550},
        "renewal_period_years": 2,
        "cpe_required": "20 CPE credits every 2 years",
        "domains": [
            "Introduction to U.S. Privacy Law — constitutional foundations, FTC authority",
            "Healthcare Privacy — HIPAA Privacy Rule, Security Rule, HITECH",
            "Financial Privacy — GLBA, FCRA",
            "Education Privacy — FERPA",
            "Children's Privacy — COPPA",
            "State Privacy Laws — CCPA/CPRA and major state comprehensive privacy laws",
            "Online Privacy — behavioral advertising, tracking, CAN-SPAM",
            "Workplace Privacy — employee monitoring, background checks",
            "Enforcement — FTC Section 5, state AG enforcement, private rights of action",
        ],
        "job_roles": ["Privacy Counsel", "Privacy Manager", "Compliance Analyst", "HIPAA Privacy Officer", "Chief Privacy Officer (CPO)", "Privacy Consultant"],
        "ideal_for": (
            "Privacy professionals working with U.S. regulations — HIPAA, CCPA/CPRA, GLBA, FERPA, COPPA. "
            "Frequently required in healthcare, financial services, and tech companies with U.S. data subjects."
        ),
        "notes": (
            "U.S. privacy law is a complex patchwork of federal and state regulations — no single federal "
            "privacy law. State laws are evolving rapidly. "
            "CIPP/US + CIPP/E is the top combination for global privacy roles. "
            "CIPP/US + CIPM is IAPP's recommended combination for privacy program leaders in the U.S."
        ),
    },

    # ── ISO ───────────────────────────────────────────────────────────────────

    "ISO 27001 LA": {
        "full_name": "ISO/IEC 27001 Lead Auditor",
        "issuer": "PECB / BSI / other accredited certification bodies",
        "website": "https://pecb.com/en/education-and-certification-for-individuals/iso-iec-27001",
        "category": "ISMS / Security Governance",
        "experience_required": (
            "No formal cert prerequisites, but 5+ years of information security experience "
            "(2 years in audit) expected for full PECB certification. "
            "Completion of an accredited 5-day training course is typically required before the exam."
        ),
        "exam_format": "Essay-based / scenario-based (PECB: 3 hours, open book); some providers use multiple choice",
        "exam_duration_minutes": 180,
        "passing_score": "70% (PECB); varies by issuing body",
        "exam_fee_usd": {
            "training_course_5_day_approx": "2000–4000",
            "exam_only_pecb_approx": "500–700",
        },
        "renewal_period_years": 3,
        "cpe_required": "Annual maintenance fees + CPD evidence every 3 years (PECB); varies by body",
        "domains": [
            "ISO/IEC 27001 standard — structure, clauses, Annex A controls",
            "ISMS implementation lifecycle — planning, design, operation, monitoring",
            "Risk assessment and treatment (ISO/IEC 27005 concepts)",
            "ISO 19011 and ISO/IEC 27007 — audit management and ISMS audit guidance",
            "Audit planning, execution, reporting, and follow-up",
            "Nonconformity identification and corrective action",
        ],
        "job_roles": ["ISO 27001 Auditor", "Information Security Manager", "ISMS Program Manager", "ISO 27001 Consultant", "Compliance Manager (IS)", "GRC Manager"],
        "ideal_for": (
            "Professionals who plan and conduct third-party ISO 27001 audits. "
            "High value at consulting firms delivering ISO 27001 certification projects. "
            "Complements CISA and CISSP for audit and governance roles."
        ),
        "notes": (
            "Lead Auditor is for those who conduct audits; Lead Implementer is for those who build ISMS programs. "
            "Training + exam typically $2,000–$4,000 total. ISO standard itself costs ~$200 from ISO.org. "
            "ISO 27001:2022 revised Annex A — update materials if you have older 2013 resources."
        ),
    },
}

# ── Aliases ───────────────────────────────────────────────────────────────────
# Maps alternate names/abbreviations to canonical CERT_DB keys

CERT_ALIASES: dict[str, str] = {
    # ISACA
    "cisa": "CISA",
    "cism": "CISM",
    "crisc": "CRISC",
    "cgeit": "CGEIT",
    "csx-p": "CSX-P",
    "csxp": "CSX-P",
    "csx p": "CSX-P",
    "cdpse": "CDPSE",
    # ISC2
    "cissp": "CISSP",
    "sscp": "SSCP",
    # CompTIA
    "security+": "Security+",
    "sec+": "Security+",
    "security plus": "Security+",
    "comptia security": "Security+",
    "cysa+": "CySA+",
    "cysa": "CySA+",
    "cysa plus": "CySA+",
    "cybersecurity analyst": "CySA+",
    # Offensive
    "ceh": "CEH",
    "certified ethical hacker": "CEH",
    "oscp": "OSCP",
    "offensive security": "OSCP",
    # SANS
    "gsec": "GSEC",
    "giac security essentials": "GSEC",
    "giac gsec": "GSEC",
    # Cloud
    "aws security": "AWS Security Specialty",
    "aws security specialty": "AWS Security Specialty",
    "aws certified security": "AWS Security Specialty",
    "az-500": "Azure Security Technologies",
    "az500": "Azure Security Technologies",
    "azure security": "Azure Security Technologies",
    "azure security engineer": "Azure Security Technologies",
    "azure security technologies": "Azure Security Technologies",
    "microsoft azure security": "Azure Security Technologies",
    # CompTIA (additional)
    "a+": "A+",
    "comptia a+": "A+",
    "comptia a plus": "A+",
    "network+": "Network+",
    "net+": "Network+",
    "comptia network+": "Network+",
    "network plus": "Network+",
    "pentest+": "PenTest+",
    "pentest plus": "PenTest+",
    "comptia pentest": "PenTest+",
    "pt0-003": "PenTest+",
    "casp+": "CASP+",
    "casp plus": "CASP+",
    "cas-004": "CASP+",
    "comptia casp": "CASP+",
    "comptia advanced security": "CASP+",
    # Cisco
    "ccna": "CCNA",
    "cisco ccna": "CCNA",
    "200-301": "CCNA",
    "cisco certified network associate": "CCNA",
    # SANS / GIAC (additional)
    "gcih": "GCIH",
    "giac incident handler": "GCIH",
    "giac certified incident handler": "GCIH",
    "gpen": "GPEN",
    "giac penetration tester": "GPEN",
    "giac gpen": "GPEN",
    "gwapt": "GWAPT",
    "giac web application penetration tester": "GWAPT",
    "giac gwapt": "GWAPT",
    "web application penetration tester": "GWAPT",
    # Microsoft (additional)
    "sc-200": "SC-200",
    "sc200": "SC-200",
    "microsoft security operations": "SC-200",
    "microsoft sentinel": "SC-200",
    "sc-100": "SC-100",
    "sc100": "SC-100",
    "microsoft cybersecurity architect": "SC-100",
    "cybersecurity architect expert": "SC-100",
    # TCM Security
    "pnpt": "PNPT",
    "practical network penetration tester": "PNPT",
    "tcm security": "PNPT",
    # IIA
    "cia": "CIA",
    "certified internal auditor": "CIA",
    "internal auditor": "CIA",
    "iia cia": "CIA",
    # IAPP Privacy
    "cipp/e": "CIPP/E",
    "cippe": "CIPP/E",
    "cipp e": "CIPP/E",
    "gdpr certification": "CIPP/E",
    "cipp/us": "CIPP/US",
    "cippus": "CIPP/US",
    "cipp us": "CIPP/US",
    "us privacy certification": "CIPP/US",
    # ISO
    "iso 27001 la": "ISO 27001 LA",
    "iso 27001 lead auditor": "ISO 27001 LA",
    "iso27001 la": "ISO 27001 LA",
    "iso27001 lead auditor": "ISO 27001 LA",
    "iso 27001": "ISO 27001 LA",
    "pecb iso 27001": "ISO 27001 LA",
}


# ── Tool function ──────────────────────────────────────────────────────────────

@tool(approval_mode="never_require")
def get_cert_facts(
    cert_name: Annotated[str, "Cert name or abbreviation, e.g. CISA, CISSP, Security+, AZ-500, OSCP"]
) -> str:
    """
    Returns verified requirements, fees, experience, exam details, and job roles
    for a certification. Call this FIRST before advising on any specific cert
    to ensure accuracy. Covers: CISA, CISM, CRISC, CGEIT, CSX-P, CDPSE (ISACA);
    CISSP, SSCP (ISC2); Security+, CySA+ (CompTIA); CEH, OSCP; GSEC (SANS/GIAC);
    AWS Security Specialty; AZ-500 Azure Security Technologies (Microsoft).
    """
    normalized = cert_name.strip().lower()

    # 1. Check alias map
    canonical = CERT_ALIASES.get(normalized)

    # 2. Direct case-insensitive key match
    if not canonical:
        for key in CERT_DB:
            if key.lower() == normalized:
                canonical = key
                break

    # 3. Partial match (e.g. "azure" → "Azure Security Technologies")
    if not canonical:
        for key in CERT_DB:
            if normalized in key.lower():
                canonical = key
                break

    if not canonical or canonical not in CERT_DB:
        available = ", ".join(CERT_DB.keys())
        return (
            f"No cert data found for '{cert_name}'. "
            f"Try using the standard abbreviation. "
            f"Available certs: {available}"
        )

    data = CERT_DB[canonical]
    logger.debug("get_cert_facts: %r", canonical)

    lines = [f"## {canonical} — {data.get('full_name', '')}"]
    lines.append(f"**Issuer:** {data.get('issuer', 'N/A')}")
    lines.append(f"**Category:** {data.get('category', 'N/A')}")
    lines.append(f"**Website:** {data.get('website', 'N/A')}")

    if exp := data.get("experience_required"):
        lines.append(f"\n**Experience Required:** {exp}")

    if q := data.get("exam_questions"):
        lines.append(f"**Exam Questions:** {q}")

    if fmt := data.get("exam_format"):
        lines.append(f"**Exam Format:** {fmt}")

    if dur := data.get("exam_duration_minutes"):
        lines.append(f"**Exam Duration:** {dur} minutes")

    if score := data.get("passing_score"):
        lines.append(f"**Passing Score:** {score}")

    if fees := data.get("exam_fee_usd"):
        fee_str = "; ".join(f"{k.replace('_', ' ')}: ${v}" for k, v in fees.items())
        lines.append(f"**Exam Fee (USD):** {fee_str}")

    if maint := data.get("annual_maintenance_fee_usd"):
        lines.append(f"**Annual Maintenance Fee:** ${maint}")

    if cpe := data.get("cpe_required"):
        lines.append(f"**CPE/Renewal:** {cpe}")

    if rp := data.get("renewal_period_years"):
        lines.append(f"**Renewal Period:** {rp}")

    if domains := data.get("domains"):
        lines.append("\n**Exam Domains:**")
        for d in domains:
            lines.append(f"  - {d}")

    if roles := data.get("job_roles"):
        lines.append(f"\n**Common Job Roles:** {', '.join(roles)}")

    if ideal := data.get("ideal_for"):
        lines.append(f"\n**Ideal For:** {ideal}")

    if notes := data.get("notes"):
        lines.append(f"\n**Notes:** {notes}")

    return "\n".join(lines)
