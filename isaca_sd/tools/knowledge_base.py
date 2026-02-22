"""
Knowledge base RAG search tool.

Builds a keyword-based index over the isaca_sd/knowledge/ markdown files at first
call, then scores chunks against a query using token overlap. No vector DB needed
for a corpus this size.

Index structure: each H2 section in each .md file becomes one chunk.
Also searches cert-index.json for lightweight data on all ~481 certs from the
Paul Jerimy Security Certification Roadmap.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Annotated

from agent_framework import tool

logger = logging.getLogger(__name__)

# Knowledge base root — two levels up from this file (isaca_sd/tools/ → isaca_sd/ → knowledge/)
_KB_ROOT = Path(__file__).parent.parent / "knowledge"
_CERT_INDEX_PATH = _KB_ROOT / "cert-index.json"

_STOPWORDS = {
    "a", "an", "the", "is", "in", "on", "at", "to", "for", "of", "and",
    "or", "but", "with", "by", "from", "as", "be", "are", "was", "were",
    "i", "my", "me", "you", "your", "what", "how", "do", "does", "can",
    "should", "would", "want", "need", "get", "have", "has", "it", "this",
    "that", "not", "no", "if", "which", "who", "when", "where", "why",
    "will", "go", "got", "just", "about", "more", "also", "than",
}

_INDEX: list[dict] | None = None  # lazily built on first search
_CERT_INDEX: list[dict] | None = None  # cert-index.json entries
_MAX_CHUNK_CHARS = 1500           # cap per chunk in results
_TOP_N = 3                        # number of results to return


def _tokenize(text: str) -> set[str]:
    """Lowercase, split on non-word chars, strip stopwords and short tokens."""
    tokens = re.findall(r"[a-zA-Z0-9+#\-]+", text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 1}


def _build_index() -> list[dict]:
    """
    Walk knowledge/ dir, split each .md file into H2 sections.
    Returns list of chunk dicts.
    """
    chunks = []
    if not _KB_ROOT.exists():
        logger.warning("Knowledge base not found at: %s", _KB_ROOT)
        return chunks

    md_files = sorted(_KB_ROOT.rglob("*.md"))
    if not md_files:
        logger.warning("No .md files found under: %s", _KB_ROOT)
        return chunks

    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Cannot read %s: %s", md_file, exc)
            continue

        rel_path = str(md_file.relative_to(_KB_ROOT))

        # Split on H2 headings (##), keeping the heading with its section
        sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.splitlines()
            heading = lines[0].lstrip("#").strip() if lines else ""
            body = "\n".join(lines[1:]).strip()

            chunks.append({
                "file_path": rel_path,
                "heading": heading,
                "body": body,
                "tokens": _tokenize(heading + " " + body),
                "file_tokens": _tokenize(
                    rel_path.replace("/", " ").replace("\\", " ")
                             .replace("-", " ").replace("_", " ")
                ),
            })

    logger.info("Knowledge base index: %d chunks from %d files", len(chunks), len(md_files))
    return chunks


def _load_cert_index() -> list[dict]:
    """Load cert-index.json if it exists. Returns list of cert entries."""
    if not _CERT_INDEX_PATH.exists():
        return []
    try:
        data = json.loads(_CERT_INDEX_PATH.read_text(encoding="utf-8"))
        certs = data.get("certs", [])
        logger.info("Cert index loaded: %d certs", len(certs))
        return certs
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Cannot load cert-index.json: %s", exc)
        return []


def _get_index() -> list[dict]:
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    return _INDEX


def _get_cert_index() -> list[dict]:
    global _CERT_INDEX
    if _CERT_INDEX is None:
        _CERT_INDEX = _load_cert_index()
    return _CERT_INDEX


def _score(chunk: dict, query_tokens: set[str]) -> float:
    """
    Score a chunk against a set of query tokens.

    Base: overlap / query length
    Boost ×1.5 if a query token appears in the heading
    Boost ×1.2 if a query token appears in the file name
    """
    overlap = query_tokens & chunk["tokens"]
    if not overlap:
        return 0.0

    score = len(overlap) / len(query_tokens)

    heading_tokens = _tokenize(chunk["heading"])
    if query_tokens & heading_tokens:
        score *= 1.5

    if query_tokens & chunk["file_tokens"]:
        score *= 1.2

    return score


def _search_cert_index(query_tokens: set[str]) -> list[dict]:
    """
    Search cert-index.json for certs matching query tokens.
    Returns matched cert entries sorted by score.
    """
    results = []
    for cert in _get_cert_index():
        searchable = " ".join([
            cert.get("abbreviation", ""),
            cert.get("full_name", ""),
            cert.get("issuer", ""),
            cert.get("category", ""),
            cert.get("brief", ""),
        ])
        cert_tokens = _tokenize(searchable)
        overlap = query_tokens & cert_tokens
        if overlap:
            # Boost if abbreviation matches directly
            abbr_tokens = _tokenize(cert.get("abbreviation", ""))
            score = len(overlap) / len(query_tokens)
            if query_tokens & abbr_tokens:
                score *= 2.0
            results.append((score, cert))

    results.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in results[:3]]


@tool(approval_mode="never_require")
def search_knowledge_base(
    query: Annotated[str, "Search query about certifications, career paths, or ISACA San Diego chapter"]
) -> str:
    """
    Search the local knowledge base for certification details, career path guidance,
    study tips, and ISACA San Diego chapter information. Returns the top 3 most
    relevant sections. Also searches the cert index (480+ certs from the Paul Jerimy
    Security Certification Roadmap) for brief cert information. Use this for deeper
    context beyond what get_cert_facts provides, especially for study strategies,
    career path narratives, and employer context.
    """
    index = _get_index()
    query_tokens = _tokenize(query)

    if not query_tokens:
        return "Query too short or contains only common words. Please use more specific terms."

    results = []

    # Search markdown KB
    if index:
        scored: list[tuple[float, dict]] = []
        for chunk in index:
            s = _score(chunk, query_tokens)
            if s > 0:
                scored.append((s, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        for rank, (score, chunk) in enumerate(scored[:_TOP_N], 1):
            header = f"### Result {rank} — {chunk['heading']}  (from: {chunk['file_path']})"
            body = chunk["body"]
            if len(body) > _MAX_CHUNK_CHARS:
                body = body[:_MAX_CHUNK_CHARS] + "\n\n_(truncated — see full file for more)_"
            results.append(f"{header}\n\n{body}")

    # Search cert index for additional cert coverage
    cert_matches = _search_cert_index(query_tokens)
    if cert_matches:
        cert_lines = ["### Cert Index Matches (from Paul Jerimy Security Certification Roadmap)\n"]
        for cert in cert_matches:
            line = (
                f"- **{cert.get('abbreviation', '?')}** ({cert.get('full_name', '')})"
                f" — {cert.get('issuer', '')} | {cert.get('category', '')} | "
                f"Level: {cert.get('level', 'unknown')} | {cert.get('brief', '')}"
            )
            cert_lines.append(line)
        results.append("\n".join(cert_lines))

    if not results:
        return (
            f"No relevant results in knowledge base for: '{query}'. "
            "Try different keywords, or use get_cert_facts for cert-specific data."
        )

    return "\n\n---\n\n".join(results)
