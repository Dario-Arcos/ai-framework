# Sub-Agent Validation Checklist

Use this checklist to validate sub-agent implementations before delivery.

## File Structure

- [ ] File location: `agents/[category]/[agent-name].md`
- [ ] Category exists in `agents/` directory
- [ ] Filename uses `kebab-case.md`
- [ ] File encoding: UTF-8

## YAML Frontmatter

### Required Fields

- [ ] `name:` present (lowercase, hyphens only, max 64 chars)
- [ ] `description:` present (max 1024 chars, describes purpose AND when to use)
- [ ] YAML frontmatter delimited with `---` (opening and closing)

### Optional Fields (if used)

- [ ] `tools:` comma-separated list (e.g., `Read, Grep, Glob, Bash`)
- [ ] `model:` valid value (`sonnet`, `opus`, `haiku`, `inherit`)
- [ ] `color:` valid color name (for UI, optional)

### Syntax Validation

- [ ] No trailing commas in `tools:` field
- [ ] No quotes around `tools:` values (use `Read, Grep` not `"Read", "Grep"`)
- [ ] `description:` is a single-line string (no multiline)
- [ ] All field names exactly match official spec (case-sensitive)

## Markdown Body

### Structure

- [ ] Clear sections with ## headers
- [ ] Purpose/Domain section at top
- [ ] Capabilities or Focus Areas listed
- [ ] Approach or Methodology described
- [ ] Examples included (if applicable)

### Content Quality

- [ ] Instructions are clear and actionable
- [ ] Domain expertise is specific, not generic
- [ ] No contradictions with constitutional principles
- [ ] Language: English (code/AI instructions)

## Naming Conventions

- [ ] Agent name is descriptive and unique
- [ ] Name follows `snake-case` pattern (e.g., `code-reviewer`)
- [ ] Category matches existing categories or justifies new one

## Tool Access

- [ ] If `tools:` specified, only includes necessary tools (security)
- [ ] If omitted, agent inherits all tools (confirm this is intended)
- [ ] Tool names match official tool names exactly

## Constitutional Compliance

- [ ] Value/Complexity ≥ 2 (simplest solution for purpose)
- [ ] Reuses existing agent patterns where applicable
- [ ] AI-First design (clear text instructions)
- [ ] No hardcoded credentials or secrets

## Integration

- [ ] Agent category exists in project structure
- [ ] No duplicate agent names in project
- [ ] Description triggers appropriate auto-delegation

## Proactive Usage

- [ ] If agent should auto-delegate, description includes "PROACTIVELY"
- [ ] Description clearly states WHEN to use agent (not just WHAT it does)

## Quality Gates

- [ ] Would pass code review by senior engineer
- [ ] Ready for production use without modifications
- [ ] All assumptions validated against official docs
- [ ] No TODO or FIXME comments left in code

## Final Verification

- [ ] WebFetch used to verify current official syntax
- [ ] Similar agents in project reviewed for patterns
- [ ] Checklist items 100% confirmed
- [ ] Professional reputation staked on correctness

**Sign-off**: Only deliver when ALL items checked.
