# Constitutional Compliance Reference

## Overview

This reference defines constitutional compliance checks derived from the project constitution. Apply these constraints to ALL Claude Code components before delivery.

**Source**: `@.specify/memory/constitution.md` Article III (Core Principles)

---

## Principle 1: AI-First Workflow

**Constraints:**
- You MUST make components executable by AI without manual intervention because manual steps break automation
- You MUST use text/JSON interfaces (no GUI-only operations) because AI cannot interact with GUI
- You MUST follow clear patterns and established conventions because deviations cause confusion
- You MUST NOT include manual processes that cannot be delegated to AI because this defeats AI-First design

**Examples:**
- Bash scripts invoked via markdown
- Task tool for agent invocation
- JSON stdin/stdout for hooks
- "Manually edit file X and run Y" (PROHIBITED)

---

## Principle 2: Value/Complexity Ratio

**Constraints:**
- You MUST deliver value ≥ 2x implementation complexity because lower ratios indicate poor ROI
- You MUST use simplest solution that meets requirements because over-engineering wastes resources
- You MUST NOT optimize prematurely because optimization without measurement is speculation
- You MUST NOT add speculative features ("in case we need...") because YAGNI applies

**Scoring:**
- Benefit (1-5) - Complexity (1-5) = ROI
- ROI MUST be ≥ 2

**Examples:**
- Reuse existing agent instead of creating new one
- Simple if/else instead of complex state machine
- Framework for single use case (PROHIBITED)
- Abstraction without ≥30% duplication (PROHIBITED)

---

## Principle 3: Test-First Development

**Constraints:**
- You MUST write tests before implementation (if applicable) because tests define expected behavior
- You MUST write contract tests for integrations because integrations fail silently without tests
- You SHOULD prefer integration tests over mocks because mocks can diverge from reality
- You MUST NOT implement without failing tests first because passing tests prove nothing without failure

**Applicability:**
| Component | Test Method |
|-----------|-------------|
| Commands | Logic testable via `bash -n` |
| Hooks | I/O testable via mock stdin |
| Agents | Behavior testable via Task tool |
| MCP | Integration testable via `claude mcp list` |

---

## Principle 4: Complexity Budget

**Size classes** (Δ LOC = additions - deletions):

| Size | Δ LOC | New files | New deps | Δ CPU/RAM |
|------|------:|----------:|---------:|----------:|
| S    |  ≤ 80 |       ≤ 1 |        0 |     ≤ 1 % |
| M    | ≤ 250 |       ≤ 3 |      ≤ 1 |     ≤ 3 % |
| L    | ≤ 600 |       ≤ 5 |      ≤ 2 |     ≤ 5 % |

**Constraints:**
- You MUST match component size to complexity budget because exceeding budget indicates over-engineering
- You MUST decompose OR justify with ROI analysis if exceeding budget because large changes need validation
- You SHOULD limit initial implementation to max 3 projects (Anti-Abstraction) because broad abstractions fail
- You MUST use framework features directly and avoid unnecessary layers because abstraction has cost

---

## Principle 5: Reuse First & Simplicity

**Constraints:**
- You MUST search for existing components before creating new because duplication increases maintenance
- You MUST justify new abstraction with ≥30% duplication OR future-cost reduction because unjustified abstraction wastes resources
- You SHOULD begin features as standalone libraries if applicable (Library-First) because isolation enables reuse
- You MUST follow Einstein principle: "As simple as possible, but not simpler" because over-simplification breaks functionality

**Workflow:**
1. Search existing: `agents/`, `commands/`, `hooks/`
2. Reuse if possible: Copy pattern, adapt minimally
3. New only if: No similar exists OR ≥30% different

---

## Final Constitutional Check

**Constraints:**
- You MUST answer all questions YES before delivery because partial compliance is non-compliance

**Before delivery, answer:**
1. **AI-First**: Can AI execute this autonomously? → MUST be YES
2. **Value/ROI**: Is benefit ≥ 2x complexity? → MUST be YES
3. **TDD**: Were tests written first (if applicable)? → MUST be YES
4. **Budget**: Within complexity budget OR justified? → MUST be YES
5. **Reuse**: Existing patterns reused OR justified? → MUST be YES

If ANY is NO → Fix or justify exception with Constitutional Council.

---

## Troubleshooting

### ROI Calculation Unclear

If Value/Complexity ratio is difficult to assess:
- You SHOULD break down benefits into concrete metrics
- You SHOULD estimate implementation time as proxy for complexity
- You MUST err on side of simpler solution if uncertain because over-engineering is costly

### Budget Exceeded Legitimately

If component legitimately needs more complexity:
- You MUST document ROI justification explicitly
- You MUST get approval before proceeding
- You SHOULD consider decomposition as alternative because smaller pieces are easier to validate

### No Existing Pattern Found

If search finds no reusable components:
- You SHOULD verify search was thorough (all directories checked)
- You SHOULD consider if problem is actually different
- You MUST document why new component is justified because this prevents future questions

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
