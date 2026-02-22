"""
ISACA SD Advisor — Evaluation Runner

Runs the test dataset against the advisor agent, grades each response with
Claude Haiku (cheap, fast), and prints a scored report.

Usage:
    python isaca_sd/evals/run_eval.py
    python isaca_sd/evals/run_eval.py --verbose
    python isaca_sd/evals/run_eval.py --filter entry_level

Or via main.py:
    python main.py eval
    python main.py eval --filter cert_comparison --verbose

Results are saved to isaca_sd/evals/results/YYYY-MM-DD_HH-MM.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from agents.base import create_agent
from config.settings import configure_logging, settings
from isaca_sd.agents.isaca_sd_agent import create_isaca_sd_agent

logger = logging.getLogger("eval")

DATASET_PATH = Path(__file__).parent / "dataset.json"
RESULTS_DIR = Path(__file__).parent / "results"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
PASS_THRESHOLD = 0.7

# ── Grader prompt ─────────────────────────────────────────────────────────────

GRADER_SYSTEM_PROMPT = """
You are an expert evaluator assessing AI-generated career and certification advice
for ISACA San Diego chapter members.

Score the response on a scale of 0.0 to 1.0:

  1.0 — Excellent: Fully meets all criteria. Accurate facts, appropriate recommendation,
        nothing harmful or misleading.
  0.8 — Good: Mostly correct with minor gaps or missing context.
  0.6 — Partial: Relevant but incomplete, vague, or omits a key point.
  0.3 — Poor: Significant flaw or omission — wrong cert recommended, key fact missing.
  0.0 — Fail: Clearly wrong advice, misleading facts, or recommends something explicitly
        prohibited by the criteria.

"pass" is true if score >= 0.7.

You MUST respond with ONLY valid JSON — no text before or after:
{"score": 0.8, "pass": true, "reason": "One or two sentence explanation."}
""".strip()


def _grader_prompt(case: dict, response: str) -> str:
    return (
        f"Question asked to the advisor:\n{case['question']}\n\n"
        f"Evaluation criteria:\n{case['grader_criteria']}\n\n"
        f"Must include (case-insensitive, any of these must appear): {case.get('must_include', [])}\n"
        f"Must NOT include: {case.get('must_not_include', [])}\n\n"
        f"Advisor's response:\n{response}\n\n"
        "Score this response per the rubric."
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_dataset(category_filter: str | None = None) -> list[dict]:
    with open(DATASET_PATH, encoding="utf-8") as f:
        cases = json.load(f)
    if category_filter:
        cases = [c for c in cases if c["category"] == category_filter]
    return cases


def create_grader():
    return create_agent(
        name="EvalGrader",
        instructions=GRADER_SYSTEM_PROMPT,
        model=HAIKU_MODEL,
        extra_options={"max_tokens": 256},
    )


def check_hard_rules(case: dict, response: str) -> tuple[bool, str]:
    """
    Fast deterministic checks before calling the LLM grader.
    Returns (passed, reason).
    """
    lower = response.lower()

    for term in case.get("must_not_include", []):
        if term.lower() in lower:
            return False, f"Contains forbidden term: '{term}'"

    missing = [t for t in case.get("must_include", []) if t.lower() not in lower]
    if missing:
        return False, f"Missing required terms: {missing}"

    return True, ""


def parse_grader_output(text: str) -> dict:
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"score": 0.0, "pass": False, "reason": f"Unparseable grader output: {text[:150]}"}


# ── Core eval logic ───────────────────────────────────────────────────────────

async def run_single_case(
    case: dict,
    advisor,
    grader,
    verbose: bool = False,
) -> dict:
    case_id = case["id"]

    # 1. Run advisor (with retry on 429 rate limit)
    response = ""
    for attempt in range(4):
        try:
            result = await advisor.run(case["question"])
            response = result.text if hasattr(result, "text") else str(result)
            break
        except Exception as exc:
            exc_str = str(exc)
            if "429" in exc_str and attempt < 3:
                wait = 20 * (attempt + 1)  # 20s, 40s, 60s
                logger.warning("[%s] Rate limited, retrying in %ds (attempt %d/3)...",
                               case_id, wait, attempt + 1)
                await asyncio.sleep(wait)
            else:
                logger.error("[%s] Advisor error: %s", case_id, exc)
                return _result(case, "", score=0.0, passed=False,
                               reason=f"Advisor error: {exc}", hard_fail=False)

    # 2. Hard rules (free, instant)
    ok, reason = check_hard_rules(case, response)
    if not ok:
        if verbose:
            logger.warning("[%s] HARD FAIL: %s", case_id, reason)
        return _result(case, response, score=0.0, passed=False, reason=reason, hard_fail=True)

    # 3. LLM grader (Haiku)
    try:
        gr = await grader.run(_grader_prompt(case, response))
        grader_text = gr.text if hasattr(gr, "text") else str(gr)
    except Exception as exc:
        logger.error("[%s] Grader error: %s", case_id, exc)
        grader_text = ""

    parsed = parse_grader_output(grader_text)
    score = float(parsed.get("score", 0.0))
    passed = score >= PASS_THRESHOLD

    if verbose:
        status = "PASS" if passed else "FAIL"
        logger.info("[%s] %s score=%.2f -- %s", case_id, status, score, parsed.get("reason", ""))

    return _result(case, response, score=score, passed=passed,
                   reason=parsed.get("reason", ""), hard_fail=False)


def _result(case, response, *, score, passed, reason, hard_fail):
    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "response": response,
        "score": score,
        "pass": passed,
        "reason": reason,
        "hard_rule_fail": hard_fail,
    }


async def run_all(cases, advisor, grader, verbose=False, concurrency: int = 2) -> list[dict]:
    logger.info("Running %d eval cases (concurrency=%d)...", len(cases), concurrency)
    sem = asyncio.Semaphore(concurrency)

    async def run_with_sem(case):
        async with sem:
            return await run_single_case(case, advisor, grader, verbose)

    return list(await asyncio.gather(*[run_with_sem(c) for c in cases]))


# ── Aggregation & reporting ───────────────────────────────────────────────────

def aggregate(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r["pass"])

    by_cat: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        if cat not in by_cat:
            by_cat[cat] = {"total": 0, "passed": 0, "scores": []}
        by_cat[cat]["total"] += 1
        by_cat[cat]["passed"] += int(r["pass"])
        by_cat[cat]["scores"].append(r["score"])

    cat_summary = {
        cat: {
            "pass_rate": d["passed"] / d["total"],
            "avg_score": sum(d["scores"]) / len(d["scores"]),
            "passed": d["passed"],
            "total": d["total"],
        }
        for cat, d in by_cat.items()
    }

    return {
        "overall_pass_rate": passed / total if total else 0.0,
        "overall_avg_score": sum(r["score"] for r in results) / total if total else 0.0,
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "by_category": cat_summary,
        "failures": [r for r in results if not r["pass"]],
    }


def print_report(agg: dict) -> None:
    print("\n" + "=" * 62)
    print("  ISACA SD Advisor -- Eval Results")
    print("=" * 62)
    print(f"  Overall Pass Rate : {agg['overall_pass_rate']:.0%}  ({agg['passed']}/{agg['total_cases']})")
    print(f"  Avg Score         : {agg['overall_avg_score']:.2f}")
    print()
    print("  By Category:")
    for cat, data in agg["by_category"].items():
        bar = "#" * int(data["pass_rate"] * 20)
        print(f"    {cat:<26} {data['pass_rate']:.0%}  [{bar:<20}]  ({data['passed']}/{data['total']})")
    print()
    if agg["failures"]:
        print(f"  Failures ({len(agg['failures'])}):")
        for f in agg["failures"]:
            tag = "[HARD]" if f.get("hard_rule_fail") else f"[{f['score']:.2f}]"
            print(f"    {tag} {f['id']}: {f['reason'][:90]}")
    print("=" * 62)


def save_results(results: list[dict], agg: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M")
    path = RESULTS_DIR / f"{ts}.json"
    payload = {
        "run_at": datetime.now(UTC).isoformat(),
        "model": settings.model,
        "grader_model": HAIKU_MODEL,
        "summary": agg,
        "cases": results,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


# ── Entrypoint ────────────────────────────────────────────────────────────────

async def main() -> None:
    configure_logging()

    parser = argparse.ArgumentParser(description="ISACA SD advisor eval suite")
    parser.add_argument("--filter", metavar="CATEGORY", help="Run only this category")
    parser.add_argument("--verbose", action="store_true", help="Log each case result")
    parser.add_argument("--concurrency", type=int, default=2, metavar="N",
                        help="Max parallel eval cases (default: 2)")
    parser.add_argument("--min-pass-rate", type=float, default=0.0, metavar="RATE",
                        help="Exit with code 1 if overall pass rate is below RATE (0.0–1.0). "
                             "Use in CI to catch regressions, e.g. --min-pass-rate 0.90")
    args = parser.parse_args()

    cases = load_dataset(category_filter=args.filter)
    print(f"Loaded {len(cases)} eval cases" + (f" (category: {args.filter})" if args.filter else ""))

    advisor = create_isaca_sd_agent()
    grader = create_grader()

    results = await run_all(cases, advisor, grader, verbose=args.verbose, concurrency=args.concurrency)
    agg = aggregate(results)
    print_report(agg)

    out = save_results(results, agg)
    print(f"\n  Results saved: {out}")

    if args.min_pass_rate > 0 and agg["overall_pass_rate"] < args.min_pass_rate:
        print(
            f"\n  REGRESSION: pass rate {agg['overall_pass_rate']:.0%} is below "
            f"threshold {args.min_pass_rate:.0%}"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
