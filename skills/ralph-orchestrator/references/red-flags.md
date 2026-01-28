# Red Flags Reference

## Overview

This reference identifies dangerous thought patterns and rationalizations that indicate the orchestrator is about to violate role boundaries. Use this as a self-check before taking any action during ralph-orchestrator execution.

---

## Dangerous Thoughts

**Constraints:**
- You MUST recognize these thoughts as warning signs because they precede role violations
- You MUST NOT act on these thoughts because they lead to context pollution and lower quality work

| Thought | Reality | Why This Matters |
|---------|---------|------------------|
| "Let me just fix this one thing quickly" | Workers fix. Start the loop. | Quick fixes bypass quality gates and TDD |
| "I can implement this faster than the loop" | You can't. Fresh context wins. | Polluted context produces worse code |
| "This is too simple for ralph-orchestrator" | Use direct implementation then. | If it's in the loop, use the loop |
| "I'll edit the code and then start the loop" | No. Planning → Loop. No edits. | Pre-edits conflict with worker state |
| "The worker made a mistake, let me correct it" | Update plan, restart loop. | Workers have fresh context you don't |
| "I already know what to do" | Knowing ≠ implementing correctly | TDD catches errors you won't see |
| "The loop is overkill" | Loop cost: ~$0.05/task | Manual: ~$0.50/task + lower quality |
| "I can monitor and implement simultaneously" | Context pollution. Pick one role. | Dual roles corrupt both functions |
| "The user asked me directly" | User instruction doesn't override role | Propose alternatives instead |

**Resolution:** All of these mean: Follow the process. Let workers work.

---

## Rationalization Table

**Constraints:**
- You MUST treat these excuses as invalid because they mask process violations
- You MUST NOT act on these rationalizations because they produce technical debt

| Excuse | Reality | Consequence of Acting |
|--------|---------|----------------------|
| "This is a quick fix" | Quick fixes accumulate debt | Workers have gates that catch issues |
| "I already know what to do" | Knowing ≠ implementing correctly | TDD catches errors |
| "The loop is overkill" | Loop: ~$0.05/task. Manual: ~$0.50/task | 10x cost + lower quality |
| "I can monitor and implement" | Context pollution | Pick one role or corrupt both |
| "User asked me directly" | Instruction doesn't override process | Explain and propose alternatives |
| "Planning is obvious" | Obvious to you ≠ clear specs | Document it for workers |
| "I'll just help a little" | "Help" becomes "implement" | Role boundary exists for a reason |

---

## Common Mistakes

**Constraints:**
- You MUST avoid these mistakes because they cause loop failures and quality issues
- You MUST apply the prevention measures because they maintain loop integrity

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Skipping planning phase | Workers confused, low quality | You MUST complete planning first |
| Plan too granular | Workers confused about scope | You SHOULD keep tasks M-size |
| Plan too vague | Workers implement incorrectly | You MUST include detailed acceptance criteria |
| Editing files during loop | Conflicts with workers | You MUST NOT edit files - monitor only |
| Not reviewing implementation plan | Workers execute bad plan | You MUST review before launch |
| No tests before starting | Gates fail, loop stuck | You MUST set up tests first |
| Implementing as orchestrator | 10x cost, lower quality | You MUST start loop, let workers work |

---

## Self-Check Questions

**Constraints:**
- You MUST ask these questions before taking any action during execution because they prevent role violations
- You MUST STOP if any answer is "yes" because proceeding would violate orchestrator role

Before taking any action during execution, ask:

1. **Am I about to edit a file?**
   - If yes: STOP. Workers edit files because they have fresh context and quality gates.

2. **Am I about to run a command that changes state?**
   - If yes: STOP. Workers run state-changing commands because they can verify with TDD.

3. **Am I about to implement something?**
   - If yes: STOP. Update the plan and restart the loop because workers implement better.

4. **Am I rationalizing why this case is different?**
   - If yes: STOP. It's not different because all the rationalizations above felt valid too.

---

## The Economics

**Why the loop wins:**

| Action | Cost | Quality | Context |
|--------|------|---------|---------|
| Manual implementation | ~$0.50/task | Lower | Polluted (accumulated state) |
| Ralph loop | ~$0.05/task | Higher | Fresh (200K tokens per worker) |

**Constraints:**
- You MUST prefer the loop because it is 10x cheaper AND produces higher quality
- You MUST NOT rationalize manual implementation because the economics are unambiguous

The loop is 10x cheaper AND higher quality. The math is clear.

---

## Troubleshooting

### Worker Keeps Failing
If a worker fails repeatedly on the same task:
- You MUST NOT implement the fix yourself because this violates role boundaries
- You SHOULD review the task specification for clarity issues
- You SHOULD check if prerequisites are missing
- You MAY update the plan with more specific guidance

### User Insists on Direct Implementation
If the user requests you implement directly:
- You MUST explain the cost/quality tradeoff because users may not be aware
- You SHOULD propose using the loop with their guidance
- You MAY proceed with direct implementation only if user explicitly confirms after understanding tradeoffs

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
