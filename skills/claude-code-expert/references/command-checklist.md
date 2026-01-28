# Slash Command Validation Checklist

## Overview

This reference defines the validation checklist for slash command implementations. Use this checklist to verify commands meet all requirements before delivery.

---

## File Structure

**Constraints:**
- You MUST place command files at `commands/[category]/[command-name].md` because this enables discovery
- You MUST verify the category exists or justify new category because proliferation reduces discoverability
- You MUST use `kebab-case.md` for filenames because this is the naming convention
- You MUST use UTF-8 encoding because other encodings cause parsing errors

---

## YAML Frontmatter

### Optional Fields

**Note**: All frontmatter fields are technically optional for commands, but `description` is highly recommended.

**Constraints:**
- You SHOULD include `description:` field (explains what command does) because this appears in `/help` output
- You SHOULD include `argument-hint:` showing expected parameters (e.g., `[message]`, `[PR-number]`) because this guides users
- You MAY include `allowed-tools:` comma-separated list (e.g., `Bash(git *), Read, Grep`) to restrict access
- You MAY include `model:` with valid value (`sonnet`, `opus`, `haiku`) if model selection needed
- You MAY include `disable-model-invocation:` boolean to prevent SlashCommand tool from invoking
- You MUST delimit frontmatter with `---` (opening and closing) if present because YAML parsing requires delimiters

### Syntax Validation

**Constraints:**
- You MUST format tool patterns correctly (e.g., `Bash(git add:*)` for wildcards) because incorrect patterns fail
- You MUST NOT use trailing commas in lists because parsing fails
- You MUST keep `description:` concise (1-2 sentences) because verbose descriptions clutter help output
- You MUST use exact field names (case-sensitive) because unknown fields are ignored

---

## Markdown Body

### Structure

**Constraints:**
- You MUST include clear workflow steps or phases because this organizes execution
- You MUST document parameter usage (`$1`, `$2`, `$ARGUMENTS`) because users need to know how to invoke
- You SHOULD list prerequisites if any because missing prerequisites cause failures
- You SHOULD define success criteria because this enables verification
- You SHOULD document error handling because failures need graceful handling

### Content Quality

**Constraints:**
- You MUST write clear, actionable instructions because vague instructions produce poor output
- You MUST use sequential, logical workflow because out-of-order steps cause failures
- You MUST NOT contradict constitutional principles because this creates conflicts
- You MUST use English for code and Spanish for user messages because this is the convention

### Advanced Features

**Constraints:**
- You MUST use correct Bash execution syntax (`!` prefix) if used because incorrect syntax fails
- You MUST use correct file reference syntax (`@` prefix) if used because incorrect syntax fails
- You SHOULD use thinking mode keywords appropriately because this affects output quality
- You SHOULD document environment variable usage because undocumented vars cause confusion

---

## Naming Conventions

**Constraints:**
- You MUST use descriptive and unique command names because duplicates cause conflicts
- You MUST follow pattern `[category]-[command]` (e.g., `git-commit`, `worktree-create`) because this is the convention
- You MUST organize categories logically (git-github, utils, etc.) because this aids discovery

---

## Tool Access

**Constraints:**
- You SHOULD specify only necessary tools in `allowed-tools:` because excessive access is a security risk
- You MUST use correct tool pattern syntax (e.g., `Bash(git add:*)` for wildcards) because incorrect syntax fails
- You SHOULD restrict sensitive operations (git commit, file write) appropriately because unrestricted access is dangerous

---

## Parameter Handling

**Constraints:**
- You MUST clearly document parameter positions (`$1`, `$2`, etc.) because users need to know invocation format
- You MUST use `$ARGUMENTS` when all params needed as single string because this is the correct accessor
- You SHOULD indicate optional vs required parameters because users need to know what's mandatory
- You SHOULD describe parameter validation if applicable because this prevents invalid input

---

## Constitutional Compliance

**Constraints:**
- You MUST achieve Value/Complexity ≥ 2 because lower ratios indicate over-engineering
- You MUST reuse existing command patterns where applicable because duplication increases maintenance
- You MUST use AI-First design (clear text workflow) because this enables agent execution
- You MUST NOT include hardcoded credentials or secrets because they get committed to version control
- You MUST require explicit user authorization for git operations because auto-commit/push is dangerous

---

## Integration

**Constraints:**
- You MUST verify command category exists in project structure because missing categories prevent loading
- You MUST NOT use duplicate command names because name collisions cause undefined behavior
- You MUST use clear invocation pattern (e.g., `/ai-framework:utils:understand <area>`) because users need to know how to invoke

---

## User Experience

**Constraints:**
- You SHOULD provide clear `argument-hint:` guidance for parameters because this helps users
- You SHOULD ensure `description:` appears useful in `/help` output because this aids discovery
- You MUST write error messages in Spanish because this is the convention for user-facing content
- You SHOULD provide clear, concise success feedback because users need confirmation

---

## Workflow Logic

**Constraints:**
- You MUST sequence steps correctly (dependencies respected) because out-of-order execution fails
- You SHOULD identify parallel operations when applicable because parallelism improves performance
- You SHOULD use `&&` for chaining sequential operations because this ensures dependency ordering
- You MUST handle failure modes appropriately because unhandled failures cause poor user experience

---

## Quality Gates

**Constraints:**
- You MUST pass code review by senior engineer standard because this ensures quality
- You MUST be ready for production use without modifications because partial implementations fail
- You MUST validate all assumptions against official docs because stale training data causes errors
- You MUST NOT leave TODO or FIXME comments because these indicate incomplete implementation

---

## Final Verification

**Constraints:**
- You SHOULD use WebFetch to verify current official syntax because documentation evolves
- You SHOULD review similar commands in project for patterns because consistency aids maintenance
- You MUST confirm 100% of checklist items because partial compliance causes failures
- You MUST stake professional reputation on correctness because this is the standard

**Sign-off**: Only deliver when ALL constraints satisfied.

---

## Troubleshooting

### Command Not Found

If command is not discoverable:
- You SHOULD verify file location matches expected path
- You SHOULD check filename uses kebab-case.md
- You MUST verify file encoding is UTF-8

### Parameter Issues

If parameters are not passed correctly:
- You SHOULD verify parameter positions are documented correctly
- You SHOULD check `$ARGUMENTS` vs `$1`, `$2` usage
- You MUST verify argument-hint matches actual usage

### Tool Access Errors

If command cannot use expected tools:
- You SHOULD verify `allowed-tools:` field includes required tools
- You SHOULD check tool patterns use correct syntax
- You MUST verify tool names match official names exactly

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
