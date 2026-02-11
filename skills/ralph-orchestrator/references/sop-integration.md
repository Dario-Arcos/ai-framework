# SOP Integration Reference

## Overview

This reference defines how ralph-orchestrator integrates with the SOP (Standard Operating Procedure) skills framework. Understanding this integration is essential for proper workflow orchestration and phase transitions.

---

## Workflow Structure

**Constraints:**
- You MUST follow the two-phase structure because mixing planning and execution degrades both
- You MUST complete planning phase before execution because teammates need clear specifications
- You MUST NOT skip any planning step because incomplete specs cause implementation failures

Ralph orchestrates SOP skills to transform ideas into implementations through a two-phase workflow:

1. **Planning Phase (Interactive)**: Interactive session using SOP skills
2. **Execution Phase**: Agent Teams cockpit executing the plan

```mermaid
graph TD
    subgraph "Planning Phase - Interactive"
        A[/ralph-orchestrator invoked] --> R[sop-reverse referent]
        R --> R2[referents/ catalog]
        R2 --> H[sop-planning]
        H --> I[sop-task-generator]
        I --> J[Configure execution]
    end

    subgraph "Execution Phase - Agent Teams"
        J --> K[Launch cockpit via bash .ralph/launch-build.sh]
        K --> L[Teammate task cycles]
        L --> M{Complete?}
        M -->|No| L
        M -->|Yes| N[Done]
    end

    style A fill:#e1f0ff
    style R fill:#f0ffe1
    style H fill:#f0e1ff
    style I fill:#e1ffe1
    style K fill:#ffe1e1
```

---

## SOP Skills in the Workflow

### 1. sop-reverse (Referent Discovery)

**Constraints:**
- You MUST use sop-reverse in referent mode as the first step of every Ralph flow because building on proven patterns beats guessing
- You MUST complete batch analysis before refinement questions because context informs follow-up
- You SHOULD use sop-reverse standalone (outside Ralph) for pure investigation or reverse engineering

**Purpose**: Find world-class implementations before designing something new. Ralph ALWAYS uses referent mode (`search_mode=referent`).

> **Note**: sop-reverse also supports `search_mode=reverse` for investigating existing artifacts, but that mode is used standalone — not as part of the Ralph flow. For investigation-only tasks, invoke `sop-reverse` directly instead of Ralph.

**When invoked**: First step of the Ralph flow

**Input**: Path to artifact, URL, concept name, or domain description

**Artifacts supported**:
- Codebase: `/path/to/repo`
- API documentation: `https://api.example.com/docs`
- Design documents: `/path/to/docs/`
- Processes: "Our deployment workflow"
- Concepts: "Event sourcing pattern"
- Domains for referent search: "real-time collaboration", "developer API with excellent DX"

**Output**:
- **Reverse mode**: `.ralph/specs/{investigation}/specs-generated/`
- **Referent mode**: `.ralph/specs/{goal}/referents/`

**What it contains**:

*Reverse mode:*
- Artifact analysis
- Architecture patterns found
- Dependencies discovered
- Issues and improvements identified
- Generated specifications

*Referent mode:*
- Per-referent analysis files
- Comparative analysis across referents
- Extracted patterns ready for adoption
- Catalog with scores and recommendations

**Duration**: 20-40 minutes (varies by artifact size and number of referents)

**Interaction style**:
- Batch analysis (automatic)
- Interactive refinement (one question at a time)

**Example (Reverse — investigate existing)**:
```bash
User: "Investigate legacy payment processing module"

sop-reverse (search_mode=reverse):
1. Analyzes /src/payments/ (automatic)
2. Discovers: Stripe integration, manual retry logic, no tests
3. Asks refinement questions:
   - Focus on error handling or integration?
   - Migrating to new payment provider?
   - Adding new payment methods?

Output: .ralph/specs/payment-investigation/specs-generated/
├── architecture.md
├── integration-patterns.md
├── issues-found.md
└── improvement-opportunities.md

User: "Now build PayPal support using Ralph"
→ Proceeds to Ralph orchestrator, which runs referent discovery + planning
```

**Example (Referent — discover before building)**:
```bash
User: "Build a real-time collaboration engine"

sop-reverse (search_mode=referent):
1. Identifies referents: Yjs, Automerge, ShareDB, Liveblocks
2. Analyzes each: architecture, CRDT approach, API design, performance
3. Comparative synthesis: pattern frequency, best-of-breed per aspect
4. Extracts adoptable patterns

Output: .ralph/specs/collab-engine/referents/
├── catalog.md
├── yjs-analysis.md
├── automerge-analysis.md
├── sharedb-analysis.md
├── comparative-analysis.md
└── extracted-patterns.md

→ Proceeds to sop-planning with referent patterns as design foundation
```

---

### 2. sop-planning

**Constraints:**
- You MUST validate discovery completeness before proceeding because incomplete discovery causes flawed designs
- You MUST research technology choices before design decisions because uninformed decisions create technical debt
- You SHOULD document all research findings because this prevents repeated investigation

**Purpose**: Create detailed requirements, research, and design

**When invoked**: After referent discovery (Step 2)

**Input**:
- `.ralph/specs/{goal}/referents/catalog.md` (from sop-reverse referent mode)
- Goal description as `rough_idea`

**Output**:
- `.ralph/specs/{goal}/rough-idea.md`
- `.ralph/specs/{goal}/idea-honing.md` (Q&A log)
- `.ralph/specs/{goal}/research/*.md`
- `.ralph/specs/{goal}/design/detailed-design.md`

**What it contains**:

**rough-idea.md**:
- Initial concept
- High-level goals
- Success criteria

**idea-honing.md**:
- Clarification questions asked
- User responses
- Decisions made
- Scope refinements

**research/**.md:
- Technical research findings
- Library comparisons
- Pattern investigations
- Best practices

**design/detailed-design.md**:
- System architecture
- Component design
- Data models
- API contracts
- Security considerations
- Performance requirements
- Testing strategy

**Duration**: 20-40 minutes

**Interaction style**: Interactive loops
- Clarification questions (requirements)
- Research questions (investigation)
- Design validation (review)

**Example**:
```bash
Input: .ralph/specs/user-auth/referents/catalog.md

sop-planning phases:

1. Clarification (requirements):
   - User schema fields needed?
   - Token expiration policy?
   - Password reset flow?

2. Research:
   - JWT libraries: jsonwebtoken vs jose
   - Bcrypt vs Argon2 for hashing
   - Rate limiting approaches

3. Design:
   - Routes: POST /auth/login, POST /auth/refresh
   - Middleware: authenticateToken
   - Database: users table with hashed passwords
   - Security: bcrypt rounds=10, JWT expiry=15m

Output: .ralph/specs/user-auth/design/detailed-design.md
```

---

### 3. sop-task-generator

**Constraints:**
- You MUST include acceptance criteria for each task because teammates need clear completion criteria
- You MUST size tasks appropriately (M-size optimal) because oversized tasks exhaust context
- You MUST NOT create tasks without file lists because teammates need to know scope

**Purpose**: Generate structured implementation tasks from design

---

### 4. sop-code-assist

**Constraints:**
- You MUST implement scenarios BEFORE implementation code because SDD ensures testability
- You MUST NOT place code in documentation directories because separation of concerns matters
- You SHOULD use autonomous mode for batch processing because it reduces interruptions
- You SHOULD use interactive mode for learning because it provides educational context

**Purpose**: Execute code tasks using SDD workflow (Explore → Plan → Code → Commit)

**When invoked**: After sop-task-generator creates .code-task.md files

**Input**: `.code-task.md` file path, task description, or direct text

**Output**:
- Implementation code in repo_root
- Test code in appropriate test directories
- Artifacts in `.ralph/specs/{goal}/implementation/{task_name}/`

**Artifacts created**:
- `blockers.md` - Blockers encountered (autonomous mode, if blocked)
- `logs/` - Build outputs

**Modes**:
- **interactive**: User confirmation at each step (learning, uncertain requirements)
- **autonomous**: Autonomous execution (batch processing, ralph-orchestrator integration)

**Duration**: 10-60 minutes per task (varies by complexity)

**Example**:
```bash
# Interactive mode for learning
/sop-code-assist task_description=".ralph/specs/user-auth/implementation/step01/task-01-jwt-utils.code-task.md" mode="interactive"

# Auto mode for batch execution
/sop-code-assist task_description=".ralph/specs/user-auth/implementation/step01/task-01-jwt-utils.code-task.md" mode="autonomous"
```

**SDD Workflow**:
```
1. Setup: Create artifacts, discover project context
2. Explore: Analyze requirements, research patterns
3. Plan: Design test strategy, plan implementation
4. Code: SCENARIO → SATISFY → REFACTOR cycle
5. Commit: Conventional commit with all changes
```

---

### 5. sop-task-generator (continued)

**When invoked**: After planning completes

**Input**: `.ralph/specs/{goal}/implementation/plan.md` (created by sop-planning)

**Output**: `.ralph/specs/{goal}/implementation/step*/task-*.code-task.md` files

**What it contains**:
- `.code-task.md` files for each task
- Each task file with:
  - Clear description
  - File list
  - Size estimate (S/M/L)
  - Acceptance criteria
  - Dependencies (if any)

**Task format**: Individual `.code-task.md` files with structured metadata:
```markdown
## Status: PENDING
## Blocked-By:
## Completed:

# Task: Implement JWT token generation

## Description
Create utils/jwt.ts with sign() and verify() functions.

## Acceptance Criteria
1. **Token Generation**
   - Given valid user credentials
   - When sign() is called
   - Then a valid JWT is returned with correct claims

## Metadata
- **Complexity**: Medium
- **Scenario-Strategy**: required
- **Files to Modify**: src/utils/jwt.ts
```

**Duration**: 5-15 minutes

**Interaction style**: Mostly automatic with approval checkpoints

**Output**: Individual `.code-task.md` files per task in `step*/` subdirectories:
```bash
Input: .ralph/specs/user-auth/implementation/plan.md

sop-task-generator creates:

.ralph/specs/user-auth/implementation/
├── plan.md
├── step01/
│   ├── task-01-install-dependencies.code-task.md
│   └── task-02-create-migration.code-task.md
├── step02/
│   ├── task-01-password-hashing.code-task.md
│   ├── task-02-login-endpoint.code-task.md
│   ├── task-03-token-middleware.code-task.md
│   └── task-04-refresh-endpoint.code-task.md
└── step03/
    ├── task-01-jwt-unit-tests.code-task.md
    ├── task-02-auth-integration-tests.code-task.md
    └── task-03-security-tests.code-task.md
```

---

## The Complete Ralph Flow

**Constraints:**
- You MUST complete referent discovery before planning because proven patterns inform better designs
- You MUST analyze multiple referents because single-referent analysis risks cargo-culting
- You SHOULD extract patterns into structured format because raw analysis is harder to consume during planning

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant R as sop-reverse (referent)
    participant P as sop-planning
    participant T as sop-task-generator
    participant C as Agent Teams Cockpit
    participant S as Teammates
    participant Rev as Reviewer

    U->>O: /ralph-orchestrator

    O->>R: Invoke with concept + search_mode=referent
    R->>U: What domain/concept?
    U->>R: Real-time collaboration engine

    Note over R: Identify referents (Yjs, Automerge, ShareDB...)
    Note over R: Analyze each referent
    Note over R: Comparative synthesis

    R->>U: Best foundation: Yjs for CRDT, Liveblocks for API DX
    R-->>O: referents/ catalog created

    O->>P: Invoke with referent catalog
    Note over P: Planning uses extracted patterns as design input
    P->>U: Architecture based on Yjs CRDT pattern?
    U->>P: Yes, with custom awareness protocol
    P-->>O: detailed-design.md created

    O->>T: Invoke with design
    T->>U: Approve task list?
    U->>T: Approved
    T-->>O: plan.md created

    O->>C: Launch cockpit: bash .ralph/launch-build.sh
    C->>S: Task 1 (implementer)
    S->>C: Complete + gates pass
    C->>Rev: Review Task 1 (reviewer)
    Rev->>C: 8-word summary
    Note over C,S,Rev: Continues until all tasks implemented + reviewed
    C-->>O: All tasks completed
    O->>U: Implementation complete
```

**Invocation example:**
```bash
# Invoke Ralph — referent discovery happens automatically
/ralph-orchestrator goal="real-time collaboration engine"

# Orchestrator invokes Step 2: Referent Discovery
/sop-reverse target="real-time collaboration engine" search_mode="referent" output_dir=".ralph/specs/realtime-collab" mode={PLANNING_MODE}

# Orchestrator invokes Step 3: Planning with referent patterns
/sop-planning rough_idea="real-time collaboration engine" discovery_path=".ralph/specs/realtime-collab/referents/catalog.md" project_dir=".ralph/specs/realtime-collab" mode={PLANNING_MODE}

# Steps 4-8: Task generation, AGENTS.md, review, configure, launch
```

---

## Directory Structure After Full Flow

**Constraints:**
- You MUST maintain directory structure because teammates expect standard paths
- You MUST NOT modify specs structure during execution because teammates read from fixed locations
- You SHOULD commit specs before execution because this creates recovery point

```
project-root/
├── .ralph/                           # Created by install.sh
│   ├── config.sh
│   ├── agents.md                     # Project context
│   ├── guardrails.md                 # Shared memory (error lessons, constraints, patterns)
│   ├── metrics.json                  # Created during execution
│   └── specs/
│       └── user-auth/                # Goal name
│           ├── referents/            # From sop-reverse (referent mode)
│           │   ├── catalog.md
│           │   ├── comparative-analysis.md
│           │   └── extracted-patterns.md
│           ├── rough-idea.md         # From sop-planning
│           ├── idea-honing.md        # From sop-planning
│           ├── research/             # From sop-planning
│           │   ├── jwt-libraries.md
│           │   └── password-hashing.md
│           ├── design/               # From sop-planning
│           │   └── detailed-design.md
│           └── implementation/       # From sop-task-generator
│               └── plan.md
│
└── src/                              # Implementation output
    ├── routes/
    │   └── auth.ts
    ├── middleware/
    │   └── authenticate.ts
    └── utils/
        └── jwt.ts
```

---

## Handoff Between Skills

**Constraints:**
- You MUST use file paths for skill-to-skill data transfer because this maintains separation of concerns
- You MUST verify output files exist before proceeding because missing files cause failures

### Referent Discovery → Planning

**Handoff mechanism**: Referent catalog + extracted patterns

```javascript
// sop-reverse (referent mode) outputs:
.ralph/specs/realtime-collab/referents/
├── catalog.md                  // Summary + recommendation
├── yjs-analysis.md             // Per-referent analysis
├── automerge-analysis.md
├── comparative-analysis.md     // Cross-referent comparison
└── extracted-patterns.md       // Ready-to-adopt patterns

// Orchestrator invokes sop-planning with:
/sop-planning rough_idea="{goal}" discovery_path=".ralph/specs/{goal}/referents/catalog.md" project_dir=".ralph/specs/{goal}" mode={PLANNING_MODE}

// sop-planning reads catalog.md for proven patterns
// sop-planning reads extracted-patterns.md for design foundations
```

### Planning → Task Generation

**Handoff mechanism**: Design document

```javascript
// sop-planning outputs:
.ralph/specs/user-auth/design/detailed-design.md

// Orchestrator invokes sop-task-generator with:
{
  input: ".ralph/specs/user-auth/implementation/plan.md",
  mode: "{PLANNING_MODE}"
}

// sop-task-generator reads design and generates tasks
```

### Task Generation → sop-code-assist (Interactive)

**Handoff mechanism**: .code-task.md files

```bash
# sop-task-generator outputs:
.ralph/specs/user-auth/implementation/
├── plan.md
└── step01/
    ├── task-01-jwt-utils.code-task.md
    ├── task-02-login-endpoint.code-task.md
    └── task-03-middleware.code-task.md

# For INTERACTIVE execution, use sop-code-assist skill:
/sop-code-assist task_description=".ralph/specs/user-auth/implementation/step01/task-01-jwt-utils.code-task.md" mode="interactive"

# sop-code-assist reads:
# - The .code-task.md file (requirements)
# - .ralph/specs/user-auth/design/detailed-design.md (context)
# - Creates .ralph/specs/{goal}/implementation/{task_name}/ artifacts
```

### Task Generation → Execution (Agent Teams Cockpit)

**Handoff mechanism**: Specs directory path

```bash
# sop-task-generator outputs:
.ralph/specs/user-auth/implementation/plan.md

# Orchestrator launches the Agent Teams cockpit with:
bash .ralph/launch-build.sh

# Teammates read:
# - .ralph/specs/user-auth/implementation/plan.md (tasks)
# - .ralph/specs/user-auth/implementation/step*/task-*.code-task.md (if exist)
# - .ralph/specs/user-auth/design/detailed-design.md (context)
# - .ralph/specs/user-auth/referents/catalog.md (proven patterns)
# - .ralph/guardrails.md (shared memory across all agents)
```

**Note:** The cockpit operates in **SOP mode only**:
- Reads `.ralph/specs/{goal}/implementation/plan.md` (generated by sop-task-generator)
- Reads `.code-task.md` files for detailed task execution
- Quality gates run via TaskCompleted hook (test → typecheck → lint → build)

> **DEPRECATED**: Legacy `IMPLEMENTATION_PLAN.md` in project root is no longer supported.
> All planning goes through the SOP structure: `.ralph/specs/{goal}/implementation/plan.md`

---

## Error Handling Across Skills

**Constraints:**
- You MUST validate phase outputs before proceeding because incomplete outputs cause downstream failures
- You MUST NOT proceed with vague requirements because this causes implementation confusion
- You SHOULD trigger research when knowledge is missing because informed decisions require investigation

### Referent Discovery Incomplete

**Symptom**: Too few referents identified or shallow analysis

**Detection**: sop-reverse validation — catalog.md missing or incomplete

**Action**: Expand referent search, add more exemplars, deepen analysis

**Example**:
```
Referent search: "Only found 1 referent for real-time collaboration"
Action: "Expand search — look for Yjs, Automerge, ShareDB, Liveblocks, Convergence"
```

### Planning Without Sufficient Research

**Symptom**: Design decisions made without investigation

**Detection**: sop-planning validation

**Action**: Trigger research loop before design

**Example**:
```
Planning: "Need to choose JWT library. Researching options..."
→ Creates research/jwt-libraries.md
→ Returns to design phase with findings
```

### Task Plan Too Vague

**Symptom**: Tasks without clear acceptance criteria

**Detection**: sop-task-generator validation

**Action**: Reject plan, ask for clarification

**Example**:
```
Bad task: "- [ ] Add authentication"

Rejection: "Too vague. What specific auth component?"

Good task: "- [ ] Implement JWT token generation | Size: M
  Create utils/jwt.ts with sign() and verify() functions"
```

### Execution Failure

**Symptom**: Teammate cannot complete task

**Detection**: Quality gates fail repeatedly (TaskCompleted hook)

**Action**: Circuit breaker stops task cycle, update plan, restart cockpit

**Example**:
```
Task cycle 5: Tests fail (authentication logic incomplete)
Task cycle 6: Tests fail (same issue)
Task cycle 7: Tests fail (same issue)
→ Circuit breaker triggers (EXIT_CIRCUIT_BREAKER)

Human reviews logs, updates plan.md with clarification:
"- [ ] Implement JWT generation - use RS256 algorithm, not HS256"

Resume: bash .ralph/launch-build.sh
```

---

## Quality Gates Across Phases

**Constraints:**
- You MUST pass phase validation before proceeding because skipping gates causes downstream failures
- You MUST reject incomplete outputs because quality compounds through phases
- You SHOULD document rejection reasons because this guides correction

Each phase has validation:

| Phase | Validation | Rejection Criteria |
|-------|------------|-------------------|
| **Discovery** | Completeness check | Missing constraints, risks not addressed |
| **Planning** | Design review | Vague requirements, insufficient research |
| **Task Generation** | Task structure | Missing acceptance criteria, size unclear |
| **Execution** | Backpressure gates | Tests fail, types fail, lint fails, build fails |

---

## Cost Model

**Constraints:**
- You SHOULD estimate costs before starting because this sets expectations
- You SHOULD compare with manual implementation because this justifies approach
- You MUST NOT reduce quality gates to cut costs because production excellence is non-negotiable

Typical cost breakdown for medium-sized feature:

| Phase | Duration | Tokens | Cost |
|-------|----------|--------|------|
| sop-reverse (referent) | 20-40 min | ~30K | $0.15 |
| sop-planning | 30 min | ~40K | $0.20 |
| sop-task-generator | 10 min | ~15K | $0.08 |
| Configuration | 5 min | ~5K | $0.02 |
| **Planning Total** | **65-85 min** | **~90K** | **$0.45** |
| | | | |
| Execution (10 tasks) | 3 hours | ~500K | $2.50 |
| **Total** | **~4-5 hours** | **~590K** | **~$2.95** |

**ROI Comparison**:
- Manual implementation: ~8 hours developer time
- Agent Teams cockpit: ~1-1.5 hours human time + ~3 hours autonomous
- Cost: $2.95 vs $400+ developer cost
- Quality: SDD enforced, all gates passed

---

## Advanced Patterns

**Constraints:**
- You MUST complete one goal before starting dependent goal because context from prior work informs later work
- You SHOULD reference prior specs when building dependent features because this maintains consistency
- You MAY use sop-reverse standalone for research without implementation because analysis has standalone value

### Pattern 1: Multi-Goal Projects

```bash
# Goal 1: Authentication
/ralph-orchestrator goal="user authentication system"
→ Referent discovery → Planning → Execution
bash .ralph/launch-build.sh

# Goal 2: User Profile (depends on auth)
/ralph-orchestrator goal="user profile management"
# In planning, reference .ralph/specs/user-auth/ for context
bash .ralph/launch-build.sh
```

### Pattern 2: Iterative Improvement

```bash
# Round 1: Basic auth
/ralph-orchestrator goal="basic authentication"
bash .ralph/launch-build.sh

# Round 2: Add MFA (use sop-reverse standalone to investigate v1, then Ralph for building)
/sop-reverse target="/src/auth" search_mode="reverse"
→ Understand existing auth implementation

/ralph-orchestrator goal="add MFA to authentication"
→ Referent discovery finds best MFA implementations → Planning → Execution
bash .ralph/launch-build.sh
```

### Pattern 3: Research Then Build

```bash
# Research phase (standalone sop-reverse, not Ralph)
/sop-reverse target="rate limiting best practices" search_mode="referent"
→ Creates analysis artifacts for reference

# Later, build with Ralph
/ralph-orchestrator goal="API rate limiter"
# In planning, reference prior research artifacts
bash .ralph/launch-build.sh
```

---

## Troubleshooting

### Referent Discovery Takes Too Long

If referent discovery exceeds 40 minutes:
- You SHOULD time-box referent discovery to 40 minutes
- You SHOULD limit the number of referents analyzed (3-5 is optimal)
- You MUST NOT skip comparative analysis regardless of time pressure

### Planning Generates Too Much Research

If research loop doesn't converge:
- You SHOULD limit research files to 3-5 per goal
- You SHOULD prioritize implementation-critical topics
- You MUST stop research when sufficient for design decisions

### Task List Too Granular

If task list has many S-size tasks:
- You SHOULD combine related micro-tasks into M-size
- You SHOULD aim for 40-60% context usage per task
- You MUST NOT create tasks smaller than single function implementation

### Teammates Can't Find Context in Specs

If teammates report missing information:
- You SHOULD verify detailed-design.md has all implementation details
- You SHOULD add cross-references from plan.md to design files
- You MUST update specs and restart the cockpit if information is truly missing

---

## Related Documentation

- [mode-selection.md](mode-selection.md) - Choosing when to use Ralph vs direct implementation
- [supervision-modes.md](supervision-modes.md) - Autonomous vs Checkpoint execution
- [observability.md](observability.md) - Monitoring during execution
- [backpressure.md](backpressure.md) - Quality gates and checkpoints

---

*Version: 2.1.0 | Updated: 2026-02-11*
*Compliant with strands-agents SOP format (RFC 2119)*
