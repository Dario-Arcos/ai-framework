# Sub-Agent Validation Checklist

## Overview

This reference defines the validation checklist for sub-agent implementations. Use this checklist to verify agents meet all requirements before delivery.

---

## File Structure

**Constraints:**
- You MUST place agent files at `agents/[category]/[agent-name].md` because this enables discovery
- You MUST verify the category exists in `agents/` directory because missing categories prevent loading
- You MUST use `kebab-case.md` for filenames because this is the naming convention
- You MUST use UTF-8 encoding because other encodings cause parsing errors

---

## YAML Frontmatter

### Required Fields

**Constraints:**
- You MUST include `name:` field (lowercase, hyphens only, max 64 chars) because this identifies the agent
- You MUST include `description:` field (max 1024 chars) because this enables auto-delegation
- You MUST delimit frontmatter with `---` (opening and closing) because YAML parsing requires delimiters
- You MUST describe purpose AND when to use in description because this enables correct invocation

### Optional Fields

**Constraints:**
- You SHOULD specify `tools:` as comma-separated list if restricting access (e.g., `Read, Grep, Glob, Bash`)
- You MAY specify `model:` with valid value (`sonnet`, `opus`, `haiku`, `inherit`) if model selection needed
- You MAY specify `color:` for UI presentation

### Syntax Validation

**Constraints:**
- You MUST NOT use trailing commas in `tools:` field because YAML parsing fails
- You MUST NOT quote `tools:` values (use `Read, Grep` not `"Read", "Grep"`) because this changes parsing
- You MUST use single-line string for `description:` because multiline breaks parsing
- You MUST use exact field names (case-sensitive) because unknown fields are ignored

---

## Markdown Body

### Structure

**Constraints:**
- You MUST include clear sections with ## headers because this organizes content
- You MUST include Purpose/Domain section at top because this orients the reader
- You SHOULD list Capabilities or Focus Areas because this defines scope
- You SHOULD describe Approach or Methodology because this guides behavior
- You MAY include Examples if applicable

### Content Quality

**Constraints:**
- You MUST write clear, actionable instructions because vague instructions produce poor output
- You MUST make domain expertise specific, not generic because generic expertise adds no value
- You MUST NOT contradict constitutional principles because this creates conflicts
- You MUST use English for code/AI instructions because this is the standard

---

## Naming Conventions

**Constraints:**
- You MUST use descriptive and unique agent names because duplicates cause conflicts
- You MUST follow `kebab-case` pattern (e.g., `code-reviewer`) because this is the convention
- You MUST match existing categories or justify new ones because proliferation reduces discoverability

---

## Tool Access

**Constraints:**
- You SHOULD specify only necessary tools in `tools:` field because excessive access is a security risk
- You MUST confirm intent if omitting `tools:` because agent inherits all tools
- You MUST use exact official tool names because incorrect names cause failures

---

## Constitutional Compliance

**Constraints:**
- You MUST achieve Value/Complexity ≥ 2 because lower ratios indicate over-engineering
- You MUST reuse existing agent patterns where applicable because duplication increases maintenance
- You MUST use AI-First design (clear text instructions) because this enables agent execution
- You MUST NOT include hardcoded credentials or secrets because they get committed to version control

---

## Integration

**Constraints:**
- You MUST verify agent category exists in project structure because missing categories prevent loading
- You MUST NOT use duplicate agent names because name collisions cause undefined behavior
- You MUST write description to trigger appropriate auto-delegation because this enables discovery

---

## Proactive Usage

**Constraints:**
- You SHOULD include "PROACTIVELY" in description if agent should auto-delegate because this triggers automatic use
- You MUST clearly state WHEN to use agent (not just WHAT it does) because this enables correct invocation

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
- You SHOULD review similar agents in project for patterns because consistency aids maintenance
- You MUST confirm 100% of checklist items because partial compliance causes failures
- You MUST stake professional reputation on correctness because this is the standard

**Sign-off**: Only deliver when ALL constraints satisfied.

---

## Troubleshooting

### Agent Not Loading

If agent fails to load:
- You SHOULD verify YAML frontmatter syntax (no trailing commas, correct delimiters)
- You SHOULD check file location matches expected path
- You MUST verify file encoding is UTF-8

### Auto-Delegation Not Working

If agent is not auto-invoked when expected:
- You SHOULD review description for clear trigger conditions
- You SHOULD add "PROACTIVELY" keyword if automatic use intended
- You MUST ensure description states WHEN to use, not just WHAT it does

### Tool Access Errors

If agent cannot use expected tools:
- You SHOULD verify `tools:` field includes required tools
- You SHOULD check tool names match official names exactly
- You MUST NOT omit `tools:` if restricted access is intended

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
