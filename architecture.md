# Agentic Pipeline Factory — Architecture

## ISACA SD Bot: Multi-Agent Pipeline

```mermaid
flowchart TD
    USER([User]) -->|message| PIPE

    subgraph PIPE["ISACASdPipeline  (isaca_sd/pipelines/isaca_sd_pipeline.py)"]
        direction TB

        SAFE["Safety Agent
        claude-haiku-4-5
        agents/safety_agent.py"]

        ORCH["Orchestrator / Router
        claude-haiku-4-5
        isaca_sd/agents/orchestrator.py"]

        subgraph SPEC["Specialist Agents  (claude-sonnet-4-6)"]
            direction LR
            GA["General\nAdvisor"]
            RA["Resume\nAgent"]
            CA["Career\nCoach"]
            RE["Research\nAgent"]
            JA["Job Search\nAgent"]
        end

        SAFE -->|"safe"| ORCH
        SAFE -->|"unsafe / injection"| REJ

        ORCH -->|"general"| GA
        ORCH -->|"resume"| RA
        ORCH -->|"career"| CA
        ORCH -->|"research"| RE
        ORCH -->|"job_search"| JA
    end

    REJ([Rejection Message]) --> USER
    PIPE --> RESP([Response]) --> USER

    subgraph TOOLS["Tools"]
        direction LR
        CF["get_cert_facts()
        CERT_DB: 15 certs"]
        KB["search_knowledge_base()
        35 MD files + 211-cert JSON index"]
        WEB["web_search()"]
    end

    GA & RA & CA & RE --> CF
    GA & RA & CA & RE --> KB
    RA & RE & JA --> WEB
```

### Tool Access by Agent

| Agent | get_cert_facts | search_knowledge_base | web_search |
|---|:---:|:---:|:---:|
| General Advisor | Yes | Yes | Yes |
| Resume Agent | Yes | Yes | Yes |
| Career Coach | Yes | Yes | — |
| Research Agent | Yes | Yes | Yes |
| Job Search Agent | — | — | Yes |

---

## Knowledge Base Structure

```mermaid
flowchart LR
    subgraph KB["isaca_sd/knowledge/"]
        direction TB

        subgraph MD["Markdown Files  (35 files, 299 chunks)"]
            direction TB
            ISACA["ISACA Certs
            cisa · cism · crisc · cgeit · csx-p · cdpse"]
            ISC2["ISC2 Certs
            cissp · sscp"]
            COMP["CompTIA
            sec+ · csa+ · pentest+ · casp+ · a+ · net+"]
            CLOUD["Cloud & Microsoft
            aws-sec · az-sec · sc-200 · sc-100"]
            OFF["Offensive / Forensics
            oscp · ceh · pnpt"]
            SANS["SANS/GIAC
            gsec · gcih · gpen · gwapt"]
            PRIV["Privacy / Audit
            cipp-e · cipp-us · cia · iso27001-la"]
            CISCO["Cisco
            ccna"]
            CP["Career Paths
            grc · it-audit · ciso-track · cyber-analyst"]
        end

        CI["cert-index.json
        211 certs (Paul Jerimy roadmap)
        Network · IAM · Cloud · GRC · Offensive · Forensics · SOC"]
    end

    KB --> KBT["search_knowledge_base()
    Keyword index + token scoring
    2x boost for abbreviation match"]
```

---

## Generic Scaffolding Layer

```mermaid
flowchart LR
    subgraph SCAFFOLD["Generic Scaffolding  (reusable across projects)"]
        direction TB

        subgraph AG["agents/"]
            BASE["base.py
            create_agent()
            create_thinking_agent()
            create_client()"]
            SAF["safety_agent.py
            create_safety_agent()
            run_safety_check()
            → (is_safe, reason)"]
            QUA["quality_agent.py
            create_quality_agent()
            run_quality_check()
            → (passed, score, issues)"]
        end

        subgraph WF["workflows/"]
            WFBASE["base.py
            run_sequential()
            run_parallel()
            run_with_retry()"]
            WFMA["multi_agent.py
            run_with_safety()
            run_orchestrated()"]
        end

        subgraph CFG["config/"]
            SET["settings.py
            All config from .env
            Import everywhere"]
        end
    end

    SCAFFOLD --> ISACASD["ISACA SD Bot
    (isaca_sd/ package)"]
    SCAFFOLD -.->|"future projects"| FUT["Other Pipelines
    (research, ticketing, etc.)"]
```

---

## Deployment Target

```mermaid
flowchart LR
    CLI["CLI
    python main.py isaca-sd"] --> PIPE
    API["FastAPI
    api/ + Azure AD B2C auth"] --> PIPE

    PIPE["ISACASdPipeline"] --> ANT["Anthropic API
    (direct, not Azure Foundry)"]

    PIPE -.->|"future"| ACA["Azure Container Apps"]
```
