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
