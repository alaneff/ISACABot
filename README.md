# Agentic Pipeline Factory

A reusable scaffolding for building and deploying AI agentic pipelines in Azure,
powered by Claude (Anthropic) and the Microsoft Agent Framework.

---

## Table of Contents

1. [What this is](#what-this-is)
2. [Prerequisites](#prerequisites)
3. [First-time setup](#first-time-setup)
4. [Running your first pipeline](#running-your-first-pipeline)
5. [Project structure explained](#project-structure-explained)
6. [Building a new pipeline](#building-a-new-pipeline)
7. [Claude model options](#claude-model-options)
8. [Deploying to Azure](#deploying-to-azure)
9. [Troubleshooting](#troubleshooting)

---

## What this is

This repo is a **starting point**, not a finished product. The idea is:

- Every new AI project starts by copying this repo.
- The scaffolding handles the boilerplate (config, agent creation, logging, Docker).
- You focus on writing the actual pipeline logic.

The example included is a **research pipeline**: ask a question, Claude searches the web and returns a structured summary.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11–3.14 | [python.org](https://www.python.org/downloads/) — **install from python.org, not the Microsoft Store** |
| pip | latest | comes with Python |
| Docker Desktop | latest | [docker.com](https://www.docker.com/products/docker-desktop/) — optional, for Azure deploy |
| Azure CLI | latest | [learn.microsoft.com/cli/azure](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) — optional |
| Anthropic API key | — | [console.anthropic.com](https://console.anthropic.com/) → API Keys |

---

## First-time setup

### 1. Create your .env file

Copy the example config and fill in your API key:

```bash
cp .env.example .env
```

Open `.env` and set your key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Everything else in `.env` has defaults that work out of the box.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs the Microsoft Agent Framework, the Anthropic SDK, and supporting libraries.

### 4. Verify everything works

```bash
python main.py verify
```

Expected output:
```
Verifying environment...
  Model   : claude-sonnet-4-6
  Thinking: disabled
  API test: OK

Environment OK.
```

If you see an error here, check [Troubleshooting](#troubleshooting).

---

## Running your first pipeline

The included example is the **research pipeline**. It takes a question,
searches the web, and returns a structured summary.

```bash
python main.py research "What is Azure Container Apps and when should I use it?"
```

You can also run the pipeline file directly:

```bash
python pipelines/examples/research_pipeline.py "What is Azure Container Apps?"
```

To see all available pipelines:

```bash
python main.py --help
```

---

## Project structure explained

```
agentic-pipeline-factory/
│
├── .env.example          Your secrets template — copy to .env
├── .env                  Your actual secrets — never commit this
├── requirements.txt      Python dependencies
├── main.py               CLI entrypoint — runs any pipeline by name
│
├── config/
│   └── settings.py       All config in one place. Import `settings` anywhere.
│
├── agents/
│   ├── base.py           create_agent() factory — use this to make all agents
│   └── examples/
│       └── research_agent.py   Example: agent with web search
│
├── tools/
│   └── common.py         Reusable tool functions (datetime, file write, etc.)
│
├── workflows/
│   ├── base.py           run_sequential(), run_parallel(), run_with_retry()
│   └── examples/
│       └── research_workflow.py  Example: researcher → summarizer chain
│
├── pipelines/
│   └── examples/
│       └── research_pipeline.py  Example: full pipeline with structured output
│
├── Dockerfile            Container definition for Azure deployment
└── docker-compose.yml    Local container testing
```

### The four layers

Think of the project in four layers, each building on the one below:

```
[ Pipeline ]   ← top-level entry point, structured input/output
    ↓
[ Workflow ]   ← orchestrates multiple agents (sequential, parallel, graph)
    ↓
[ Agent ]      ← single Claude instance with a role and tools
    ↓
[ Tool ]       ← Python function Claude can call
```

A **pipeline** is what gets triggered (by CLI, HTTP, Azure queue, etc.).
A **workflow** coordinates the agents needed to fulfill the pipeline's goal.
An **agent** is one focused Claude instance — give it a clear single responsibility.
A **tool** is a function Claude can invoke during its reasoning.

---

## Building a new pipeline

Follow these steps to add a pipeline for a new use case.

### Step 1 — Define your tools (if needed)

Add functions to `tools/common.py` or create a new file in `tools/`:

```python
from agent_framework import tool
from typing import Annotated

@tool(approval_mode="never_require")   # safe read-only tool
def lookup_customer(
    customer_id: Annotated[str, "The customer ID to look up."],
) -> str:
    """Look up a customer record by ID and return their details."""
    # your logic here
    return f"Customer {customer_id}: ..."
```

**Approval modes:**
- `"never_require"` — Claude calls it automatically (use for safe, read-only operations)
- `"always_require"` — Claude pauses and asks a human before calling (use for writes, sends, deletes)

### Step 2 — Create your agents

Add a file to `agents/` or use the factory directly in your workflow:

```python
from agents.base import create_agent
from tools.common import lookup_customer

support_agent = create_agent(
    name="SupportAgent",
    instructions=(
        "You are a customer support specialist. "
        "Look up the customer, then answer their question clearly and briefly."
    ),
    tools=[lookup_customer],
)
```

**Tip:** Give each agent a single, focused job. Two specialized agents outperform one generalist agent.

### Step 3 — Create your workflow

Add a file to `workflows/`:

```python
from workflows.base import run_sequential
from agents.base import create_agent

class SupportWorkflow:
    def __init__(self):
        self._agent = create_agent(name="SupportAgent", instructions="...")

    async def run(self, customer_id: str, question: str) -> str:
        prompt = f"Customer ID: {customer_id}\nQuestion: {question}"
        return await run_sequential([
            (self._agent, prompt),
        ])
```

For multi-agent chains, pass `"{previous}"` to inject the previous agent's output:

```python
await run_sequential([
    (researcher,  "Research this topic: {query}"),
    (summarizer,  "Summarize these findings:\n\n{previous}"),
    (formatter,   "Format this as a report:\n\n{previous}"),
])
```

### Step 4 — Create your pipeline

Copy `pipelines/examples/research_pipeline.py` and modify it:

```python
from dataclasses import dataclass, field
from datetime import UTC, datetime
from config.settings import settings

@dataclass
class PipelineResult:
    query: str
    answer: str
    pipeline_name: str = "SupportPipeline"
    model: str = field(default_factory=lambda: settings.model)
    completed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    success: bool = True
    error: str | None = None

class SupportPipeline:
    def __init__(self):
        self._workflow = SupportWorkflow()

    async def run(self, query: str) -> PipelineResult:
        try:
            answer = await self._workflow.run(query)
            return PipelineResult(query=query, answer=answer)
        except Exception as e:
            return PipelineResult(query=query, answer="", success=False, error=str(e))
```

### Step 5 — Register it in main.py

Open `main.py` and add your pipeline to the registry:

```python
PIPELINE_REGISTRY = {
    "research": "pipelines.examples.research_pipeline.ResearchPipeline",
    "support":  "pipelines.examples.support_pipeline.SupportPipeline",   # add this
}
```

Now you can run it:

```bash
python main.py support "Customer ID 12345 is asking about their invoice"
```

---

## Claude model options

Set `ANTHROPIC_MODEL` in your `.env` file.

| Model | Use when |
|---|---|
| `claude-sonnet-4-6` | Default — best balance of speed and quality |
| `claude-opus-4-6` | Complex reasoning, long documents, hard problems |
| `claude-haiku-4-5-20251001` | Simple classification, fast cheap steps in a pipeline |

To use extended thinking (Claude shows its reasoning before answering):

```
EXTENDED_THINKING=true
THINKING_BUDGET_TOKENS=5000
```

Extended thinking improves quality on complex multi-step tasks but uses more tokens.

You can also override the model for a single agent without changing the global default:

```python
heavy_agent = create_agent(
    name="Analyzer",
    instructions="...",
    model="claude-opus-4-6",   # only this agent uses Opus
)
```

---

## Deploying to Azure

### Build and test the container locally

```bash
docker compose up
```

### Deploy to Azure Container Apps

1. Log in to Azure:
```bash
az login
```

2. Create a resource group (first time only):
```bash
az group create --name my-resource-group --location eastus
```

3. Build and push the container image:
```bash
az acr create --resource-group my-resource-group --name mypipelineregistry --sku Basic
az acr build --registry mypipelineregistry --image agentic-pipeline-factory:latest .
```

4. Deploy as a Container App:
```bash
az containerapp create \
  --name my-pipeline-app \
  --resource-group my-resource-group \
  --image mypipelineregistry.azurecr.io/agentic-pipeline-factory:latest \
  --secrets anthropic-key=your-key-here \
  --env-vars ANTHROPIC_API_KEY=secretref:anthropic-key \
             ANTHROPIC_MODEL=claude-sonnet-4-6
```

**Important:** Pass `ANTHROPIC_API_KEY` as a secret, not a plain environment variable, so it doesn't appear in logs.

---

## Troubleshooting

### `ANTHROPIC_API_KEY is not set`
You haven't created a `.env` file yet, or the key is blank.
```bash
cp .env.example .env
# then edit .env and add your key
```

### `ModuleNotFoundError: No module named 'agent_framework'`
Your virtual environment is not activated, or you haven't installed dependencies.
```bash
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### `AuthenticationError` from Anthropic
Your API key is invalid or has no credits. Check at [console.anthropic.com](https://console.anthropic.com/).

### Agent returns empty or truncated output
The response hit the `MAX_TOKENS` limit. Increase it in `.env`:
```
MAX_TOKENS=16000
```

### Extended thinking error
Extended thinking requires `MAX_TOKENS > THINKING_BUDGET_TOKENS`.
If `THINKING_BUDGET_TOKENS=5000`, set `MAX_TOKENS` to at least `9000`.
The `settings.py` auto-corrects this, but explicit values in `.env` override it.
