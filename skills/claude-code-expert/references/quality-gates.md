# Quality Gates Reference

## Overview

This reference defines the quality gates for Claude Code components including sub-agents, commands, hooks, and MCP integrations. Use this checklist to validate components before delivery.

---

## Gate 1: Syntax Validation

**Validator**: `scripts/validate_*.py` (Automated)

**Constraints:**
- You MUST ensure YAML/JSON syntax is valid because parsing errors cause immediate component failures
- You MUST verify all required fields are present because missing fields cause undefined behavior
- You MUST check that data types match specifications because type mismatches cause runtime errors
- You MUST NOT leave trailing commas or syntax errors because these prevent component loading

**Responsibility**: Script (automated)

---

## Gate 2: Security Validation

**Validator**: Scripts + Manual review (Automated + Manual)

**Constraints:**
- You MUST NOT include hardcoded credentials (strings >20 chars without `${VAR}`) because exposed secrets compromise security
- You MUST quote bash variables (`"$var"` not `$var`) because unquoted variables cause word splitting and glob expansion vulnerabilities
- You MUST NOT use `eval()` or `exec()` without explicit justification because arbitrary code execution enables injection attacks
- You SHOULD avoid `subprocess` with `shell=True` because shell injection vulnerabilities become possible
- You MUST implement input validation because unvalidated input enables injection and overflow attacks

**Responsibility**: Script detects patterns, human validates context

---

## Gate 3: Logic Consistency

**Validator**: AI Self-Review (SKILL.md Step 6) (AI-Powered)

**Constraints:**
- You MUST define variables before use because undefined variables cause runtime failures
- You MUST complete all branches (if/then/fi, try/catch) because incomplete branches cause unpredictable behavior
- You MUST include cleanup in error paths because resource leaks degrade system stability
- You MUST NOT invoke tools before context loads because tool calls without context fail silently
- You MUST NOT create circular dependencies because they cause infinite loops and stack overflows

**Responsibility**: Claude executing skill

---

## Gate 4: Constitutional Compliance

**Reference**: `@.specify/memory/constitution.md`

**Constraints:**
- You MUST achieve Value/Complexity ratio ≥ 2 because lower ratios indicate over-engineering
- You MUST prioritize Reuse First (existing patterns) because duplication increases maintenance burden
- You MUST use AI-First design (text/JSON interfaces) because other formats reduce AI interoperability
- You SHOULD apply TDD when applicable because untested code has higher defect rates
- You MUST NOT over-engineer solutions because unnecessary complexity reduces maintainability

**Responsibility**: Human + AI review

---

## Gate 5: Integration Validation

**Constraints:**
- You MUST verify component integrates with existing project because isolated components provide no value
- You MUST NOT use duplicate names because name collisions cause loading conflicts
- You MUST verify category and paths are correct because incorrect paths prevent discovery
- You MUST confirm dependencies are available because missing dependencies cause runtime failures

**Responsibility**: Human

---

## Gate 6: Production Readiness

**The Ultimate Test:**

> **"Would you bet your professional reputation on this working correctly in production?"**

- If YES: Deliver
- If NO: Fix and re-validate

**Constraints:**
- You MUST pass all previous gates because skipping gates allows defects to reach production
- You MUST NOT leave TODO/FIXME comments because they indicate incomplete implementation
- You SHOULD test against real scenarios because synthetic tests miss edge cases
- You MUST complete documentation because undocumented components cannot be maintained

**Responsibility**: Human (final accountability)

---

## Troubleshooting

### Gate Failure Patterns

If Gate 1 (Syntax) fails repeatedly:
- You SHOULD use a YAML/JSON linter before submission
- You SHOULD validate against schema definitions
- You MAY use online validators to identify specific errors

If Gate 2 (Security) flags false positives:
- You SHOULD document justification in code comments
- You MUST get human review approval for exceptions
- You MUST NOT disable security checks globally because this defeats the purpose

If Gate 3 (Logic) identifies issues:
- You SHOULD trace execution path step by step
- You SHOULD add explicit logging at branch points
- You MAY simplify complex logic to reduce error surface

### Escalation

If multiple gates fail:
- You SHOULD consider redesigning the component
- You MUST NOT bypass gates by claiming urgency because defects in production cost more than delays

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
