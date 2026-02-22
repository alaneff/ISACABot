"""
Example pipeline: Research & Summarize.

This is the simplest complete example of a production-ready pipeline.
It accepts a question, runs the research workflow, and returns the answer.

Run directly:
    python pipelines/examples/research_pipeline.py "What is Azure Container Apps?"

Or import and call from main.py / an Azure Function / a FastAPI endpoint:
    from pipelines.examples.research_pipeline import ResearchPipeline
    result = await ResearchPipeline().run("your question here")
"""

import asyncio
import logging
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dataclasses import dataclass, field
from datetime import UTC, datetime

from config.settings import configure_logging, settings
from workflows.examples.research_workflow import ResearchWorkflow

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Structured result returned by every pipeline — keep this consistent."""

    query: str
    answer: str
    pipeline_name: str = "ResearchPipeline"
    model: str = field(default_factory=lambda: settings.model)
    completed_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    success: bool = True
    error: str | None = None


class ResearchPipeline:
    """
    End-to-end research pipeline.

    This class is intentionally thin — it delegates to the workflow and
    wraps the result in a structured PipelineResult.

    To build a new pipeline:
    1. Copy this file and rename the class.
    2. Swap ResearchWorkflow for your own workflow.
    3. Adjust PipelineResult fields as needed.
    4. Register it in main.py.
    """

    def __init__(self) -> None:
        self._workflow = ResearchWorkflow()

    async def run(self, query: str) -> PipelineResult:
        logger.info("ResearchPipeline.run — query=%.80s", query)
        try:
            answer = await self._workflow.run(query)
            return PipelineResult(query=query, answer=answer)
        except Exception as e:
            logger.exception("Pipeline failed: %s", e)
            return PipelineResult(
                query=query,
                answer="",
                success=False,
                error=str(e),
            )


async def _cli_main() -> None:
    configure_logging()
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is Azure Container Apps?"
    print(f"\nRunning ResearchPipeline\nModel: {settings.model}\nQuery: {query}\n")
    print("─" * 60)

    result = await ResearchPipeline().run(query)

    if result.success:
        print(result.answer)
    else:
        print(f"Pipeline failed: {result.error}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "─" * 60)
    print(f"Completed at: {result.completed_at}")


if __name__ == "__main__":
    asyncio.run(_cli_main())
