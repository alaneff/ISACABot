"""
ISACA San Diego — Interactive Career & Certification Advisor

Runs as an interactive command-line chatbot. Maintains conversation history
so the agent remembers context within the session (e.g. "my background is X").

Usage:
    python pipelines/isaca_sd_pipeline.py

Or via main.py:
    python main.py isaca-sd
"""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from agents.isaca_sd_agent import create_isaca_sd_agent
from config.settings import configure_logging, settings

WELCOME = """
╔══════════════════════════════════════════════════════════════╗
║         ISACA San Diego — Career & Certification Advisor     ║
║                    isaca-sd.org                              ║
╚══════════════════════════════════════════════════════════════╝

I can help you with:
  • Cybersecurity / IT audit resume advice
  • Career path guidance (entry-level through executive)
  • Certification selection — honest advice, not just ISACA certs

Type your question and press Enter. Type 'quit' or 'exit' to leave.
──────────────────────────────────────────────────────────────
"""


async def chat_loop() -> None:
    configure_logging()
    print(WELCOME)

    agent = create_isaca_sd_agent()
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

        # Build the prompt with conversation history for context
        if history:
            history_text = "\n".join(
                f"{'User' if m['role'] == 'user' else 'Advisor'}: {m['content']}"
                for m in history[-6:]  # last 3 exchanges keeps context without ballooning tokens
            )
            prompt = (
                f"[Previous conversation]\n{history_text}\n\n"
                f"[New message]\nUser: {user_input}"
            )
        else:
            prompt = user_input

        print("\nAdvisor: ", end="", flush=True)

        full_response = ""
        try:
            async for chunk in agent.run(prompt, stream=True):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text
        except Exception as e:
            print(f"\n[Error: {e}]")
            continue

        print("\n" + "─" * 62)

        # Store turn in history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": full_response})


class ISACASdPipeline:
    """
    Wrapper so this pipeline can be registered in main.py.

    When called from main.py with a query argument, runs a single-turn response.
    When called with no query (or 'chat'), starts the interactive loop.
    """

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
            # Drop into interactive mode
            await chat_loop()
            return PipelineResult(query=query, answer="[interactive session ended]")

        # Single-turn mode
        agent = create_isaca_sd_agent()
        try:
            result = await agent.run(query)
            answer = result.text if hasattr(result, "text") else str(result)
            return PipelineResult(query=query, answer=answer)
        except Exception as e:
            return PipelineResult(query=query, answer="", success=False, error=str(e))


if __name__ == "__main__":
    asyncio.run(chat_loop())
