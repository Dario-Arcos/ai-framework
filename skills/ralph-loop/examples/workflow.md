# Ralph Loop: Complete Example Workflow

This example shows the full Ralph workflow from requirements to shipped code.

---

## Scenario

Build a task management API with authentication, CRUD operations, filtering, and reminders.

---

## Phase 1: Requirements Definition (Interactive Session)

### Step 1: Identify JTBD

```
Human: I need a task management API

Claude: Let me identify Jobs to Be Done. I see:
1. Users need to manage their task lists
2. Users need to authenticate
3. Users need to receive reminders
4. Users need to filter/search tasks

Let me break these into topics of concern.
```

### Step 2: Create Specs

Claude creates `specs/` directory with:

**specs/authentication.md**
```markdown
# Authentication

## Requirements
- JWT-based authentication
- Login endpoint
- Token refresh
- Logout (token invalidation)

## Acceptance Criteria
- Login returns valid JWT
- Protected endpoints reject invalid tokens
- Tokens expire after 24h
- Refresh extends expiry
```

**specs/task-crud.md**
```markdown
# Task CRUD Operations

## Requirements
- Create task (title, description, due_date)
- Read tasks (user's own only)
- Update task
- Delete task
- Soft delete (archive)

## Acceptance Criteria
- Users can only access their own tasks
- Validation on all inputs
- 404 for non-existent tasks
- Archive preserves data
```

**specs/filtering.md**
```markdown
# Task Filtering

## Requirements
- Filter by status (pending, completed, archived)
- Filter by due date range
- Search by title/description
- Sort by: created, due_date, priority

## Acceptance Criteria
- Filters combine with AND logic
- Empty filters return all tasks
- Case-insensitive search
```

---

## Phase 2: Planning Loop

### Iteration 1: Generate Initial Plan

```bash
$ ./loop.sh plan 1
```

**Claude reads:**
- `specs/authentication.md`
- `specs/task-crud.md`
- `specs/filtering.md`
- `src/*` (existing code - finds Express boilerplate)

**Claude writes `IMPLEMENTATION_PLAN.md`:**

```markdown
# Implementation Plan

## High Priority (Foundation)
- [ ] Database schema: users and tasks tables
- [ ] User model with password hashing
- [ ] JWT middleware for protected routes
- [ ] Login endpoint (POST /auth/login)
- [ ] Token refresh endpoint (POST /auth/refresh)

## Medium Priority (Core Features)
- [ ] Create task endpoint (POST /tasks)
- [ ] Read tasks endpoint (GET /tasks)
- [ ] Update task endpoint (PUT /tasks/:id)
- [ ] Delete task endpoint (DELETE /tasks/:id)
- [ ] Task ownership validation middleware

## Medium Priority (Filtering)
- [ ] Filter by status query param
- [ ] Filter by due date range
- [ ] Search by text in title/description
- [ ] Sort implementation

## Low Priority (Polish)
- [ ] Error message consistency
- [ ] Input validation error details
- [ ] API documentation

## Notes
- Build auth first - all other endpoints depend on it
- Validate task ownership on ALL task endpoints
- Use src/lib/ for shared middleware
```

---

## Phase 3: Building Loop

### Iteration 1: Database Schema

```bash
$ ./loop.sh build
```

**Claude reads (fresh context):**
- `guardrails.md` (empty - first iteration)
- `IMPLEMENTATION_PLAN.md`
- `progress.txt` (empty)

**Claude selects:** "Database schema: users and tasks tables"

**Claude implements:**
1. Creates migration: `migrations/001_create_users_and_tasks.sql`
2. Writes test: `tests/db/schema.test.ts`
3. RED: Test fails (tables don't exist)
4. Runs migration script
5. GREEN: Test passes
6. Commits: `feat: add database schema for users and tasks`

**Claude updates:**
- `IMPLEMENTATION_PLAN.md`: Marks task `[x]`
- `progress.txt`:

```markdown
## [2026-01-18 10:15] - Iteration 1

**Task**: Database schema: users and tasks tables

**Changes**:
- migrations/001_create_users_and_tasks.sql: Added users table (id, email, password_hash) and tasks table (id, user_id, title, description, due_date, status)
- tests/db/schema.test.ts: Schema validation tests

**Learnings**:
- Project uses PostgreSQL with node-pg-migrate
- Migration command: npm run migrate:up
- Tests use testcontainers for isolated DB

**Codebase Patterns**:
- Migrations in migrations/ with numeric prefix
- Test databases use docker-compose.test.yml
```

**Exit** → Context destroyed

---

### Iteration 2: User Model

**Claude reads (fresh context):**
- `guardrails.md` (still empty)
- `IMPLEMENTATION_PLAN.md` (task 1 marked done)
- `progress.txt` (knows migrations pattern now)

**Claude selects:** "User model with password hashing"

**Claude searches first:**
```bash
grep -r "bcrypt" src/
grep -r "hashPassword" src/
ls src/lib/
```

**Found:** Nothing. Proceeds with implementation.

**Claude implements:**
1. Creates `src/models/User.ts`
2. Writes test: `tests/models/User.test.ts`
3. TDD cycle: RED → GREEN → REFACTOR
4. All gates pass
5. Commits: `feat: add User model with bcrypt password hashing`

**Claude updates progress.txt, marks task `[x]`

**Exit** → Context destroyed

---

### Iteration 3: JWT Middleware (Error Encountered)

**Claude reads:**
- `guardrails.md`
- `IMPLEMENTATION_PLAN.md`
- `progress.txt` (knows migrations and User model patterns)

**Claude selects:** "JWT middleware for protected routes"

**Claude implements:**
1. Writes test for middleware
2. Creates `src/middleware/auth.ts`
3. Uses `jsonwebtoken` library
4. Tests FAIL: "jsonwebtoken not found"

**Claude attempts:**
```bash
npm install jsonwebtoken @types/jsonwebtoken
```

**Tests pass, commits**

**BUT discovers issue:**
- Should have added dependency BEFORE using it in code
- This is a pattern to remember

**Claude adds Sign to `guardrails.md`:**

```markdown
### Sign: Missing dependency installation
- **Trigger**: Import statement for library not in package.json
- **Instruction**: Install dependency FIRST (npm install), THEN implement code that uses it
- **Added after**: Iteration 3
```

**Claude updates progress, marks task `[x]`

**Exit** → Context destroyed

---

### Iteration 4: Login Endpoint (Sign Applied)

**Claude reads:**
- `guardrails.md` (now has Sign about dependencies!)
- `IMPLEMENTATION_PLAN.md`
- `progress.txt`

**Claude selects:** "Login endpoint (POST /auth/login)"

**Claude sees:** Needs `express-validator` for input validation

**Applies Sign:** Installs dependency FIRST

```bash
npm install express-validator
```

**Then implements:**
1. Test for login endpoint
2. Controller implementation
3. Route registration
4. TDD cycle
5. All gates pass
6. Commits

**No error this time** - Sign prevented the mistake!

**Progress shows:** "Applied Sign from iteration 3 - installed express-validator before using"

**Exit** → Context destroyed

---

### Iterations 5-15: Continued Building

Each iteration:
1. Fresh context
2. Reads state files (including accumulated Signs)
3. Implements ONE task
4. Validates with backpressure
5. Commits
6. Updates state
7. Exits clean

**Signs accumulate:**
```markdown
### Sign: Missing dependency installation
### Sign: Test database not cleaned between tests
### Sign: Task ownership validation missing
### Sign: Error responses need consistent format
```

**Each new iteration is smarter** because it reads all previous Signs.

---

### Iteration 16: Completion

**Claude reads:**
- `guardrails.md` (4 Signs now)
- `IMPLEMENTATION_PLAN.md` (all tasks marked `[x]`)
- `progress.txt` (full session history)

**Claude checks:** All tasks complete?

```markdown
## High Priority (Foundation)
- [x] Database schema
- [x] User model
- [x] JWT middleware
- [x] Login endpoint
- [x] Token refresh endpoint

## Medium Priority (Core Features)
- [x] Create task endpoint
- [x] Read tasks endpoint
- [x] Update task endpoint
- [x] Delete task endpoint
- [x] Task ownership validation

## Medium Priority (Filtering)
- [x] Filter by status
- [x] Filter by due date range
- [x] Search by text
- [x] Sort implementation

## Low Priority (Polish)
- [x] Error messages
- [x] Input validation
- [x] API documentation
```

**All marked `[x]`!**

**Claude outputs:**

```
<promise>COMPLETE</promise>
```

**Loop exits successfully.**

---

## Post-Completion

### Review State Files

**progress.txt** (16 iterations of learnings):
```markdown
## Summary
- 16 iterations
- 4 Signs added
- 15 commits
- All gates passed
- Zero rollbacks
```

**guardrails.md** (4 Signs for future projects):
```markdown
### Sign: Missing dependency installation
### Sign: Test database cleanup
### Sign: Task ownership validation pattern
### Sign: Consistent error response format
```

**Git history** (clean, atomic commits):
```
feat: add API documentation
feat: add consistent error responses
feat: add task filtering and search
...
feat: add database schema for users and tasks
```

---

## Key Observations

### What Made This Work

1. **Small tasks**: Each fit in one context window
2. **Fresh context**: No pollution across 16 iterations
3. **Signs system**: Error in iteration 3 prevented in iteration 4+
4. **Backpressure**: All commits had passing tests
5. **TDD**: Every feature test-driven
6. **Search first**: No duplicate code

### What Would Have Failed Without Ralph

**Traditional long session:**
- Iteration 8: Context rot starts
- Iteration 12: Quality degrades
- Iteration 15: Repeats mistakes from iteration 5
- Iteration 16: Context >90%, confused, poor decisions

**With Ralph:**
- Every iteration: Fresh and sharp
- Signs prevent repeated errors
- Quality consistent across all 16 iterations
- Context never exceeds 60%

---

## Time Comparison

**Human developer:** ~3-5 days
**HITL (human-in-loop) AI:** ~1-2 days
**AFK Ralph:** ~8 hours overnight

**Cost:** $15-30 in API calls (vs $800-2000 human developer cost)

---

## Artifacts Generated

```
ralph/
├── specs/
│   ├── authentication.md (180 lines)
│   ├── task-crud.md (220 lines)
│   └── filtering.md (150 lines)
├── IMPLEMENTATION_PLAN.md (60 lines, all [x])
├── progress.txt (320 lines, 16 iterations)
├── guardrails.md (4 Signs)
└── AGENTS.md (58 lines)

src/
├── migrations/
│   └── 001_create_users_and_tasks.sql
├── models/
│   ├── User.ts
│   └── Task.ts
├── middleware/
│   ├── auth.ts
│   └── validateOwnership.ts
├── controllers/
│   ├── authController.ts
│   └── taskController.ts
├── routes/
│   ├── auth.ts
│   └── tasks.ts
└── lib/
    ├── jwt.ts
    └── errorResponse.ts

tests/
├── db/
│   └── schema.test.ts
├── models/
│   ├── User.test.ts
│   └── Task.test.ts
├── controllers/
│   ├── authController.test.ts
│   └── taskController.test.ts
└── integration/
    └── api.test.ts

Total: 28 files, ~2,400 LOC, 85 tests, 100% passing
```

---

## Lessons for Your Implementation

1. **Spec scoping**: One topic = one file (auth, CRUD, filtering)
2. **Task sizing**: Database schema is ONE task, not "build database"
3. **Priority order**: Auth → CRUD → Filtering (foundation first)
4. **Signs value**: Error in iteration 3 saved time in iterations 4-16
5. **Progress.txt**: Concise session memory, not verbose narrative
6. **Fresh context**: Quality consistent across all 16 iterations

---

This is Ralph working as designed.
