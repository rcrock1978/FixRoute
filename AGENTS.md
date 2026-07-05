# FixRoute

Spec-Driven Dev (SDD) project using **Spec Kit** + **OpenCode**. No application code yet — the repo is an SDD scaffold.

## Workflow

`/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`

Supporting commands: `/speckit.clarify`, `/speckit.checklist`, `/speckit.converge`, `/speckit.analyze`.

## Feature directories

Features live under `specs/<NNN>-<short-name>/` (e.g. `specs/003-user-auth/`). Each contains `spec.md`, `plan.md`, `tasks.md`, plus optional `research.md`, `data-model.md`, `quickstart.md`, `contracts/`, `checklists/`.

Current feature context is tracked in `.specify/feature.json` or `$SPECIFY_FEATURE_DIRECTORY`.

## Available scripts

- `.specify/scripts/bash/setup-plan.sh --json` — bootstrap plan template
- `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` — validate readiness for `/speckit.implement`
- `.specify/scripts/bash/setup-tasks.sh --json` — resolve tasks template
- `.specify/scripts/bash/create-new-feature.sh` — create feature dir (used by hooks)
- `.specify/scripts/bash/common.sh` — shared helpers (path resolution, JSON, template resolution)

## Key files

| File | Purpose |
|------|---------|
| `.specify/memory/constitution.md` | Project principles & governance |
| `.specify/templates/*.md` | Template sources for spec, plan, tasks, checklist |
| `.specify/integration.json` | Integration config (opencode, `"script": "sh"`, `"invoke_separator": "."`) |
| `.opencode/commands/speckit.*.md` | Speckit command definitions for OpenCode |
| `AGENTS.md` (between SPECKIT markers) | Managed section — do not edit manually |

## Notes

- No runtime dependencies exist yet — they get defined during `/speckit.plan` and installed during `/speckit.implement`
- The `AGENTS.md` SPECKIT section (`<!-- SPECKIT START -->` … `<!-- SPECKIT END -->`) is auto-managed by the agent-context extension; edit outside those markers only
- All speckit commands use `.` separator (e.g. `/speckit.specify`)

<!-- SPECKIT START -->
The current implementation plan is at `specs/001-fixroute-platform/plan.md`.
Companion artifacts:
- `specs/001-fixroute-platform/spec.md` — authoritative spec (15 FRs, 7 SCs, 3 clarification sessions)
- `specs/001-fixroute-platform/research.md` — tech decisions (DRF, pgvector, Celery, ACS, Azure Blob, etc.)
- `specs/001-fixroute-platform/data-model.md` — entities with soft-delete + pgvector embeddings
- `specs/001-fixroute-platform/quickstart.md` — 10 validation scenarios including DR failover
- `specs/001-fixroute-platform/contracts/openapi.yaml` — API contract (incl. /erasure-requests, /health, /work-orders/{id}/duplicates)
Tech stack: Django 5 + DRF, Vue.js 3, PostgreSQL 16 + pgvector, Redis 7, Celery, Azure Blob Storage, ACS, APNs/FCM, AKS (multi-region active-passive, RTO 4h / RPO 15min), Entra ID OIDC.
<!-- SPECKIT END -->
