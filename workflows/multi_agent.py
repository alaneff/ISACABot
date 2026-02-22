"""
Multi-agent workflow helpers.

Higher-level orchestration patterns built on top of workflows/base.py.
These are generic helpers — not ISACA-specific.

Usage:
    from workflows.multi_agent import run_with_safety, run_orchestrated

    # Simple safety wrapper:
    response = await run_with_safety(safety_agent, my_agent_fn, user_message)

    # Full orchestrated flow:
    response = await run_orchestrated(safety_agent, orchestrator, specialists, message, history)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

GENERIC_REJECTION = (
    "I'm not able to help with that. Please ask a question related to this chatbot's purpose."
)


async def run_with_safety(
    safety_agent,
    main_agent,
    user_message: str,
    rejection_message: str = GENERIC_REJECTION,
) -> str:
    """
    Run a safety check, then call main_agent if safe.

    Args:
        safety_agent:       Agent created by create_safety_agent()
        main_agent:         Any agent with .run(prompt) method
        user_message:       Raw user input
        rejection_message:  Response returned if safety check fails

    Returns:
        Agent response text, or rejection_message if unsafe.
    """
    from agents.safety_agent import run_safety_check

    is_safe, reason = await run_safety_check(safety_agent, user_message)
    if not is_safe:
        logger.info("Safety check rejected message. Reason: %s", reason)
        return rejection_message

    result = await main_agent.run(user_message)
    return result.text if hasattr(result, "text") else str(result)


async def run_orchestrated(
    safety_agent,
    orchestrator,
    specialists: dict,
    user_message: str,
    history: list[dict] | None = None,
    rejection_message: str = GENERIC_REJECTION,
    default_route: str = "general",
) -> tuple[str, str]:
    """
    Full orchestrated multi-agent flow: safety → route → specialist.

    Args:
        safety_agent:   Agent from create_safety_agent()
        orchestrator:   Routing classifier agent
        specialists:    Dict mapping route keys to agents, e.g.
                        {"general": agent, "resume": agent, ...}
        user_message:   Raw user input
        history:        Conversation history (list of {role, content} dicts)
        rejection_message: Returned if safety check fails
        default_route:  Fallback route if classifier fails or route unknown

    Returns:
        (response_text, route_used)
    """
    from agents.safety_agent import run_safety_check

    # 1. Safety check
    is_safe, reason = await run_safety_check(safety_agent, user_message)
    if not is_safe:
        logger.info("Safety check rejected message. Reason: %s", reason)
        return rejection_message, "rejected"

    # 2. Route classification
    try:
        from isaca_sd.agents.orchestrator import classify_route
        route = await classify_route(orchestrator, user_message)
    except Exception as exc:
        logger.warning("Orchestrator failed: %s — using default route '%s'", exc, default_route)
        route = default_route

    if route not in specialists:
        logger.warning("Unknown route '%s' — falling back to '%s'", route, default_route)
        route = default_route

    # 3. Run specialist
    specialist = specialists[route]
    prompt = _build_prompt(user_message, history or [])
    result = await specialist.run(prompt)
    response = result.text if hasattr(result, "text") else str(result)

    return response, route


def _build_prompt(user_message: str, history: list[dict]) -> str:
    """Build prompt with optional conversation history context."""
    if not history:
        return user_message
    history_text = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Advisor'}: {m['content']}"
        for m in history[-6:]
    )
    return (
        f"[Previous conversation]\n{history_text}\n\n"
        f"[New message]\nUser: {user_message}"
    )
