# FixRoute — Product Overview

**AI-powered maintenance triage for property management**

---

## What is FixRoute?

FixRoute is an intelligent maintenance operations platform built for property
management companies. It ingests tenant maintenance requests (text, photos, voice),
classifies urgency using AI, provides self-serve troubleshooting for simple issues,
and dispatches the right vendor with calibrated priority — all in under five minutes.

The product eliminates the manual triage bottleneck that costs property managers
hours every week, reduces mis-triage of emergencies, and gives tenants immediate
acknowledgment that their problem is being handled.

---

## Why do we need it?

Property management is a high-volume, time-sensitive service. The traditional
maintenance workflow has three structural problems:

| Problem | Business Impact |
|---|---|
| **Manual triage** — every request is read by a human coordinator | Property managers spend 40%+ of their day on intake and routing |
| **Slow vendor dispatch** — phone calls, callbacks, missed connections | Average time-to-dispatch for urgent issues exceeds 1 hour |
| **Emergency mis-routing** — gas leaks and floods wait behind dripping faucets | Safety incidents, tenant churn, regulatory exposure |

FixRoute addresses all three with automation that augments rather than replaces
human coordinators. Tenants get immediate response. Coordinators focus on
exceptions. Vendors get fully-contextualized work orders.

---

## How it works — the user journey

### Tenant perspective

1. **Submit** a request with text, photo, or voice recording from any device.
2. **Receive** an immediate acknowledgment with the AI-classified category and urgency.
3. **Try self-serve** troubleshooting steps for common issues (e.g., "how to
   reset a tripped breaker").
4. **Track** status updates as the work order moves through dispatch to completion.

### Property manager perspective

1. **Review** incoming requests on a single dashboard.
2. **Confirm** AI triage recommendations, adjust thresholds per property or trade.
3. **Approve** vendor matches — ranked by proximity, availability, rating, cost.
4. **Approve** cost estimates with one click.
5. **Analyze** spend trends across properties, trades, vendors, and time periods.

### Vendor perspective

1. **Receive** a fully-contextualized work order with photos, urgency, and SLA.
2. **Submit** a cost estimate with line items.
3. **Update** status (en route, on site, completed) from a mobile-friendly interface.

---

## Architecture overview

FixRoute is built on a multi-tenant cloud architecture with strong data isolation,
disaster recovery posture, and compliance with GDPR/CCPA and SOC 2 Type II
controls.

### Tech stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | Python 3.12 + Django 5 + DRF | Mature ecosystem, async support, strong ORM |
| **Frontend** | Vue.js 3 + Vite + Pinia | Reactive, performant, easy onboarding |
| **Database** | PostgreSQL 16 + pgvector | Operational + vector embeddings in one store |
| **Cache / Queue** | Redis 7 + Celery | Async tasks, rate limiting, session store |
| **AI** | LangChain + Azure OpenAI | Pluggable provider, RAG, agent tooling |
| **Auth** | Microsoft Entra ID (OIDC/OAuth2) | Enterprise SSO, MFA, SCIM provisioning |
| **Notifications** | Azure Communication Services + APNs/FCM | SMS + native push + email |
| **Media** | Azure Blob Storage with SAS tokens | Photo/voice with lifecycle tiering |
| **Deployment** | Azure Kubernetes Service (multi-region) | Active-passive, RTO 4h / RPO 15min |
| **IaC** | Terraform | Reproducible infrastructure |
| **CI/CD** | GitHub Actions | Lint → test → build → deploy |
| **Observability** | OpenTelemetry + structlog + Azure Monitor | Distributed tracing, SLO alerting |

### Bounded contexts

The codebase follows Domain-Driven Design with five bounded contexts, each as
an independent Django app:

- **Intake** — request submission, media, duplicate detection
- **Triage** — AI classification, troubleshooting knowledge base
- **Dispatch** — vendor matching, status tracking, emergency escalation
- **Vendor Management** — vendor profiles, cost estimates
- **Analytics** — spend aggregation, variance reporting

---

## Reliability and compliance

### Multi-tenant isolation

Every database table carries a `tenant_id`. PostgreSQL row-level security
enforces isolation at the database layer; the application enforces it at the
service layer. A single misconfigured query cannot leak data across tenants.

### Data retention and right-to-erasure

- **Operational records** (work orders, estimates, audit logs) retained for
  **7 years** to satisfy landlord-tenant and tax recordkeeping obligations.
- **Personal data** is soft-deleted immediately on erasure request and
  hard-deleted within **30 days**. Audit-log tombstones preserve referential
  integrity for compliance reporting.

### Disaster recovery

- Multi-region active-passive deployment on Azure Kubernetes Service.
- **RTO**: 4 hours (time to restore service after a regional failure).
- **RPO**: 15 minutes (maximum data loss in a regional failure).
- Quarterly failover drills validate both targets.

### Observability

- Structured JSON logs (NDJSON, daily rotation) with correlation IDs.
- OpenTelemetry traces span every request from gateway through AI inference.
- Circuit breakers on all external calls (database, AI provider, third-party APIs).
- SLO-based alerting before any service serves production traffic.

### Security

- OIDC/OAuth2 via Microsoft Entra ID with role-based access control.
- All AI inputs and outputs pass through guardrails (prompt-injection, PII redaction, output moderation).
- Secrets never appear in code, images, or logs.
- Short-lived SAS tokens scope per-request media access.

---

## Success criteria

| Goal | Target |
|---|---|
| Time to dispatch decision (urgent) | < 5 minutes |
| Time to dispatch decision (routine) | < 30 minutes |
| Self-serve resolution rate | ≥ 30% of low-urgency requests |
| Emergency mis-triage rate | < 2% |
| PM time savings on triage | ≥ 40% within 3 months of adoption |
| Triage API uptime | 99.95% |
| Dispatch uptime | 99.9% |
| Erasure SLA | 100% within 30 days |

---

## What's next

The current implementation is a deployable MVP covering the full vertical
slice: intake, AI triage, vendor matching, dispatch, cost estimates, and
spend analytics. Next-quarter investments include:

- **Native mobile apps** for tenants (currently responsive web).
- **Third-party PMS integration** (AppFolio, Buildium) for tenant roster sync.
- **Computer-vision damage assessment** from photos using multimodal models.
- **Predictive maintenance** using historical work-order embeddings.

---

*FixRoute is built and maintained by an engineering team committed to clean
architecture, test-driven development, and AI safety. The full Spec-Driven
Development artifacts (spec, plan, tasks, contracts, data model) are
maintained alongside the codebase as the authoritative source of truth.*
