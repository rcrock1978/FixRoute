# Implementation Plan: FixRoute Platform

**Branch**: `001-fixroute-platform` | **Date**: 2026-07-01 | **Spec**: `specs/001-fixroute-platform/spec.md`

**Input**: Feature specification from `specs/001-fixroute-platform/spec.md`

## Summary

FixRoute is an AI-powered maintenance triage system for property management.
Tenants submit requests (text/photo/voice); AI classifies urgency, provides
self-serve troubleshooting for simple issues, and dispatches the right vendor
with calibrated urgency. The system is built as a multi-tenant Django web
application with a Vue.js 3 frontend, PostgreSQL + pgvector for operational
and vector storage, Celery for async task processing, and Azure Kubernetes
for deployment.

## Technical Context

**Language/Version**: Python 3.12+ (Django 5.x + DRF), Vue.js 3 (Vite, Pinia, Vue Router)

**Primary Dependencies**: Django REST Framework, Celery, LangChain / LlamaIndex, structlog, psycopg2, django-guardian, django-filter, drf-spectacular

**Storage**: PostgreSQL 16 + pgvector extension (operational + vector embeddings), Redis 7 (caching + Celery broker), Azure Blob Storage (photo + voice media with lifecycle tiering and SAS-token access)

**Testing**: pytest, pytest-django (unit/integration), drf-spectacular contract tests, Ragas-style AI eval harness

**Target Platform**: Linux amd64 containers on Azure Kubernetes Service (AKS), multi-region active-passive (RTO 4h, RPO 15min)

**Project Type**: Web application (Django REST API backend + Vue.js 3 SPA frontend)

**Performance Goals**: 
- API reads: p95 < 200ms
- API writes: p95 < 400ms
- AI classification first-token: < 1.5s
- AI grounded answer: < 6s (streamed)
- Self-serve troubleshooting response: < 5s

**Constraints**:
- Multi-tenant row-level security on every table
- All state changes logged to append-only audit trail
- Structured JSON logging (NDJSON) to daily-rotated files
- AI outputs must pass guardrails (prompt-injection, PII, grounding) before surfacing
- SOC 2 Type II and GDPR/CCPA readiness by design
- 7-year operational data retention with 30-day hard-delete SLA on erasure request
- Notifications delivered via Azure Communication Services (SMS), native APNs/FCM (push), and a transactional email provider
- Duplicate work-order detection via pgvector cosine similarity (text + image embeddings, threshold ≥0.85)

**Scale/Scope**: MVP targets 100–500 properties, 500–5,000 work orders/month; architecture must scale linearly beyond without redesign

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. SDD First | ✅ Pass | Spec exists, plan in progress, tasks follow. |
| II. Clean Architecture & DDD | ✅ Pass | Django apps map to bounded contexts; service layer enforces dependency rules. |
| III. Test & Eval Discipline | ✅ Pass | pytest + AI evals mandated; tests-first approach in implementation. |
| IV. Security & Multi-Tenancy | ✅ Pass | RLS, tenant keys, OIDC/OAuth2, AI guardrails planned. |
| V. Observability & Reliability | ✅ Pass | NDJSON logging, OpenTelemetry, circuit breakers, SLO alerting planned. |

No violations identified. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/001-fixroute-platform/
├── plan.md              # This file
├── research.md          # Phase 0 output (tech research)
├── data-model.md        # Phase 1 output (entities, relationships)
├── quickstart.md        # Phase 1 output (validation guide)
├── contracts/           # Phase 1 output (OpenAPI, event schemas)
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── intake/            # Bounded context: Intake
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── api/
│   │   ├── tests/
│   │   └── domain/
│   ├── triage/            # Bounded context: Triage
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── api/
│   │   ├── tests/
│   │   └── domain/
│   ├── dispatch/          # Bounded context: Dispatch
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── api/
│   │   ├── tests/
│   │   └── domain/
│   ├── vendormanagement/  # Bounded context: Vendor Management
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── api/
│   │   ├── tests/
│   │   └── domain/
│   └── analytics/         # Bounded context: Analytics
│       ├── models.py
│       ├── services.py
│       ├── api/
│       ├── tests/
│       └── domain/
├── ai/                    # Python AI service (LLM, RAG, agents)
│   ├── classification/
│   ├── troubleshooting/
│   ├── rag/
│   ├── agents/
│   └── mcp/
├── common/
│   ├── middleware/
│   ├── auth/
│   ├── logging/
│   └── utils/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── Dockerfile
├── manage.py
└── pyproject.toml

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── stores/
│   ├── services/
│   ├── router/
│   └── assets/
├── public/
├── index.html
├── vite.config.ts
├── package.json
└── tsconfig.json

infra/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── k8s/
│   ├── backend/
│   ├── frontend/
│   └── ai-service/
└── helm/

tests/
├── contract/
├── integration/
├── unit/
└── eval/
```

**Structure Decision**: Option 2 (Web application) with separate `backend/` and
`frontend/` directories. Each bounded context lives as a Django app under
`backend/apps/`. The AI service lives under `backend/ai/` as part of the same
Django project but deployed as a separately scalable service. Infrastructure
code (`infra/`) is separated from application code.

## Complexity Tracking

> **No violations — all Constitution Check gates pass.**
