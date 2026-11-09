# Changelog

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

### Added (this round)
- Frontend unit tests for SMSTemplateForm component (6 tests covering create/edit modes, validation, preview, save, cancel)

### Changed
- Updated PLAN.md and feature-plan.json with correct test paths for sms-otp-templates feature

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-30

### Added
- Initial project skeleton with FastAPI backend and React frontend
- Health check endpoints (`/health`, `/health/ready`, `/health/live`)
- Docker Compose with PostgreSQL, Keycloak, backend, frontend
- Keycloak realm configuration with roles and clients
- GitHub Actions CI workflow for backend/frontend tests and Docker builds
- Basic frontend with login page, dashboard, and protected routes
- TypeScript configuration with strict mode
- ESLint and Vitest setup

### Security
- Non-root Docker users
- Health checks on all services
- CORS configuration
- Environment-based secrets management

### Authentication (auth-foundation)
- Keycloak realm import via docker-compose
- Backend JWT token validation with JWKS caching (RS256)
- Backend auth API endpoints: `/auth/login`, `/auth/token`, `/auth/logout`, `/auth/me`, `/auth/config`
- FastAPI dependency injection for current user (`get_current_user`, `get_optional_user`, `require_roles`)
- Frontend AuthProvider with Keycloak/OIDC authorization code flow
- Frontend auth service for token exchange, user info fetch, and session management
- Frontend login page redirects to Keycloak for authentication
- Protected routes require valid JWT token
- Frontend auth tests: 11 passing (6 AuthService + 5 useAuth hook)

## [1.1.0] - 2026-11-03

### Added
- SMS OTP Template Management (sms-otp-templates, Issue #6435)
  - Backend API endpoints: `GET/POST /sms-templates`, `GET/PUT/DELETE /sms-templates/{name}`, `POST /sms-templates/validate`, `POST /sms-templates/preview`
  - Template validation with WebOTP compatibility checks (requires `{otp}` or `{{otp}}` placeholder)
  - Template preview with variable substitution supporting both `{var}` and `{{var}}` formats
  - Newline support in template content
  - Character count and SMS segment calculation (160 chars per segment)
  - Role-based access: admin/operator for CRUD, admin for delete
  - In-memory storage (database-ready for future migration)
- Frontend SMS Templates page with:
  - Template list view with edit/preview/delete actions
  - Create/edit form with real-time validation
  - Live preview with variable substitution
  - Validation status display (errors, warnings, WebOTP compatibility)
  - Navigation integrated into app header
- Backend tests: 6 new tests for SMS template validation, rendering, and newline support
- Frontend builds successfully with new components

### Changed
- Added SMS templates router to FastAPI app (`/api/v1/sms-templates`)
- Extended frontend types with SMS template interfaces
- Added SMS template service with API client functions
- New UI components: `SMSTemplateList`, `SMSTemplateForm`, `SMSTemplatesPage`

### Security
- SMS template endpoints protected by role-based access control
