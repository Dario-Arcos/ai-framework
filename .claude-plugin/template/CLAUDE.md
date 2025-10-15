# Project Configuration

AI-first development workspace with constitutional governance framework.

## Operating Protocol

"Everything should be made as simple as possible, but not simpler.”

1. **First principle** your value is measured by the ratio **value / complexity ≥ 2**.
2. **Frame the problem**

- Restate the goal in ≤ 3 bullet points.
- Size class: **S** ≤ 2 h · **M** ≤ 1 day · **L** > 1 day.

3. **Complexity budget**
   | Size | Δ LOC | New files | New deps | Δ CPU/RAM |
   |------|------:|----------:|---------:|----------:|
   | S | ≤ 80 | ≤ 1 | 0 | ≤ 1 % |
   | M | ≤ 250 | ≤ 3 | ≤ 1 | ≤ 3 % |
   | L | ≤ 600 | ≤ 5 | ≤ 2 | ≤ 5 % |

   **Δ LOC = additions - deletions** (net change in lines of code)

_If you expect to exceed the budget: **stop and ask**._

4. **Guided exploration**
   Propose **2-3** approaches. For each:  
   `benefit (1-5) | complexity (1-5) | ROI = benefit − complexity`.  
   Choose the highest ROI; tie-break toward the simpler one.
5. **Implementation rules**

- **Reuse first** — list reused components/functions.
- **New abstraction ⇒ justification ≥ 30 % duplication or future-cost reduction.**
- **TDD loop** — red → green → refactor.
- **Self-audit** — confirm §3 metrics are met.

6. **Parallel-first execution (MANDATORY)**

- **Use Task tool for parallel execution** when tasks are independent.
- **Launch multiple agents concurrently** in a single message with multiple tool uses.
- **Examples of parallelizable tasks:**
  - Multiple file reads/searches (Read, Grep, Glob in parallel)
  - Independent code reviews (security + performance + quality agents)
  - Separate feature implementations (frontend + backend agents)
  - Multi-repo operations (clone/update repositories)
- **When NOT to parallelize:** Sequential dependencies (must read before editing, must test before committing).
- **Default mindset:** "Can these tasks run simultaneously?" If yes → parallel. If unsure → ask.

7. All your proposed plans and outcomes, of any kind, **MUST BE AI-first**, meaning they must be executed by an advanced AI like Claude Code and overseen and directed by a human.

## Interaction Language

1. **Always use Spanish** as the language of communication with the user
2. **Only in the first message of a session**, show: _(You can change the interaction language by asking me whenever you want.)_

## Summary instructions

### Always preserve

- **Project objective** and measurable success criteria.
- **High-level roadmap** (milestones, deadlines).
- **Material code changes**: file paths, diffs, migrations.
- **Open TODO / backlog items** with assignees and due dates.
- **Key file or directory paths** referenced in the conversation.

### Omit or condense

- Casual conversation or small talk.
- Verbose CLI/test logs or stack traces unless directly required.
- Duplicate or trivial messages.

## Documentation References

**Essential guides for Claude Code ecosystem:**

**Constitution**: @.specify/memory/constitution.md

- AI-first workflow principles and governance framework
- Value/complexity ratio requirements and complexity budgets
- Test-first development methodology (TDD mandatory)
- Quality standards and implementation rules

**Project Context**: @.specify/memory/project-context.md

- Auto-detected tech stack and architecture
- Project-specific conventions and patterns
- Recommended agents for your codebase
- Integration points and dependencies

**Always Works™**: @.claude/rules/always-works.md

- Comprehensive testing methodology and implementation validation
- 30-second reality check for functionality and simplicity
- Anti-over-engineering principles and complexity budget enforcement
- Systematic approach to ensure production-ready solutions

**Product Design Principles**: @.specify/memory/product-design-principles.md

- Steve Jobs design philosophy: simplicity as ultimate sophistication
- User experience first, technology second
- Focus and saying no to 1,000 things
- Perfection in details and obsessive craft
- Innovation through seeing what others can't see

**UIX Design Principles**: @.specify/memory/uix-design-principles.md

- S-Tier SaaS dashboard design checklist (Stripe/Airbnb/Linear standards)
- Complete design system foundation and UI component specifications
- Module-specific design tactics for data tables, moderation, and configuration
- CSS architecture and responsive design best practices

**Effective AI Agents**: @.claude/rules/effective-agents-guide.md

- Golden Rule: smallest set of high-signal tokens for desired outcome
- System prompts: Right Altitude Principle (clear signals, flexible heuristics)
- Tool design: decisiveness test, token efficiency, single responsibility
- Dynamic context: just-in-time loading, progressive disclosure
- Long-horizon strategies: compaction, note-taking, sub-agents
- **MUST follow when creating/using agents via Task tool or sub-agent architectures**

## guidelines for code review (claude bot review)

- Priority: **SECURITY**, **BUG**, **RELIABILITY**, **PERFORMANCE** with production impact.
- Ignore style/nits if they do not affect clarity or security.
- Do not suggest repo-wide refactors outside the diff.

### Project conventions

- **JS/TS**: use `camelCase` names, avoid magic numbers, handle errors with `Result` or consistent `try/catch`.
- **Testing**: do not comment on snapshots/coverage unless there are signs of real fragility.

### Exclusions

- `build/`, `dist/`, `vendor/`, `**/*.lock`, assets (`*.png`/`*.jpg`/`*.svg`), `coverage/`, `snapshots/`

## Claude Code Memories

### Project Operations

- **Complexity Budget**: Validate against Size S/M/L metrics before exceeding scope.
- **AI-First Principle**: All plans must be executable by AI with human oversight.

### Quality Standards

- **Language Consistency**: English for code/AI documentation, Spanish for human documentation. Never mix languages in same file.
- **Communication Style**: Professional, minimalist, clear language. Eliminate promotional content.
- **Output Quality**: Production-ready with quantified business impact and executive-presentable value.
- **Quality Gates**: Use code-quality-reviewer proactively for security and performance validation.

### Agent Integration

- **Design Requirements**: All agents SHOULD follow @.claude/rules/effective-agents-guide.md for optimal context efficiency
  - System prompts at "right altitude" (clear signals, not hardcoded logic)
  - Tools with unambiguous decisiveness (human must know which tool to use)
  - Just-in-time context loading (references, not full content)
  - Appropriate long-horizon strategy (compaction/notes/sub-agents)
- **Contextual Suggestions**: Suggest proactively specialists based on challenge type, never mandate usage.
- **Orchestrator Priority**: Use `tech-lead-orchestrator` for multi-step challenges and strategic coordination.
- **Specialist Selection**: Core specialists for quality, framework specialists for implementation.

### Git Operations (MANDATORY)

- **Commit Authorization**: NEVER execute `git commit` without explicit user authorization. Always ask before committing changes.
- **Push Authorization**: NEVER execute `git push` without explicit user authorization. Always ask before pushing to remote.
- **Explicit Request Required**: Only perform git commit/push operations when user explicitly requests them with clear intent.
- **No Proactive Commits**: Do not assume commit/push is part of task completion. User controls all git operations.
- **Violation Severity**: Unauthorized git commit/push is a critical violation of user trust and project governance.
