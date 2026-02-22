"""
ISACA San Diego — Interactive Career & Certification Advisor Pipeline

Runs as an interactive command-line chatbot. Maintains conversation history
so the agent remembers context within the session.

The pipeline uses a multi-agent architecture internally:
  Safety Agent → Orchestrator → Specialist Agent → Response

Usage:
    python main.py isaca-sd
    python main.py isaca-sd "What cert should I get?"
"""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from agents.base import create_client
from agents.safety_agent import create_safety_agent, run_safety_check
from config.settings import configure_logging, settings
from isaca_sd.agents.career_coach import create_career_coach
from isaca_sd.agents.isaca_sd_agent import create_isaca_sd_agent
from isaca_sd.agents.job_search_agent import create_job_search_agent
from isaca_sd.agents.orchestrator import classify_route, create_orchestrator
from isaca_sd.agents.research_agent import create_research_agent
from isaca_sd.agents.resume_agent import create_resume_agent

WELCOME = """
+==============================================================+
|         ISACA San Diego -- Career & Certification Advisor    |
|                    isaca-sd.org                              |
+==============================================================+

I can help you with:
  - Cybersecurity / IT audit resume advice
  - Career path guidance (entry-level through executive)
  - Certification selection -- honest advice, not just ISACA certs

Type your question and press Enter. Type 'quit' or 'exit' to leave.
--------------------------------------------------------------
"""

SAFETY_REJECTION = (
    "I can only help with cybersecurity career and certification questions. "
    "Please ask me about certs, career paths, resumes, or job search in the security field."
)


def _build_prompt(user_message: str, history: list[dict]) -> str:
    """Build prompt with conversation history context."""
    if not history:
        return user_message
    history_text = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Advisor'}: {m['content']}"
        for m in history[-6:]  # last 3 exchanges
    )
    return (
        f"[Previous conversation]\n{history_text}\n\n"
        f"[New message]\nUser: {user_message}"
    )


class ISACASdPipeline:
    """
    Multi-agent ISACA SD advisor pipeline.

    Agents are created once at init (avoid per-turn cold starts).
    Each user turn goes through: safety check → route → specialist agent.
    """

    def __init__(self):
        # Share one client across all Sonnet agents to reduce overhead
        client = create_client()
        self._agents = {
            "safety":       create_safety_agent(),
            "orchestrator": create_orchestrator(),
            "general":      create_isaca_sd_agent(client=client),
            "resume":       create_resume_agent(client=client),
            "career":       create_career_coach(client=client),
            "research":     create_research_agent(client=client),
            "job_search":   create_job_search_agent(client=client),
        }

    async def _run_turn(self, user_message: str, history: list[dict]) -> str:
        """Run one conversation turn through the full multi-agent flow."""
        # 1. Safety check
        is_safe, reason = await run_safety_check(self._agents["safety"], user_message)
        if not is_safe:
            return SAFETY_REJECTION

        # 2. Route to specialist
        route = await classify_route(self._agents["orchestrator"], user_message)

        # 3. Run specialist with conversation context
        specialist = self._agents.get(route, self._agents["general"])
        prompt = _build_prompt(user_message, history)
        result = await specialist.run(prompt)
        return result.text if hasattr(result, "text") else str(result)

    async def _chat_loop(self) -> None:
        """Interactive REPL for conversational use."""
        configure_logging()
        print(WELCOME)

        history: list[dict] = []

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "bye", "q"):
                print("\nGoodbye! Visit isaca-sd.org for upcoming events and resources.")
                break

            print("\nAdvisor: ", end="", flush=True)

            try:
                response = await self._run_turn(user_input, history)
                print(response)
            except Exception as e:
                print(f"\n[Error: {e}]")
                continue

            print("\n" + "-" * 62)

            # Store turn in history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

    async def run(self, query: str):
        from dataclasses import dataclass, field
        from datetime import UTC, datetime

        @dataclass
        class PipelineResult:
            query: str
            answer: str
            pipeline_name: str = "ISACASdPipeline"
            model: str = field(default_factory=lambda: settings.model)
            completed_at: str = field(
                default_factory=lambda: datetime.now(UTC).isoformat()
            )
            success: bool = True
            error: str | None = None

        if not query or query.lower() in ("chat", "interactive", ""):
            await self._chat_loop()
            return PipelineResult(query=query, answer="[interactive session ended]")

        # Single-turn mode
        try:
            answer = await self._run_turn(query, history=[])
            return PipelineResult(query=query, answer=answer)
        except Exception as e:
            return PipelineResult(query=query, answer="", success=False, error=str(e))


if __name__ == "__main__":
    asyncio.run(ISACASdPipeline()._chat_loop())
