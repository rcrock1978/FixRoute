# Quickstart: FixRoute Platform

## Prerequisites

- Python 3.12+
- Node.js 20+ (for frontend)
- Docker & Docker Compose (for local services: PostgreSQL, Redis)
- `npx` (for skills.sh: `npx skills add <owner/repo>`)

## Local Development Setup

```bash
# 1. Clone and enter the repository
git clone <repo-url> fixroute
cd fixroute

# 2. Start infrastructure services
docker compose up -d postgres redis

# 3. Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env   # edit database URLs, API keys
python manage.py migrate
python manage.py createsuperuser

# 4. Frontend setup
cd ../frontend
npm install
cp .env.example .env.local
npm run dev

# 5. Run backend dev server
cd ../backend
python manage.py runserver
```

## Validation Scenarios

### Scenario 1: Tenant submits a maintenance request

```bash
# Submit a work order with text + photo
curl -X POST http://localhost:8000/api/v1/work-orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -F "property_id=$PROPERTY_ID" \
  -F "title=Leaking kitchen faucet" \
  -F "description=Water is leaking from the base of the faucet" \
  -F "media=@photo.jpg"

# Expected: 201 Created
# Response includes: work order ID, status="submitted"
# Verify: audit log entry created for work_order.submitted
```

### Scenario 2: AI classifies the request

```bash
# Check triage result (poll after submission)
curl -X GET http://localhost:8000/api/v1/work-orders/$WO_ID/triage \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID"

# Expected: 200 OK
# Response includes: category="plumbing", urgency="routine",
#   confidence=0.92, troubleshooting_steps with 3 items
# Verify: WorkOrder status changed to "classified" or "troubleshooting"
```

### Scenario 3: Self-serve troubleshooting fails, dispatch triggered

```bash
# After tenant reports troubleshooting didn't work, dispatch is needed.
# Verify vendor matching:
curl -X GET http://localhost:8000/api/v1/work-orders/$WO_ID/match-vendors \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID"

# Expected: 200 OK
# Response includes: ranked list of plumbing vendors with distance
```

### Scenario 4: Dispatch vendor

```bash
# Dispatch the top-matched vendor
curl -X POST http://localhost:8000/api/v1/work-orders/$WO_ID/dispatch \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{"vendor_id": "$VENDOR_ID"}'

# Expected: 201 Created
# Verify: notification sent via in-app + email (and SMS if urgency=emergency)
```

### Scenario 5: Vendor provides estimate, manager approves

```bash
# Vendor submits estimate
curl -X POST http://localhost:8000/api/v1/dispatches/$DISPATCH_ID/estimate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"line_items": [{"description": "Labor", "amount": 85}, {"description": "Parts", "amount": 45}], "total": 130}'

# Property manager approves
curl -X POST http://localhost:8000/api/v1/estimates/$ESTIMATE_ID/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
```

### Scenario 6: Vendor completes work

```bash
# Vendor marks as completed with final costs
curl -X PATCH http://localhost:8000/api/v1/dispatches/$DISPATCH_ID/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed", "notes": "Replaced faucet cartridge"}'

# Expected: 200 OK
# Verify: WorkOrder status changed to "completed"
# Verify: final_cost recorded, notification sent
```

### Scenario 7: View spend analytics

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/spend?start_date=2026-06-01&end_date=2026-06-30&group_by=trade" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID"

# Expected: 200 OK
# Response includes: spend totals grouped by trade for the period
```

### Scenario 8: Duplicate work-order detection (pgvector)

```bash
# Submit a near-duplicate of an existing work order
curl -X POST http://localhost:8000/api/v1/work-orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -F "property_id=$PROPERTY_ID" \
  -F "title=Dripping tap in kitchen" \
  -F "description=Water is dripping from the base of the faucet" \
  -F "media=@photo.jpg"

# Expected: 200 OK (not 201) with status="duplicate_suspected"
# Response includes: matched_work_order_id, similarity_score, follow_up_prompt
# Verify: similarity_score >= 0.85 against the prior "Leaking kitchen faucet" work order
```

### Scenario 9: GDPR/CCPA erasure request and 30-day SLA

```bash
# Tenant requests erasure of their PII
curl -X POST http://localhost:8000/api/v1/erasure-requests \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{"subject_id": "$TENANT_PROFILE_ID", "reason": "gdpr_art_17"}'

# Expected: 202 Accepted
# Verify: work_orders and media_assets for this tenant have soft_deleted_at set
# Verify: hard_delete_at is scheduled exactly 30 days out

# Trigger the daily erasure Celery beat task (or wait for it)
celery -A config call config.tasks.run_erasure_sweep

# Expected: hard-deleted records for those past the 30-day window
# Verify: AuditLog tombstones exist for each hard-deleted record
```

### Scenario 10: Multi-region DR failover drill

```bash
# Trigger a controlled failover to the passive region
az aks nodepool scale --name backend --node-count 0 --resource-group fixroute-primary
kubectl --context=fixroute-secondary scale deployment backend --replicas=3

# Verify Triage API responds from passive region within RTO 4h
curl -X GET https://api.fixroute.example.com/api/v1/health \
  -H "X-Tenant-ID: $TENANT_ID"
# Expected: 200 OK with region=secondary

# Verify no more than 15 minutes of data loss (RPO 15min) by comparing
# work-order IDs created in the last 15 min before failover
```

## Running Tests

```bash
# Backend tests
cd backend
pytest                           # all tests
pytest apps/intake/tests/        # single app
pytest -k "test_classify"        # filtered by name
pytest --cov=apps                # with coverage

# AI evaluation tests
pytest tests/eval/               # AI eval harness (Ragas-style)

# Contract tests (API schema conformance)
pytest tests/contract/           # validates responses against OpenAPI spec
```

## Expected Outcomes

| Scenario | Expected Result | Verification |
|----------|----------------|--------------|
| Submit work order | 201, work order created | Check DB for WorkOrder row |
| AI classification | Category + urgency returned | TriageResult exists |
| Troubleshooting shown | Steps displayed to tenant | Check troubleshooting_steps |
| Vendor matched | Ranked vendor list | Verify trade/area match logic |
| Vendor dispatched | 201, dispatch created | Dispatch row in DB, notification sent |
| Estimate approved | Status=approved | CostEstimate.status updated |
| Work completed | Status=completed | WorkOrder.status updated, final_cost recorded |
| Spend analytics | Aggregated data | Correct totals by group |
| Tenant isolation | Cross-tenant 404/403 | Request tenant B's data from tenant A's context |
| Duplicate detection | Similar work order linked | similarity_score ≥ 0.85 |
| Erasure request | 30-day hard-delete SLA | soft_deleted_at set, hard_delete_at scheduled 30d out |
| DR failover | Recovery within RTO 4h | Triage API responds from passive region |
