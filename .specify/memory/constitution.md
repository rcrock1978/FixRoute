<!--
  Sync Impact Report — Constitution v1.0.0

  Version change: (template) → 1.0.0
  Principles added: 5 (SDD First, Clean Architecture & DDD, Test & Eval Discipline,
                     Security & Multi-Tenancy by Design, Observability & Reliability)
  Sections added: Tech Stack & Constraints, Development Workflow
  Sections removed: none
  Templates reviewed:
    ✅ `.specify/templates/plan-template.md` — no changes needed; Constitution Check section already references Gates.
    ✅ `.specify/templates/spec-template.md` — no changes needed; scope/requirements sections remain aligned.
    ✅ `.specify/templates/tasks-template.md` — no changes needed; task categories match all 5 principles.
  Follow-up TODOs: none
-->

# FixRoute Constitution

## Core Principles

### I. Spec-Driven Development (SDD)

All feature work MUST start with a spec (`spec.md`), a plan (`plan.md`), and
tasks (`tasks.md`) before any implementation code is written. The spec is the
authoritative source of truth for intent, scope, and acceptance criteria. No
code is merged without a corresponding spec artifact update. This prevents ad-
hoc prompting and ensures every build is traceable back to a documented business
requirement.

Rationale: The entire delivery pipeline (agents, CI, reviews) relies on executable
specs as the shared contract between intent and implementation.

### II. Clean Architecture & Domain-Driven Design

The codebase MUST follow Clean Architecture with strict dependency inversion:
Domain → Application → Infrastructure → Presentation. Bounded contexts map to
independent Django apps. Domain aggregates encapsulate business invariants;
application services (CQRS) orchestrate use cases; infrastructure adapters
implement ports (database, message bus, AI providers). Anti-Corruption Layers
MUST isolate every third-party integration.

Rationale: This protects the domain from framework churn and vendor lock-in,
and enables parallel development across teams aligned to bounded contexts.

### III. Test & Eval Discipline

Every feature MUST include:
- Unit tests for domain logic (pytest)
- Integration tests for service-layer orchestration
- Contract tests for API and event schemas
- AI evaluation thresholds (relevance, faithfulness, task success) for any
  LLM-generated output

Tests MUST be written FIRST (red), verified failing, then implemented (green).
The eval suite runs in CI as a mandatory gate — no change ships without passing
both traditional tests and AI evals. Exceptions require written justification
and explicit governance approval.

### IV. Security & Multi-Tenancy by Design

Every feature MUST respect tenant isolation at the data and application layer.
Row-level security and a tenant key on every table are non-negotiable.
Authentication uses OIDC/OAuth2; authorization enforces RBAC/ABAC at the
application boundary. Secrets never appear in code, images, or logs. All AI
inputs/outputs MUST pass through guardrails (prompt-injection, PII redaction,
output moderation). SOC 2 Type II and GDPR/CCPA readiness are design constraints.

Rationale: FixRoute is multi-tenant by construction; a single isolation failure
is a critical business risk.

### V. Observability & Reliability

Every service MUST emit structured JSON logs (daily-rotated files, NDJSON format)
with correlation IDs, trace IDs, and tenant IDs. Every external call (database,
AI provider, third-party API) MUST be instrumented with retries, circuit breakers,
and latency tracking. OpenTelemetry traces span every user request from gateway
through AI inference. SLO-based alerting must be in place before any service
serves production traffic.

Rationale: Debugging AI-driven systems without observability is impossible. Logs,
traces, and metrics are the primary debugging interface.

## Tech Stack & Constraints

| Concern | Mandated Choice |
|---------|----------------|
| Backend runtime | Python 3.12+ (Django + DRF) |
| Frontend | Vue.js 3 (Vite, Pinia, Vue Router) |
| Operational store | PostgreSQL + pgvector |
| Caching | Redis |
| Async task queue | Celery |
| Message broker | RabbitMQ or Azure Service Bus |
| Container runtime | Docker + Kubernetes (AKS) |
| Infrastructure as Code | Terraform |
| CI/CD | GitHub Actions |
| Observability | OpenTelemetry + structlog |
| AI orchestration | LangChain / LlamaIndex |
| MCP integration | MCP server/client for agent tool exposure |

All technology choices in this table are binding. Deviations require a
constitution amendment.

## Development Workflow

1. **Specify** — `/speckit.specify` creates the spec from the feature description.
2. **Plan** — `/speckit.plan` produces research, data model, contracts, and plan.
3. **Tasks** — `/speckit.tasks` decomposes the plan into executable task items.
4. **Implement** — `/speckit.implement` executes tasks in phase order, writing
   tests first (red → green). CI gates on tests + AI evals + SAST/SCA.
5. **Review** — every PR is reviewed against the spec; Constitution Check gates
   ensure no principle is violated.
6. **Release** — trunk-based development; feature flags decouple deploy from
   release; progressive rollouts via Argo Rollouts.

## Governance

This Constitution supersedes all other development practices. Amendments require:
1. Documentation of the proposed change and its rationale.
2. Approval from the Solution Architect.
3. Update to this file with a version bump following semver.
4. Propagation to any affected templates or CI gates.

All PRs MUST be reviewed for compliance with this Constitution. Complexity
additions (new services, new dependencies, architectural deviations) MUST be
justified in the Complexity Tracking section of the plan.

Any violation detected in code review or CI MUST be resolved before merge, or
documented as a tracked exception with an expiration date.

**Version**: 1.0.0 | **Ratified**: 2026-06-30 | **Last Amended**: 2026-07-01
