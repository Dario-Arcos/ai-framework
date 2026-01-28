# Mode Selection Reference

## Overview

This reference provides decision flowcharts for choosing the right workflow approach in Ralph. Proper mode selection ensures optimal resource usage and quality outcomes.

---

## Flow Selection: Forward vs Reverse

**Constraints:**
- You MUST use Forward Flow for new ideas because there's no existing artifact to investigate
- You MUST use Reverse Flow when understanding existing code before improving because blind changes break assumptions
- You SHOULD continue to Forward after Reverse if planning improvements because Reverse generates specs that feed planning

```mermaid
graph TD
    Start[Starting a task] --> Q1{Do you have<br/>existing artifact<br/>to investigate?}

    Q1 -->|No, new idea| Forward[Forward Flow]
    Q1 -->|Yes, existing code/docs| Q2{Purpose?}

    Q2 -->|Understand before improving| Reverse[Reverse Flow]
    Q2 -->|Just improve it| Forward

    Forward --> FwdSteps[1. sop-discovery<br/>2. sop-planning<br/>3. sop-task-generator<br/>4. ralph-loop execution]

    Reverse --> RevSteps[1. sop-reverse<br/>2. Generate specs<br/>3. Continue to forward?]

    RevSteps --> Q3{Continue?}
    Q3 -->|Yes| FwdSteps
    Q3 -->|No| Done1[Specs only]

    FwdSteps --> Done2[Implementation complete]
```

---

## When to Use Ralph-Loop vs Direct Implementation

**Constraints:**
- You MUST NOT use ralph-loop for trivial tasks (1-2 steps) because overhead exceeds benefit
- You MUST use ralph-loop for complex tasks (5+ steps) because fresh context improves quality
- You SHOULD use ralph-loop when context exceeds 100K tokens because compaction loses information

```mermaid
graph TD
    Task[New Task] --> Size{Task complexity?}

    Size -->|Trivial<br/>1-2 steps| Direct[Direct Implementation]
    Size -->|Small<br/>3-5 steps| Q1{Context concerns?}
    Size -->|Medium+<br/>5+ steps| Ralph[Use ralph-loop]

    Q1 -->|No concerns| Direct
    Q1 -->|Yes, large context| Ralph

    Ralph --> Plan[Interactive Planning Phase]
    Plan --> Exec[Autonomous Execution]

    Direct --> Done[Implement directly]

    style Ralph fill:#e1f5e1
    style Direct fill:#f5e1e1
```

### Decision Criteria Table

| Factor | Direct | Ralph-Loop |
|--------|--------|------------|
| **Steps** | ≤ 3 | ≥ 3 |
| **Files** | ≤ 2 | ≥ 3 |
| **Duration** | < 30 min | > 1 hour |
| **Context** | < 50K tokens | > 100K tokens |
| **Tests** | None or simple | TDD required |
| **Overnight** | No | Possible |
| **Quality gates** | Not needed | Critical |

---

## Forward Flow Decision Points

**Constraints:**
- You MUST NOT skip discovery if requirements are unclear because vague requirements cause rework
- You MUST NOT skip planning if design doesn't exist because ad-hoc design leads to poor architecture
- You MUST complete task generation before execution because workers need structured tasks

```mermaid
graph TD
    Idea[Have an idea] --> Q1{Requirements<br/>clear?}

    Q1 -->|No| Disc[Start with<br/>sop-discovery]
    Q1 -->|Yes| Q2{Design<br/>exists?}

    Disc --> Plan[sop-planning]

    Q2 -->|No| Plan
    Q2 -->|Yes| Q3{Tasks<br/>defined?}

    Plan --> Tasks[sop-task-generator]

    Q3 -->|No| Tasks
    Q3 -->|Yes| Exec[ralph-loop execution]

    Tasks --> Exec

    style Disc fill:#fff4e1
    style Plan fill:#e1f0ff
    style Tasks fill:#f0e1ff
    style Exec fill:#e1ffe1
```

---

## Reverse Flow Use Cases

**Constraints:**
- You MUST use Reverse Flow for legacy code before refactoring because understanding prevents breaking changes
- You SHOULD use Reverse Flow for third-party library integration because patterns must be understood first
- You MAY skip Reverse Flow for well-documented systems with clear architecture

**Use Reverse Flow when investigating:**

### Code Artifacts
- Legacy codebase to understand before refactoring
- Third-party library integration patterns
- Existing API implementation
- Authentication/authorization flows

### Documentation
- API specifications to implement
- Architecture decision records
- Requirements documents
- Technical design documents

### Processes
- Deployment workflows
- CI/CD pipelines
- Development workflows
- Testing strategies

### Concepts
- Design patterns in use
- Architectural patterns (event sourcing, CQRS, etc.)
- Technical approaches
- Integration patterns

### Example Decision Flow

```mermaid
graph LR
    A[Legacy auth system] --> B{Goal?}
    B -->|Understand only| C[Reverse → Specs]
    B -->|Improve it| D[Reverse → Specs → Forward]
    B -->|Replace it| E[Forward from scratch]

    style C fill:#e1f0ff
    style D fill:#ffe1e1
    style E fill:#f0ffe1
```

---

## Task Sizing for Ralph-Loop

**Constraints:**
- You MUST decompose XL tasks into multiple loops because single loops cannot handle weeks of work
- You MUST NOT use ralph-loop for trivial tasks (< 3 steps) because overhead exceeds value
- You SHOULD target M-L size tasks for optimal loop efficiency

### Perfect for Ralph-Loop (M-L size)

```
✓ Add authentication system with JWT
  - Multiple files (controllers, middleware, tests)
  - TDD approach required
  - Clear acceptance criteria
  - 3-8 hours estimated

✓ Implement caching layer with Redis
  - Database abstraction
  - Cache invalidation strategy
  - Performance tests
  - 4-6 hours estimated
```

### Too Small for Ralph-Loop (S size)

```
✗ Fix typo in error message
  - Single file change
  - No tests needed
  - 5 minutes

✗ Update dependency version
  - Edit package.json
  - Run npm install
  - 10 minutes
```

### Too Large (XL size) - Needs Decomposition

```
✗ Build entire e-commerce platform
  - Too many unknowns
  - Unclear boundaries
  - Weeks of work
  → Split into: Auth, Products, Cart, Checkout, etc.

✗ Complete microservices migration
  - Architectural change
  - Multiple systems
  - Risk assessment needed
  → Split by service: User Service, Order Service, etc.
```

---

## Execution Mode Selection

**Constraints:**
- You MUST use HITL mode for first-time ralph-loop users because learning requires observation
- You MUST use HITL mode with checkpoints for high-risk tasks because auth/payments need human review
- You MAY use AFK mode when confident in quality gates and codebase

After planning, choose execution approach:

```mermaid
graph TD
    Ready[Planning Complete] --> Q1{First time<br/>with ralph-loop?}

    Q1 -->|Yes| HITL1[HITL mode<br/>1-5 iterations]
    Q1 -->|No| Q2{Task risk?}

    Q2 -->|High<br/>Auth/Payments| HITL2[HITL with checkpoints]
    Q2 -->|Low| Q3{Duration?}

    Q3 -->|< 1 hour| AFK1[AFK short<br/>10-20 iterations]
    Q3 -->|> 1 hour| AFK2[AFK unlimited<br/>Until complete]

    HITL1 --> Review[Review & Learn]
    HITL2 --> Review
    AFK1 --> Monitor[Passive monitoring]
    AFK2 --> Monitor

    Review --> Q4{Confident?}
    Q4 -->|Yes| AFK2
    Q4 -->|No| HITL1
```

---

## Common Scenarios

### Scenario 1: New Feature from Scratch

```
Situation: Build user profile page
Complexity: Medium (4-6 files, tests, styling)
Experience: Familiar with stack

Decision: Forward Flow → AFK mode
Steps:
1. /ralph-loop → Forward
2. sop-discovery (15 min)
3. sop-planning (30 min)
4. sop-task-generator (10 min)
5. Configure: AFK, production quality
6. Launch and monitor
```

### Scenario 2: Understanding Legacy Code

```
Situation: Old payment processing module
Complexity: High (unfamiliar code)
Goal: Understand before migrating

Decision: Reverse Flow → Specs only
Steps:
1. /ralph-loop → Reverse
2. sop-reverse → /path/to/payment-module
3. Generate specs (automatic)
4. Review findings
5. Stop (no implementation yet)
```

### Scenario 3: Quick Bug Fix

```
Situation: Button click not working
Complexity: Trivial (1 file, 1 function)
Duration: 5-10 minutes

Decision: Direct Implementation
Reason: Ralph-loop overhead > task complexity
```

### Scenario 4: Large Refactoring

```
Situation: Extract shared utilities into library
Complexity: Large (15+ files)
Risk: Breaking changes

Decision: Forward Flow → HITL with checkpoints
Steps:
1. /ralph-loop → Forward
2. Planning phase (interactive)
3. Configure: Checkpoints every 5 iterations
4. Review after each checkpoint
5. Adjust plan if needed
```

---

## Anti-Patterns to Avoid

**Constraints:**
- You MUST NOT use ralph-loop for 1-line fixes because 10x overhead wastes resources
- You MUST NOT skip planning phase because confused workers produce poor output
- You MUST NOT use Forward Flow on legacy code without understanding because changes break existing assumptions
- You MUST NOT run single loop for XL tasks because unclear progress leads to infinite loops

### ❌ Using Ralph-Loop for Everything

```
Problem: "I'll use ralph-loop for this 1-line fix"
Reality: 10x overhead for trivial task
Solution: Direct implementation for tasks < 3 steps
```

### ❌ Skipping Planning Phase

```
Problem: "I'll just start the loop, I know what I want"
Reality: Workers confused, poor quality output
Solution: Always complete planning first
```

### ❌ Wrong Flow Direction

```
Problem: "Forward flow to improve legacy code without understanding it"
Reality: Changes break existing assumptions
Solution: Reverse → understand → Forward → improve
```

### ❌ Task Too Large

```
Problem: "Build entire CRM system with ralph-loop"
Reality: Loop runs forever, unclear progress
Solution: Decompose into features, run multiple loops
```

---

## Quick Reference

| If you... | Then use... |
|-----------|-------------|
| Have a new idea | Forward Flow |
| Need to understand existing code | Reverse Flow |
| Want to improve after understanding | Reverse → Forward |
| Task is trivial (< 3 steps) | Direct implementation |
| Task is complex (> 5 steps) | Ralph-loop |
| First time using ralph-loop | HITL mode first |
| High-risk task (auth, payments) | HITL with checkpoints |
| Overnight development needed | AFK unlimited |
| Learning codebase patterns | Start HITL, graduate to AFK |

---

## Troubleshooting

### Unsure Which Flow to Use

If flow direction is unclear:
- You SHOULD ask: "Do I need to understand something first?"
- You SHOULD default to Reverse if existing artifact is involved
- You MUST NOT proceed with Forward if requirements are vague

### Task Size Ambiguous

If task sizing is unclear:
- You SHOULD estimate number of files to modify
- You SHOULD estimate hours of work
- You MUST decompose if estimate exceeds 1 week

### Mode Selection Difficult

If execution mode choice is hard:
- You SHOULD start with HITL for safety
- You SHOULD graduate to AFK after 5-10 successful HITL iterations
- You MUST NOT use AFK for high-risk tasks regardless of experience

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
