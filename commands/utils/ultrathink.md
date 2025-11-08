---
description: Activate deep work mode for complex problems requiring maximum focus and systematic thinking
argument-hint: "[optional: specific focus area]"
allowed-tools: All tools
---

# /ultrathink — Deep Work Protocol

Activates systematic deep work mode for complex, high-stakes problems.

**Usage:**
```bash
/ai-framework:utils:ultrathink
/ai-framework:utils:ultrathink API architecture redesign
```

---

## When to Use

Invoke for:
- Complex architectural decisions
- High-stakes refactoring
- Performance-critical optimization
- Security-sensitive implementations
- Problems requiring multi-disciplinary analysis

**Do NOT use for**: Routine tasks, simple bug fixes, trivial changes

---

## Deep Work Protocol

### 1. Systematic Problem Framing

**Take a deep breath and work on this step-by-step.**

Frame the problem:
- [ ] What exactly are we solving? (≤3 bullets)
- [ ] Why is this critical? (business/user impact)
- [ ] What are we NOT solving? (scope boundaries)
- [ ] Size estimate (S/M/L from CLAUDE.md §3)

---

### 2. Multi-Approach Analysis

**Generate 2-3 fundamentally different approaches**:

For each approach:
```
Approach X: [Name]
- Core idea: [1 line]
- Pros: [2-3 bullets]
- Cons: [2-3 bullets]
- Complexity: [1-5]
- Benefit: [1-5]
- ROI: [benefit - complexity]
```

Select approach with **highest ROI**, tie-break toward simplest.

---

### 3. Challenge Assumptions

Before proceeding, question:
- [ ] Why does it have to work this way?
- [ ] What if we started from zero?
- [ ] Is there a 10x simpler solution delivering 80% value?
- [ ] What constraints are real vs assumed?

**If uncertain**: Use AskUserQuestion to validate assumptions.

---

### 4. Implementation Excellence

**Plan before code**:
- [ ] Architectural sketch (components, data flow, interfaces)
- [ ] Test strategy (what to test, how to verify)
- [ ] Success criteria (measurable, specific)

**During implementation**:
- [ ] TDD: Red → Green → Refactor
- [ ] Reality Check: Actually run/test the code
- [ ] Simplify: Remove complexity without losing power

**Validation**:
- [ ] Would I bet my professional reputation on this?
- [ ] Can I remove any abstraction without breaking functionality?
- [ ] Would a new contributor understand this in 5 minutes?

---

### 5. Continuous Refinement

**Iterate until**:
- Tests pass (100% coverage of critical paths)
- Performance meets requirements (<X ms, <Y% CPU)
- Code is as simple as possible (Einstein principle)
- Edge cases handled gracefully

**Quality bar**: Not just working, but production-ready.

---

## Output Format

Always conclude with:

```
✓ Validated: CLAUDE.md §[X,Y,Z]

Deep Work Summary:
- Approaches analyzed: [N]
- ROI selected: [X]
- Complexity: [S/M/L]
- Tests: [pass/fail count]
```

---

## Evidence Base

This protocol integrates research-validated techniques:

- **"Take a deep breath"**: Google DeepMind OPRO (2023) — +46.2 points math accuracy
- **Multi-approach analysis**: ATLAS study (2024) — +57.7% quality with concrete instructions
- **Systematic framing**: Reduces scope creep, establishes boundaries
- **Challenge assumptions**: CLAUDE.md §8 Objectivity principle
- **Simplify ruthlessly**: Einstein + constitution reuse-first principle

**Sources**: 9 academic papers (2024-2025), Anthropic/OpenAI official guidance

---

## Constitutional Compliance

- **Value/Complexity ≥ 2**: Systematic approach maximizes ROI
- **TDD**: Red-green-refactor enforced
- **Simplicity**: Einstein principle applied
- **Objectivity**: Assumption challenging mandatory
- **AI-First**: Fully executable by AI with human oversight
