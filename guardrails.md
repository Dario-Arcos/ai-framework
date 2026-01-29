# Signs

<!--
## Overview

Signs capture learnings across iterations within a loop session. Read FIRST every time.
An empty guardrails.md after multiple iterations is a FAILURE - it means nothing was learned.

## Signs vs Memories - Key Distinction

**Signs (this file)**: Session-scoped technical gotchas
- "I hit this error" → Add a Sign
- ESM quirks, config issues, build workarounds
- Relevant for current loop session

**Memories (memories.md)**: Permanent architectural decisions
- "We decided this because..." → Add a Memory
- Why library X over Y, trade-offs made
- Survives session restarts, for future developers

**Rule of thumb**: If it's a gotcha you hit → Sign. If it's a decision you made → Memory.

## Usage Constraints

- You MUST read this file FIRST at every iteration because signs prevent repeated mistakes
- You MUST add signs when you discover gotchas because this captures institutional knowledge
- You MUST use the Sign format (Trigger + Instruction) because consistency enables search
- You SHOULD categorize signs by area because this aids discovery
- You SHOULD NOT duplicate memories here because signs are session-scoped, memories are permanent
- You SHOULD NOT leave this file empty after multiple iterations because that indicates learning failure
-->

## Example Signs (Remove and replace with your own)

### Frontend Examples

### Sign: Test Framework Requires jsdom
- **Trigger**: Writing React component tests
- **Instruction**: Use `testEnvironment: 'jsdom'` in jest.config.js, not 'node'

### Sign: Recharts Needs Client Component
- **Trigger**: Using Recharts in Next.js App Router
- **Instruction**: Add 'use client' directive - Recharts requires browser APIs

### Backend Examples

### Sign: Connection Pool Exhaustion
- **Trigger**: Database queries timing out after many iterations
- **Instruction**: Always close connections in finally block. Use `pool.end()` in cleanup.

### Sign: ESM vs CommonJS Import
- **Trigger**: "Cannot use import statement outside a module" error
- **Instruction**: Check package.json `"type": "module"`. Use `.mjs` extension or configure tsconfig.

### Tooling Examples

### Sign: Path Encoding in Claude Data
- **Trigger**: Working with `~/.claude/projects/` directory names
- **Instruction**: Directory names use dash-encoding: `-Users-foo-bar` = `/Users/foo/bar`

### Sign: Git Hook Bypassing Build
- **Trigger**: Pre-commit hook fails but changes were already committed
- **Instruction**: The commit did NOT happen when hook fails. Stage again and commit fresh.

### Pattern Examples

### Sign: Race Condition in Parallel Tests
- **Trigger**: Tests pass individually but fail when run together
- **Instruction**: Tests sharing database/state need isolation. Use unique IDs or run serially.

### Sign: Environment Variable Not Found
- **Trigger**: Works locally but fails in CI
- **Instruction**: Check CI secrets config. Local `.env` not committed. Add to CI secrets.

### Documentation Examples

### Sign: Broken Internal Links
- **Trigger**: Links between docs files returning 404
- **Instruction**: Use relative paths (../other-file.md). Verify with `find . -name "*.md" -exec grep -l "](/" {} \;`

### Sign: Inconsistent Terminology
- **Trigger**: Same concept called different names across docs
- **Instruction**: Check glossary.md first. Use grep to find all usages before renaming.

### Sign: Word Count Exceeded
- **Trigger**: Documentation exceeds word limit in AGENTS.md
- **Instruction**: Run `wc -w docs/**/*.md` before finalizing. Cut verbose sections.

### Sign: Placeholder URLs Not Replaced
- **Trigger**: URLs like "your-org", "example.com" in production docs
- **Instruction**: Search for placeholder patterns before commit: `grep -r "your-org\|example\.com" docs/`

### Research Examples

### Sign: Source Bias Detection
- **Trigger**: Evaluating frameworks or tools
- **Instruction**: Check if source is vendor docs (biased) vs independent comparison. Weight accordingly.

### Sign: Scope Creep in Analysis
- **Trigger**: Research expanding beyond original question
- **Instruction**: Re-read original criteria.md. Cut tangential sections that don't serve the core question.

### Sign: Outdated Information
- **Trigger**: Citing version numbers or features
- **Instruction**: Verify against official docs. Note "as of [date]" for time-sensitive claims.

### Sign: Missing Comparison Criteria
- **Trigger**: Comparing alternatives without consistent framework
- **Instruction**: Define criteria.md FIRST. Score each alternative against same dimensions.

---

## Your Signs (Add here as you learn)

### Sign: Node.js Test Fixture Directory Conflicts
- **Trigger**: Multiple test files with ENOTEMPTY errors or "no such file or directory" for fixtures
- **Instruction**: Use separate fixture directories per test file (e.g., `.server-test-fixtures`, `.readers-test-fixtures`). Node.js `node:test` runs tests in parallel, so shared directories cause race conditions.

<!--
## Sign Format

**Constraints:**
- You MUST include Trigger because this defines when the sign applies
- You MUST include Instruction because this tells what to do
- You SHOULD be specific in triggers because vague triggers are useless
- You SHOULD keep instructions actionable because theory doesn't help in the moment

### Sign: [Problem/Learning]
- **Trigger**: [When this applies]
- **Instruction**: [What to do]

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
-->
