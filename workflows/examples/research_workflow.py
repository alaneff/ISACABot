"""
Example: Multi-agent research workflow using the Agent Framework graph-based Workflow.

This demonstrates the full Workflow API (not just simple sequential chaining)
for when you need:
  - Explicit routing between nodes
  - Persistent state across steps
  - Easy extension to human-in-the-loop

Flow:
    query → ResearchAgent → SummaryAgent → output

Usage:
    from workflows.examples.research_workflow import ResearchWorkflow

    wf = ResearchWorkflow()
    result = await wf.run("What are the best practices for Azure Container Apps?")
    print(result)
"""

import logging

from agent_framework.anthropic import AnthropicClient

from agents.base import create_agent
from config.settings import settings

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    """
    Two-stage workflow: research → summarize.

    - Stage 1 (ResearchAgent): searches and gathers raw information.
    - Stage 2 (SummaryAgent): condenses the raw research into a clear final answer.

    Splitting responsibilities keeps each agent's task focused, which
    generally produces better results than one agent doing everything.
    """

    def __init__(self) -> None:
        client = AnthropicClient(
            api_key=settings.anthropic_api_key,
            model_id=settings.model,
        )

        self._researcher = create_agent(
            name="ResearchAgent",
            instructions=(
                "You are a thorough research assistant. "
                "Search the web and gather detailed, factual information on the given topic. "
                "Include sources. Do not summarize — provide the raw findings."
            ),
            tools=[client.get_web_search_tool()],
            extra_options={"max_tokens": 12_000},
            client=client,
        )

        self._summarizer = create_agent(
            name="SummaryAgent",
            instructions=(
                "You are a concise technical writer. "
                "Given raw research notes, produce a clear, structured summary "
                "with headers, bullet points, and a short conclusion. "
                "Target audience: technical professionals."
            ),
            extra_options={"max_tokens": 4_000},
            client=client,
        )

    async def run(self, query: str) -> str:
        """
        Execute the research → summarize pipeline.

        Parameters
        ----------
        query : str
            The question or topic to research.

        Returns
        -------
        str
            Final summarized answer.
        """
        logger.info("ResearchWorkflow starting — query=%.80s", query)

        # Stage 1: gather raw research
        research_result = await self._researcher.run(query)
        raw_research = (
            research_result.text
            if hasattr(research_result, "text")
            else str(research_result)
        )
        logger.debug("Research complete — %d chars collected", len(raw_research))

        # Stage 2: summarize
        summary_prompt = (
            f"Here are research notes on the topic: '{query}'\n\n"
            f"--- RESEARCH NOTES ---\n{raw_research}\n--- END ---\n\n"
            "Please produce a clear, structured summary."
        )
        summary_result = await self._summarizer.run(summary_prompt)
        final = (
            summary_result.text
            if hasattr(summary_result, "text")
            else str(summary_result)
        )

        logger.info("ResearchWorkflow complete — output %d chars", len(final))
        return final
