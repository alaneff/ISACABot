# ISACA San Diego — Chatbot Project Plan

**Goal:** Build a high-quality, trustworthy AI advisor that helps ISACA SD members learn about
cybersecurity certifications, advance their careers, and find employment — with strong controls
to prevent abuse.

**Date:** 2026-02-21
**Status:** MVP complete — this document defines the path to production-grade quality.

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Gap Analysis](#2-gap-analysis)
3. [Target Architecture](#3-target-architecture)
4. [Phased Roadmap](#4-phased-roadmap)
5. [Technology Stack](#5-technology-stack)
6. [Quality & Controls](#6-quality--controls)
7. [Success Metrics](#7-success-metrics)

---

## 1. Current State Assessment

### What Works Well

| Capability | Status | Notes |
|---|---|---|
| Multi-agent pipeline | ✓ Working | Safety → Orchestrator → 5 Specialists |
| LLM safety classifier | ✓ Working | Haiku-based, blocks injection/off-topic |
| Knowledge base (35 certs) | ✓ Working | Markdown files, keyword search |
| Cert index (211 certs) | ✓ Working | Lightweight JSON from Paul Jerimy roadmap |
| 5 specialist agents | ✓ Working | General, Resume, Career, Research, Job Search |
| Eval suite (30 cases) | ✓ Working | 100% pass rate on tested categories |
| Honest advice philosophy | ✓ Strong | Recommends best cert, not just ISACA certs |
| CLI interface | ✓ Working | `python main.py isaca-sd` |
| FastAPI layer skeleton | ✓ Exists | `api/` with Azure AD B2C auth stubs |

### What Is Missing or Fragile

| Gap | Severity | Impact |
|---|---|---|
| Keyword-only RAG | High | Misses semantically related content |
| In-memory sessions only | High | Context lost on restart; no multi-device |
| No API rate limiting | High | Single user can exhaust quota; DoS risk |
| Hardcoded salary data in prompts | High | Data goes stale immediately |
| Safety agent defaults to "safe" on failure | Medium | Attack surface if Haiku is unavailable |
| No audit logging | Medium | Can't review conversations or spot abuse |
| Orchestrator confidence score unused | Medium | Low-confidence routes always proceed |
| get_cert_facts() DB has 15 of 35 certs | Medium | Agents miss detail for 20 KB certs |
| No user feedback mechanism | Medium | No signal to improve quality |
| No web UI | Medium | CLI-only limits real user adoption |
| Static KB — no refresh process | Low | Cert details, costs, and exams change |
| Job search agent is web-only | Low | Fails gracefully but gives shallow results |

---

## 2. Gap Analysis

### Control Risks (Abuse Prevention)

The strongest risk to the chatbot being misused is **quota exhaustion and prompt injection**. A
single malicious user making rapid requests with jailbreak attempts could:

1. Exhaust API credits in minutes (no per-user throttling)
2. Slip an injection past the LLM safety agent when it defaults to "safe" on error
3. Get the bot to produce off-topic or harmful content

**Mitigation requirements:**
- Per-user rate limiting (e.g., 20 requests/hour)
- Secondary hard-pattern injection check (regex, no LLM dependency)
- Safety agent must fail-closed (default reject on error, not default safe)
- Audit log every conversation turn

### Knowledge Quality Risks

The current keyword search misses synonyms and paraphrasing. A user asking "what cert proves I
can manage risk in IT systems" won't reliably find CRISC. The cert facts DB (15 certs) means
specialist agents don't have structured data for 20 of the 35 detailed KB certs.

**Mitigation requirements:**
- Semantic (vector) search alongside keyword search
- Expand get_cert_facts() to cover all 35 KB certs
- KB refresh process (quarterly or triggered)

### Session & Scale Risks

All conversation history is stored in memory in the pipeline object. In production:
- Restarting the API loses all session context
- Two API instances can't share sessions
- History grows unbounded; older turns get dropped arbitrarily (currently last 3 exchanges)

**Mitigation requirements:**
- Externalize sessions to Redis or a database
- Implement conversation summarization for long sessions
- TTL-based session expiry (e.g., 24 hours idle)

---

## 3. Target Architecture

### Production Pipeline (Per-Request Flow)

```mermaid
flowchart TD
    USER([User]) -->|HTTP POST /chat| APIM

    subgraph AZURE_FRONT[\"Azure Front Door / API Management\"]
        APIM[\"Rate Limiter\n20 req/hr per user\nAzure API Management\"]
    end

    APIM --> AUTH

    subgraph API[\"FastAPI  (api/)\"]
        AUTH[\"Azure AD B2C\nAuthenticate user\"]
        SESSION[\"Session Store\nLoad history from Redis\"]
        AUTH --> SESSION
        SESSION --> PIPELINE
    end

    subgraph PIPELINE[\"ISACASdPipeline\"]
        direction TB

        HARD[\"Hard-Pattern Check\n(regex, no LLM)\nBlock obvious injections instantly\"]
        SAFE[\"Safety Agent\nHaiku — LLM classifier\nFail-CLOSED on error\"]
        ORCH[\"Orchestrator\nHaiku — route classifier\nConfidence threshold ≥ 0.5\"]

        subgraph SPEC[\"Specialist Agents  (Sonnet)\"]
            direction LR
            GA[\"General\"]
            RA[\"Resume\"]
            CA[\"Career\"]
            RE[\"Research\"]
            JA[\"Job Search\"]
        end

        HARD -->|\"clean\"| SAFE
        HARD -->|\"injection\"| REJ_H([Reject])
        SAFE -->|\"safe\"| ORCH
        SAFE -->|\"unsafe / error\"| REJ_S([Reject])
        ORCH --> SPEC
    end

    subgraph KB[\"Knowledge Layer\"]
        direction LR
        VEC[\"Semantic Search\nAzure AI Search\nvector + BM25 hybrid\"]
        CF[\"get_cert_facts()\n35 certs — structured\"]
        WEB[\"web_search()\nBrave / Bing API\"]
    end

    SPEC --> VEC
    SPEC --> CF
    JA & RA & RE --> WEB

    PIPELINE --> SAVE[\"Save turn to Redis\nAppend to session\"]
    PIPELINE --> LOG[\"Audit Log\nAzure App Insights\nno PII in logs\"]

    SAVE --> RESP([Response to User])
    LOG --> RESP
    RESP --> USER
```

### Knowledge Base & RAG Architecture

```mermaid
flowchart LR
    subgraph BUILD[\"Offline KB Build  (quarterly or on-demand)\"]
        direction TB
        SRC[\"Source Markdown\n35 cert files\n4 career path files\"]
        IDX[\"cert-index.json\n211 certs (Paul Jerimy)\"]
        CHUNK[\"Chunk at H2 headers\n~300 tokens each\"]
        EMBED[\"Embed chunks\nAzure OpenAI\ntext-embedding-3-small\"]
        UPLOAD[\"Upload to\nAzure AI Search index\"]
        SRC --> CHUNK --> EMBED --> UPLOAD
        IDX --> UPLOAD
    end

    subgraph QUERY[\"Runtime search_knowledge_base()\"]
        direction TB
        Q[\"User query\"] --> QE[\"Embed query\"]
        QE --> HYBRID[\"Hybrid search\nBM25 keyword +\nvector cosine similarity\"]
        HYBRID --> RERANK[\"Re-rank top-10\nreturn top-5 chunks\"]
    end

    UPLOAD -.->|\"index\"| HYBRID
```

### Session Management

```mermaid
flowchart LR
    subgraph SESSION[\"Session Lifecycle\"]
        CREATE[\"First message\nGenerate session_id\nCreate Redis key\"] -->
        LOAD[\"Load N recent turns\nfrom Redis\"] -->
        RUN[\"Run pipeline turn\"] -->
        STORE[\"Append turn\nSet TTL 24h\"] -->
        CHECK{\"Turn count > 20?\"}
        CHECK -->|\"yes\"| SUMMARIZE[\"Summarize older turns\nwith Haiku\nreplace with summary\"]
        CHECK -->|\"no\"| DONE([Done])
        SUMMARIZE --> DONE
    end
```

---

## 4. Phased Roadmap

### Phase A — Hardening (Controls & Reliability)
**Target: Ready for beta users. No known abuse vectors.**

| # | Task | Effort | Priority |
|---|------|--------|----------|
| A1 | Add regex pre-filter before safety agent — block `ignore.*instructions`, `you are now`, `DAN`, `jailbreak` etc. | 1 day | Critical |
| A2 | Change safety agent to fail-CLOSED (default reject on error, not default safe) | 1 hour | Critical |
| A3 | Add `slowapi` rate limiting to FastAPI — 20 req/hr per authenticated user, 5 req/hr anonymous | 1 day | Critical |
| A4 | Add structured audit logging per turn — session_id, route taken, safety result, token counts — to a file or App Insights | 1 day | High |
| A5 | Add orchestrator confidence threshold — if confidence < 0.5, route to "general" instead of low-confidence specialist | 2 hours | High |
| A6 | Add graceful error responses — catch specialist agent exceptions, return user-friendly message not stack trace | 2 hours | High |

**Verify:** Run adversarial input suite against the hardened pipeline. Run `python main.py eval`.

---

### Phase B — Knowledge Quality
**Target: Accurate, complete, semantically searchable KB.**

| # | Task | Effort | Priority |
|---|------|--------|----------|
| B1 | Expand `get_cert_facts()` CERT_DB from 15 → 35 certs to match all KB markdown files | 1 day | High |
| B2 | Extract salary ranges from agent system prompts → move into `isaca_sd/knowledge/salary-data.json` — load at agent init | 1 day | High |
| B3 | Add Azure AI Search integration to `search_knowledge_base()` — hybrid BM25 + vector search — fall back to current keyword if unavailable | 3 days | High |
| B4 | Re-embed all 35 cert files + 4 career paths + cert-index entries into Azure AI Search index | 1 day | High |
| B5 | Write a `scripts/refresh_kb.py` script to re-chunk, re-embed, and re-upload KB — run quarterly or when certs change | 1 day | Medium |
| B6 | Add 10–15 more detailed cert markdown files: `gcfe.md`, `cfe.md`, `cissp-issap.md`, `ccsp.md`, `gcfe.md`, `cloud+.md`, `cnd.md` | 3 days | Medium |

**Verify:** Manual search tests for synonyms ("risk management cert" → CRISC, "cloud security" → CCSP/AWS Security). Run full eval suite.

---

### Phase C — Sessions & Scale
**Target: Multi-turn conversations that persist across restarts and API instances.**

| # | Task | Effort | Priority |
|---|------|--------|----------|
| C1 | Deploy Azure Cache for Redis (or use `fakeredis` for local dev) | 1 day | High |
| C2 | Implement `SessionStore` class — `load_history(session_id)`, `append_turn()`, `set_ttl(24h)` | 1 day | High |
| C3 | Wire `SessionStore` into `ISACASdPipeline._run_turn()` — replace in-memory `history: list` | 1 day | High |
| C4 | Implement conversation summarization — when turn count > 20, summarize oldest 15 turns with Haiku, replace with summary block | 2 days | Medium |
| C5 | Add session_id to API responses — allow client to pass back on next request (or store in cookie/JWT) | 1 day | Medium |

**Verify:** Start two pipeline instances. Confirm same session_id retrieves same history from both.

---

### Phase D — User Interface
**Target: Real users can access the bot without the CLI.**

| # | Task | Effort | Priority |
|---|------|--------|----------|
| D1 | Finalize FastAPI endpoints: `POST /chat`, `GET /health`, `GET /session/{id}` | 2 days | High |
| D2 | Complete Azure AD B2C integration — ISACA SD member login (or simpler: email + OTP) | 3 days | High |
| D3 | Build minimal web chat UI — plain HTML/JS or React — connects to FastAPI | 3 days | High |
| D4 | Add user feedback buttons (👍 / 👎) per response — log to App Insights | 1 day | Medium |
| D5 | Add "cite your source" — include KB chunk titles in response metadata | 2 days | Medium |
| D6 | Consider Microsoft Teams bot integration — ISACA SD may already use Teams | 2 days | Low |

**Verify:** End-to-end test from browser through Azure AD B2C, through FastAPI, to advisor response.

---

### Phase E — Observability & Continuous Improvement
**Target: Data-driven quality improvement loop.**

| # | Task | Effort | Priority |
|---|------|--------|----------|
| E1 | Set up Azure Application Insights dashboard — daily active users, pass-through rate, route distribution, top rejected queries | 2 days | High |
| E2 | Weekly eval run — automate `python main.py eval` in CI (GitHub Actions) and alert on regressions | 1 day | High |
| E3 | Expand eval dataset to 60 cases — add factual accuracy, salary_career, honest_guidance, job_search categories | 2 days | Medium |
| E4 | Monthly KB freshness review — check cert costs/exam updates against official sources, update markdown + re-embed | Ongoing | Medium |
| E5 | Thumbs-down analysis — monthly review of flagged responses, update KB or agent prompts accordingly | Ongoing | Medium |
| E6 | A/B eval: test prompt changes against baseline score before deploying | 2 days | Low |

---

## 5. Technology Stack

### Current (Keep)
| Component | Technology |
|---|---|
| LLM provider | Anthropic (direct API, not Azure Foundry) |
| Orchestration / routing | claude-haiku-4-5-20251001 |
| Specialist agents | claude-sonnet-4-6 |
| Agent framework | Microsoft `agent-framework-anthropic` |
| API layer | FastAPI |
| Auth | Azure AD B2C |
| Deployment | Azure Container Apps |

### Add for Production
| Component | Technology | Reason |
|---|---|---|
| Semantic search | Azure AI Search (vector + BM25 hybrid) | Best-in-class hybrid retrieval; already in Azure ecosystem |
| Embeddings | Azure OpenAI `text-embedding-3-small` | Low cost, fast, high quality |
| Session store | Azure Cache for Redis | Persistent, shared across instances, TTL built-in |
| Rate limiting | `slowapi` (FastAPI middleware) | Simple, per-user throttling without external infra |
| Audit logging | Azure Application Insights | Structured, queryable, integrates with Azure Monitor |
| Injection pre-filter | Python `re` (regex) — no new dep | Zero latency, no LLM cost, catches obvious attacks |

### Considered & Not Recommended
| Technology | Why Not |
|---|---|
| Azure Content Safety API | Adds latency and cost per turn; our LLM safety agent + regex pre-filter is sufficient for this domain |
| Azure OpenAI GPT-4o | More expensive than Anthropic direct; no benefit for this use case |
| LangChain / LlamaIndex | Framework overhead; current custom pipeline is clean and well-understood |
| Pinecone / Weaviate | Azure AI Search is already in the ecosystem and handles hybrid search well |

---

## 6. Quality & Controls

### Defense-in-Depth Model

```
Request                    Control Layer                        Action on Trigger
─────────────────────────────────────────────────────────────────────────────────
Incoming HTTP      →  Rate limiter (API Management / slowapi)  → 429 Too Many Requests
Authenticated?     →  Azure AD B2C JWT validation              → 401 Unauthorized
Message text       →  Regex pre-filter (fast, no LLM)          → Instant reject
Message text       →  Safety Agent (Haiku LLM, fail-closed)    → Canned rejection message
Route chosen       →  Confidence threshold (≥ 0.5)             → Fall back to "general"
Agent response     →  Audit log (every turn)                   → No action, observability
Response text      →  No PII logging (no names/emails in logs) → Compliance
```

### Honest Advice Commitment

The advisor is explicitly instructed to:
- Recommend the **best cert for the user's goal**, not the most popular or most expensive
- Acknowledge when **web search is needed** for current salary/job data
- State **experience requirements clearly** (including waivers)
- Say **"I don't know"** rather than hallucinate cert details
- Not oversell ISACA certifications over better alternatives for a given goal

This is a core differentiator from generic AI chatbots. It must be preserved in all agent prompt updates.

### Content Boundaries

| Topic | Policy |
|---|---|
| Cybersecurity cert advice | Always allowed |
| Career path guidance | Always allowed |
| Resume and salary questions | Always allowed |
| Current job postings | Allowed via web_search |
| General IT career questions | Allowed (borderline safe) |
| Coding help / writing code | Rejected (off-topic) |
| Political / social topics | Rejected (off-topic) |
| Prompt injection attempts | Rejected (injection) |
| Questions about illegal activity | Rejected (injection/off-topic) |

---

## 7. Success Metrics

### Quality Metrics (Eval Suite)
| Metric | Current | Target |
|---|---|---|
| Eval pass rate (all categories) | 100% on 15 tested | ≥ 90% on 60 cases |
| Avg eval score | ~0.85 | ≥ 0.80 |
| Hard rule failures | 0 | 0 |
| Factual accuracy (must_include) | 100% | 100% |

### Reliability Metrics
| Metric | Target |
|---|---|
| Safety agent block rate (injections) | > 99% of injections caught |
| False positive rate (safe queries blocked) | < 1% |
| API error rate | < 0.5% |
| P95 response latency | < 8 seconds |

### User Engagement (once live)
| Metric | Target |
|---|---|
| Thumbs-up rate | ≥ 80% |
| Session length (turns per session) | ≥ 3 (indicates value) |
| Return user rate (30-day) | ≥ 40% |
| Blocked query rate | < 5% (high = safety too aggressive) |

---

## Build Order Summary

| Phase | Focus | Gate to Next Phase |
|---|---|---|
| **A — Hardening** | Abuse controls, fail-closed safety, rate limiting, audit logs | All A tasks done; adversarial tests pass |
| **B — Knowledge** | Vector search, expand cert DB, move salary data to file | Full eval suite ≥ 90% pass |
| **C — Sessions** | Redis session store, conversation summarization | Sessions persist across restart |
| **D — UI** | Web chat, Azure AD B2C, user feedback | Real user can log in and chat |
| **E — Observability** | Dashboards, CI eval, KB refresh process | Weekly eval runs automated |

**Phases A and B can run in parallel** — they don't share files.
**Phase C** depends on B (session store needs to be in place before scaling).
**Phase D** depends on C (UI needs persistent sessions to work well).
**Phase E** runs alongside D and beyond.

---

*Document generated 2026-02-21. Review when architecture changes significantly.*
