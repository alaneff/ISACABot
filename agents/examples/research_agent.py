"""
Example: Research agent with web search.

This agent can search the web and synthesize findings.
It demonstrates:
- Hosted tool (web search) via Anthropic API
- Extended thinking for complex research tasks
- Streaming output

Usage:
    from agents.examples.research_agent import create_research_agent

    agent = create_research_agent()
    result = await agent.run("What are the key differences between Azure Container Apps and AKS?")
    print(result.text)
"""

import asyncio
import logging

from agent_framework.anthropic import AnthropicClient

from config.settings import settings

logger = logging.getLogger(__name__)

RESEARCH_INSTRUCTIONS = """
You are a thorough research assistant. When given a topic or question:
1. Search for recent, authoritative sources.
2. Synthesize findings into a clear, structured answer.
3. Always cite where your information comes from.
4. Flag anything uncertain or that needs verification.

Be concise but complete. Use bullet points and headers for readability.
""".strip()


def create_research_agent(client: AnthropicClient | None = None):
    """
    Research agent with web search and extended thinking.

    The web search tool is hosted by Anthropic — no API key needed for it.
    Extended thinking lets Claude plan its research approach before searching.
    """
    resolved_client = client or AnthropicClient(
        api_key=settings.anthropic_api_key,
        model_id=settings.model,
    )

    return resolved_client.as_agent(
        name="ResearchAgent",
        instructions=RESEARCH_INSTRUCTIONS,
        tools=[resolved_client.get_web_search_tool()],
        default_options={
            "max_tokens": 16_000,
            "thinking": {"type": "enabled", "budget_tokens": 8_000},
        },
    )


async def run_example() -> None:
    """Quick smoke-test — run this file directly to verify your API key works."""
    logging.basicConfig(level=logging.INFO)
    agent = create_research_agent()

    query = "What is Microsoft Agent Framework and how does it compare to AutoGen?"
    print(f"\nUser: {query}\n")
    print("Agent (streaming):\n")

    async for chunk in agent.run(query, stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    asyncio.run(run_example())
