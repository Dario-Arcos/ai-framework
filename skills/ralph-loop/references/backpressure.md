# Backpressure Reference

Quality gates that reject incomplete work.

## Standard Gates

```bash
npm test          # Tests must pass
npm run typecheck # Types must check
npm run lint      # Lint must pass
npm run build     # Build must succeed
```

**All gates must pass before commit. No exceptions.**

---

## Quality Levels

Define expectations in AGENTS.md:

| Level | Shortcuts OK | Tests Required | Polish Required |
|-------|--------------|----------------|-----------------|
| **Prototype** | Yes | No | No |
| **Production** | No | Yes | Some |
| **Library** | No | Yes | Yes |

### Behavior by Level

- **Prototype** - Fast iteration, skip backpressure gates
- **Production** - TDD mandatory, all gates must pass
- **Library** - Full coverage, documentation, edge cases

**Set in:** `AGENTS.md` -> Quality Level section

---

## Task Sizing

One task = one context window.

### Right-sized

- Add database column + migration
- Add UI component to existing page
- Fix bug in login flow

### Too Large

- Build entire auth system
- Implement complete dashboard

**Test:** If >2000 lines to understand or >5 files -> split.

---

## Context Thresholds

| Zone | Usage | Action |
|------|-------|--------|
| Green | <40% | Operate freely |
| Yellow | 40-60% | Wrap up current task |
| Red | >60% | Force rotation |

---

## Gutter Detection

**You're stuck if:**
- Same command fails 3 times
- Same file modified 5+ times
- No progress in 30 minutes

**Recovery:** Add Sign -> Exit -> Fresh approach next iteration.

---

## Circuit Breaker

After 3 consecutive failures, loop.sh stops:

1. Check errors.log for details
2. Review last Claude output
3. Fix manually or adjust specs
4. Run ./loop.sh again

---

## Plan Format

**The plan is disposable.** Regeneration costs one planning loop.

### Constraints

| Element | Limit |
|---------|-------|
| Entire plan | <100 lines |
| Each task | 3-5 lines |
| Implementation details | None |

### Task Format

```markdown
- [ ] Task title | Size: S/M | Files: N
  Acceptance: [single sentence]
```

### Anti-patterns

- 400-line plans
- Research summaries in plan (move to specs/)
- Step-by-step implementation notes
- Keeping completed tasks forever

**Recovery:** If plan exceeds 100 lines -> `./loop.sh plan 1`
