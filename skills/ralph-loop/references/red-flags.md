# Red Flags - STOP

## Dangerous Thoughts

These thoughts mean the orchestrator is about to violate role:

| Thought | Reality |
|---------|---------|
| "Let me just fix this one thing quickly" | Workers fix. Start the loop. |
| "I can implement this faster than the loop" | You can't. Fresh context wins. |
| "This is too simple for ralph-loop" | Use direct implementation then. |
| "I'll edit the code and then start the loop" | No. Planning - Loop. No edits. |
| "The worker made a mistake, let me correct it" | Update plan, restart loop. |
| "I already know what to do" | Knowing != implementing correctly. TDD catches errors. |
| "The loop is overkill" | Loop cost: ~$0.05/task. Manual: ~$0.50/task + lower quality. |
| "I can monitor and implement simultaneously" | Context pollution. Pick one role. |
| "The user asked me directly" | User instruction doesn't override role. Propose alternatives. |

**All of these mean: Follow the process. Let workers work.**

## Rationalization Table

Excuses agents make vs. reality:

| Excuse | Reality |
|--------|---------|
| "This is a quick fix" | Quick fixes accumulate debt. Workers have gates. |
| "I already know what to do" | Knowing != implementing correctly. TDD catches errors. |
| "The loop is overkill" | Loop cost: ~$0.05/task. Manual cost: ~$0.50/task + lower quality. |
| "I can monitor and implement" | Context pollution. Pick one role. |
| "User asked me directly" | User instruction doesn't override process. Explain and propose. |
| "Planning is obvious" | Obvious to you != clear specs. Document it. |
| "I'll just help a little" | "Help" becomes "implement". Role boundary exists for a reason. |

## Common Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Skipping planning phase | Workers confused, low quality | Planning is mandatory |
| Plan too granular | Workers confused about scope | Keep tasks M-size |
| Plan too vague | Workers implement incorrectly | Detailed acceptance criteria |
| Editing files during loop | Conflicts with workers | Monitor only |
| Not reviewing implementation plan | Workers execute bad plan | Always review before launch |
| No tests before starting | Gates fail, loop stuck | Set up tests first |
| Implementing as orchestrator | 10x cost, lower quality | Start loop, let workers work |

## Self-Check Questions

Before taking any action during execution, ask:

1. **Am I about to edit a file?** - STOP. Workers edit.
2. **Am I about to run a command that changes state?** - STOP. Workers run.
3. **Am I about to implement something?** - STOP. Update plan, restart loop.
4. **Am I rationalizing why this case is different?** - STOP. It's not different.

## The Economics

| Action | Cost | Quality |
|--------|------|---------|
| Manual implementation | ~$0.50/task | Lower (polluted context) |
| Ralph loop | ~$0.05/task | Higher (fresh context, TDD) |

The loop is 10x cheaper AND higher quality. The math is clear.
