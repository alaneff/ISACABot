"""
main.py — Central entrypoint for the Agentic Pipeline Factory.

Use this to:
  - Run any registered pipeline from the CLI
  - Verify your environment is correctly configured
  - Add new pipelines to the registry

Usage:
    python main.py                          # show help
    python main.py research "your question" # run the research pipeline
    python main.py verify                   # check env vars and connectivity
"""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from config.settings import configure_logging, settings

logger = configure_logging()

# ── Pipeline registry ──────────────────────────────────────────────────────────
# Add new pipelines here as you build them.
# Format: "command_name": (ImportPath, ClassName)
PIPELINE_REGISTRY = {
    "research":  "pipelines.examples.research_pipeline.ResearchPipeline",
    "isaca-sd":  "isaca_sd.pipelines.isaca_sd_pipeline.ISACASdPipeline",
}


def _load_pipeline(dotted_path: str):
    """Dynamically import a pipeline class by its dotted module.ClassName path."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


async def run_pipeline(name: str, query: str) -> None:
    if name not in PIPELINE_REGISTRY:
        print(f"Unknown pipeline: {name!r}", file=sys.stderr)
        print(f"Available: {', '.join(PIPELINE_REGISTRY)}")
        sys.exit(1)

    PipelineClass = _load_pipeline(PIPELINE_REGISTRY[name])
    pipeline = PipelineClass()

    print(f"\nPipeline : {name}")
    print(f"Model    : {settings.model}")
    print(f"Query    : {query}")
    print("─" * 60)

    result = await pipeline.run(query)

    if result.success:
        print(result.answer)
    else:
        print(f"\nPipeline failed: {result.error}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "─" * 60)
    print(f"Completed at: {result.completed_at}")


async def verify_env() -> None:
    """Quick sanity check — confirms API key and model are reachable."""
    print("Verifying environment...")
    print(f"  Model   : {settings.model}")
    print(f"  Thinking: {'enabled' if settings.extended_thinking else 'disabled'}")

    # Minimal live check — one token round-trip
    from agents.base import create_agent
    agent = create_agent(
        name="Verifier",
        instructions="Reply with exactly: OK",
        extra_options={"max_tokens": 10},
    )
    result = await agent.run("Reply with OK")
    text = result.text if hasattr(result, "text") else str(result)
    print(f"  API test: {text.strip()}")
    print("\nEnvironment OK.")


def print_help() -> None:
    print(__doc__)
    print("Registered pipelines:")
    for name, path in PIPELINE_REGISTRY.items():
        print(f"  {name:<15} → {path}")
    print()
    print("Other commands:")
    print("  eval                   Run the accuracy eval suite")
    print("  eval --filter CATEGORY Run one category (entry_level, factual, ...)")
    print("  eval --verbose         Show per-case scores")
    print("  verify                 Check environment and API connectivity")


async def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return

    command = args[0]

    if command == "verify":
        await verify_env()
        return

    if command == "eval":
        # Forward remaining args (--filter, --verbose) to the eval runner
        original_argv = sys.argv
        sys.argv = ["isaca_sd/evals/run_eval.py"] + args[1:]
        try:
            from isaca_sd.evals.run_eval import main as eval_main
            await eval_main()
        finally:
            sys.argv = original_argv
        return

    query = " ".join(args[1:])
    await run_pipeline(command, query)


if __name__ == "__main__":
    asyncio.run(main())
