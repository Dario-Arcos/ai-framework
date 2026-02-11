# Mode Selection Reference

## Overview

This reference provides decision flowcharts for choosing the right workflow approach in Ralph. Proper mode selection ensures optimal resource usage and quality outcomes.

---

## Tool Selection: Ralph vs Standalone Skills

**Constraints:**
- You MUST use Ralph for demanding tasks requiring exhaustive investigation and implementation because Ralph enforces referent discovery before design
- You MUST use `sop-reverse` standalone for investigation-only tasks because Ralph always leads to implementation
- You MUST NOT use Ralph for simple tasks because overhead exceeds benefit

```mermaid
graph TD
    Start[Starting a task] --> Q1{Task complexity<br/>and type?}

    Q1 -->|Complex build task| Ralph[Ralph Orchestrator]
    Q1 -->|Investigation only| Standalone[sop-reverse standalone]
    Q1 -->|Simple change| Direct[Direct implementation]

    Ralph --> RalphSteps[1. sop-reverse referent<br/>2. sop-planning<br/>3. sop-task-generator<br/>4. Agent Teams execution]

    Standalone --> StandaloneSteps[sop-reverse reverse/referent<br/>→ Analysis artifacts only]

    RalphSteps --> Done1[Implementation complete]
    StandaloneSteps --> Done2[Specs/analysis available]
    Direct --> Done3[Change applied]
```

---

## When to Use Ralph Agent Teams vs Direct Implementation

**Constraints:**
- You MUST NOT use ralph-orchestrator for trivial tasks (1-2 steps) because overhead exceeds benefit
- You MUST use ralph-orchestrator for complex tasks (5+ steps) because fresh context improves quality
- You SHOULD use ralph-orchestrator when context exceeds 100K tokens because compaction loses information

```mermaid
graph TD
    Task[New Task] --> Size{Task complexity?}

    Size -->|Trivial<br/>1-2 steps| Direct[Direct Implementation]
    Size -->|Small<br/>3-5 steps| Q1{Context concerns?}
    Size -->|Medium+<br/>5+ steps| Ralph[Use ralph-orchestrator]

    Q1 -->|No concerns| Direct
    Q1 -->|Yes, large context| Ralph

    Ralph --> Plan[Interactive Planning Phase]
    Plan --> Exec[Autonomous Execution]

    Direct --> Done[Implement directly]

    style Ralph fill:#e1f5e1
    style Direct fill:#f5e1e1
```

### Decision Criteria Table

| Factor | Direct | Ralph Agent Teams |
|--------|--------|------------|
| **Steps** | ≤ 3 | ≥ 3 |
| **Files** | ≤ 2 | ≥ 3 |
| **Duration** | < 30 min | > 1 hour |
| **Context** | < 50K tokens | > 100K tokens |
| **Scenarios** | None or simple | SDD required |
| **Overnight** | No | Possible |
| **Quality gates** | Not needed | Critical |

---

## Ralph Flow Decision Points

**Constraints:**
- You MUST NOT skip referent discovery because proven patterns inform better designs
- You MUST NOT skip planning if design doesn't exist because ad-hoc design leads to poor architecture
- You MUST complete task generation before execution because teammates need structured tasks

```mermaid
graph TD
    Idea[Have an idea] --> Ref[sop-reverse referent<br/>Find world-class exemplars]

    Ref --> Q1{Design<br/>exists?}

    Q1 -->|No| Plan[sop-planning]
    Q1 -->|Yes| Q2{Tasks<br/>defined?}

    Plan --> Tasks[sop-task-generator]

    Q2 -->|No| Tasks
    Q2 -->|Yes| Exec[Agent Teams execution]

    Tasks --> Exec

    style Ref fill:#f0ffe1
    style Plan fill:#e1f0ff
    style Tasks fill:#f0e1ff
    style Exec fill:#e1ffe1
```

---

## Standalone sop-reverse Use Cases

**Constraints:**
- You MUST use `sop-reverse` standalone (not Ralph) for investigation-only tasks because Ralph always leads to implementation
- You SHOULD use `sop-reverse` standalone for legacy code understanding before refactoring because investigation may not require full Ralph
- You MAY skip standalone investigation for well-documented systems with clear architecture

**Use `sop-reverse` standalone when investigating:**

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
    B -->|Understand only| C[sop-reverse standalone → Specs]
    B -->|Improve it| D[sop-reverse standalone → then Ralph]
    B -->|Replace it| E[Ralph directly]

    style C fill:#e1f0ff
    style D fill:#ffe1e1
    style E fill:#f0ffe1
```

---

## Task Sizing for Ralph Agent Teams

**Constraints:**
- You MUST decompose XL tasks into multiple team runs because a single team run cannot handle weeks of work
- You MUST NOT use ralph-orchestrator for trivial tasks (< 3 steps) because overhead exceeds value
- You SHOULD target M-L size tasks for optimal Agent Teams efficiency

### Perfect for Ralph Agent Teams (M-L size)

```
✓ Add authentication system with JWT
  - Multiple files (controllers, middleware, tests)
  - SDD approach required
  - Clear acceptance criteria
  - 3-8 hours estimated

✓ Implement caching layer with Redis
  - Database abstraction
  - Cache invalidation strategy
  - Performance tests
  - 4-6 hours estimated
```

### Too Small for Ralph Agent Teams (S size)

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

## Safety Configuration

**Constraints:**
- You MUST configure safety limits before execution because defaults may not match your risk tolerance
- You MUST review `.ralph/config.sh` for high-risk tasks because auth/payments need tighter limits
- You MAY adjust MAX_CONSECUTIVE_FAILURES based on task complexity

After planning, configure safety limits in `.ralph/config.sh`:

> **Key insight**: Execution is ALWAYS autonomous via Agent Teams cockpit (`bash .ralph/launch-build.sh`). Safety is enforced by circuit breakers, not by human pauses.

```mermaid
graph TD
    Ready[Planning Complete] --> Config[Configure .ralph/config.sh]

    Config --> Q1{Task risk?}

    Q1 -->|High<br/>Auth/Payments| Strict[Strict limits<br/>MAX_CONSECUTIVE_FAILURES=2]
    Q1 -->|Normal| Default[Default limits<br/>MAX_CONSECUTIVE_FAILURES=3]
    Q1 -->|Low/Familiar| Relaxed[Relaxed limits<br/>MAX_CONSECUTIVE_FAILURES=5]

    Strict --> Launch[Launch Agent Teams cockpit]
    Default --> Launch
    Relaxed --> Launch

    Launch --> Monitor[Monitor .ralph/metrics.json<br/>and .ralph/failures.json]
```

---

## Common Scenarios

### Scenario 1: New Feature from Scratch

```
Situation: Build user profile page
Complexity: Medium (4-6 files, tests, styling)
Experience: Familiar with stack

Decision: Ralph Orchestrator
Steps:
1. /ralph-orchestrator goal="user profile page"
2. sop-reverse referent (20-40 min) — find best profile page implementations
3. sop-planning (30 min)
4. sop-task-generator (10 min)
5. Configure quality gates in .ralph/config.sh
6. Launch and monitor
```

### Scenario 2: Understanding Legacy Code

```
Situation: Old payment processing module
Complexity: High (unfamiliar code)
Goal: Understand before migrating

Decision: sop-reverse standalone (NOT Ralph)
Steps:
1. /sop-reverse target="/src/payments" search_mode="reverse"
2. Analyze findings
3. Review specs
4. Later, use /ralph-orchestrator if building a replacement
```

### Scenario 3: Quick Bug Fix

```
Situation: Button click not working
Complexity: Trivial (1 file, 1 function)
Duration: 5-10 minutes

Decision: Direct Implementation
Reason: Ralph Agent Teams overhead > task complexity
```

### Scenario 4: Large Refactoring

```
Situation: Extract shared utilities into library
Complexity: Large (15+ files)
Risk: Breaking changes

Decision: Ralph Orchestrator with strict safety limits
Steps:
1. /ralph-orchestrator goal="extract shared utilities into library"
2. Referent discovery + Planning phase (interactive)
3. Configure: MAX_CONSECUTIVE_FAILURES=2 in .ralph/config.sh
4. Monitor .ralph/metrics.json for progress
5. Review .ralph/failures.json if issues arise
```

---

## Anti-Patterns to Avoid

**Constraints:**
- You MUST NOT use ralph-orchestrator for 1-line fixes because 10x overhead wastes resources
- You MUST NOT skip planning phase because confused teammates produce poor output
- You MUST NOT use Ralph on legacy code without first understanding it via standalone sop-reverse because changes break existing assumptions
- You MUST NOT run a single team for XL tasks because unclear progress leads to stalled execution

### ❌ Using Ralph Agent Teams for Everything

```
Problem: "I'll use ralph-orchestrator for this 1-line fix"
Reality: 10x overhead for trivial task
Solution: Direct implementation for tasks < 3 steps
```

### ❌ Skipping Planning Phase

```
Problem: "I'll just start the cockpit, I know what I want"
Reality: Teammates confused, poor quality output
Solution: Always complete planning first
```

### ❌ Using Ralph Without Understanding Legacy Code

```
Problem: "Ralph to improve legacy code without understanding it"
Reality: Changes break existing assumptions
Solution: sop-reverse standalone → understand → then Ralph to build improvements
```

### ❌ Task Too Large

```
Problem: "Build entire CRM system with ralph-orchestrator"
Reality: Team runs forever, unclear progress
Solution: Decompose into features, run multiple team sessions
```

---

## Quick Reference

| If you... | Then use... |
|-----------|-------------|
| Have a new idea to build | Ralph Orchestrator |
| Need to understand existing code only | `sop-reverse` standalone |
| Want to improve after understanding | `sop-reverse` standalone → then Ralph |
| Task is trivial (< 3 steps) | Direct implementation |
| Task is complex (> 5 steps) | Ralph Orchestrator |
| First time using ralph-orchestrator | Strict safety limits (low MAX_CONSECUTIVE_FAILURES) |
| High-risk task (auth, payments) | Strict safety limits + high GATE_COVERAGE |
| Overnight development needed | Default safety limits |
| Learning codebase patterns | Start strict, relax limits as confidence grows |

---

## Troubleshooting

### Unsure Whether to Use Ralph

If the right tool is unclear:
- You SHOULD ask: "Am I building something, or just investigating?"
- If building → use Ralph (referent discovery is automatic)
- If investigating only → use `sop-reverse` standalone
- You MUST NOT use Ralph for investigation-only tasks

### Task Size Ambiguous

If task sizing is unclear:
- You SHOULD estimate number of files to modify
- You SHOULD estimate hours of work
- You MUST decompose if estimate exceeds 1 week

### Safety Configuration Unclear

If safety configuration is unclear:
- You SHOULD start with strict limits (MAX_CONSECUTIVE_FAILURES=2) for safety
- You SHOULD relax limits after 5-10 successful runs with confidence
- You MUST NOT set MAX_CONSECUTIVE_FAILURES above 5 for high-risk tasks

---

*Version: 2.1.0 | Updated: 2026-02-11*
*Compliant with strands-agents SOP format (RFC 2119)*
