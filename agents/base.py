"""
Agent factory — the single place where all agents are created.

Why a factory instead of building agents inline?
- Enforces consistent Claude configuration across every pipeline.
- One place to change the model, token limits, or thinking settings.
- Makes swapping providers (e.g. Anthropic → Azure Foundry) a one-line change.

Usage:
    from agents.base import create_agent

    agent = create_agent(
        name="Summarizer",
        instructions="You summarize documents clearly and concisely.",
        tools=[my_tool],           # optional
        model="claude-opus-4-6",   # optional override
    )
    result = await agent.run("Summarize this article: ...")
"""

import logging
from collections.abc import Callable
from typing import Any

from agent_framework.anthropic import AnthropicClient

from config.settings import settings

logger = logging.getLogger(__name__)


def create_client(
    api_key: str | None = None,
    model_id: str | None = None,
) -> AnthropicClient:
    """
    Build an AnthropicClient.

    The model_id must be set on the client (not on as_agent()).
    Pass api_key explicitly in tests; leave None to read from ANTHROPIC_API_KEY.
    """
    return AnthropicClient(
        api_key=api_key or settings.anthropic_api_key,
        model_id=model_id or settings.model,
    )


def create_agent(
    name: str,
    instructions: str,
    *,
    tools: list[Callable] | Callable | None = None,
    model: str | None = None,
    extra_options: dict[str, Any] | None = None,
    client: AnthropicClient | None = None,
):
    """
    Create a Claude-backed AIAgent with best-practice defaults applied.

    Parameters
    ----------
    name : str
        Human-readable name shown in logs and traces.
    instructions : str
        The system prompt / persona for this agent.
        Tip: be specific. Claude performs better with clear role + scope.
    tools : list[Callable] | Callable | None
        Functions decorated with @tool (from agent_framework).
        Pass a single tool or a list.
    model : str | None
        Override the default model from settings.
        e.g. "claude-opus-4-6" for a heavy reasoning step.
    extra_options : dict | None
        Merged on top of settings.default_options.
        Use to override max_tokens or thinking per-agent.
    client : AnthropicClient | None
        Reuse an existing client (avoids creating a new HTTP connection pool).

    Returns
    -------
    AIAgent  (agent_framework.AIAgent)
    """
    resolved_model = model or settings.model
    # model_id must be on the client, not on as_agent() — create a fresh client
    # if a model override is requested or no client was supplied
    resolved_client = client if (client and not model) else create_client(model_id=resolved_model)

    # Start from global defaults, then layer in any per-agent overrides
    options = {**settings.default_options}
    if extra_options:
        options.update(extra_options)

    logger.debug(
        "Creating agent name=%r model=%r max_tokens=%s thinking=%s",
        name,
        resolved_model,
        options.get("max_tokens"),
        options.get("thinking", {}).get("type", "disabled"),
    )

    agent_kwargs: dict[str, Any] = {
        "name": name,
        "instructions": instructions,
        "default_options": options,
    }
    if tools is not None:
        agent_kwargs["tools"] = tools

    return resolved_client.as_agent(**agent_kwargs)


def create_thinking_agent(
    name: str,
    instructions: str,
    *,
    tools: list[Callable] | Callable | None = None,
    model: str = "claude-sonnet-4-6",
    budget_tokens: int = 10_000,
    max_tokens: int = 16_000,
    client: AnthropicClient | None = None,
):
    """
    Convenience wrapper for agents that need extended thinking.

    Extended thinking makes Claude show its reasoning chain before answering.
    Use this for:
    - Complex multi-step analysis
    - Tasks requiring careful planning before acting
    - Situations where you want to audit Claude's reasoning

    budget_tokens must be less than max_tokens.
    """
    return create_agent(
        name=name,
        instructions=instructions,
        tools=tools,
        model=model,
        extra_options={
            "max_tokens": max_tokens,
            "thinking": {"type": "enabled", "budget_tokens": budget_tokens},
        },
        client=client,
    )
