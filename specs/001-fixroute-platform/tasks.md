---

description: "Task list for FixRoute Platform implementation"

---

# Tasks: FixRoute Platform

**Input**: Design documents from `specs/001-fixroute-platform/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The spec mandates unit, integration, contract, and AI eval tests per the constitution (Principle III). Test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/` at repository root
- **Backend apps**: `backend/apps/intake/`, `backend/apps/triage/`, `backend/apps/dispatch/`, `backend/apps/vendormanagement/`, `backend/apps/analytics/`
- **AI service**: `backend/ai/`
- **Common**: `backend/common/`
- **Frontend**: `frontend/src/`
- **Infrastructure**: `infra/`
- **Tests**: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend Django project with `backend/config/settings/base.py`, `dev.py`, `prod.py` and pyproject.toml
- [x] T002 [P] Create frontend Vue.js 3 project with Vite, Pinia, Vue Router in `frontend/`
- [x] T003 [P] Create infrastructure directory structure at `infra/terraform/`, `infra/k8s/`, `infra/helm/`
- [x] T004 [P] Create `backend/requirements/base.txt`, `dev.txt`, `prod.txt` with Django, DRF, Celery, psycopg2, django-guardian, drf-spectacular, structlog
- [x] T005 [P] Configure ruff (linting) and mypy (type checking) in `backend/pyproject.toml`
- [x] T006 [P] Configure ESLint and Prettier for Vue.js frontend
- [x] T007 Create `docker-compose.yml` at repo root with PostgreSQL 16+pgvector, Redis 7 services
- [x] T008 [P] Create `.github/workflows/ci.yml` with lint → test → build pipeline

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Implement Tenant model and RLS middleware in `backend/apps/intake/models.py` and `backend/common/middleware/tenant.py`
- [x] T010 [P] Implement OIDC/OAuth2 authentication backend in `backend/common/auth/backends.py`
- [x] T011 [P] Implement RBAC permission system with django-guardian in `backend/common/auth/permissions.py`
- [x] T012 [P] Implement AuditLog model and auto-logging middleware in `backend/common/middleware/audit.py`
- [x] T013 [P] Configure structlog for structured JSON logging (NDJSON, daily rotation) in `backend/common/logging/config.py`
- [x] T014 [P] Configure Celery with Redis broker in `backend/config/celery.py`
- [x] T015 [P] Configure OpenTelemetry instrumentation for Django, Celery, PostgreSQL in `backend/common/telemetry.py`
- [x] T016 [P] Create Django app skeleton for all 5 bounded contexts (`intake`, `triage`, `dispatch`, `vendormanagement`, `analytics`)
- [x] T017 Create `backend/Dockerfile` with multi-stage build for Django application
- [x] T018 [P] Create `frontend/Dockerfile` for Vue.js SPA with Nginx
- [x] T019a [P] Implement soft-delete + hard-delete columns migration on all tenant-scoped models in `backend/common/db/soft_delete.py`
- [x] T019b [P] Implement daily Celery beat task for erasure sweep in `backend/common/tasks/erasure.py`
- [x] T019c [P] Configure Azure Blob Storage client and SAS-token generator in `backend/common/storage/blob.py`
- [x] T019d [P] Configure Azure Communication Services (ACS) client in `backend/common/notifications/acs.py`
- [x] T019e [P] Configure native APNs/FCM push client in `backend/common/notifications/push.py`
- [x] T019f [P] Enable pgvector extension and HNSW indexes in initial migration in `backend/apps/intake/migrations/0001_pgvector.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Tenant submits maintenance request with AI triage (Priority: P1) 🎯 MVP

**Goal**: A tenant can submit a maintenance request (text/photo/voice), the system classifies it by category and urgency, provides self-serve troubleshooting for simple issues, and escalates to dispatch when needed.

**Independent Test**: A property manager can submit a "leaking faucet" request with a photo, verify the system classifies it as "plumbing / non-urgent", and see troubleshooting steps returned within 5 seconds.

### Tests for User Story 1

- [x] T019 [P] [US1] Contract test for `POST /api/v1/work-orders` in `tests/contract/test_work_order_create.py`
- [x] T020 [P] [US1] Contract test for `GET /api/v1/work-orders/{id}/triage` in `tests/contract/test_triage.py`
- [x] T020a [P] [US1] Contract test for `GET /api/v1/work-orders/{id}/duplicates` in `tests/contract/test_duplicates.py`
- [x] T021 [P] [US1] Integration test for intake-to-classification flow in `tests/integration/test_intake_triage_flow.py`
- [x] T022 [P] [US1] Integration test for self-serve troubleshooting escalation in `tests/integration/test_troubleshooting_escalation.py`
- [x] T022a [P] [US1] Integration test for pgvector duplicate detection in `tests/integration/test_duplicate_detection.py`
- [x] T022b [P] [US1] Integration test for media upload to Azure Blob with SAS in `tests/integration/test_media_upload.py`
- [x] T023 [P] [US1] AI eval test for classification accuracy in `tests/eval/test_classification_accuracy.py`

### Implementation for User Story 1

- [x] T024 [P] [US1] Create Property, TenantProfile models in `backend/apps/intake/models.py`
- [x] T025 [P] [US1] Create WorkOrder model in `backend/apps/intake/models.py` (with description_embedding, image_embedding, soft_deleted_at, hard_delete_at)
- [x] T025a [P] [US1] Create MediaAsset model in `backend/apps/intake/models.py` (Azure Blob storage with lifecycle tier field)
- [x] T026 [P] [US1] Create TriageResult model in `backend/apps/triage/models.py`
- [x] T027 [P] [US1] Create Property, TenantProfile serializers in `backend/apps/intake/api/serializers.py`
- [x] T028 [P] [US1] Create WorkOrder serializer in `backend/apps/intake/api/serializers.py` (returning SAS-token URLs for media)
- [x] T028a [P] [US1] Create MediaAsset serializer and SAS-token URL helper in `backend/apps/intake/api/serializers.py`
- [x] T029 [US1] Implement WorkOrderService.submit() in `backend/apps/intake/services.py` (uploads media to Azure Blob, computes embeddings, persists soft-delete timestamps)
- [x] T029a [US1] Implement DuplicateDetectionService.find_similar() with pgvector cosine ≥0.85 in `backend/apps/intake/services.py`
- [x] T030 [US1] Implement WorkOrderService.list() with cursor pagination in `backend/apps/intake/services.py`
- [x] T030a [US1] Implement WorkOrderService.soft_delete() and schedule hard_delete_at in `backend/apps/intake/services.py`
- [x] T031 [US1] Implement work order create/list viewsets in `backend/apps/intake/api/views.py`
- [x] T031a [US1] Implement `GET /api/v1/work-orders/{id}/duplicates` viewset in `backend/apps/intake/api/views.py`
- [x] T032 [US1] Configure URL routing for intake endpoints in `backend/apps/intake/api/urls.py`
- [x] T033 [P] [US1] Create AI classification service in `backend/ai/classification/classifier.py`
- [x] T033a [P] [US1] Create embedding service (text + CLIP image) in `backend/ai/embeddings/embedder.py`
- [x] T034 [P] [US1] Create AI troubleshooting service in `backend/ai/troubleshooting/knowledge_base.py`
- [x] T035 [US1] Implement TriageService.classify() in `backend/apps/triage/services.py`
- [x] T035a [US1] Implement per-tenant confidence threshold gate in `backend/apps/triage/services.py` (returns fallback-to-dispatcher when confidence < tenant.threshold)
- [x] T036 [US1] Implement TriageService.get_troubleshooting() in `backend/apps/triage/services.py`
- [x] T037 [US1] Wire triage into intake flow (auto-classify on submission) in `backend/apps/intake/services.py`
- [x] T037a [US1] Wire duplicate detection into intake flow (return match before creating new WorkOrder) in `backend/apps/intake/services.py`
- [x] T038 [P] [US1] Create Vue.js API client service in `frontend/src/services/api.ts`
- [x] T039 [P] [US1] Create request submission page in `frontend/src/pages/RequestSubmit.vue`
- [x] T039a [P] [US1] Create duplicate-match prompt page in `frontend/src/pages/DuplicateMatch.vue`
- [x] T040 [P] [US1] Create request status page in `frontend/src/pages/RequestStatus.vue`
- [x] T041 [US1] Create Pinia store for work orders in `frontend/src/stores/workorder.ts`
- [x] T042 [US1] Configure Vue Router with submission and status routes in `frontend/src/router/index.ts`
- [x] T043 [P] [US1] Create audio recording component in `frontend/src/components/AudioRecorder.vue`
- [x] T044 [US1] Add logging for user story 1 operations (intake, classification, troubleshooting, duplicate, media)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. A tenant can submit a request, see it classified, receive troubleshooting steps, and escalate if needed.

---

## Phase 4: User Story 2 - Vendor matching and dispatch with status tracking (Priority: P2)

**Goal**: The system matches the classified issue to the best available vendor by trade, location, and response-time. The vendor receives the work order, the property manager approves dispatch, and all parties receive status updates.

**Independent Test**: A property manager can see the system recommend 3 plumbing vendors for a non-urgent leak, select one, confirm dispatch, and receive an ETA.

### Tests for User Story 2

- [x] T045 [P] [US2] Contract test for `GET /api/v1/work-orders/{id}/match-vendors` in `tests/contract/test_vendor_match.py`
- [x] T046 [P] [US2] Contract test for `POST /api/v1/work-orders/{id}/dispatch` in `tests/contract/test_dispatch.py`
- [x] T047 [P] [US2] Contract test for `PATCH /api/v1/dispatches/{id}/status` in `tests/contract/test_dispatch_status.py`
- [x] T048 [P] [US2] Integration test for dispatch flow in `tests/integration/test_dispatch_flow.py`
- [x] T049 [P] [US2] Integration test for vendor ranking in `tests/integration/test_vendor_ranking.py`
- [x] T050 [P] [US2] Integration test for notification delivery in `tests/integration/test_notifications.py`

### Implementation for User Story 2

- [x] T051 [P] [US2] Create Vendor model in `backend/apps/vendormanagement/models.py`
- [x] T052 [P] [US2] Create Dispatch model in `backend/apps/dispatch/models.py`
- [x] T053 [P] [US2] Create Vendor serializer in `backend/apps/vendormanagement/api/serializers.py`
- [x] T054 [P] [US2] Create Dispatch serializer in `backend/apps/vendormanagement/api/serializers.py`
- [x] T055 [US2] Implement VendorService.match() with trade/area/proximity ranking in `backend/apps/vendormanagement/services.py`
- [x] T056 [US2] Implement DispatchService.create() in `backend/apps/dispatch/services.py`
- [x] T056a [US2] Implement dispatch approval gate in `backend/apps/dispatch/services.py` requiring `property_manager` role and an approval token
- [x] T056b [P] [US2] Create dispatch review/approval page in `frontend/src/pages/DispatchReview.vue`
- [x] T057 [US2] Implement DispatchService.update_status() in `backend/apps/dispatch/services.py`
- [x] T058 [US2] Implement DispatchService.escalate_on_timeout() in `backend/apps/dispatch/services.py`
- [x] T059 [US2] Create vendor list/match viewsets in `backend/apps/vendormanagement/api/views.py`
- [x] T060 [US2] Create dispatch viewsets in `backend/apps/dispatch/api/views.py`
- [x] T061 [US2] Configure URL routing for vendor and dispatch endpoints
- [x] T062 [P] [US2] Implement notification service (email + ACS SMS + APNs/FCM push + in-app) in `backend/common/notifications/service.py`
- [x] T062a [P] [US2] Implement ACS SMS adapter in `backend/common/notifications/acs.py`
- [x] T062b [P] [US2] Implement APNs/FCM push adapter in `backend/common/notifications/push.py`
- [x] T063 [P] [US2] Create Celery tasks for async notification dispatch in `backend/common/tasks/notifications.py`
- [x] T064 [P] [US2] Create Vue.js vendor management page in `frontend/src/pages/VendorManagement.vue`
- [x] T065 [P] [US2] Create Vue.js dispatch workflow page in `frontend/src/pages/DispatchWorkflow.vue`
- [x] T066 [US2] Create Pinia store for vendors and dispatches in `frontend/src/stores/vendor.ts` and `frontend/src/stores/dispatch.ts`
- [x] T067 [US2] Add dispatch and vendor routes to Vue Router
- [x] T068 [US2] Add logging for user story 2 operations (dispatch, notification)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Requests flow from intake through triage to vendor dispatch with notifications.

---

## Phase 5: User Story 3 - Cost estimate, approval, and spend analytics (Priority: P3)

**Goal**: Vendors provide cost estimates, property managers approve/reject with comments, actual costs are recorded on completion, and spend analytics show trends by property, trade, and vendor.

**Independent Test**: A property manager can approve an estimate from a vendor, receive the final invoice after work completes, and view a monthly spend report broken down by property and trade.

### Tests for User Story 3

- [x] T069 [P] [US3] Contract test for `POST /api/v1/dispatches/{id}/estimate` in `tests/contract/test_estimate.py`
- [x] T070 [P] [US3] Contract test for `POST /api/v1/estimates/{id}/approve` in `tests/contract/test_estimate_review.py`
- [x] T071 [P] [US3] Contract test for `GET /api/v1/analytics/spend` in `tests/contract/test_spend_analytics.py`
- [x] T072 [P] [US3] Integration test for estimate-to-completion flow in `tests/integration/test_estimate_flow.py`

### Implementation for User Story 3

- [x] T073 [P] [US3] Create CostEstimate model in `backend/apps/vendormanagement/models.py`
- [x] T074 [P] [US3] Create CostEstimate serializer in `backend/apps/vendormanagement/api/serializers.py`
- [x] T075 [US3] Implement EstimateService.submit() in `backend/apps/dispatch/services.py`
- [x] T076 [US3] Implement EstimateService.review() with approve/reject/revision in `backend/apps/dispatch/services.py`
- [x] T077 [US3] Implement AnalyticsService.get_spend() in `backend/apps/analytics/services.py`
- [x] T078 [US3] Create estimate viewsets in `backend/apps/dispatch/api/views.py`
- [x] T079 [US3] Create analytics viewsets in `backend/apps/analytics/api/views.py`
- [x] T080 [US3] Configure URL routing for estimate and analytics endpoints
- [x] T081 [P] [US3] Create Vue.js estimate review page in `frontend/src/pages/EstimateReview.vue`
- [x] T082 [P] [US3] Create Vue.js analytics dashboard page in `frontend/src/pages/AnalyticsDashboard.vue`
- [x] T083 [US3] Create Pinia store for estimates and analytics in `frontend/src/stores/estimate.ts` and `frontend/src/stores/analytics.ts`
- [x] T084 [US3] Add estimate and analytics routes to Vue Router
- [x] T085 [US3] Add logging for user story 3 operations (estimates, analytics)
- [x] T085v [US3] Implement EstimateService.record_completion() persisting variance = final_cost - estimated_total in `backend/apps/dispatch/services.py`
- [x] T085w [P] [US3] Add variance field to CostEstimate model and serializer in `backend/apps/vendormanagement/models.py` and `backend/apps/vendormanagement/api/serializers.py`
- [x] T085x [P] [US3] Add variance column to estimate review page in `frontend/src/pages/EstimateReview.vue`

**Checkpoint**: All user stories should now be independently functional. The complete workflow from submission through cost tracking and analytics is operational.

---

## Phase 6: User Story 4 - Compliance, retention, and erasure (Priority: P2) 🔒

**Goal**: Tenants and property managers can submit GDPR/CCPA erasure requests, the system soft-deletes affected records immediately, hard-deletes them within 30 days, and reconciles the SLA via automated jobs. Operational data is retained for 7 years per landlord-tenant and tax recordkeeping obligations.

**Independent Test**: A tenant can submit an erasure request, the affected work orders and media show `soft_deleted_at` set with `hard_delete_at` scheduled 30 days out, the daily erasure sweep task hard-deletes them past the window, and tombstone audit-log entries remain for referential integrity.

### Tests for User Story 4

- [ ] T085a [P] [US4] Contract test for `POST /api/v1/erasure-requests` in `tests/contract/test_erasure.py`
- [ ] T085b [P] [US4] Integration test for soft-delete cascade in `tests/integration/test_soft_delete_cascade.py`
- [ ] T085c [P] [US4] Integration test for 30-day hard-delete sweep in `tests/integration/test_erasure_sweep.py`
- [ ] T085d [P] [US4] Integration test for tombstone audit-log retention in `tests/integration/test_erasure_audit_trail.py`
- [ ] T085e [P] [US4] Compliance test verifying 7-year retention for non-erased records in `tests/integration/test_retention_window.py`

### Implementation for User Story 4

- [ ] T085f [P] [US4] Create ErasureRequest model in `backend/apps/compliance/models.py` (new bounded context)
- [ ] T085g [P] [US4] Create Django app skeleton for `compliance` bounded context
- [ ] T085h [US4] Implement ErasureService.submit() in `backend/apps/compliance/services.py` (soft-deletes WorkOrder, MediaAsset, TenantProfile; schedules hard_delete_at = now + 30d)
- [ ] T085i [US4] Implement ErasureService.sweep() in `backend/apps/compliance/services.py` (called by daily Celery beat; hard-deletes past-window records; writes tombstones to AuditLog)
- [ ] T085j [US4] Implement erasure request viewset in `backend/apps/compliance/api/views.py`
- [ ] T085k [US4] Configure URL routing for `/api/v1/erasure-requests` in `backend/apps/compliance/api/urls.py`
- [ ] T085l [P] [US4] Create Azure Blob lifecycle policy Terraform in `infra/terraform/blob_lifecycle.tf` (Hot ≤30d, Cool 30d-1y, Archive 1-7y)
- [ ] T085m [P] [US4] Configure Azure Blob soft-delete + immutable blob policy in `infra/terraform/blob_erasure.tf`
- [ ] T085n [US4] Add retention policy documentation in `docs/compliance/retention.md`
- [ ] T085o [US4] Add logging for erasure events (submit, sweep, hard_delete) with tenant_id, request_id correlation
- [ ] T085p [US4] Implement tombstone reconciliation job in `backend/common/tasks/reconciliation.py` (verifies every ErasureRequest has a corresponding AuditLog tombstone within 30 days; alerts on SLA breach)

**Checkpoint**: Erasure SLA is enforceable end-to-end with audit-trail continuity; 7-year retention is preserved for non-erased records.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, multi-region DR posture, and operational readiness

- [ ] T086 [P] Run quickstart.md validation scenarios end-to-end (all 10 scenarios)
- [ ] T087 [P] Security review: verify RLS on all tenant-scoped tables, OIDC config, secret scanning
- [ ] T088 [P] Performance load test: verify p95 < 200ms read, < 400ms write targets
- [ ] T089 [P] Infrastructure: apply Terraform for AKS, PostgreSQL, Redis, ACS, Blob Storage in `infra/terraform/`
- [ ] T090 [P] Infrastructure: apply Kubernetes manifests for backend, frontend, AI service in `infra/k8s/`
- [ ] T091 [P] Add Helm charts for backend and frontend deployments in `infra/helm/`
- [ ] T092 [P] Run AI eval suite (classification accuracy, troubleshooting relevance) in `tests/eval/`
- [ ] T093 [P] Create Grafana dashboards for RED/USE metrics and business KPIs
- [ ] T094 [P] Create runbooks for common operational scenarios (vendor timeout, AI failure, tenant isolation breach)
- [ ] T095 [P] Run SQL migration dry-run on staging to verify backward-compatible changes
- [ ] T095a [P] Implement `GET /api/v1/health` endpoint returning component status and active region in `backend/apps/operations/api/views.py`
- [ ] T095b [P] Configure Azure PostgreSQL flexible server cross-region read replica in `infra/terraform/postgres_replica.tf`
- [ ] T095c [P] Configure AKS active-passive cluster pair (primary + secondary) in `infra/terraform/aks_multi_region.tf`
- [ ] T095d [P] Configure Azure Blob GRS (geo-redundant storage) for media in `infra/terraform/blob_grs.tf`
- [ ] T095e [P] Configure Traffic Manager or Front Door with active-passive routing in `infra/terraform/traffic_manager.tf`
- [ ] T095f [P] Implement automated failover runbook script in `infra/scripts/failover.sh`
- [ ] T095g [P] Schedule quarterly DR drill with RTO 4h / RPO 15min validation in `infra/scripts/dr_drill.sh`
- [ ] T095h [P] Configure SLO alerting in Azure Monitor (Triage 99.95%, Dispatch 99.9%, Analytics 99.5%) in `infra/terraform/slo_alerts.tf`
- [ ] T095i [P] Add pgvector HNSW index maintenance Celery beat task in `backend/common/tasks/pgvector_maintenance.py`
- [ ] T095j [P] Instrument SLO measurement pipeline (Triage/Dispatch/Analytics p95 + success rate Prometheus exporters) in `backend/common/slo/metrics.py`
- [ ] T095k [P] Implement DR drill report generation in `infra/scripts/dr_drill_report.sh` (output: measured RTO/RPO vs target)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US2 can start in parallel after US1's WorkOrder and TriageResult models exist
  - US3 can start after US2's Dispatch model exists
  - US4 (Compliance) can start in parallel with US2/US3 once soft-delete columns and Azure Blob/ACS clients are configured in Foundational
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2). No dependencies on other stories. This is the MVP.
- **User Story 2 (P2)**: Depends on WorkOrder and TriageResult from US1. May be worked on after US1 models are stable.
- **User Story 3 (P3)**: Depends on Dispatch model from US2. Must wait for US2 dispatch infrastructure.
- **User Story 4 (P2 Compliance)**: Depends on Foundational (soft-delete + Azure Blob + ACS scaffolding) and on US1's WorkOrder/MediaAsset models. Can run in parallel with US2/US3.

### Within Each User Story

- Tests (mandated by constitution) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 can start immediately; US2 model tasks can start alongside US1
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Frontend tasks can run in parallel with backend tasks within the same story

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T019 "Contract test for POST /api/v1/work-orders in tests/contract/test_work_order_create.py"
Task: T020 "Contract test for GET /api/v1/work-orders/{id}/triage in tests/contract/test_triage.py"
Task: T021 "Integration test for intake-to-classification flow in tests/integration/test_intake_triage_flow.py"
Task: T022 "Integration test for troubleshooting escalation in tests/integration/test_troubleshooting_escalation.py"
Task: T023 "AI eval test for classification accuracy in tests/eval/test_classification_accuracy.py"

# Launch all models for User Story 1 together:
Task: T024 "Create Property, TenantProfile models in backend/apps/intake/models.py"
Task: T025 "Create WorkOrder model in backend/apps/intake/models.py"
Task: T026 "Create TriageResult model in backend/apps/triage/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (tenant intake + AI triage + troubleshooting + duplicate detection + media to Azure Blob)
4. **STOP and VALIDATE**: Test User Story 1 independently per acceptance criteria
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (vendors + dispatch + ACS/APNs notifications)
4. Add User Story 3 → Test independently → Deploy/Demo (estimates + analytics)
5. Add User Story 4 → Test independently → Deploy/Demo (erasure + 7-year retention)
6. Complete Phase 7 (DR / multi-region / health / SLO alerting) → Production-ready
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (intake + triage + frontend + duplicate detection + media)
   - Developer B: User Story 2 (vendor + dispatch + ACS/APNs notifications)
   - Developer C: User Story 3 (estimates + analytics)
   - Developer D: User Story 4 (compliance + erasure + retention) + Phase 7 infra (DR, multi-region, SLO)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- US1 alone forms the deployable vertical slice (MVP)
- US1 + US4 (compliance) are the minimum production-ready scope (covers GDPR/CCPA)
- All 4 user stories together form the full MVP scope; Phase 7 (multi-region DR + SLO alerting) is required before serving production traffic
- Media handling uses Azure Blob with lifecycle tiering (Hot → Cool → Archive) aligned to the 7-year retention window
- Duplicate detection uses pgvector cosine similarity (text + image embeddings) with threshold ≥0.85
- Notification delivery uses ACS for SMS, native APNs/FCM for push, and a transactional email provider
- Disaster recovery targets RTO 4h / RPO 15min on a multi-region active-passive AKS topology
