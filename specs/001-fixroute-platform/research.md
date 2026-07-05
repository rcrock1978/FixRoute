# Research: FixRoute Platform

## Django REST Framework for API Layer

**Decision**: Django REST Framework (DRF) with drf-spectacular for OpenAPI generation.

**Rationale**: DRF is the most mature, well-documented REST framework for
Django. It provides serializers, viewsets, routers, authentication classes,
permission classes, and browsable API out of the box. drf-spectacular
generates OpenAPI 3.0 schemas from DRF code with minimal configuration,
replacing the now-archived drf-yasg.

**Alternatives considered**: 
- FastAPI (separate async framework, would split the Python runtime)
- Django Ninja (newer, smaller ecosystem, fewer third-party packages)

## PostgreSQL + pgvector for Vector Storage

**Decision**: PostgreSQL with pgvector extension for both operational data and
embeddings.

**Rationale**: Eliminates the operational complexity of managing a separate
vector database. pgvector supports exact and approximate nearest neighbor
search (IVFFlat, HNSW indexes), hybrid search (combine with full-text search),
and works with Django ORM via the `pgvector` Python package. For the MVP
scale (500-5,000 work orders/month), a dedicated vector DB is unnecessary
overhead.

**Alternatives considered**:
- Pinecone (managed, higher cost, additional network hop)
- Weaviate (separate service, operational overhead)
- Qdrant (separate service, good performance but more complexity)

## Celery for Async Task Processing

**Decision**: Celery with Redis as broker and result backend.

**Rationale**: Celery is the de facto standard for Django async task processing.
It handles AI inference calls (classification, transcription, RAG), notification
dispatch (email/SMS), and scheduled maintenance tasks. Redis serves dual duty as
cache and broker, simplifying the infrastructure stack for MVP.

**Alternatives considered**:
- Django Q2 (smaller ecosystem, fewer community resources)
- Huey (lightweight but less suitable for AI workloads)
- RabbitMQ as pure broker (adds operational complexity; Redis sufficient for MVP)

## LLM Orchestration

**Decision**: LangChain for initial development, with abstraction layer to swap
providers.

**Rationale**: LangChain has the largest ecosystem of integrations (Azure OpenAI,
Anthropic, open models via Ollama), tool calling support, and RAG primitives.
The adapter/ACL pattern (per constitution Principle II) wraps LangChain usage
so the domain layer never depends on it directly — future migrations to
LlamaIndex or custom orchestration are isolated behind the port.

**Alternatives considered**:
- LlamaIndex (stronger for RAG, weaker for agent/tool workflows)
- Direct provider SDKs (more control, but more boilerplate for common patterns)

## Authentication & Authorization

**Decision**: OIDC/OAuth2 via Microsoft Entra ID with django-guardian for
object-level permissions.

**Rationale**: Entra ID provides SSO, MFA, SCIM provisioning, and is the
standard identity provider for Azure-deployed applications. django-guardian
provides per-object permissions (e.g., Property Manager A cannot see Property
Manager B's data beyond tenant isolation).

**Alternatives considered**:
- Auth0 (equivalent capabilities, third-party, additional cost)
- django-allauth (social auth only, lacks enterprise SSO)
- Django's built-in auth groups (too coarse for object-level RBAC)

## Multi-Tenant Isolation

**Decision**: Row-level security (RLS) via PostgreSQL + tenant key on every
table, enforced at the database level.

**Rationale**: RLS guarantees isolation even if application-layer permissions
are misconfigured — defense in depth. The tenant key is set via a database
session variable at connection time (Django middleware sets it from the
authenticated request). django-guardian adds a second layer at the app level.

**Alternatives considered**:
- Separate database per tenant (stronger isolation, but operational complexity
  and connection overhead at 100-500 properties scale)
- Schema per tenant (shared pool but separate schemas; well-supported in Django
  with tenant-schemas packages but adds migration complexity)

## Observability Stack

**Decision**: OpenTelemetry SDK + structlog + Azure Monitor / Grafana.

**Rationale**: structlog provides structured JSON logging with zero effort for
NDJSON daily rotation. OpenTelemetry SDK auto-instruments Django views,
database queries, HTTP calls, and Celery tasks. Export to Azure Monitor for
tight Azure integration, with Grafana dashboards as a vendor-neutral overlay.

**Alternatives considered**:
- Loguru (cleaner API but less Django ecosystem integration)
- Sentry (excellent for errors, not a full observability solution)
- Datadog (best-in-class but expensive for a startup)

## AI Evaluation Framework

**Decision**: Custom eval harness (Ragas-inspired) with pytest integration.

**Rationale**: Ragas metrics (faithfulness, answer relevance, context precision)
map directly to FixRoute's quality requirements. Running evals as pytest tests
means they gate CI natively. Eval datasets are stored in the repo under
`tests/eval/` as versioned fixtures.

**Alternatives considered**:
- LangSmith (managed, expensive, vendor lock-in)
- Weights & Biases Prompts (good but another SaaS to manage)

## Data Retention & Right-to-Erasure

**Decision**: 7-year operational retention with soft-delete → 30-day
hard-delete SLA on erasure request.

**Rationale**: Landlord-tenant and tax recordkeeping obligations require
multi-year retention of maintenance and financial records. Privacy
regulations (GDPR Art. 17, CCPA) require defined erasure SLAs. The
soft-delete → 30-day hard-delete pattern preserves referential integrity
(audit trails, spend analytics) during the SLA window via tombstone
records, then hard-deletes PII.

**Alternatives considered**:
- 30-day hard retention (fails audit/legal recordkeeping)
- Indefinite retention with PII anonymization (incomplete erasure)
- 3-year retention (insufficient for IRS / state landlord-tenant law)

## Disaster Recovery

**Decision**: Multi-region active-passive, RTO 4h / RPO 15min, validated
by quarterly failover drills.

**Rationale**: The differentiated SLOs (Triage 99.95%, Dispatch 99.9%) cannot
be met with single-region deployments (single-AZ SLAs top out around
99.5-99.9%). Active-passive warm-standby is the cost-effective choice at
MVP scale (100-500 properties); active-active doubles infra cost without
proportional benefit. RTO 4h / RPO 15min is realistic for warm-standby
failover and tight enough to avoid losing triage decisions on regional
failure.

**Alternatives considered**:
- Single-region with daily backups (RTO 24h+; fails SLO)
- Active-active multi-region (RTO <1h but ~2x infra cost)
- Single-region with hourly backups (RTO 8h; borderline SLO)

## Notification Provider

**Decision**: Azure Communication Services (ACS) for SMS; native APNs + FCM
for mobile/web push; transactional email provider for email.

**Rationale**: ACS lives in the same Azure control plane as Entra ID and
AKS, supports both SMS and email with unified SDK, and offers data
residency matching the multi-region DR posture. Native APNs/FCM (rather
than a paid aggregator) avoids per-message fees at MVP scale and reduces
vendor surface.

**Alternatives considered**:
- Twilio for SMS + push (industry-standard but introduces a second vendor
  identity story on top of Entra ID)
- SendGrid email + separate SMS provider (two vendors, no unified SDK)
- Self-hosted open-source (Matrix, Gotify) — operationally heavy for MVP

## Media Storage

**Decision**: Azure Blob Storage with SAS-token access and lifecycle tiering
(Hot → Cool → Archive).

**Rationale**: Native Azure storage matches the Azure-first stack, supports
the 7-year retention via lifecycle policies (Hot ≤30d, Cool 30d-1y, Archive
1-7y), enables the 30-day erasure SLA via soft-delete + immutable blob
policies, and short-lived SAS tokens enforce tenant isolation per request.
Local NFS or Postgres bytea collides with multi-region DR; S3 multi-cloud
adds second-vendor overhead with no proportional benefit.

**Alternatives considered**:
- AWS S3 with presigned URLs (multi-cloud sprawl)
- PostgreSQL bytea / large objects (storage bloat at scale; collides with
  pgvector separation)
- Self-hosted MinIO on AKS persistent volumes (incompatible with multi-region DR)

## Duplicate Work-Order Detection

**Decision**: pgvector cosine similarity over text + image embeddings,
threshold ≥0.85, scoped to open + recent (≤14 day) work orders for the
same tenant/property.

**Rationale**: The Constitution mandates PostgreSQL + pgvector, so
vector-based deduplication avoids new infrastructure. Combining text
embeddings (from the LLM triage step that already runs) with image
embeddings (CLIP) catches both reworded and re-photographed duplicates.
A cosine threshold of 0.85 is the standard pragmatic cutoff — high enough
to avoid false positives, low enough to catch reworded duplicates.

**Alternatives considered**:
- Exact-hash on media + normalized text fingerprint (misses semantic dupes)
- LLM-as-judge equivalence (adds latency incompatible with <5min triage SLA)
- PostgreSQL trigram fuzzy text match only (ignores photo duplicates)
