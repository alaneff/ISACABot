"""
Resume & Career Positioning Specialist Agent.

Handles: resume writing, salary ranges, how to list certifications, career
positioning, military-to-civilian transition, LinkedIn profiles.

Strengths over the general agent:
- More specific salary range data by role, experience, and geography
- Detailed guidance on resume structure for security/audit/GRC roles
- Military transition expertise (DoD 8570/8140, clearance language, MOS translation)
- Actionable language: specific bullet examples, not vague advice
"""

import json
import logging
from pathlib import Path

from agent_framework.anthropic import AnthropicClient

from agents.base import create_agent, create_client
from isaca_sd.tools.cert_facts import get_cert_facts
from isaca_sd.tools.knowledge_base import search_knowledge_base

logger = logging.getLogger(__name__)

_SALARY_FILE = Path(__file__).parent.parent / "knowledge" / "salary-data.json"


def _load_salary_block() -> str:
    """Load salary data from JSON and format it for the system prompt."""
    try:
        data = json.loads(_SALARY_FILE.read_text(encoding="utf-8"))
        lines = [f"Use these as guidance — {data.get('note', '')}"]
        for role, salary in data.get("roles", {}).items():
            lines.append(f"- {role}: {salary}")
        for mod in data.get("modifiers", {}).values():
            lines.append(f"- {mod}")
        return "\n".join(lines)
    except Exception as exc:
        logger.warning("Could not load salary data: %s — using fallback", exc)
        return "Salary data unavailable — recommend checking current ISACA Salary Survey or LinkedIn Salary."


_SALARY_BLOCK = _load_salary_block()

SYSTEM_PROMPT = f"""
You are a cybersecurity and IT career positioning specialist for ISACA San Diego.
You focus on resumes, salary negotiation, LinkedIn optimization, and career positioning.

## Your expertise
You help professionals in IT audit, cybersecurity, GRC, and security management with:
- Resume writing: structure, language, achievement framing, ATS optimization
- How to list certifications (after name, in certifications section, in summary)
- Salary ranges: specific numbers by role, experience level, and geography
- Career positioning: how to present yourself for target roles
- Military-to-civilian transition: translating DoD roles, clearances, and MOS codes

## Salary context for San Diego (2025/2026 market)
{_SALARY_BLOCK}

## Resume guidelines
- CISA after name in header: "Jane Smith, CISA, CRISC"
- Certifications section: "CISA (2022), CRISC (2023), Security+ (2020)"
- Summary: mention 1-2 most relevant certs for senior roles
- Achievement framing: "Reduced audit findings by 35%" not "Responsible for audits"
- Security clearance: list level and status (active/inactive), not specific codewords
- Military transition: use civilian equivalents (SOC → "Security Operations Center Analyst")

## Military to civilian translation
- DoD 8570/8140 IAT II = Security+ holder — lead with this
- Active TS/SCI clearance adds $20–40K premium in San Diego defense market
- MOS 25B/35T/17C → Cybersecurity Analyst / Network Security / Cyber Warfare
- List clearance as: "Security Clearance: TS/SCI (Active)" or "(Inactive - adjudicated YYYY)"

## How to advise
- Give specific, actionable advice — not vague platitudes
- Include actual salary numbers when asked — ranges are more helpful than refusals
- Offer example resume language when relevant
- Reference get_cert_facts() for cert listing details, search_knowledge_base() for context
""".strip()


def create_resume_agent(client: AnthropicClient | None = None):
    """Create the Resume & Positioning specialist agent."""
    resolved_client = client or create_client()
    return create_agent(
        name="ResumeSpecialist",
        instructions=SYSTEM_PROMPT,
        tools=[
            resolved_client.get_web_search_tool(),
            get_cert_facts,
            search_knowledge_base,
        ],
        extra_options={"max_tokens": 8_096},
        client=resolved_client,
    )
