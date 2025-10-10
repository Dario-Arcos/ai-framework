# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)

```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] [Agent] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Agent]**: Specialized agent type for optimal task execution
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Agent Types

- **general-purpose**: Setup, configuration, generic tasks, project initialization
- **test-automator**: Unit tests, integration tests, contract tests, test automation
- **backend-architect**: API endpoints, services, business logic, server-side implementation
- **frontend-developer**: UI components, client-side logic, user interfaces
- **database-optimizer**: Models, schemas, migrations, data layer optimization
- **devops-troubleshooter**: Infrastructure, deployment, CI/CD, system operations
- **docs-architect**: Documentation, API docs, README updates, technical writing

## Phase 3.1: Setup

- [ ] T001 [general-purpose] Create project structure per implementation plan
- [ ] T002 [general-purpose] Initialize [language] project with [framework] dependencies
- [ ] T003 [P] [general-purpose] Configure linting and formatting tools

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] T004 [P] [test-automator] Contract test POST /api/users in tests/contract/test_users_post.py
- [ ] T005 [P] [test-automator] Contract test GET /api/users/{id} in tests/contract/test_users_get.py
- [ ] T006 [P] [test-automator] Integration test user registration in tests/integration/test_registration.py
- [ ] T007 [P] [test-automator] Integration test auth flow in tests/integration/test_auth.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] T008 [P] [database-optimizer] User model in src/models/user.py
- [ ] T009 [P] [backend-architect] UserService CRUD in src/services/user_service.py
- [ ] T010 [P] [backend-architect] CLI --create-user in src/cli/user_commands.py
- [ ] T011 [backend-architect] POST /api/users endpoint
- [ ] T012 [backend-architect] GET /api/users/{id} endpoint
- [ ] T013 [backend-architect] Input validation
- [ ] T014 [backend-architect] Error handling and logging

## Phase 3.4: Integration

- [ ] T015 [backend-architect] Connect UserService to DB
- [ ] T016 [backend-architect] Auth middleware
- [ ] T017 [backend-architect] Request/response logging
- [ ] T018 [backend-architect] CORS and security headers

## Phase 3.5: Polish

- [ ] T019 [P] [test-automator] Unit tests for validation in tests/unit/test_validation.py
- [ ] T020 [test-automator] Performance tests (<200ms)
- [ ] T021 [P] [docs-architect] Update docs/api.md
- [ ] T022 [general-purpose] Remove duplication
- [ ] T023 [test-automator] Run manual-testing.md

## Dependencies

- Tests (T004-T007) before implementation (T008-T014)
- T008 blocks T009, T015
- T016 blocks T018
- Implementation before polish (T019-T023)

## Parallel Example

```
# Launch T004-T007 together with specialized agents:
Task(test-automator): "Contract test POST /api/users in tests/contract/test_users_post.py"
Task(test-automator): "Contract test GET /api/users/{id} in tests/contract/test_users_get.py"
Task(test-automator): "Integration test registration in tests/integration/test_registration.py"
Task(test-automator): "Integration test auth in tests/integration/test_auth.py"

# Mixed parallel execution example:
Task(database-optimizer): "User model in src/models/user.py"
Task(backend-architect): "UserService CRUD in src/services/user_service.py"
Task(backend-architect): "CLI --create-user in src/cli/user_commands.py"
```

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules

_Applied during main() execution_

1. **From Contracts**:
   - Each contract file → contract test task [P] [test-automator]
   - Each endpoint → implementation task [backend-architect]
2. **From Data Model**:
   - Each entity → model creation task [P] [database-optimizer]
   - Relationships → service layer tasks [backend-architect]
3. **From User Stories**:
   - Each story → integration test [P] [test-automator]
   - Quickstart scenarios → validation tasks [test-automator]

4. **Agent Assignment Rules**:
   - Setup/Config tasks → [general-purpose]
   - All test tasks → [test-automator]
   - Models/Schemas → [database-optimizer]
   - APIs/Services → [backend-architect]
   - UI Components → [frontend-developer]
   - Documentation → [docs-architect]

5. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist

_GATE: Checked by main() before returning_

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
- [ ] All tasks have appropriate agent assignments
- [ ] Test tasks assigned to [test-automator]
- [ ] Model tasks assigned to [database-optimizer]
- [ ] API tasks assigned to [backend-architect]
