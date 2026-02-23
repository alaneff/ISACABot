# ISACA San Diego — Chatbot Project Plan

**Goal:** Build a high-quality, trustworthy AI advisor that helps ISACA SD members learn about
cybersecurity certifications, advance their careers, and find employment — with strong controls
to prevent abuse.

**Date:** 2026-02-21
**Status:** Phase A complete. Phase B1/B2 complete. Phase D1/D2/D3 + E2 complete. See roadmap below for current task status.

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
| REST API | ✓ Working | `api/app.py` — full pipeline behind `/api/chat` |
| Web chat UI | ✓ Working | `api/static/index.html` — served at `/` by FastAPI |
| Beta auth (API key) | ✓ Working | `X-API-Key` header; set `API_KEY` in `.env` |
| CI eval (GitHub Actions) | ✓ Working | Weekly on Mondays; fails on regression below 90% |

### What Is Missing or Fragile

| Gap | Severity | Status |
|---|---|---|
| Keyword-only RAG | High | Open — B3 deferred (cost/benefit; no measured retrieval failures) |
| In-memory sessions only | High | Open — Phase C |
| ~~No API rate limiting~~ | ~~High~~ | **Fixed (Phase A3)** — slowapi, 20 req/hr per authenticated user |
| ~~Hardcoded salary data in prompts~~ | ~~High~~ | **Fixed (Phase B2)** — `salary-data.json`, loaded at agent init |
| ~~Safety agent defaults to "safe" on failure~~ | ~~Medium~~ | **Fixed (Phase A2)** — fail-closed, rejects on any error |
| ~~No audit logging~~ | ~~Medium~~ | **Fixed (Phase A4)** — structured JSON log per turn (no PII) |
| ~~Orchestrator confidence score unused~~ | ~~Medium~~ | **Fixed (Phase A5)** — falls back to "general" if confidence < 0.5 |
| ~~get_cert_facts() DB has 15 of 35 certs~~ | ~~Medium~~ | **Fixed (Phase B1)** — expanded to 30 certs; 5 KB files still pending |
| No user feedback mechanism | Medium | Open — Phase D4 |
| ~~No web UI~~ | ~~Medium~~ | **Fixed (Phase D3)** — `api/static/index.html`, served at `/` |
| Static KB — no refresh process | Low | Open — Phase B5/E4 |
| Job search agent is web-only | Low | Open — acceptable for now |

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
**Status: COMPLETE**

| # | Task | Status |
|---|------|--------|
| A1 | Add regex pre-filter before safety agent — block `ignore.*instructions`, `you are now`, `DAN`, `jailbreak` etc. | **Done** — `isaca_sd/filters/injection_filter.py`, 12 patterns |
| A2 | Change safety agent to fail-CLOSED (default reject on error, not default safe) | **Done** — `agents/safety_agent.py` |
| A3 | Add `slowapi` rate limiting to FastAPI — 20 req/hr per authenticated user | **Done** — `api/app.py`, keyed on JWT `sub` |
| A4 | Add structured audit logging per turn — route taken, safety result, success | **Done** — `isaca_sd.audit` logger, JSON per turn, no PII |
| A5 | Add orchestrator confidence threshold — if confidence < 0.5, route to "general" | **Done** — `isaca_sd/agents/orchestrator.py` |
| A6 | Add graceful error responses — catch specialist agent exceptions, return user-friendly message | **Done** — `isaca_sd/pipelines/isaca_sd_pipeline.py` |

**Verified:** Adversarial inputs rejected by regex pre-filter before LLM call. Normal queries work normally.

---

### Phase B — Knowledge Quality
**Target: Accurate, complete, semantically searchable KB.**
**Status: B1 + B2 complete. B3/B4 deferred. B5/B6 open.**

| # | Task | Status |
|---|------|--------|
| B1 | Expand `get_cert_facts()` CERT_DB from 15 → 35 certs to match all KB markdown files | **Done (partial)** — expanded to 30 certs; 5 KB files still pending |
| B2 | Extract salary ranges from agent system prompts → move into `isaca_sd/knowledge/salary-data.json` | **Done** — JSON loaded at resume_agent init |
| B3 | Add Azure AI Search hybrid BM25 + vector search integration | **Deferred** — $74+/mo Basic tier not justified; no measured retrieval failures |
| B4 | Re-embed all cert files into Azure AI Search index | **Deferred** — depends on B3 |
| B5 | Write `scripts/refresh_kb.py` — re-chunk, re-embed, re-upload KB quarterly | Open |
| B6 | Add 10–15 more detailed cert markdown files: `gcfe.md`, `cfe.md`, `cissp-issap.md`, `ccsp.md`, `cloud+.md`, `cnd.md` | Open |

**Verify:** Run `python main.py eval` after B6 to confirm no regressions.

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
**Status: D1/D2/D3 complete (beta-ready). D4/D5/D6 open.**

| # | Task | Status |
|---|------|--------|
| D1 | Finalize FastAPI endpoints: `POST /chat`, `GET /health` | **Done** — `api/app.py` wired to `ISACASdPipeline._run_turn()` |
| D2 | Auth — ISACA SD member login | **Done (beta)** — API key mode (`X-API-Key`); Azure AD B2C ready for production when needed |
| D3 | Build minimal web chat UI | **Done** — `api/static/index.html`; served at `/`; `?key=` URL param for beta access |
| D4 | Add user feedback buttons (👍 / 👎) per response — log to App Insights | Open |
| D5 | Add "cite your source" — include KB chunk titles in response metadata | Open |
| D6 | Consider Microsoft Teams bot integration — ISACA SD may already use Teams | Open — Low priority |

**To run locally:**
```bash
# Set API_KEY in .env, then:
uvicorn api.app:app --reload
# Open: http://localhost:8000/?key=<API_KEY>
```

**Next gate:** Real beta users testing the bot and providing feedback.

---

### Phase E — Observability & Continuous Improvement
**Target: Data-driven quality improvement loop.**
**Status: E2 complete. E1/E3–E6 open.**

| # | Task | Status |
|---|------|--------|
| E1 | Set up Azure Application Insights dashboard — daily active users, pass-through rate, route distribution, top rejected queries | Open |
| E2 | Weekly eval run in CI — automate `python main.py eval`, fail on regression | **Done** — `.github/workflows/eval.yml`; runs Mondays; `--min-pass-rate 0.90` |
| E3 | Expand eval dataset to 60 cases — add factual accuracy, salary_career, honest_guidance, job_search categories | Open |
| E4 | Monthly KB freshness review — check cert costs/exam updates against official sources, update markdown | Ongoing |
| E5 | Thumbs-down analysis — monthly review of flagged responses, update KB or agent prompts accordingly | Open — depends on D4 |
| E6 | A/B eval: test prompt changes against baseline score before deploying | Open — Low priority |

---

## 5. Technology Stack

### Current (Deployed)
| Component | Technology | Notes |
|---|---|---|
| LLM provider | Anthropic direct API | Not Azure Foundry |
| Orchestration / routing | claude-haiku-4-5-20251001 | Safety agent + orchestrator |
| Specialist agents | claude-sonnet-4-6 | 5 specialists |
| Agent framework | Microsoft `agent-framework-anthropic` | |
| API layer | FastAPI + uvicorn | `api/app.py` |
| Auth (beta) | API key (`X-API-Key` header) | Set `API_KEY` in `.env` |
| Auth (production) | Azure AD B2C JWT (RS256) | Ready; needs B2C tenant config |
| Rate limiting | `slowapi` | 20 req/hr keyed on JWT sub or IP |
| Injection pre-filter | Python `re` (regex) | 12 patterns, zero LLM cost |
| Audit logging | Python `logging` (JSON per turn) | No PII; ready for App Insights sink |
| Web UI | Static HTML/JS | Served at `/` by FastAPI |
| CI eval | GitHub Actions | Weekly + manual; fails on regression |
| Deployment target | Azure Container Apps | Dockerfile ready |

### Still Needed for Production
| Component | Technology | Reason |
|---|---|---|
| Session store | Azure Cache for Redis | Persist sessions across restarts / instances |
| Observability | Azure Application Insights | Queryable audit logs, usage dashboards |
| Semantic search | Azure AI Search (vector + BM25 hybrid) | Deferred — no measured retrieval failures yet |

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
| Eval pass rate (all categories) | 100% on 15 tested (credit limit hit at 15/30) | ≥ 90% on 60 cases |
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

| Phase | Focus | Status |
|---|---|---|
| **A — Hardening** | Regex pre-filter, fail-closed safety, rate limiting, audit logs, error handling | **COMPLETE** |
| **B — Knowledge** | Expand cert DB (15→30), salary JSON, vector search (deferred) | **Partial** — B1/B2 done; B3 deferred; B5/B6 open |
| **C — Sessions** | Redis session store, conversation summarization | Not started |
| **D — UI** | Web chat, API/beta auth, user feedback | **Partial** — D1/D2/D3 done (beta-ready); D4/D5 open |
| **E — Observability** | Dashboards, CI eval, KB refresh process | **Partial** — E2 done; E1/E3–E6 open |

**Phase C** (Redis sessions) is the next critical path item — sessions currently reset on API restart.
**Phase D4/D5** (feedback + source citations) can follow C.
**Phase E** observability runs continuously alongside other phases.

---

*Document generated 2026-02-21. Last updated 2026-02-21 (Phase A + B1/B2 complete).*
