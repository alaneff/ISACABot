"""
ISACA SD query routing orchestrator.

A fast Haiku classifier that routes each user message to the most appropriate
specialist agent. This is a pure classifier — it does NOT generate the actual
response, just determines which specialist should handle the query.

Routes:
  resume      — resume writing, salary, how to list certs, career positioning
  career      — career path planning, progression timelines, what to do next
  research    — cert details, comparison, exam prep, study resources
  job_search  — current job postings, who's hiring, job market data
  general     — general cert advice or anything that doesn't clearly fit above
"""

from __future__ import annotations

import json
import logging
import re

from agents.base import create_agent

logger = logging.getLogger(__name__)

ROUTING_SYSTEM_PROMPT = """
You are a routing classifier for a cybersecurity career advisor chatbot.
Classify the user's question into exactly one category so it can be sent
to the best specialist agent.

Categories:
- "resume": Questions about resumes, LinkedIn profiles, salary negotiation,
  how to list certifications, career positioning, military-to-civilian transition,
  how to present experience, job application strategy.

- "career": Questions about career path planning, progression timelines, what
  certification to get next, how to move into a new role, how long it takes to
  advance, what experience is needed, CISO track, audit to security pivots.

- "research": Questions requiring deep cert knowledge — comparing specific certs,
  exam prep advice, study resources, pass rates, domain breakdowns, whether a
  cert is worth it, cert requirements and costs.

- "job_search": Questions about current job openings, who's hiring, what skills
  employers want, current salary surveys, job market trends, specific companies.

- "general": General cert advice, entry-level guidance, membership questions,
  or anything that doesn't clearly fit the above.

You MUST respond with ONLY valid JSON — no text before or after:
{"route": "resume", "confidence": 0.9}
""".strip()


def create_orchestrator():
    """Create a fast Haiku-powered routing classifier."""
    return create_agent(
        name="ISACAOrchestrator",
        instructions=ROUTING_SYSTEM_PROMPT,
        model="claude-haiku-4-5-20251001",
        extra_options={"max_tokens": 64},
    )


async def classify_route(agent, user_message: str, default: str = "general") -> str:
    """
    Classify the user message into a route string.

    Returns one of: "resume", "career", "research", "job_search", "general"
    Defaults to "general" on parse failure — never raises.
    """
    valid_routes = {"resume", "career", "research", "job_search", "general"}
    try:
        result = await agent.run(f"Classify: {user_message}")
        text = result.text if hasattr(result, "text") else str(result)

        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            route = parsed.get("route", default)
            if route in valid_routes:
                confidence = parsed.get("confidence", 0.0)
                logger.debug("Route: %s (confidence: %.2f)", route, confidence)
                return route

    except Exception as exc:
        logger.warning("Orchestrator classify_route error: %s — using '%s'", exc, default)

    return default
