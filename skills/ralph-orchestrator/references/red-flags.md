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
| "Let me just fix this one thing quickly" | Teammates fix. Start the task cycle. | Quick fixes bypass quality gates and SDD |
| "I can implement this faster than the task cycle" | You can't. Fresh context via teammates wins. | Polluted context produces worse code |
| "This is too simple for ralph-orchestrator" | Use direct implementation then. | If it's in the task cycle, use the task cycle |
| "I'll edit the code and then start the task cycle" | No. Planning → Task cycle. No edits. | Pre-edits conflict with teammate state |
| "The teammate made a mistake, let me correct it" | Update plan, restart task cycle. | Teammates have fresh context you don't |
| "I already know what to do" | Knowing ≠ implementing correctly | SDD catches errors you won't see |
| "The task cycle is overkill" | Task cycle cost: ~$0.05/task | Manual: ~$0.50/task + lower quality |
| "I can monitor and implement simultaneously" | Context pollution. Pick one role. | Dual roles corrupt both functions |
| "The user asked me directly" | User instruction doesn't override role | Propose alternatives instead |

**Resolution:** All of these mean: Follow the process. Let teammates work.

---

## Rationalization Table

**Constraints:**
- You MUST treat these excuses as invalid because they mask process violations
- You MUST NOT act on these rationalizations because they produce technical debt

| Excuse | Reality | Consequence of Acting |
|--------|---------|----------------------|
| "This is a quick fix" | Quick fixes accumulate debt | Teammates have gates that catch issues |
| "I already know what to do" | Knowing ≠ implementing correctly | SDD catches errors |
| "The task cycle is overkill" | Task cycle: ~$0.05/task. Manual: ~$0.50/task | 10x cost + lower quality |
| "I can monitor and implement" | Context pollution | Pick one role or corrupt both |
| "User asked me directly" | Instruction doesn't override process | Explain and propose alternatives |
| "Planning is obvious" | Obvious to you ≠ clear specs | Document it for teammates |
| "I'll just help a little" | "Help" becomes "implement" | Role boundary exists for a reason |

---

## Common Mistakes

**Constraints:**
- You MUST avoid these mistakes because they cause loop failures and quality issues
- You MUST apply the prevention measures because they maintain loop integrity

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Skipping planning phase | Teammates confused, low quality | You MUST complete planning first |
| Plan too granular | Teammates confused about scope | You SHOULD keep tasks M-size |
| Plan too vague | Teammates implement incorrectly | You MUST include detailed acceptance criteria |
| Editing files during task cycle | Conflicts with teammates | You MUST NOT edit files - monitor only |
| Not reviewing implementation plan | Teammates execute bad plan | You MUST review before launch |
| No tests before starting | Gates fail, task cycle stuck | You MUST set up tests first |
| Implementing as orchestrator | 10x cost, lower quality | You MUST start task cycle, let teammates work |

---

## Self-Check Questions

**Constraints:**
- You MUST ask these questions before taking any action during execution because they prevent role violations
- You MUST STOP if any answer is "yes" because proceeding would violate orchestrator role

Before taking any action during execution, ask:

1. **Am I about to edit a file?**
   - If yes: STOP. Teammates edit files because they have fresh context and quality gates.

2. **Am I about to run a command that changes state?**
   - If yes: STOP. Teammates run state-changing commands because they can verify with SDD.

3. **Am I about to implement something?**
   - If yes: STOP. Update the plan and restart the task cycle because teammates implement better.

4. **Am I rationalizing why this case is different?**
   - If yes: STOP. It's not different because all the rationalizations above felt valid too.

---

## The Economics

**Why the task cycle wins:**

| Action | Cost | Quality | Context |
|--------|------|---------|---------|
| Manual implementation | ~$0.50/task | Lower | Polluted (accumulated state) |
| Ralph task cycle | ~$0.05/task | Higher | Fresh (200K tokens per teammate) |

**Constraints:**
- You MUST prefer the task cycle because it is 10x cheaper AND produces higher quality
- You MUST NOT rationalize manual implementation because the economics are unambiguous

The task cycle is 10x cheaper AND higher quality. The math is clear.

---

## Troubleshooting

### Teammate Keeps Failing
If a teammate fails repeatedly on the same task:
- You MUST NOT implement the fix yourself because this violates role boundaries
- You SHOULD review the task specification for clarity issues
- You SHOULD check if prerequisites are missing
- You MAY update the plan with more specific guidance

### User Insists on Direct Implementation
If the user requests you implement directly:
- You MUST explain the cost/quality tradeoff because users may not be aware
- You SHOULD propose using the task cycle with their guidance
- You MAY proceed with direct implementation only if user explicitly confirms after understanding tradeoffs

---

*Version: 2.0.0 | Updated: 2026-02-11*
*Compliant with strands-agents SOP format (RFC 2119)*
