# FixRoute

**AI-powered maintenance triage for property management.**

FixRoute ingests tenant maintenance requests (text, photos, voice), classifies
urgency with AI, provides self-serve troubleshooting for simple issues, and
dispatches the right vendor with calibrated priority — all in under five
minutes.

> Tenant submission → AI classification → right vendor in under 5 minutes.

---

## Highlights

- **AI triage** — text + image embeddings, cosine-similarity duplicate detection, per-tenant confidence thresholds
- **Vendor matching** — weighted scoring across trade, proximity, availability, rating, cost, and response time
- **Multi-channel notifications** — Azure Communication Services (SMS) + APNs/FCM (push) + email
- **Multi-tenant by design** — PostgreSQL row-level security + application-layer enforcement
- **Production-grade reliability** — multi-region AKS, RTO 4h, RPO 15min, SLO-based alerting
- **Compliance-ready** — 7-year retention, 30-day erasure SLA, SOC 2 Type II controls, GDPR/CCPA aligned

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · Django 5 · DRF |
| Frontend | Vue.js 3 · Vite · Pinia · Vue Router |
| Database | PostgreSQL 16 + pgvector |
| Cache / Queue | Redis 7 · Celery |
| AI | LangChain · Azure OpenAI |
| Auth | Microsoft Entra ID (OIDC/OAuth2) |
| Notifications | Azure Communication Services · APNs · FCM |
| Media | Azure Blob Storage with SAS tokens |
| Infrastructure | Azure Kubernetes Service (multi-region) · Terraform |
| CI/CD | GitHub Actions |
| Observability | OpenTelemetry · structlog · Azure Monitor |

---

## Repository structure

```text
.
├── backend/                # Django + DRF backend
│   ├── apps/
│   │   ├── intake/         # Bounded context: work order submission, media, duplicate detection
│   │   ├── triage/         # Bounded context: AI classification, troubleshooting
│   │   ├── dispatch/       # Bounded context: vendor assignment, status tracking
│   │   ├── vendormanagement/  # Bounded context: vendor profiles, cost estimates
│   │   └── analytics/      # Bounded context: spend aggregation
│   ├── ai/                 # AI services (classifier, embeddings, knowledge base)
│   ├── common/             # Cross-cutting (auth, audit, storage, notifications, tasks)
│   ├── config/             # Django settings, URLs, Celery
│   └── tests/              # Unit, integration, contract, AI eval
├── frontend/               # Vue 3 SPA
│   ├── src/
│   │   ├── components/     # AudioRecorder
│   │   ├── pages/          # RequestSubmit, RequestStatus, DispatchWorkflow, EstimateReview, AnalyticsDashboard
│   │   ├── stores/         # Pinia: tenant, workorder
│   │   ├── services/       # API client
│   │   └── router/         # Vue Router
│   ├── Dockerfile
│   └── package.json
├── infra/                  # Infrastructure-as-code, Kubernetes manifests, Helm charts
├── specs/001-fixroute-platform/  # Spec-Driven Development artifacts
│   ├── spec.md             # Authoritative spec (15 FRs, 7 SCs, 4 user stories)
│   ├── plan.md             # Implementation plan
│   ├── research.md         # Tech decisions (DRF, pgvector, ACS, Azure Blob, etc.)
│   ├── data-model.md       # Entities with soft-delete + pgvector embeddings
│   ├── quickstart.md       # 10 validation scenarios
│   ├── contracts/          # OpenAPI 3.0 schema
│   ├── tasks.md            # 147 executable tasks
│   └── checklists/         # Quality checklists
├── docs/                   # Project documentation
│   ├── FixRoute-Overview.md       # Product overview
│   ├── LinkedIn-Pitch.md          # 120-second pitch
│   └── presentations/             # Client PowerPoint deck
├── docker-compose.yml      # Local dev stack (Postgres+pgvector, Redis, Django, Celery, Vue)
├── .github/workflows/      # CI: lint → test → eval → build
└── AGENTS.md               # Managed agent context (between SPECKIT markers)
```

---

## Quickstart

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- (Optional) Azure subscription for full cloud deployment

### Local development

```bash
# 1. Start infrastructure services (Postgres+pgvector, Redis)
docker compose up -d postgres redis

# 2. Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 3. Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev

# 4. (Optional) Celery worker + beat for async tasks
celery -A backend.config worker --loglevel=info
celery -A backend.config beat --loglevel=info
```

Frontend: <http://localhost:5173>  ·  Backend API: <http://localhost:8000/api/v1/>  ·  API docs: <http://localhost:8000/api/docs/>

### End-to-end validation

See `specs/001-fixroute-platform/quickstart.md` for 10 runnable scenarios covering
intake, AI triage, dispatch, cost estimates, spend analytics, GDPR/CCPA erasure,
and multi-region DR failover.

---

## Architecture

### Bounded contexts

| Context | Responsibility |
|---|---|
| **Intake** | Work order submission, media upload to Azure Blob, pgvector duplicate detection |
| **Triage** | AI classification, troubleshooting knowledge base, per-tenant confidence threshold |
| **Dispatch** | Vendor matching, status lifecycle, emergency escalation, notifications |
| **Vendor Management** | Vendor profiles, cost estimates, PM review workflow |
| **Analytics** | Spend aggregation by property / trade / vendor / month with variance tracking |

### Request flow

```
Tenant submits request
        ↓
[ Intake ] compute text + image embeddings → Azure Blob for media
        ↓
[ Triage ] AI classifies (category · urgency · confidence)
        ↓
        ├─ Confidence < threshold → escalate to human dispatcher
        └─ Confidence ≥ threshold
                ↓
        Self-serve troubleshooting OR vendor match
                ↓
[ Dispatch ] weighted vendor scoring → PM approval → ACS SMS + APNs/FCM push
        ↓
[ Vendor ] submits estimate → PM approves
        ↓
[ Analytics ] spend aggregated by property, trade, vendor
```

### Reliability and compliance

- **Multi-tenant isolation** — every table carries a `tenant_id`; PostgreSQL row-level security enforces it at the database layer
- **Disaster recovery** — multi-region active-passive on AKS, RTO 4h / RPO 15min, validated by quarterly drills
- **Data retention** — operational records kept 7 years; personal data soft-deleted on erasure request, hard-deleted within 30 days
- **Audit trail** — every state change logged with actor, timestamp, and before/after state
- **AI safety** — all LLM inputs/outputs pass through guardrails (prompt-injection, PII redaction, output moderation)
- **Encryption** — TLS in transit, encrypted at rest, short-lived SAS tokens for media

---

## Development workflow

This project uses **Spec-Driven Development (SDD)** with the full artifact
chain maintained alongside the code:

```
specify → plan → tasks → implement
```

The `specs/001-fixroute-platform/` directory is the authoritative source of
truth for intent, scope, and acceptance criteria. The `AGENTS.md` managed
section (between `<!-- SPECKIT START -->` and `<!-- SPECKIT END -->` markers)
points to the current plan and is auto-updated by the agent-context extension.

### Project principles (Constitution v1.0.0)

1. **SDD First** — every build traces back to a spec, plan, and task
2. **Clean Architecture & DDD** — bounded contexts, dependency inversion, anti-corruption layers
3. **Test & Eval Discipline** — unit, integration, contract, and AI eval tests gate CI
4. **Security & Multi-Tenancy by Design** — row-level security, OIDC, AI guardrails
5. **Observability & Reliability** — structured logs, distributed tracing, SLO alerting

The full constitution is at `.specify/memory/constitution.md`.

### Tests

```bash
# Backend tests
cd backend
pytest                                  # all tests
pytest apps/intake/tests/               # single app
pytest --cov=. --cov-report=term-missing # with coverage

# AI evaluation tests
pytest tests/eval/                      # classification accuracy, troubleshooting relevance

# Contract tests (API schema conformance)
pytest tests/contract/                  # validates responses against OpenAPI spec

# Frontend
cd frontend
npm run lint
npm run type-check
npm run build
```

---

## Project status

**MVP vertical slice complete (110/147 tasks, 75%).**

- ✅ Phase 1: Setup (project scaffolding, Docker, CI)
- ✅ Phase 2: Foundational (auth, audit, soft-delete, Azure Blob, ACS, APNs/FCM, pgvector)
- ✅ Phase 3: US1 — Tenant intake + AI triage (US1 acceptance scenarios green)
- ✅ Phase 4: US2 — Vendor matching + dispatch
- ✅ Phase 5: US3 — Cost estimates, PM approval, spend analytics
- ⏳ Phase 6: US4 — GDPR/CCPA erasure + 7-year retention
- ⏳ Phase 7: Polish + multi-region DR + SLO alerting

The MVP runs end-to-end on local Docker. Cloud deployment to AKS requires
Azure provisioning (see roadmap below).

---

## Roadmap

- **Q4 2026** — MVP launch (current state)
- **Q1 2027** — Native iOS and Android apps for tenants
- **Q2 2027** — AppFolio and Buildium PMS integrations
- **Q3 2027** — Computer-vision damage assessment from photos
- **Q4 2027** — Predictive maintenance using historical work-order embeddings

---

## Documentation

| Document | Purpose |
|---|---|
| `docs/FixRoute-Overview.md` | Product overview for clients and stakeholders |
| `docs/LinkedIn-Pitch.md` | 120-second social media pitch |
| `docs/presentations/FixRoute-Client-Presentation.pptx` | 14-slide client presentation |
| `specs/001-fixroute-platform/spec.md` | Authoritative feature specification |
| `specs/001-fixroute-platform/plan.md` | Implementation plan + architecture |
| `specs/001-fixroute-platform/research.md` | Tech stack decisions and rationale |
| `specs/001-fixroute-platform/data-model.md` | Entity relationships, indexes, soft-delete flow |
| `specs/001-fixroute-platform/quickstart.md` | 10 runnable validation scenarios |
| `specs/001-fixroute-platform/contracts/openapi.yaml` | OpenAPI 3.0 API contract |
| `specs/001-fixroute-platform/tasks.md` | 147 executable tasks with status |
| `.specify/memory/constitution.md` | Project principles and governance |

---

## License

Proprietary — all rights reserved. Contact engineering@fixroute.example.com
for licensing inquiries.

---

## Contact

- **Engineering** — engineering@fixroute.example.com
- **Product** — product@fixroute.example.com
- **Security** — security@fixroute.example.com
