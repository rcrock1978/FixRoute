# PRD 15 — FixRoute

> **AI maintenance triage that classifies requests, troubleshoots, and dispatches the right vendor.**

| | |
|---|---|
| **Product ID** | MSP-15 |
| **Category** | Property Management |
| **Type** | AI-Powered Micro SaaS |
| **Complexity** | Intermediate |
| **Methodology** | Spec-Driven Development (SDD) |
| **Primary stack** | Django + Python AI services |
| **Status** | Draft v1.0 |
| **Owner** | Solution Architect (portfolio: Raymund) |
| **Last updated** | 2026-06-24 |


## 1. Coverage Map

This PRD is written for production-grade delivery. Each required focus area maps to a section:

| Focus area | Where addressed |
| --- | --- |
| Business Requirements | Section 2 |
| System Design | Section 5.1 |
| Clean Architecture | Section 5.2 |
| Domain-Driven Design (DDD) | Section 5.3 |
| CQRS | Section 5.4 |
| Application Services (CQRS) | Section 5.5 |
| Design Patterns | Section 5.6 |
| Event-Driven Architecture | Section 5.7 |
| Integration Patterns | Section 5.8 |
| Database Design | Section 6 |
| AI: LLMs / RAG / Agents / MCP / Vector DB / Memory / MLOps | Section 10 — AI Architecture |
| Web APIs | Section 11 |
| Performance Optimization | Section 13 |
| Security | Section 12 |
| Docker / Kubernetes / Cloud | Section 15 |
| CI/CD | Section 15.4 |
| Monitoring & Logging | Section 16 |
| Cost Optimization | Section 17 |
| Cross-Team Collaboration | Section 18 |
| Goals / Definition of Done | Section 21 |
| Agent Skills (skills.sh) | Section 8 |

## 2. Business Requirements

### 2.1 Problem
Property managers triage maintenance tickets manually, mis-prioritize emergencies, and dispatch the wrong trades.

### 2.2 Why now (2026)
2026 multimodal triage (photos + text) plus agents can auto-classify, self-serve troubleshoot, and dispatch.

### 2.3 Target users & personas
- Property manager
- Maintenance coordinator
- Tenant

### 2.4 Value proposition
Auto-triage every request, deflect simple fixes, and dispatch the right vendor with the right urgency.

### 2.5 Differentiator
Deflects simple fixes and matches the right trade with calibrated urgency, reducing truck rolls.

### 2.6 Business goals
1. Build working software that ships to real users, not a demo.
2. Build scalable software that grows from first customer to thousands of tenants.
3. Help teams deliver predictably via Spec-Driven Development and CI/CD.
4. Solve a real business problem: property managers triage maintenance tickets manually, mis-prioritize emergencies, and dispatch the wrong trades.
5. Build a system that learns — improving from feedback, evaluations, and usage over time.

### 2.7 Success metrics (KPIs)
- Time-to-dispatch
- Self-serve deflection rate
- Emergency mis-triage rate
- Maintenance spend per unit

### 2.8 Monetization
Per-unit-under-management subscription. This aligns with the 2026 shift to usage-based and hybrid pricing as autonomous features do measurable work.

### 2.9 Representative user stories
- As a **property manager**, I want **tenant intake (photo/text/voice)** so that I get measurable value with less manual effort.
- As a **property manager**, I want **ai classification + urgency scoring** so that I get measurable value with less manual effort.
- As a **property manager**, I want **self-serve troubleshooting** so that I get measurable value with less manual effort.
- As a **property manager**, I want **vendor matching + dispatch** so that I get measurable value with less manual effort.
- As a **property manager**, I want **cost estimate + approval flow** so that I get measurable value with less manual effort.
- As a **property manager**, I want **status updates to tenant** so that I get measurable value with less manual effort.


## 3. Product Scope

### 3.1 In scope (MVP)
- Tenant intake (photo/text/voice)
- AI classification + urgency scoring
- Self-serve troubleshooting
- Vendor matching + dispatch
- Cost estimate + approval flow
- Status updates to tenant
- Spend analytics

### 3.2 Out of scope (initial release)
- Native mobile apps beyond a responsive/PWA client (phase 2 unless noted).
- On-prem self-hosting in the MVP (cloud-first; revisit for enterprise).
- Languages/locales beyond the launch set (i18n-ready, not fully localized at MVP).

### 3.3 Build emphasis (engineering scope)
This product is a vehicle to demonstrate: **CRUD Applications, Web APIs, Intelligent System, Event Driven Architecture, Autonomous Solution**. Across the portfolio it also exercises CRUD, Web APIs, database design, scalable applications, microservices, distributed systems, end-to-end solution architecture, cross-team collaboration, and intelligent & autonomous systems.


## 4. Spec-Driven Development (SDD) Plan

This product is built **spec-first**: an executable specification — not ad-hoc prompting — is the source of truth, following the 2026 SDD practice popularized by GitHub Spec Kit, AWS Kiro, and the BMAD method. Tests, code, and docs are generated from and validated against the spec.

### 4.1 Spec artifacts (repo: `/spec`)
| Artifact | Purpose |
|---|---|
| `spec.md` | Intent, scope, personas, business rules, NFRs, constraints (this PRD distilled). |
| `plan.md` | Architecture decisions, bounded contexts, tech choices, milestone plan. |
| `tasks.md` | Decomposed, agent-executable tasks with acceptance criteria and traceability IDs. |
| `contracts/` | OpenAPI + event schemas + MCP tool schemas — the machine-readable contracts. |
| `evals/` | AI evaluation datasets and thresholds. |

### 4.2 SDD lifecycle
1. **Define intent** — capture the business problem and outcomes (Section 2).
2. **Remove ambiguity** — encode business rules and NFRs as testable statements.
3. **Plan with constraints** — Clean Architecture, DDD boundaries, NFRs (Sections 5–6).
4. **Implement with agents under oversight** — generate code/tests against `tasks.md`.
5. **Validate against the spec** — acceptance tests + AI evals gate every change in CI.

### 4.3 Sample acceptance criteria (executable specs)
- GIVEN a valid request to `SubmitWorkOrder` WHEN processed THEN the corresponding aggregate state changes and a `WorkOrderSubmitted` event is published.
- GIVEN insufficient permissions WHEN any command is issued THEN the API returns 403 and no state changes.
- GIVEN a `GetWorkOrder` request THEN results are returned within the performance budget (Section 13) and respect tenant isolation.
- GIVEN an AI-generated output THEN it includes grounding/citations where applicable and passes the evaluation guardrails (Section 10.7) before being surfaced.

### 4.4 Traceability
Every requirement has an ID (`REQ-MSP15-n`) referenced by tasks, code, tests, and eval cases, so coverage is auditable end to end.


## 5. System Design & Architecture

### 5.1 High-level system design
FixRoute is a **cloud-native, multi-tenant** system decomposed along bounded contexts. A Vue.js 3 SPA talks to an **API Gateway / BFF**, which routes to context-aligned Django (Python) services. A Python AI service hosts inference, RAG, and agents and is integrated through stable domain ports and MCP. Services communicate synchronously via REST/gRPC and asynchronously via a message bus using **integration events**. State changes are persisted transactionally and published reliably via the **outbox pattern**.

**Logical services / components**

| Service / component | Responsibility |
| --- | --- |
| Intake Service | Owns the Intake bounded context; exposes APIs and emits domain events. |
| Triage Service | Owns the Triage bounded context; exposes APIs and emits domain events. |
| Dispatch Service | Owns the Dispatch bounded context; exposes APIs and emits domain events. |
| Vendor Management Service | Owns the Vendor Management bounded context; exposes APIs and emits domain events. |
| Analytics Service | Owns the Analytics bounded context; exposes APIs and emits domain events. |
| AI/Inference Service (Python) | Hosts LLM orchestration, RAG, agents, and model serving; called via internal API/gRPC and MCP. |
| API Gateway / BFF | AuthN/Z, rate limiting, request routing, aggregation for the front-end. |

This satisfies the build goals of *microservices*, *distributed systems*, *scalable applications*, and *end-to-end solution architecture*.

### 5.2 Clean Architecture
The codebase follows Clean Architecture with strict dependency rules (dependencies point inward):

- **Domain** — entities, value objects, aggregates, domain events, and business rules. No framework dependencies.
- **Application** — use cases as service-layer commands/queries, ports (interfaces), DTOs, validators.
- **Infrastructure** — Django ORM, message bus, caching, external/AI adapters implementing the ports.
- **Presentation (API)** — Django REST Framework views, gateway, authentication.

Module-boundary tests enforce layering so the architecture cannot silently erode.

### 5.3 Domain-Driven Design (DDD)
**Bounded contexts:** Intake, Triage, Dispatch, Vendor Management, Analytics.

**Aggregates & entities**

| Aggregate | Responsibility |
| --- | --- |
| WorkOrder | request + status |
| TriageResult | class + urgency |
| Vendor | trade + coverage |
| Dispatch | assignment + ETA |
| Property | units + portfolio |

**Ubiquitous language (selected terms):** Analytics, Dispatch, Intake, Property, Triage, TriageResult, Vendor, Vendor Management, WorkOrder.

Context boundaries become service and module boundaries; a context map documents upstream/downstream relationships and where Anti-Corruption Layers protect the domain from external models.

### 5.4 CQRS
Commands and queries are separated. Commands enforce invariants on aggregates and emit events; queries read from denormalized, cache-friendly read models (and, where load demands, a separate read store).

**Commands**

| Command | Type | Behavior |
| --- | --- | --- |
| SubmitWorkOrder | Command | Mutates state in the Intake context; validated, handled, emits event(s). |
| TriageWorkOrder | Command | Mutates state in the Triage context; validated, handled, emits event(s). |
| DispatchVendor | Command | Mutates state in the Dispatch context; validated, handled, emits event(s). |
| ApproveEstimate | Command | Mutates state in the Vendor Management context; validated, handled, emits event(s). |
| UpdateStatus | Command | Mutates state in the Analytics context; validated, handled, emits event(s). |

**Queries**

| Query | Type | Behavior |
| --- | --- | --- |
| GetWorkOrder | Query | Reads from optimized read model; no side effects; cacheable. |
| ListOpenByProperty | Query | Reads from optimized read model; no side effects; cacheable. |
| GetVendorMatches | Query | Reads from optimized read model; no side effects; cacheable. |
| GetSpendAnalytics | Query | Reads from optimized read model; no side effects; cacheable. |

### 5.5 Application Services (CQRS with Service Layer)
Application requests are mediated through a service layer, keeping views thin and use cases isolated and testable.

**Representative services**
- `WorkOrderService.submit()` — validates, loads aggregate, applies behavior, persists, publishes event.
- `TriageService.triage()` — validates, loads aggregate, applies behavior, persists, publishes event.
- `DispatchService.dispatch()` — validates, loads aggregate, applies behavior, persists, publishes event.
- `VendorService.approve_estimate()` — validates, loads aggregate, applies behavior, persists, publishes event.
- `AnalyticsService.update_status()` — validates, loads aggregate, applies behavior, persists, publishes event.

**Cross-cutting concerns (via Django middleware + decorators):**
- `ValidationMiddleware` — DRF serializer validation on every request.
- `LoggingMiddleware` — structured request/response logging with correlation IDs.
- `PerformanceMiddleware` — flags slow handlers against the budget.
- `TransactionMiddleware` — wraps command views in a DB transaction + outbox.
- `CacheMiddleware` — caches idempotent query results in Redis.
- `AiGuardrailMiddleware` — applies prompt-injection, PII, and output-safety checks around AI calls.

### 5.6 Design Patterns
- **CQRS** — separate command and query models and, where useful, stores.
- **Service Layer** — decouples views from application logic.
- **Repository + Unit of Work** — persistence abstraction over Django ORM.
- **Specification / Q** — composable, testable query/business rules.
- **Domain Events + Outbox** — reliable event publication with the transactional outbox pattern.
- **Factory / Builder** — construct complex aggregates and value objects.
- **Strategy** — pluggable algorithms (pricing, routing, scoring, ranking as applicable).
- **Middleware / Decorators** — cross-cutting concerns (validation, logging, caching, retries).
- **Circuit Breaker + Retry (tenacity)** — resilient calls to external/AI services.
- **Saga / Process Manager** — coordinate multi-step, cross-service workflows.
- **Adapter / Anti-Corruption Layer** — isolate LLM/provider SDKs behind stable domain ports.

### 5.7 Event-Driven Architecture (EDA)
The system is event-driven internally and at its boundaries.

**Domain events**
- `WorkOrderSubmitted` — domain event raised within a bounded context.
- `WorkOrderTriaged` — domain event raised within a bounded context.
- `VendorDispatched` — domain event raised within a bounded context.
- `EstimateApproved` — domain event raised within a bounded context.
- `WorkOrderClosed` — domain event raised within a bounded context.

**Integration events (published to the bus)**
- `WorkOrderSubmittedIntegrationEvent` — published to the bus for other services/consumers.
- `WorkOrderTriagedIntegrationEvent` — published to the bus for other services/consumers.
- `VendorDispatchedIntegrationEvent` — published to the bus for other services/consumers.
- `EstimateApprovedIntegrationEvent` — published to the bus for other services/consumers.

Events enable choreography between services, audit trails, and AI/ML feedback signals. Delivery uses the outbox pattern (exactly-once-effect), idempotent consumers, and a dead-letter queue for poison messages.

### 5.8 Integration Patterns
- **REST + OpenAPI** for synchronous external/internal APIs (versioned).
- **Async messaging** (integration events) for cross-service workflows and decoupling.
- **Webhooks** for inbound/outbound third-party event exchange (signed + idempotent).
- **Anti-Corruption Layer** wrapping each third-party integration: AppFolio/Buildium, Vendor marketplace APIs, SMS/email, Accounting export.
- **Model Context Protocol (MCP)** server/client to expose and consume tools for agents (Section 10.4).


## 6. Data & Database Design

### 6.1 Storage strategy
Primary operational store: **PostgreSQL + pgvector**. Reads use CQRS read models / materialized views; hot paths are cached in **Redis**. Each tenant's data is isolated (row-level security + tenant key on every table). Migrations are managed through Django's migration framework and run automatically in CI/CD with safe, backward-compatible changes.

### 6.2 Core entities (selected)
| Table / entity | Concern | Notes |
| --- | --- | --- |
| WorkOrder | Write model (normalized) | request + status |
| TriageResult | Write model (normalized) | class + urgency |
| Vendor | Write model (normalized) | trade + coverage |
| Dispatch | Write model (normalized) | assignment + ETA |
| Property | Write model (normalized) | units + portfolio |
| OutboxMessage | Reliability | Stores domain/integration events for transactional publication. |
| AuditLog | Compliance | Append-only record of security-relevant and state-changing actions. |
| Tenant | Multi-tenancy | Tenant registry; drives row-level isolation and routing. |

### 6.3 Vector & semantic store
Embeddings and semantic search use **pgvector over work-order history + guides**. Chunked content is stored with rich metadata (source, ACL, timestamps, version) to support filtered, hybrid retrieval (Section 10.2).

### 6.4 Data lifecycle & governance
Retention policies per data class, soft-delete with purge windows, encryption at rest, PII tagging, and per-tenant export/delete to satisfy GDPR/CCPA. Backups are automated with tested point-in-time restore.


## 7. Tech Stack

The recommended stack is **Django + Python AI services**, using a single consistent language across the entire backend while leveraging the strongest Python AI/ML ecosystem.

| Layer | Choice |
| --- | --- |
| Language / runtime | Python 3.12 (Django + AI services) |
| Web/API | Django + Django REST Framework |
| Persistence | PostgreSQL + pgvector via Django ORM |
| Caching | Redis |
| Messaging | Celery + RabbitMQ / Redis + transactional outbox |
| Auth | OpenID Connect (Entra ID / Auth0), RBAC/ABAC with django-guardian |
| Front-end | Vue.js 3 SPA (Vite, Pinia, Vue Router) |
| Task queue | Celery for async/background work |
| Containers/Orchestration | Docker + Kubernetes (AKS), Helm/Kustomize, Argo Rollouts |
| IaC | Terraform |
| CI/CD | GitHub Actions, cosign, SBOM |
| Observability | OpenTelemetry, structlog, Grafana/Azure Monitor |
| AI service | Python triage service (same runtime) |
| LLM orchestration | LangChain / LlamaIndex |
| Vector / search | pgvector over work-order history + guides |
| Model providers | Azure OpenAI / Anthropic / open models via an adapter; routing by cost & task |
| AI integration | MCP (server/client) + internal gRPC |
| MLOps/eval | Eval harness (Ragas-style), prompt/model registry, drift monitors |

## 8. Agent Skills (skills.sh)

Skills from [skills.sh](https://www.skills.sh) provide reusable, installable
capabilities for AI agents. The following skills are recommended for this
project, organized by domain.

Install with: `npx skills add <owner/repo>`

### Infrastructure & Azure

| Skill | Repo | Purpose |
|-------|------|---------|
| `azure-kubernetes` | `microsoft/azure-skills` | AKS cluster setup, node pools, scaling, networking |
| `azure-observability` | `microsoft/azure-skills` | OpenTelemetry, Azure Monitor, log analytics |
| `azure-reliability` | `microsoft/azure-skills` | HA, DR, backup, SLA design for Azure services |
| `azure-rbac` | `microsoft/azure-skills` | Role-based access control and identity management |
| `azure-cost-optimization` | `microsoft/azure-skills` | FinOps, reserved instances, right-sizing |
| `azure-ai` | `microsoft/azure-skills` | Azure AI Services, OpenAI, Cognitive Search |
| `azure-aigateway` | `microsoft/azure-skills` | API management, throttling, routing for AI endpoints |
| `azure-messaging` | `microsoft/azure-skills` | Service Bus, Event Grid, message broker patterns |
| `entra-app-registration` | `microsoft/azure-skills` | OIDC/OAuth2 app registration, SSO, token configuration |
| `appinsights-instrumentation` | `microsoft/azure-skills` | Application Insights telemetry and distributed tracing |
| `azure-compliance` | `microsoft/azure-skills` | SOC 2, GDPR, CCPA compliance guardrails on Azure |
| `azure-deploy` | `microsoft/azure-skills` | CI/CD deployment pipelines for Azure targets |
| `azure-storage` | `microsoft/azure-skills` | Blob Storage, disk encryption, lifecycle policies |

### Database

| Skill | Repo | Purpose |
|-------|------|---------|
| `supabase-postgres-best-practices` | `supabase/agent-skills` | PostgreSQL schema design, indexing, RLS, query performance |

### CI/CD

| Skill | Repo | Purpose |
|-------|------|---------|
| `github-actions-docs` | `xixu-me/skills` | GitHub Actions workflow patterns and troubleshooting |

### Frontend & Design

| Skill | Repo | Purpose |
|-------|------|---------|
| `frontend-design` | `anthropics/skills` | Frontend design patterns and visual polish |
| `web-design-guidelines` | `vercel-labs/agent-skills` | Spacing, typography, interaction, accessibility standards |
| `ui-ux-pro-max` | `nextlevelbuilder/ui-ux-pro-max-skill` | Advanced UI/UX patterns for complex interfaces |

### Testing

| Skill | Repo | Purpose |
|-------|------|---------|
| `test-driven-development` | `obra/superpowers` | Red-green-refactor TDD loop enforcement |
| `webapp-testing` | `anthropics/skills` | Unit, integration, and end-to-end test patterns |
| `verification-before-completion` | `obra/superpowers` | Verification pass before marking tasks done |

### Agent Workflows

| Skill | Repo | Purpose |
|-------|------|---------|
| `writing-plans` | `obra/superpowers` | Structured implementation plans before code |
| `executing-plans` | `obra/superpowers` | Step-by-step plan execution with checkpoints |
| `subagent-driven-development` | `obra/superpowers` | Orchestrate specialized subagents per task |
| `dispatching-parallel-agents` | `obra/superpowers` | Parallel work streams for independent components |
| `systematic-debugging` | `obra/superpowers` | Hypothesis-driven debugging loop |
| `requesting-code-review` | `obra/superpowers` | Self-review, test coverage, PR description prep |
| `finishing-a-development-branch` | `obra/superpowers` | Branch close checklist: tests, commit, PR, review |
| `find-skills` | `vercel-labs/skills` | Discover and install new skills mid-session |

### Marketing (SaaS)

| Skill | Repo | Purpose |
|-------|------|---------|
| `copywriting` | `coreyhaines31/marketingskills` | Product messaging and feature copy |
| `seo-audit` | `coreyhaines31/marketingskills` | SEO analysis and content optimization |

## 9. Build Scope Mapping

This product especially showcases: **CRUD Applications, Web APIs, Intelligent System, Event Driven Architecture, Autonomous Solution**.

| Build capability | How this product demonstrates it |
| --- | --- |
| CRUD Applications | Core entity management across the bounded contexts with validation and audit. |
| Web APIs | Versioned REST + OpenAPI; gRPC internally (Section 11). |
| Database Design | Normalized write models, CQRS read models, multi-tenant isolation (Section 6). |
| Scalable Applications | Stateless services + HPA + caching + async (Sections 12–14). |
| Microservices | Context-aligned services with independent deploy/scaling (Section 5.1). |
| Distributed Systems | Async messaging, outbox, sagas, idempotency, resilience (Sections 5.7, 13). |
| End to End Solutions | Front-end → API → domain → data → infra → CI/CD, fully delivered. |
| Solution Architect | Documented architecture, ADRs, context map, NFRs, and trade-offs. |
| Cross Team Collaboration | Contracts-first parallel delivery (Section 18). |
| Intelligent System | Grounded LLM/RAG features that adapt to data and feedback (Section 10). |
| Autonomous Solution | Agents that plan and act via tools/MCP with human-in-the-loop guardrails (Sections 9.3–9.4). |

## 10. AI Architecture

> Principle for this portfolio: **AI amplifies software engineering, it does not replace it.** FixRoute is a production-grade intelligent system, not a demo. *Better context beats bigger models.*


### 10.1 LLMs
Multimodal LLM for triage + troubleshooting. Models are accessed behind a provider-agnostic **Adapter/ACL** so we can route by task, cost, and latency, and fail over between providers. Prompt templates are versioned in `/spec/contracts`. Token budgets, max-context windows, and temperature are configured per use case. A small/cheap model handles routing, extraction, and classification; a frontier model handles complex generation.

### 10.2 RAG (Retrieval-Augmented Generation)
RAG is treated as **the product**, not a feature — an ecosystem of interconnected layers. Product-specific role: Retrieve property history + troubleshooting guides.

- **Query construction** — transform user intent into searchable context; combine relational, graph, and vector signals to improve precision.
- **Routing** — logical + semantic routing to the right knowledge source to cut unnecessary retrieval cost.
- **Indexing** — semantic chunking, multi-representation indexing, hierarchical indexing (RAPTOR), and advanced embeddings (hybrid / ColBERT-style late interaction).
- **Retrieval** — multi-stage pipeline with query refinement, re-ranking, and context optimization before generation.
- **Generation** — retrieval-aware prompting, active context selection, grounded answers with citations.
- **Evaluation** — measure retrieval quality and answer relevance/faithfulness, benchmark performance, and continuously improve (Section 10.7).

The competitive edge comes from knowledge quality, retrieval accuracy, context relevance, and the evaluation framework — not model choice alone.

### 10.3 AI Agents
Triage/dispatch agent with approval gates. The agent layer implements **tool calling**, **planning & reasoning**, **memory**, and (where useful) **multi-agent** collaboration. Tools are typed, permissioned, and observable; every tool call is logged with inputs/outputs for audit and evaluation. Agent autonomy is bounded by policies and human-in-the-loop checkpoints for high-impact actions.

### 10.4 MCP (Model Context Protocol)
MCP tools for vendor + dispatch MCP is the 2026 standard integration layer (adopted across major AI platforms), which lowers integration cost and makes capabilities reusable across agents.

**MCP tools (server surface)**

| Tool | Description |
| --- | --- |
| `classify_issue` | Tool exposed/consumed via MCP for agent use. |
| `match_vendor` | Tool exposed/consumed via MCP for agent use. |
| `create_dispatch` | Tool exposed/consumed via MCP for agent use. |
| `estimate_cost` | Tool exposed/consumed via MCP for agent use. |

Tools are schema-defined, authorized per tenant/scope, rate-limited, and audited.

### 10.5 Vector Databases
**pgvector over work-order history + guides** stores embeddings with metadata for filtered, hybrid (keyword + vector) search and re-ranking. Index lifecycle (build, refresh, compaction), embedding versioning, and backfills are automated. Retrieval respects tenant isolation and document-level ACLs.

### 10.6 AI Memory Systems
Unit/asset maintenance memory. Memory is layered: **short-term working memory** (per task/conversation), **episodic memory** (events and interactions), and **semantic memory** (durable facts/preferences). Memory writes are governed (what is stored, for how long, and with what consent) and are retrievable through the same RAG layer for grounding.

### 10.7 MLOps & Production AI
Triage-accuracy eval, urgency-calibration monitoring

- **Data pipelines** — ingestion, cleaning, chunking, and embedding jobs are versioned and reproducible.
- **Model/prompt registry** — versioned prompts, models, and configs with staged rollout.
- **Evaluation** — automated eval sets for relevance, faithfulness/grounding, and task success run in CI; no AI change ships without passing thresholds.
- **Guardrails** — prompt-injection defense, PII redaction, output moderation, and grounding checks (the `AiGuardrailBehavior`).
- **Observability** — trace every LLM/agent/tool call (tokens, cost, latency, outcome); see Section 16.
- **Drift detection** — monitor input/output distributions and quality KPIs; alert and trigger re-index/re-tune.
- **Human feedback loops** — capture accept/reject/edit signals to improve retrieval, prompts, and (where justified) fine-tuning.
- **Reliability & cost** — caching, batching, fallbacks, and budget caps (Sections 12 & 16).

## 11. Web API Design
RESTful, versioned (`/api/v1`), documented with OpenAPI (auto-generated via DRF Spectacular). JSON over HTTPS, cursor pagination, RFC 7807 problem-details errors, idempotency keys on commands, ETags on resources, and consistent rate-limit headers. An internal gRPC contract connects Django services to the Python AI service for low-latency inference.

**Representative endpoints**

| Method | Path | Kind | Notes |
| --- | --- | --- | --- |
| POST | /api/v1/submitWorkOrder | Command | Auth required; validated; idempotency-key supported. |
| POST | /api/v1/triageWorkOrder | Command | Auth required; validated; idempotency-key supported. |
| POST | /api/v1/dispatchVendor | Command | Auth required; validated; idempotency-key supported. |
| POST | /api/v1/approveEstimate | Command | Auth required; validated; idempotency-key supported. |
| POST | /api/v1/updateStatus | Command | Auth required; validated; idempotency-key supported. |
| GET | /api/v1/workorder | Query | Auth required; cacheable; paginated. |
| GET | /api/v1/openbyproperty | Query | Auth required; cacheable; paginated. |
| GET | /api/v1/vendormatches | Query | Auth required; cacheable; paginated. |
| GET | /api/v1/spendanalytics | Query | Auth required; cacheable; paginated. |

Webhooks (signed, versioned, retried) let customers subscribe to events such as `WorkOrderSubmitted`. An MCP server exposes the same capabilities to AI agents (Section 10.4).


## 12. Security
Security is designed in from day one (SOC 2 Type II and GDPR/CCPA readiness).

- **AuthN** — OIDC/OAuth2 (e.g., Microsoft Entra ID / Auth0); SSO + SCIM for enterprise; MFA.
- **AuthZ** — role- and attribute-based access control; per-tenant authorization enforced in the application layer.
- **Multi-tenant isolation** — tenant key on every row + row-level security; no cross-tenant data access by construction.
- **Secrets** — managed vault (Azure Key Vault / AWS Secrets Manager); no secrets in code or images.
- **Data protection** — TLS 1.2+ in transit, AES-256 at rest, field-level encryption for sensitive data, PII tagging.
- **API security** — input validation, output encoding, rate limiting, WAF, OWASP API Top 10 controls.
- **Auditability** — append-only audit log of security-relevant actions; tamper-evident.
- **Supply chain** — SCA/SAST/secret scanning and signed images in CI/CD; SBOM generated per build.
- **Prompt-injection & jailbreak defense** — input/output filtering, tool-permission scoping, and content provenance.
- **Data governance for AI** — retrieval respects ACLs; no training on customer data without explicit consent; PII redaction before model calls.
- **Output safety** — grounding/citation checks and moderation before AI output is shown or acted upon.


## 13. Performance Optimization
**Budgets:** API reads p95 < 200 ms, writes p95 < 400 ms, AI responses streamed with first-token < 1.5 s and grounded answer < 6 s.

- Multi-layer caching (Redis + HTTP/CDN) for hot queries; cache-aside with invalidation on events.
- CQRS read models / materialized views to avoid expensive joins on hot paths.
- Async, non-blocking I/O; bulk/batch operations; connection pooling; pagination everywhere.
- Database indexing strategy reviewed per query; N+1 prevention; query plans monitored.
- Back-pressure and queue-based load leveling for spiky/expensive work (including AI inference).
- AI-specific: prompt/result caching, embedding caching, response streaming, model routing (small model first), and batching of embeddings.


## 14. Scalability & Reliability
- **Stateless services** scale horizontally behind the gateway; sticky state externalized to data/cache.
- **Async workers** scale independently for inference, ingestion, and background and scheduled work.
- **Resilience** — Polly retries with jittered backoff, circuit breakers, timeouts, and bulkheads around external/AI dependencies.
- **Reliability** — outbox + idempotent consumers for exactly-once effects; dead-letter queues; sagas for multi-step consistency.
- **Targets** — 99.9% API availability; graceful degradation (serve cached/looked-up answers when the model is unavailable).
- **Autoscaling** — Kubernetes HPA on CPU/RPS/queue depth and GPU/inference concurrency for the AI service.


## 15. Infrastructure & DevOps

### 15.1 Docker

### 15.2 Kubernetes

### 15.3 Cloud

### 15.4 CI/CD
GitHub Actions (or Azure DevOps) pipelines: restore → build → unit/integration tests → AI evals → SAST/SCA/secret-scan → container build + sign (cosign) → push → deploy to staging → smoke/contract tests → progressive prod rollout. Trunk-based development, PR checks (including ReviewMate-style automated review), and IaC plan/apply gates. Database migrations run automatically with backward-compatible, expand-contract changes. Rollbacks are automated on failed health/eval gates.


## 16. Monitoring & Logging
Full observability via **OpenTelemetry** (traces, metrics, logs) exported to a backend (Azure Monitor / Grafana stack / Datadog).

- **Structured logging** with correlation/trace IDs across services (structlog in Python).
- **File-based JSON logging** — every service writes structured JSON logs to daily-rotated files:
  - Format: `logs/<service>/<yyyy-mm-dd>.json` (e.g. `logs/triage/2026-06-30.json`)
  - One JSON object per line (newline-delimited JSON / NDJSON), each containing: `timestamp`, `level`, `logger`, `service`, `trace_id`, `tenant_id`, `correlation_id`, `message`, `module`, `function`, `line`, and any event-specific `extra` fields.
  - Log directory is volume-mounted (`/var/log/fixroute/<service>/`) and retained for 90 days; a sidecar or cron job compresses and archives files older than 7 days to cold blob storage.
  - Log shipping: Filebeat / Fluent Bit tails each daily file and forwards to the observability backend, tracking the current file via the `logfile` field so multi-day queries remain seamless.
  - Daily rotation is driven by the logging framework at midnight UTC; old files are never overwritten.
- **Metrics** — RED/USE dashboards: rate, errors, duration, saturation per service; business KPIs from Section 2.7.
- **Tracing** — distributed traces across gateway → services → data → AI service → model/tool calls.
- **Alerting** — SLO-based alerts (error budgets), on-call routing (PagerDuty/Opsgenie), and runbooks.
- **Audit & compliance logs** retained per policy.
- **AI observability** — per-call token usage, cost, latency, retrieval hits, grounding/eval scores, and drift metrics; sampled traces of prompts/outputs (PII-scrubbed).


## 17. Cost Optimization
Cost is a first-class architectural concern (it protects the unit economics of a micro SaaS).

- Right-sized Kubernetes requests/limits; cluster autoscaler + scale-to-zero for non-prod and bursty workers.
- Spot/low-priority nodes for fault-tolerant batch jobs; reserved/savings plans for steady baseline.
- Caching and CQRS read models to cut database load; storage tiering and lifecycle policies for cold data.
- FinOps: per-tenant cost attribution and dashboards tied to usage-based pricing so margins are visible.
- Budget alerts and anomaly detection on cloud spend.
- Model routing (cheap model first), prompt/response and embedding caching, batching, and max-token caps.
- Retrieval tuning to send only the most relevant context (fewer tokens = lower cost and better answers).
- GPU scale-to-zero and serverless inference for spiky AI load; per-tenant token budgets and rate limits.


## 18. Cross-Team Collaboration & Delivery
- **Contracts as the interface** — OpenAPI, event schemas, MCP tool schemas, and `spec.md` let front-end, back-end, AI, and platform teams work in parallel against agreed boundaries.
- **DDD context map** assigns clear ownership per bounded context, reducing cross-team coupling.
- **Spec-Driven Development** gives a shared, executable source of truth; tasks are decomposed with acceptance criteria so work parallelizes cleanly.
- **CI/CD + trunk-based development** keep integration continuous; feature flags (Flagpole-style) decouple deploy from release.
- **Definition of Ready/Done**, ADRs (architecture decision records), and runbooks keep teams aligned and onboarding fast.


## 19. Roadmap & Milestones

| Phase | Outcomes |
| --- | --- |
| Phase 0 — Spec & foundations (2–3 wks) | Author `spec.md`/`plan.md`/`tasks.md`, set up repo, CI/CD skeleton, Docker/K8s base, auth, multi-tenancy. |
| Phase 1 — Core MVP (4–6 wks) | Implement core bounded contexts (Intake, Triage…), CQRS commands/queries, primary CRUD + APIs, and the top features. |
| Phase 2 — Intelligence (4–6 wks) | Stand up the Python AI service: LLM orchestration, RAG, agents/MCP, vector store, and the evaluation harness. |
| Phase 3 — Production hardening (3–4 wks) | Security review, performance/load testing, observability, cost tuning, and progressive rollout to first customers. |
| Phase 4 — Learn & expand | Close feedback/eval loops, tune retrieval & prompts, expand autonomy and integrations. |

## 20. Risks & Mitigations

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Scope creep on the MVP | Medium | SDD spec + ruthless out-of-scope list; ship the thin end-to-end slice first. |
| Multi-tenant data leakage | High | Row-level security, tenant key everywhere, automated isolation tests in CI. |
| Third-party API changes/limits | Medium | Anti-Corruption Layer, contract tests, retries/circuit breakers, vendor fallbacks. |
| Cloud cost overruns | Medium | FinOps dashboards, budgets/alerts, autoscaling, caching (Section 17). |
| Hallucination / wrong AI output | High | Grounded RAG with citations, eval thresholds in CI, guardrails, human-in-the-loop on high-impact actions. |
| Model/provider cost or outage | Medium | Model routing + caching, provider fallback via the adapter, budget caps. |
| Prompt injection / data exfiltration | High | Input/output filtering, scoped tool permissions, ACL-aware retrieval, audit of tool calls. |

## 21. Goals & Definition of Done

### 21.1 How this product delivers the portfolio goals
| Goal | How it is achieved |
| --- | --- |
| Build working software | Thin end-to-end vertical slice shipped in Phase 1; everything is deployable and tested from day one. |
| Build scalable software | Stateless services + Kubernetes HPA, CQRS read models, async messaging, multi-tenant by design (Sections 13–14). |
| Help teams deliver | Spec-Driven Development, contracts-first parallelism, CI/CD, and clear DDD ownership (Sections 4 & 18). |
| Solve a real business problem | Directly targets: property managers triage maintenance tickets manually, mis-prioritize emergencies, and dispatch the wrong trades. — measured by the KPIs in Section 2.7. |
| Build a system that learns | Evaluation harness, human-feedback loops, drift detection, memory, and continuous retrieval/prompt tuning (Section 10.7). |

### 21.2 Definition of Done
- All acceptance criteria (Section 4.3) pass in CI.
- Security checks, SAST/SCA, and tenant-isolation tests pass.
- Performance budgets (Section 13) met under load test.
- Observability dashboards and alerts live (Section 16).
- Docs/OpenAPI published and runbooks written.
- AI evaluation thresholds (relevance/faithfulness/task success) met (Section 10.7).

---
*Generated for the 2026 Micro SaaS Portfolio — built Spec-First. AI amplifies software engineering; it does not replace it.*

