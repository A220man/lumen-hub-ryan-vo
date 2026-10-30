# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

auth-foundation

## Roadmap

### project-skeleton — FastAPI/React project skeleton with basic structure

Status: done

Acceptance:
- Backend FastAPI app runs with health endpoint
- Frontend React+Vite+TS app builds and runs
- Docker compose with backend, frontend, PostgreSQL, Keycloak
- Basic CI workflow runs backend/frontend tests

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/api/health.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `docker-compose.yaml`, `.github/workflows/ci.yml`

Tests: `backend/tests/test_health.py`, `frontend/src/__tests__/App.test.tsx`

### auth-foundation — OIDC/Keycloak authentication foundation

Status: done

Acceptance:
- Keycloak realm import works
- Backend validates JWT tokens
- Frontend login/logout flow works
- Protected API endpoints require valid token

Implementation: `backend/app/core/auth.py`, `backend/app/api/auth.py`, `backend/app/core/security.py`, `frontend/src/hooks/useAuth.tsx`, `frontend/src/services/auth.ts`, `frontend/src/pages/Login.tsx`

Tests: `backend/tests/test_auth.py`, `frontend/src/__tests__/Auth.test.tsx`

### sms-otp-templates — SMS OTP template management with newline support (Issue #6435)

Status: planned

Acceptance:
- Create/update SMS templates with newlines
- WebOTP-compatible format validation
- Template preview shows rendered output

### project-health-monitoring — Postgres project health monitoring (Issue #40617)

Status: planned

Acceptance:
- Detect missing pg_pgrst_no_exposed_schemas
- Auto-create required schemas on project init
- Health dashboard shows PostgREST status

### smtp-office365-support — Custom SMTP with Office 365/Outlook support (Issue #34425)

Status: planned

Acceptance:
- TLS 1.2+ configuration for Office 365
- Connection timeout handling
- Test email sending works

