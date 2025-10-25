# Constitutional Compliance Checklist

**Source**: `@.specify/memory/constitution.md` Article III (Core Principles)

Apply these checks to ALL Claude Code components before delivery.

---

## Principle 1: AI-First Workflow

- [ ] Component executable by AI without manual intervention
- [ ] Text/JSON interfaces (no GUI-only operations)
- [ ] Clear patterns and established conventions followed
- [ ] No manual processes that cannot be delegated to AI

**Examples**:

- ✅ Bash scripts invoked via markdown
- ✅ Task tool for agent invocation
- ✅ JSON stdin/stdout for hooks
- ❌ "Manually edit file X and run Y"

---

## Principle 2: Value/Complexity Ratio

- [ ] Value delivered ≥ 2x implementation complexity
- [ ] Simplest solution that meets requirements
- [ ] No premature optimization
- [ ] No speculative features ("in case we need...")

**Scoring**:

- Benefit (1-5) - Complexity (1-5) = ROI
- ROI must be ≥ 2

**Examples**:

- ✅ Reuse existing agent instead of creating new one
- ✅ Simple if/else instead of complex state machine
- ❌ Framework for single use case
- ❌ Abstraction without ≥30% duplication

---

## Principle 3: Test-First Development

- [ ] Tests written before implementation (if applicable)
- [ ] Contract tests for integrations
- [ ] Integration tests preferred over mocks
- [ ] No implementation without failing tests first

**Applicability**:

- Commands: Logic testable via bash -n
- Hooks: I/O testable via mock stdin
- Agents: Behavior testable via Task tool
- MCP: Integration testable via claude mcp list

---

## Principle 4: Complexity Budget

**Size classes** (Δ LOC = additions - deletions):

| Size | Δ LOC | New files | New deps | Δ CPU/RAM |
| ---- | ----: | --------: | -------: | --------: |
| S    |  ≤ 80 |       ≤ 1 |        0 |     ≤ 1 % |
| M    | ≤ 250 |       ≤ 3 |      ≤ 1 |     ≤ 3 % |
| L    | ≤ 600 |       ≤ 5 |      ≤ 2 |     ≤ 5 % |

**Checks**:

- [ ] Component size matches complexity budget
- [ ] If exceeds budget: decompose OR justify with ROI analysis
- [ ] Anti-Abstraction: max 3 projects for initial implementation
- [ ] Use framework features directly, avoid unnecessary layers

---

## Principle 5: Reuse First & Simplicity

- [ ] Searched for existing components before creating new
- [ ] New abstraction justified (≥30% duplication OR future-cost reduction)
- [ ] Library-First: Feature begins as standalone library (if applicable)
- [ ] Einstein principle: "As simple as possible, but not simpler"

**Workflow**:

1. Search existing: `agents/`, `commands/`, `hooks/`
2. Reuse if possible: Copy pattern, adapt minimally
3. New only if: No similar exists OR ≥30% different

---

## Final Constitutional Check

**Before delivery, answer**:

1. **AI-First**: Can AI execute this autonomously? → YES/NO
2. **Value/ROI**: Is benefit ≥ 2x complexity? → YES/NO
3. **TDD**: Were tests written first (if applicable)? → YES/NO
4. **Budget**: Within complexity budget OR justified? → YES/NO
5. **Reuse**: Existing patterns reused OR justified? → YES/NO

**ALL must be YES to proceed.**

If ANY is NO → Fix or justify exception with Constitutional Council.

---

**Version**: 1.0.0 (aligned with Constitution v2.3.0)
