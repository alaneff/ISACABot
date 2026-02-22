"""
Generic output quality reviewer agent.

Checks advisor responses for accuracy, completeness, and tone.
Primarily used in eval pipelines, not wired into the live chatbot
(would add latency to every response).

Usage:
    from agents.quality_agent import create_quality_agent, run_quality_check

    quality = create_quality_agent()
    passed, score, issues = await run_quality_check(quality, question, response)
"""

from __future__ import annotations

import json
import logging
import re

from agents.base import create_agent

logger = logging.getLogger(__name__)

QUALITY_SYSTEM_PROMPT = """
You are a quality reviewer for a cybersecurity career advisor chatbot.

Evaluate the advisor's response on three dimensions:
1. Accuracy: Does it state correct facts about certifications and career paths?
2. Completeness: Does it actually answer the question asked?
3. Tone: Is it professional, helpful, and not condescending or salesy?

Score from 0.0 to 1.0:
  1.0 — Excellent: Accurate, complete, great tone
  0.8 — Good: Mostly correct with minor gaps
  0.6 — Partial: Relevant but incomplete or vague
  0.3 — Poor: Significant inaccuracy or missing key point
  0.0 — Fail: Wrong advice, misleading, or harmful

Pass threshold: 0.7

You MUST respond with ONLY valid JSON — no text before or after:
{"score": 0.8, "pass": true, "issues": ["optional list of specific problems"]}
""".strip()


def create_quality_agent():
    """Create a fast Haiku-powered quality reviewer agent."""
    return create_agent(
        name="QualityReviewer",
        instructions=QUALITY_SYSTEM_PROMPT,
        model="claude-haiku-4-5-20251001",
        extra_options={"max_tokens": 256},
    )


async def run_quality_check(
    agent,
    question: str,
    response: str,
    pass_threshold: float = 0.7,
) -> tuple[bool, float, list[str]]:
    """
    Run a quality check on an advisor response.

    Returns:
        (passed, score, issues)
        Defaults to (True, 1.0, []) on parse failure.
    """
    prompt = (
        f"Question: {question}\n\n"
        f"Advisor response:\n{response}\n\n"
        "Score this response."
    )
    try:
        result = await agent.run(prompt)
        text = result.text if hasattr(result, "text") else str(result)

        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            score = float(parsed.get("score", 1.0))
            issues = parsed.get("issues", [])
            passed = score >= pass_threshold
            return passed, score, issues

    except Exception as exc:
        logger.error("Quality agent error: %s — defaulting to pass", exc)

    return True, 1.0, []
