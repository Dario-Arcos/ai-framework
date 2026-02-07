# Passive Context Patterns

> Distilled from [AGENTS.md Outperforms Skills in Agent Evals](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) (Jude Gao, Vercel/Next.js Team, Jan 2026)

Empirical evidence for passive context superiority. For the Three Laws that operationalize these findings, see the parent [SKILL.md](../SKILL.md).

## The Core Finding

A static markdown file (AGENTS.md) outperformed sophisticated skill-based retrieval, even with fine-tuned triggers. Simplicity beats sophistication for delivering context to agents.

## Eval Results

| Configuration | Pass Rate | Delta |
|---|---|---|
| Baseline (no docs) | 53% | — |
| Skill (default) | 53% | +0pp |
| Skill + explicit instructions | 79% | +26pp |
| AGENTS.md docs index (passive) | 100% | +47pp |

**Critical data point**: In 56% of cases, the skill was never invoked despite being available. The agent had access to documentation but chose not to use it.

> "Agents not reliably using available tools is a known limitation of current models."

## Why Skills Fail

Three factors favor passive over active context:

| Factor | Skills (Active) | AGENTS.md (Passive) |
|---|---|---|
| Decision | Agent must decide to invoke | No decision required |
| Availability | Loaded asynchronously when invoked | Present every turn |
| Ordering | Creates sequencing decisions | No ordering problems |

## Wording Fragility

Same skill. Same docs. Different results from subtle wording changes:

| Instruction | Behavior | Outcome |
|---|---|---|
| "You MUST invoke the skill" | Reads docs first, anchors on doc patterns | Loses project context |
| "Explore project first, then invoke skill" | Builds mental model first | Better results |

**Implication**: The fix for wording fragility is structural (make context passive) rather than linguistic (find perfect phrasing).

## Compressed Index Mechanics

The index is a **navigation map**, not the documentation itself:

```
[Next.js Docs Index]|root: ./.next-docs
|IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning
|01-app/01-getting-started:{01-installation.mdx,02-project-structure.mdx}
|01-app/02-building-your-application/01-routing:{01-defining-routes.mdx,...}
```

Why it works:
1. **No decision point**: the map is already present — agent doesn't decide "should I search?"
2. **Consistent availability**: AGENTS.md is in every turn of the system prompt
3. **No ordering problems**: no sequencing decisions (docs first vs explore first)
4. **On-demand retrieval**: agent reads specific files only when needed

**Compression results**: ~40KB full docs → ~8KB index = 80% reduction, zero pass rate degradation.

## When Skills Still Win

Skills and passive context are complementary, not mutually exclusive:

| Use Case | Best Approach |
|---|---|
| General framework knowledge | Passive (AGENTS.md) — horizontal |
| Explicit action workflows | Skills — vertical |
| "Write correct code with current APIs" | Passive |
| "Upgrade my version" | Skill |
| "Migrate to App Router" | Skill |

> "Skills work better for vertical, action-specific workflows that users explicitly trigger."

## Eval Design: Hardening Methodology

Common problems in initial eval suites:
- Ambiguous prompts
- Tests validating implementation details (not observable behavior)
- Focus on APIs already in training data

Hardening steps:
1. Remove test leakage (prompts that hint at the answer)
2. Resolve contradictions between test cases
3. Switch to **behavior-based assertions** (observable output, not code structure)
4. Add tests for APIs **not in training data** — that's where doc access matters most

## Practical Recommendations

1. **Don't wait for skills to improve**: the gap may close as models improve, but results matter now
2. **Compress aggressively**: an index pointing to retrievable files works as well as full docs
3. **Test with evals targeting unknown APIs**: that's where documentation access is most valuable
4. **Structure docs for retrieval**: agents should find and read specific files, not need everything upfront
