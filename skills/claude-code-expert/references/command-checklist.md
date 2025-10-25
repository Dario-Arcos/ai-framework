# Slash Command Validation Checklist

Use this checklist to validate slash command implementations before delivery.

## File Structure

- [ ] File location: `commands/[category]/[command-name].md`
- [ ] Category exists in `commands/` directory or new category justified
- [ ] Filename uses `kebab-case.md`
- [ ] File encoding: UTF-8

## YAML Frontmatter

### Required Fields

**NOTE**: All frontmatter fields are technically optional for commands, but `description` is highly recommended.

### Optional Fields (if used)

- [ ] `description:` present and clear (explains what command does)
- [ ] `argument-hint:` shows expected parameters (e.g., `[message]`, `[PR-number]`)
- [ ] `allowed-tools:` comma-separated list (e.g., `Bash(git *), Read, Grep`)
- [ ] `model:` valid value (`sonnet`, `opus`, `haiku`)
- [ ] `disable-model-invocation:` boolean (prevents SlashCommand tool from invoking)
- [ ] YAML frontmatter delimited with `---` (opening and closing) if present

### Syntax Validation

- [ ] Tool patterns correctly formatted (e.g., `Bash(git add:*)` for wildcards)
- [ ] No trailing commas in lists
- [ ] `description:` is concise (1-2 sentences)
- [ ] All field names exactly match official spec (case-sensitive)

## Markdown Body

### Structure

- [ ] Clear workflow steps or phases
- [ ] Parameter usage documented (`$1`, `$2`, `$ARGUMENTS`)
- [ ] Prerequisites listed (if any)
- [ ] Success criteria defined
- [ ] Error handling documented

### Content Quality

- [ ] Instructions are clear and actionable
- [ ] Workflow is sequential and logical
- [ ] No contradictions with constitutional principles
- [ ] Language: English for code, Spanish for user messages

### Advanced Features (if used)

- [ ] Bash execution (`!` prefix) syntax correct
- [ ] File references (`@` prefix) syntax correct
- [ ] Thinking mode keywords used appropriately
- [ ] Environment variable usage documented

## Naming Conventions

- [ ] Command name is descriptive and unique
- [ ] Name follows pattern: `[category-prefix].[command]` (e.g., `speckit.plan`)
- [ ] Category organization logical (SDD-cycle, git-github, utils, etc.)

## Tool Access

- [ ] If `allowed-tools:` specified, only includes necessary tools (security)
- [ ] Tool patterns use correct syntax (e.g., `Bash(git add:*)` for wildcards)
- [ ] Sensitive operations (git commit, file write) appropriately restricted

## Parameter Handling

- [ ] Parameter positions clearly documented (`$1`, `$2`, etc.)
- [ ] `$ARGUMENTS` used when all params needed as single string
- [ ] Optional vs required parameters indicated
- [ ] Parameter validation described (if applicable)

## Constitutional Compliance

- [ ] Value/Complexity ≥ 2 (simplest solution for purpose)
- [ ] Reuses existing command patterns where applicable
- [ ] AI-First design (clear text workflow)
- [ ] No hardcoded credentials or secrets
- [ ] Git operations require explicit user authorization (no auto-commit/push)

## Integration

- [ ] Command category exists in project structure
- [ ] No duplicate command names in project
- [ ] Invocation pattern clear (e.g., `/ai-framework:utils:understand <area>`)

## User Experience

- [ ] `argument-hint:` provides clear guidance for parameters
- [ ] `description:` appears in `/help` output
- [ ] Error messages are helpful and in Spanish
- [ ] Success feedback is clear and concise

## Workflow Logic

- [ ] Steps are correctly sequenced (dependencies respected)
- [ ] Parallel operations identified (if applicable)
- [ ] Sequential operations use `&&` for chaining
- [ ] Failure modes handled appropriately

## Quality Gates

- [ ] Would pass code review by senior engineer
- [ ] Ready for production use without modifications
- [ ] All assumptions validated against official docs
- [ ] No TODO or FIXME comments left in code

## Final Verification

- [ ] WebFetch used to verify current official syntax
- [ ] Similar commands in project reviewed for patterns
- [ ] Checklist items 100% confirmed
- [ ] Professional reputation staked on correctness

**Sign-off**: Only deliver when ALL items checked.
