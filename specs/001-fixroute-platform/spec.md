# Feature Specification: FixRoute Platform

**Feature Branch**: `001-fixroute-platform`

**Created**: 2026-07-01

**Status**: Draft

**Input**: User description: "FixRoute PRD — AI maintenance triage that classifies requests, troubleshoots, and dispatches the right vendor."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tenant submits maintenance request with AI triage (Priority: P1)

A tenant submits a maintenance request (text description and optionally a photo
or voice recording). The system automatically classifies the issue type and
urgency, and immediately provides self-serve troubleshooting steps when the
issue is simple. If the issue cannot be resolved by the tenant, the system
queues it for vendor dispatch with the correct priority.

**Why this priority**: This is the core intake and triage flow — without it,
the product has no purpose. It is the first interaction every user has with the
system and must deliver immediate value by reducing manual triage effort.

**Independent Test**: A property manager can submit a sample "leaking faucet"
request with a photo, verify the system classifies it as "plumbing / non-urgent",
and see troubleshooting steps returned within 5 seconds — all without involving
a human dispatcher.

**Acceptance Scenarios**:

1. **Given** a tenant submits a maintenance request with text and a photo,
   **When** the system processes the submission, **Then** the request is
   classified by issue category and urgency, and the tenant receives an
   immediate acknowledgment with expected next steps.
2. **Given** a submitted request is classified as low urgency and type matches
   a known self-serve pattern (e.g., resetting a circuit breaker),
   **When** the system processes it, **Then** step-by-step troubleshooting
   guidance is shown to the tenant before any dispatch occurs.
3. **Given** a submitted request with text indicating an emergency (e.g., gas
   leak, flooding), **When** the system processes it, **Then** it is marked as
   highest urgency and a human dispatcher is notified via push notification
   and SMS with a 2-minute acknowledgment SLA, bypassing self-serve. If
   unacknowledged, the system auto-rotates to a backup dispatcher.

---

### User Story 2 - Vendor matching and dispatch with status tracking (Priority: P2)

The system matches the classified issue to the best available vendor based on
trade, location, and response-time requirements. The vendor receives the work
order with all context (photos, tenant notes, urgency). The property manager
and tenant receive status updates throughout the lifecycle.

**Why this priority**: After triage, the second most critical step is getting
the right vendor to the right place. This story closes the loop from intake to
resolution.

**Independent Test**: A property manager can see the system recommend 3 plumbing
vendors for a non-urgent leak, select one, confirm dispatch, and receive an ETA
— all from a single dashboard without phone calls.

**Acceptance Scenarios**:

1. **Given** a triaged work order for a specific trade and location,
   **When** the system queries available vendors, **Then** it returns a ranked
   list of matches showing proximity, availability, and cost estimate.
2. **Given** a property manager selects a vendor and approves dispatch,
   **When** the dispatch is confirmed, **Then** the vendor receives the full
   work order and both tenant and property manager receive a status update with
   ETA.
3. **Given** a dispatched work order, **When** the vendor updates the status
   (en route, on site, completed), **Then** all relevant parties are notified.

---

### User Story 3 - Cost estimate, approval, and spend analytics (Priority: P3)

Before work begins, the vendor provides a cost estimate. The property manager
reviews and approves it or requests adjustments. After completion, the actual
cost is recorded and spend analytics show trends across properties, trades,
and time periods.

**Why this priority**: Cost control and analytics are important for the
product's subscription value proposition but can follow after the core triage
and dispatch flows are proven.

**Independent Test**: A property manager can approve an estimate from a vendor,
receive the final invoice after work completes, and view a monthly spend report
broken down by property and trade — without manual spreadsheet tracking.

**Acceptance Scenarios**:

1. **Given** a vendor has been dispatched and provides a cost estimate,
   **When** the property manager reviews it, **Then** they can approve, reject,
   or request revision with comments.
2. **Given** an approved estimate and completed work, **When** the vendor marks
   the work order complete with final costs, **Then** the system records the
   actual spend and notifies the property manager.
3. **Given** completed work orders across properties and time, **When** a
   property manager requests a spend report, **Then** the system displays
   aggregated spend by property, trade, and period with trends.

---

### User Story 4 - Compliance, retention, and erasure (Priority: P2) 🔒

Tenants and property managers can submit GDPR/CCPA right-to-erasure requests.
Affected work orders, media assets, and tenant profiles are soft-deleted
immediately and hard-deleted within 30 days. Operational data is retained
for 7 years to satisfy landlord-tenant and tax recordkeeping obligations,
with tombstone audit-log entries preserving referential integrity after
hard-delete.

**Why this priority**: GDPR/CCPA non-compliance is a blocking business
risk — a single missing erasure SLA is a regulatory violation. This story
must ship with US1 to make the MVP production-ready.

**Independent Test**: A tenant submits an erasure request; affected
WorkOrder and MediaAsset records show `soft_deleted_at` set with
`hard_delete_at` scheduled 30 days out; the daily erasure sweep task
hard-deletes records past the window; tombstone entries in the audit log
remain visible for compliance reporting.

**Acceptance Scenarios**:

1. **Given** a tenant submits an erasure request via the API, **When** the
   system processes the request, **Then** all WorkOrder, MediaAsset, and
   TenantProfile records for that subject are soft-deleted immediately and
   `hard_delete_at` is scheduled exactly 30 days out.
2. **Given** a soft-deleted record past its 30-day hard-delete window,
   **When** the daily erasure sweep task runs, **Then** the record is
   hard-deleted and a tombstone entry is written to the audit log preserving
   the original entity reference.
3. **Given** a non-erased operational record (work order, cost estimate,
   audit log), **When** the system checks its age, **Then** the record is
   retained for 7 years from creation regardless of any subsequent subject
   erasure of related personal data.

---

### Edge Cases

- What happens when the AI cannot confidently classify an issue? The system
  falls back to a human dispatcher with all available context.
- How does the system handle a vendor that does not respond to a dispatch
  request? After a configurable timeout, the next-ranked vendor is notified.
- What happens when a tenant submits a duplicate request for the same issue?
  The system computes combined text + image embeddings, performs pgvector
  cosine similarity search against open and recent (≤14 day) work orders for
  the same tenant/property, and prompts the tenant to follow up on the
  existing request when similarity ≥0.85.
- How are emergency requests handled outside business hours? Emergency priority
  always reaches a human dispatcher via push and SMS regardless of time,
  location, or vendor availability, with 2-min acknowledgment SLA and
  auto-rotation to backup dispatchers.
- What happens if the AI self-serve guidance does not resolve the issue? The
  system seamlessly escalates to dispatch without requiring the tenant to
  re-enter information.

## Clarifications

### Session 2026-07-02 (round 2)

- Q: Data retention & right-to-erasure policy → A: 7-year operational retention, soft-delete with 30-day hard-delete SLA on erasure request
- Q: Disaster recovery RTO/RPO targets → A: RTO 4h, RPO 15min, multi-region with active-passive failover
- Q: SMS / push notification provider → A: Azure Communication Services (ACS) for SMS; native APNs + FCM for mobile/web push
- Q: Photo/voice media storage backend → A: Azure Blob Storage with SAS-token access and lifecycle tiering (Hot → Cool → Archive)
- Q: Duplicate work-order detection mechanism → A: pgvector cosine similarity over text + image embeddings with threshold ≥0.85

### Session 2026-07-02

- Q: OIDC/OAuth2 authentication provider → A: Azure AD (Entra ID)
- Q: Vendor matching criteria weighting → A: Weighted scoring model (configurable weights across proximity, availability, rating, cost, response time)
- Q: Feature-level SLO targets → A: Differentiated SLOs: Triage API 99.95%, Dispatch 99.9%, Analytics 99.5%
- Q: AI confidence threshold management → A: Per-tenant DB setting with admin UI
- Q: Emergency notification escalation path → A: Push + SMS, 2-min ack SLA, auto-rotate to backup dispatcher

### Session 2026-07-01

- Q: User roles and permissions model → A: 4 roles: tenant, property manager, maintenance coordinator, vendor — each with distinct permissions.
- Q: WorkOrder state machine → A: 6 states: submitted → classified → troubleshooting → dispatched → in_progress → completed.
- Q: Notification channels → A: Email + SMS + in-app notifications.
- Q: Data volume / scale targets → A: 100-500 properties, 500-5,000 work orders/month.
- Q: Voice intake mechanism → A: Audio recording uploaded as file, transcribed server-side via ASR.

## Requirements *(mandatory)*

### User Roles

The system has four distinct user roles with scope-based permissions:

- **Tenant**: Submits maintenance requests, receives status updates, follows
  self-serve troubleshooting.
- **Property Manager**: Oversees properties, reviews estimates, approves
  dispatch and costs, views spend analytics.
- **Maintenance Coordinator**: Day-to-day triage queue management, vendor
  communication, status tracking, emergency escalation.
- **Vendor**: Receives work orders, provides cost estimates, updates dispatch
  and completion status.

### Functional Requirements

- **FR-001**: System MUST allow tenants to submit maintenance requests via text
  description, optional photo attachments, and optional voice recording.
- **FR-002**: System MUST classify each request by issue category (plumbing,
  electrical, HVAC, structural, appliance, general) and urgency level
  (emergency, urgent, routine, low).
- **FR-003**: System MUST provide self-serve troubleshooting steps for requests
  classified as low urgency with known fix patterns.
- **FR-004**: System MUST escalate to human dispatch automatically when the AI
  confidence falls below a per-tenant configurable threshold stored in the
  database and adjustable via the property manager admin UI.
- **FR-005**: System MUST match work orders to vendors using a weighted scoring
  model across trade match, geographic proximity, availability, rating, cost
  estimate, and response-time requirements with configurable weights.
- **FR-006**: System MUST support a dispatch approval flow where property
  managers review vendor matches, select a vendor, and confirm dispatch.
- **FR-007**: System MUST send status notifications (submitted, classified,
  dispatched, en route, on site, completed) to relevant parties via email,
  SMS, and in-app notifications based on role and urgency, delivered via
  Azure Communication Services (ACS) for SMS, native APNs/FCM for push, and
  an email service provider for transactional email.
- **FR-008**: System MUST support vendor-provided cost estimates with property
  manager approval, rejection, or revision workflow.
- **FR-009**: System MUST record actual costs against estimates when work is
  completed and track variance.
- **FR-010**: System MUST provide spend analytics aggregated by property, trade,
  vendor, and time period with trend visualization.
- **FR-011**: System MUST isolate all data per Tenant (property management
  company) to prevent cross-Tenant data leakage. TenantProfile (resident)
  records are scoped to a single Property within one Tenant.
- **FR-012**: System MUST log all state-changing actions with actor identity,
  timestamp, and previous/current state for audit trail.
- **FR-013**: System MUST authenticate all users via Azure AD (Entra ID) using
  OIDC/OAuth2 with role-based access control mapped to the four user roles
  (tenant, property manager, maintenance coordinator, vendor).
- **FR-014**: System MUST retain operational records (work orders, cost
  estimates, dispatch history, audit logs) for 7 years to satisfy
  landlord-tenant and tax recordkeeping obligations. Personal data MUST be
  soft-deleted on erasure request and hard-deleted within 30 days of the
  request, with referential integrity preserved during the SLA window via
  tombstone records for audit trail continuity.
- **FR-015**: System MUST store photo and voice-recording media in Azure Blob
  Storage, accessed via short-lived SAS tokens scoped per-request to enforce
  tenant isolation. Blob lifecycle policies MUST tier media Hot → Cool →
  Archive aligned to the 7-year retention window, and soft-delete + immutable
  blob policies MUST support the 30-day erasure SLA.

### Key Entities *(include if feature involves data)*

- **WorkOrder**: Represents a maintenance request from initial submission
  through completion. Key attributes: issue description, media attachments
  (photos, voice recording stored in object storage with SAS-token access),
  status, priority, timestamps. Lifecycle states: submitted → classified →
  troubleshooting → dispatched → in_progress → completed. Relates to Property
  and Tenant.
- **TriageResult**: The AI classification outcome for a WorkOrder. Contains
  category, urgency level, confidence score, and suggested troubleshooting.
- **Vendor**: A service provider with trade specialties, coverage areas,
  availability schedule, and rating history.
- **Dispatch**: The assignment of a Vendor to a WorkOrder. Tracks assignment
  status, ETA, actual arrival, and completion times.
- **Property**: The physical unit or building under management. Contains
  address, unit details, and tenant roster.
- **CostEstimate**: A proposed cost from a Vendor for a WorkOrder. Contains
  line items, total, status (pending/approved/rejected), and actual final cost.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Time from tenant submission to dispatch decision is under
  5 minutes for urgent requests and under 30 minutes for routine requests.
- **SC-002**: At least 30% of low-urgency requests are resolved via self-serve
  troubleshooting without requiring vendor dispatch.
- **SC-003**: Emergency mis-triage rate (non-emergency marked as emergency or
  vice versa) is below 2% of all classified requests.
- **SC-004**: Property managers report at least 40% reduction in time spent on
  manual triage and dispatch coordination within 3 months of adoption.
- **SC-005**: Uptime SLOs by feature — Triage API: 99.95%, Dispatch: 99.9%,
  Analytics/Reporting: 99.5% — measured on a rolling 30-day window.
- **SC-006**: 100% of GDPR/CCPA erasure requests MUST be hard-deleted within
  30 days of submission, verified by automated tombstone reconciliation jobs.
- **SC-007**: Disaster recovery objectives — RTO of 4 hours and RPO of 15
  minutes — validated by quarterly failover drills restoring the Triage API,
  Dispatch, and Analytics services in a passive region.

## Assumptions

- Tenants have access to a smartphone or computer with a web browser to submit
  requests and photos.
- Property managers administer the system during standard business hours;
  emergency alerts bypass this assumption.
- Vendors maintain availability data and respond to dispatch notifications
  within configured time windows.
- Third-party property management system integration (AppFolio, Buildium) is
  out of scope for the initial release but anticipated for phase 2.
- Mobile native applications are out of scope for MVP; the system is accessed
  via responsive web interface.
- The system is cloud-hosted (not on-premises) for the initial release.
- AI classification accuracy improves over time via feedback loops and
  evaluation-driven tuning.
- MVP targets 100-500 properties under management with 500-5,000 work orders
  per month; architecture must scale beyond these targets without redesign.
- Operational data retention is 7 years (landlord-tenant + tax recordkeeping);
  personal data erasure follows a 30-day hard-delete SLA after soft-delete.
- Production deployment targets multi-region active-passive with RTO 4h and
  RPO 15min, validated by quarterly failover drills.
