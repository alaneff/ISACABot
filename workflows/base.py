"""
Workflow helpers — lightweight multi-agent orchestration patterns.

These sit BELOW the full Microsoft Agent Framework graph-based Workflows
(which you'd use for complex branching, checkpointing, and human-in-the-loop).
Use these helpers for simpler, linear pipelines where you just need to
chain or fan-out a few agents without the overhead of a full workflow graph.

When to upgrade to full Workflows (agent_framework.workflows):
  - You need conditional branching between agents
  - You need to checkpoint / resume long-running processes
  - You need human-in-the-loop approval gates mid-flow
  - You're coordinating more than ~4 agents

Usage:
    from workflows.base import run_sequential, run_parallel

    # Chain: output of step 1 feeds into step 2
    result = await run_sequential(
        steps=[
            (researcher_agent, user_query),
            (summarizer_agent, "{previous}"),  # {previous} → auto-filled
        ]
    )

    # Fan-out: run agents concurrently, collect all results
    results = await run_parallel(
        tasks=[(agent_a, query), (agent_b, query)]
    )
"""

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def run_sequential(steps: list[tuple[Any, str]]) -> str:
    """
    Run a chain of agents where each step's output feeds into the next.

    Parameters
    ----------
    steps : list of (agent, prompt) tuples
        Use the literal "{previous}" anywhere in a prompt to insert
        the output of the previous step.

    Returns
    -------
    str  —  the final agent's response text
    """
    previous_output = ""
    for i, (agent, prompt) in enumerate(steps):
        resolved_prompt = prompt.replace("{previous}", previous_output)
        logger.info("Sequential step %d/%d — agent=%r", i + 1, len(steps), agent.name)
        logger.debug("Prompt: %.200s…", resolved_prompt)

        result = await agent.run(resolved_prompt)
        previous_output = result.text if hasattr(result, "text") else str(result)

        logger.info("Step %d complete — output length=%d chars", i + 1, len(previous_output))

    return previous_output


async def run_parallel(tasks: list[tuple[Any, str]]) -> list[str]:
    """
    Run multiple agents concurrently and return all results.

    Use this when agents are independent and you want to minimize wall-clock time.
    e.g. three specialized agents each analyzing the same document simultaneously.

    Parameters
    ----------
    tasks : list of (agent, prompt) tuples

    Returns
    -------
    list[str]  —  one result string per task, in the same order as input
    """
    logger.info("Running %d agents in parallel", len(tasks))

    async def _run_one(agent: Any, prompt: str, index: int) -> str:
        logger.debug("Parallel task %d starting — agent=%r", index, agent.name)
        result = await agent.run(prompt)
        text = result.text if hasattr(result, "text") else str(result)
        logger.debug("Parallel task %d done — %d chars", index, len(text))
        return text

    results = await asyncio.gather(
        *[_run_one(agent, prompt, i) for i, (agent, prompt) in enumerate(tasks)]
    )
    return list(results)


async def run_with_retry(
    agent: Any,
    prompt: str,
    max_attempts: int = 3,
    delay_seconds: float = 2.0,
) -> str:
    """
    Run an agent with automatic retry on failure.

    Useful for flaky tool calls (e.g. web search rate limits).

    Parameters
    ----------
    agent       : AIAgent
    prompt      : str
    max_attempts: int   — number of attempts before giving up
    delay_seconds: float — wait time between attempts (doubles each retry)
    """
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = await agent.run(prompt)
            return result.text if hasattr(result, "text") else str(result)
        except Exception as e:
            last_error = e
            logger.warning(
                "Agent %r failed on attempt %d/%d: %s",
                getattr(agent, "name", "?"),
                attempt,
                max_attempts,
                e,
            )
            if attempt < max_attempts:
                await asyncio.sleep(delay_seconds * attempt)

    raise RuntimeError(
        f"Agent failed after {max_attempts} attempts"
    ) from last_error
