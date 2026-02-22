# ISACA San Diego — Career Advisor Chatbot

An AI-powered career and certification advisor for ISACA San Diego members.
Ask it about cybersecurity certifications, career paths, resumes, salaries, and the job market.

Built on the **Agentic Pipeline Factory** — a reusable scaffolding for multi-agent AI pipelines in Azure.

---

## What it does

The ISACA SD advisor helps cybersecurity professionals:

- **Understand certifications** — costs, prerequisites, exam details, study resources for 200+ certs
- **Plan career paths** — honest timelines, experience requirements, what cert to pursue next
- **Improve their resume** — how to position certs and experience for specific roles in San Diego
- **Navigate the job market** — who's hiring, what skills are in demand, realistic salary ranges

It recommends the **best cert for your goal** — not just ISACA certs. If CompTIA, SANS, or CISSP is a better fit, it says so.

---

## Quick Start

### Prerequisites

| Tool | Required |
|---|---|
| Python 3.11–3.14 | Yes |
| Anthropic API key | Yes — [console.anthropic.com](https://console.anthropic.com/) |
| Docker Desktop | Optional (for Azure deploy) |

### Setup

```bash
# Clone and enter the project
git clone https://github.com/alaneff/ISACABot.git
cd ISACABot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and set: ANTHROPIC_API_KEY=sk-ant-your-key-here

# Verify everything works
python main.py verify
```

### Run the chatbot

```bash
python main.py isaca-sd
```

You'll enter an interactive chat session:

```
You: What certification should I get if I want to move into GRC?
Advisor: For GRC, the primary cert ladder is Security+ → CRISC...
```

Type `exit` or `quit` to end the session.

---

## Architecture

The advisor uses a hidden multi-agent pipeline. Every message goes through three layers:

```
User message
    │
    ▼  Regex pre-filter (instant — no LLM cost)
    │  Blocks obvious injection attempts (12 patterns)
    │
    ▼  Safety Agent  (Haiku — ~100ms)
    │  LLM classifier: safe / injection / off_topic
    │  Fail-CLOSED — rejects on any error
    │
    ▼  Orchestrator  (Haiku — ~100ms)
    │  Routes to the best specialist agent
    │  Falls back to "general" if confidence < 0.5
    │
    ▼  Specialist Agent  (Sonnet)
    ├── General    — cert advice, comparisons, overviews
    ├── Research   — deep cert details, exam prep, study plans
    ├── Career     — path planning, realistic timelines, what to do next
    ├── Resume     — positioning, formatting, salary context
    └── Job Search — current openings, who's hiring, market data
```

Users never see the routing. They ask questions and get focused, expert answers.

Every turn is audit-logged (route taken, safety result, success — no message content).

### Knowledge Base

The advisor has structured knowledge on **30 certs** (detailed) and can answer basic questions about **211 additional certs** from the Paul Jerimy Security Certification Roadmap:

| Category | Certs with Detailed KB Files |
|---|---|
| ISACA | CISA, CISM, CRISC, CGEIT, CDPSE, CSX-P |
| (ISC)² | CISSP, CCSP |
| CompTIA | Security+, CySA+, A+, Network+, PenTest+, CASP+ |
| SANS/GIAC | GSEC, GCIH, GPEN, GWAPT |
| Microsoft | AZ-500, SC-200, SC-100 |
| Offensive | OSCP, PNPT |
| Cisco | CCNA |
| IIA | CIA |
| IAPP | CIPP/E, CIPP/US |
| ISO | ISO 27001 Lead Auditor/Implementer |

Career paths covered: IT Audit, GRC, CISO Track, Cybersecurity Analyst.

---

## Running the eval suite

The project includes a 30-case evaluation suite to measure knowledge quality:

```bash
python main.py eval                         # full suite (uses API credits)
python main.py eval --filter entry_level    # filter by category
python main.py eval --verbose               # show scores per question
```

Current results: 100% pass rate on tested categories.

---

## Project structure

```
ISACABot/
│
├── main.py                   CLI entrypoint — runs any pipeline by name
├── requirements.txt
├── PROJECT_PLAN.md           Architecture and phased roadmap
│
├── isaca_sd/                 ISACA SD chatbot (the main application)
│   ├── agents/
│   │   ├── isaca_sd_agent.py   General advisor
│   │   ├── orchestrator.py     Route classifier (Haiku)
│   │   ├── career_coach.py     Career path planning
│   │   ├── resume_agent.py     Resume and salary advice
│   │   ├── research_agent.py   Deep cert research
│   │   └── job_search_agent.py Job market and openings
│   ├── tools/
│   │   ├── cert_facts.py       Structured data for 30 certs (prereqs, costs, exam details)
│   │   └── knowledge_base.py   Keyword search across markdown KB files
│   ├── pipelines/
│   │   └── isaca_sd_pipeline.py  Multi-agent pipeline with safety, routing, audit logging
│   ├── filters/
│   │   └── injection_filter.py   Regex pre-filter (12 patterns, no LLM cost)
│   ├── evals/
│   │   ├── dataset.json          30 evaluation cases
│   │   └── run_eval.py           Evaluation runner with concurrency control + 429 retry
│   └── knowledge/
│       ├── cert-index.json       211 certs (Paul Jerimy roadmap)
│       ├── salary-data.json      San Diego salary ranges by role (2025/2026)
│       └── certs/                Detailed markdown files (30 certs across 10 categories)
│
├── agents/                   Generic scaffolding — reusable across projects
│   ├── base.py               create_agent() factory
│   ├── safety_agent.py       Haiku safety classifier (fail-closed)
│   └── quality_agent.py      Haiku output quality reviewer
│
├── workflows/
│   ├── base.py               run_sequential(), run_parallel(), run_with_retry()
│   └── multi_agent.py        run_with_safety(), run_orchestrated()
│
├── config/
│   └── settings.py           All config in one place — reads from .env
│
└── api/                      FastAPI layer (in progress — see PROJECT_PLAN.md Phase D)
    └── app.py                REST API with Azure AD B2C auth + rate limiting
```

---

## Building a new pipeline

The `agents/`, `workflows/`, and `config/` directories are generic scaffolding — reusable for any pipeline project. The ISACA SD chatbot (`isaca_sd/`) is the first application built on top.

To add a new pipeline:

1. Create a package (e.g., `my_project/`) following the `isaca_sd/` structure
2. Create your agents using `create_agent()` from `agents/base.py`
3. Create your pipeline class in `my_project/pipelines/`
4. Register it in `main.py`:

```python
PIPELINE_REGISTRY = {
    "research":   "pipelines.examples.research_pipeline.ResearchPipeline",
    "isaca-sd":   "isaca_sd.pipelines.isaca_sd_pipeline.ISACASdPipeline",
    "my-project": "my_project.pipelines.my_pipeline.MyPipeline",  # add this
}
```

See the [research pipeline](pipelines/examples/research_pipeline.py) for a minimal single-agent example.

### The four layers

```
[ Pipeline ]   top-level entry point — structured input/output, error handling
    ↓
[ Workflow ]   orchestrates multiple agents (sequential, parallel, graph)
    ↓
[ Agent ]      single Claude instance with a role and tools
    ↓
[ Tool ]       Python function Claude can call during its reasoning
```

### Creating agents

```python
from agents.base import create_agent
from tools.common import my_tool

agent = create_agent(
    name="MyAgent",
    instructions="You are a specialist in...",
    tools=[my_tool],
)
```

Tools use `@tool(approval_mode="never_require")` for safe read-only operations or
`@tool(approval_mode="always_require")` for writes/sends/deletes that need human approval.

---

## Claude model options

Set `ANTHROPIC_MODEL` in your `.env` file.

| Model | ID | Use when |
|---|---|---|
| Sonnet 4.6 | `claude-sonnet-4-6` | Default — specialist agents |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Fast/cheap steps: routing, safety, grading |
| Opus 4.6 | `claude-opus-4-6` | Complex reasoning tasks |

---

## Deploying to Azure

### Test locally with Docker

```bash
docker compose up
```

### Deploy to Azure Container Apps

```bash
az login
az group create --name isaca-sd-rg --location westus2
az acr create --resource-group isaca-sd-rg --name isacasdregistry --sku Basic
az acr build --registry isacasdregistry --image isaca-sd:latest .

az containerapp create \
  --name isaca-sd-app \
  --resource-group isaca-sd-rg \
  --image isacasdregistry.azurecr.io/isaca-sd:latest \
  --secrets anthropic-key=your-key-here \
  --env-vars ANTHROPIC_API_KEY=secretref:anthropic-key \
             ANTHROPIC_MODEL=claude-sonnet-4-6
```

Pass `ANTHROPIC_API_KEY` as a secret, not a plain env var, so it doesn't appear in logs.

---

## Troubleshooting

### `ANTHROPIC_API_KEY is not set`
```bash
cp .env.example .env
# edit .env and add your key
```

### `ModuleNotFoundError: No module named 'agent_framework'`
```bash
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### `AuthenticationError` / 401 from Anthropic
API key invalid or no credits. Check at [console.anthropic.com](https://console.anthropic.com/).

### Rate limited (429) during eval
The eval suite uses `asyncio.Semaphore(2)` with automatic 20/40/60s backoff retry.
If you hit limits frequently, add API credits or run with `--filter` to test a subset.

### Agent returns empty or truncated output
Increase the token limit in `.env`:
```
MAX_TOKENS=16000
```
