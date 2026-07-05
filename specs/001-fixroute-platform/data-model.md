# Data Model: FixRoute Platform

## Tenancy

All entities carry a `tenant_id` column (UUID, foreign key to `Tenant`). Row-level
security (RLS) is enabled on every tenant-scoped table. The `Tenant` model is the
root of multi-tenant isolation.

**Tenant**
- `id` (UUID, PK)
- `name` (varchar, required)
- `slug` (varchar, unique, URL-safe)
- `settings` (JSONB, tenant-level configuration)
- `created_at`, `updated_at` (timestamps)

## Core Entities

### Property
Represents a physical unit or building under management.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → Tenant, RLS |
| name | varchar | required |
| address | text | required |
| unit_count | int | default 1 |
| metadata | JSONB | optional (building info, access notes) |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

Relationships: Property → WorkOrder (1:N), Property → Tenant (N:1)

### TenantProfile
Represents a tenant living in a property (the person, not the multi-tenant org).

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| property_id | UUID | FK → Property |
| name | varchar | required |
| email | varchar | required, indexed |
| phone | varchar | optional |
| unit | varchar | optional (unit number) |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

### WorkOrder
The central aggregate. Represents a maintenance request from initial
submission through completion.

**Lifecycle states**: `submitted` → `classified` → `troubleshooting` →
`dispatched` → `in_progress` → `completed`

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → Tenant, RLS |
| property_id | UUID | FK → Property |
| submitted_by_id | UUID | FK → TenantProfile |
| title | varchar | required |
| description | text | required |
| status | varchar | enum: submitted/classified/troubleshooting/dispatched/in_progress/completed |
| priority | varchar | enum: emergency/urgent/routine/low |
| category | varchar | enum: plumbing/electrical/HVAC/structural/appliance/general |
| media_attachments | JSONB | array of {blob_url, sas_token_expires_at, type, filename} — stored in Azure Blob |
| voice_transcript | text | nullable, server-side ASR output |
| description_embedding | vector(1536) | pgvector embedding for duplicate detection |
| image_embedding | vector(512) | pgvector CLIP embedding (nullable) |
| soft_deleted_at | timestamp | nullable; tombstone for 30-day erasure SLA |
| hard_delete_at | timestamp | nullable; scheduled 30 days after soft_delete_at |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

### TriageResult
The AI classification outcome for a WorkOrder.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| work_order_id | UUID | FK → WorkOrder, unique |
| category | varchar | classified category |
| urgency | varchar | classified urgency level |
| confidence | float | 0.0–1.0 |
| troubleshooting_steps | JSONB | array of {step, description} (nullable) |
| ai_model_version | varchar | which model/version performed classification |
| classification_time_ms | int | latency of classification |
| created_at | timestamp | auto |

### MediaAsset
A blob (photo or voice recording) stored in Azure Blob Storage, linked to
a WorkOrder.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → Tenant, RLS |
| work_order_id | UUID | FK → WorkOrder |
| blob_url | varchar | Azure Blob URL (opaque) |
| container | varchar | Azure container name |
| tier | varchar | enum: hot/cool/archive — driven by lifecycle policy |
| content_type | varchar | image/jpeg, image/png, audio/wav, audio/mpeg |
| size_bytes | bigint | nullable until upload complete |
| checksum_sha256 | varchar | integrity verification |
| uploaded_at | timestamp | auto |
| soft_deleted_at | timestamp | nullable; 30-day erasure SLA |
| hard_delete_at | timestamp | nullable; scheduled 30 days after soft_deleted_at |

### Vendor
A service provider with trade specialties.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → Tenant, RLS |
| name | varchar | required |
| trades | JSONB | array of trade specialties |
| coverage_areas | JSONB | array of geographic areas / postal codes |
| availability | JSONB | schedule (optional) |
| rating | float | 0.0–5.0, computed from feedback |
| contact_email | varchar | required |
| contact_phone | varchar | required |
| insurance_verified | bool | default false |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

### Dispatch
The assignment of a Vendor to a WorkOrder.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| work_order_id | UUID | FK → WorkOrder |
| vendor_id | UUID | FK → Vendor |
| status | varchar | enum: pending/assigned/accepted/en_route/on_site/completed/cancelled |
| estimated_cost | decimal | nullable, vendor-provided estimate |
| final_cost | decimal | nullable, actual cost after completion |
| estimated_arrival_at | timestamp | nullable |
| actual_arrival_at | timestamp | nullable |
| completed_at | timestamp | nullable |
| notes | text | nullable |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

### CostEstimate
A proposed or actual cost for a WorkOrder.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| dispatch_id | UUID | FK → Dispatch |
| line_items | JSONB | array of {description, amount, type} |
| total | decimal | computed sum of line items |
| status | varchar | enum: pending/approved/rejected/revised |
| approved_by_id | UUID | FK → User (property manager), nullable |
| approved_at | timestamp | nullable |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

### AuditLog
Append-only record of all state-changing actions.

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → Tenant, RLS |
| actor_id | UUID | who performed the action |
| actor_role | varchar | tenant/property_manager/maintenance_coordinator/vendor |
| action | varchar | e.g., work_order.submitted, dispatch.confirmed |
| entity_type | varchar | e.g., WorkOrder, Dispatch |
| entity_id | UUID | the affected entity |
| previous_state | JSONB | snapshot before change |
| new_state | JSONB | snapshot after change |
| timestamp | timestamp | auto |

## State Transition Diagram

```text
WorkOrder:
  submitted ──→ classified ──→ troubleshooting ──→ dispatched ──→ in_progress ──→ completed
       │              │               │                                      │
       │              │               └── (escalate to dispatch if           │
       │              │                    self-serve fails)                  │
       │              │                                                      │
       └── (emergency override: skip to dispatch immediately)

Dispatch:
  pending ──→ assigned ──→ accepted ──→ en_route ──→ on_site ──→ completed
       │                                                     │
       └── (timeout → next vendor)      cancelled ──────────┘
```

## Indexing Strategy

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| WorkOrder | (tenant_id, status) | B-tree | Dashboard queries by status |
| WorkOrder | (tenant_id, created_at DESC) | B-tree | Recent requests listing |
| WorkOrder | (property_id, status) | B-tree | Property-specific views |
| WorkOrder | description_embedding | HNSW (pgvector) | Cosine similarity duplicate search (≥0.85) |
| WorkOrder | image_embedding | HNSW (pgvector) | Image-based duplicate search |
| MediaAsset | (work_order_id) | B-tree | Media lookup per work order |
| MediaAsset | (soft_deleted_at) | B-tree | Erasure SLA scheduler |
| TriageResult | (work_order_id) | unique | 1:1 lookup |
| Vendor | (trades, coverage_areas) | GIN | Trade/area matching queries |
| Dispatch | (vendor_id, status) | B-tree | Vendor workload queries |
| AuditLog | (tenant_id, entity_type, entity_id) | B-tree | Audit trail lookup |
| AuditLog | (created_at) | B-tree | Time-range audit queries |

## Soft-Delete & Erasure Flow

All tenant-scoped entities (`WorkOrder`, `MediaAsset`, `TenantProfile`,
`AuditLog`) carry `soft_deleted_at` + `hard_delete_at` columns. The
`hard_delete_at` is scheduled to `soft_deleted_at + 30 days` at the time
of soft-delete. A daily Celery beat task scans for `hard_delete_at <= now`
records and executes hard deletes (with tombstone rows written to
`AuditLog` for referential integrity). Blob lifecycle policies enforce the
same window for media in Azure Blob Storage.

Tombstones preserve the audit trail (`AuditLog` is itself append-only and
not subject to erasure of historical entries per FR-014).

## Data Volume Estimates

| Entity | MVP Volume | Growth (12mo) |
|--------|-----------|----------------|
| Tenant | 5–25 | 50–100 |
| Property | 100–500 | 500–2,000 |
| WorkOrder | 500–5,000/mo | 5,000–50,000/mo |
| TriageResult | = WorkOrder | = WorkOrder |
| Vendor | 50–200 | 200–1,000 |
| Dispatch | = WorkOrder | = WorkOrder |
| AuditLog | 5× WorkOrder | 5× WorkOrder |

Using UUID primary keys. PostgreSQL can handle this volume without sharding.
Partition WorkOrder and AuditLog by month at 50,000+ monthly records.
