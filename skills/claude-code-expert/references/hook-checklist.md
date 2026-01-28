# Hook Validation Checklist

## Overview

This reference defines the validation checklist for hook implementations. Use this checklist to verify hooks meet all requirements before delivery.

---

## File Structure

**Constraints:**
- You MUST place hook files at `hooks/[hook-name].py` because this enables discovery
- You MUST use `snake_case.py` for filenames because this is the Python convention
- You MUST use UTF-8 encoding because other encodings cause parsing errors
- You MUST include shebang `#!/usr/bin/env python3` because this enables execution
- You MUST make file executable (`chmod +x`) because non-executable hooks fail

---

## Configuration Registration

**Constraints:**
- You MUST register hook in `hooks/hooks.json` because unregistered hooks are not invoked
- You MUST use correct event type (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, etc.) because wrong events prevent triggering
- You MUST use correct matcher pattern (exact string, regex, or wildcard) because wrong patterns prevent matching
- You MUST use `${CLAUDE_PLUGIN_ROOT}` variable in command path because hardcoded paths break portability
- You SHOULD specify timeout if not default 60s because long-running hooks may need more time

### hooks.json Structure

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "pattern",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/hook-name.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

---

## Python Implementation

### Dependencies

**Constraints:**
- You MUST NOT use external dependencies because hooks must work without pip install
- You MUST use only stdlib modules (`sys`, `json`, `os`, `subprocess`, `pathlib`, etc.) because these are always available

### Input Handling

**Constraints:**
- You MUST read JSON from `sys.stdin` because this is the input channel
- You MUST handle missing or malformed JSON gracefully because input may be corrupted
- You MUST validate required fields in input JSON because missing fields cause failures
- You MUST use try/except for JSON parsing because parse errors must be caught

### Output Format

**Constraints:**
- You MUST write normal output to `sys.stdout` because this is the data channel
- You MUST write errors to `sys.stderr` (error messages in Spanish) because this is the error channel
- You MUST output valid JSON if advanced control needed because invalid JSON breaks parsing
- You MUST NOT use print statements outside stdout/stderr because they cause unexpected output

### Exit Codes

**Constraints:**
- You MUST return `sys.exit(0)` for success because non-zero indicates failure
- You MUST return `sys.exit(2)` for blocking errors because this stops Claude
- You MUST match exit code to intended behavior because wrong codes cause wrong handling

### JSON Output Schema (if used)

```json
{
  "continue": true|false,
  "decision": "allow"|"deny"|"block",
  "reason": "explanation",
  "hookSpecificOutput": {
    "additionalContext": "text",
    "permissionDecision": "allow"|"deny"
  }
}
```

---

## Error Handling

**Constraints:**
- You MUST use try/except blocks for all I/O operations because uncaught exceptions crash hooks
- You MUST fail gracefully (safe degradation) because hard failures break workflows
- You MUST write error messages in Spanish for users because this is the convention
- You MUST NOT include sensitive data in error output because this is a security risk
- You MUST log to stderr, not stdout because mixing channels corrupts output

---

## Security

**Constraints:**
- You MUST validate input (no injection vulnerabilities) because hooks process untrusted data
- You MUST NOT use eval() or exec() because these enable code injection
- You MUST use list args for subprocess (not shell=True unless necessary) because shell=True enables injection
- You MUST prevent path traversal (validate paths) because traversal enables unauthorized access
- You MUST NOT include hardcoded credentials because they get committed to version control

---

## Absolute Paths

**Constraints:**
- You MUST use `$CLAUDE_PROJECT_DIR` for project files because this enables portability
- You MUST use `$CLAUDE_PLUGIN_ROOT` for plugin files because this enables portability
- You MUST NOT use relative paths because they fail in different contexts
- You SHOULD handle paths cross-platform because hooks may run on different systems

---

## Language Conventions

**Constraints:**
- You MUST write user-facing messages in Spanish because this is the convention
- You MUST write code comments in English because this is the technical standard
- You MUST write technical error details in English (logs) because developers read English
- You MUST write help text in Spanish because users read Spanish

---

## Hook-Specific Logic

### SessionStart

**Constraints:**
- You MUST perform initialization only because state modification during session causes issues
- You MUST be idempotent (safe to run multiple times) because hooks may be re-invoked
- You MUST execute fast (< 2 seconds) because slow startup degrades user experience

### PreToolUse

**Constraints:**
- You MUST validate tool parameters because invalid params cause tool failures
- You MUST return `permissionDecision` in JSON output because this controls tool access
- You MUST block dangerous operations with exit code 2 because this prevents harm

### PostToolUse

**Constraints:**
- You SHOULD process tool results as needed because post-processing adds value
- You MAY add context if needed because enrichment improves output
- You SHOULD NOT modify tool output unless necessary because modifications may cause issues

### UserPromptSubmit

**Constraints:**
- You SHOULD inject context via `additionalContext` field because this enriches prompts
- You MUST NOT block user prompts unnecessarily because this degrades experience
- You MUST execute fast (< 500ms) because slow hooks delay response

---

## Constitutional Compliance

**Constraints:**
- You MUST achieve Value/Complexity ≥ 2 because lower ratios indicate over-engineering
- You MUST reuse existing hook patterns where applicable because duplication increases maintenance
- You MUST use AI-First design (JSON I/O) because this enables agent integration
- You MUST NOT over-engineer solutions because unnecessary complexity reduces maintainability

---

## Integration

**Constraints:**
- You MUST match hook event type to use case because wrong events prevent triggering
- You MUST use specific matcher pattern (not too broad) because broad patterns cause unintended matching
- You MUST NOT create duplicate hooks for same event/matcher because this causes conflicts
- You SHOULD test with actual Claude Code session because synthetic tests miss edge cases

---

## Performance

**Constraints:**
- You MUST execute within timeout (default 60s) because timeouts cause failures
- You MUST NOT use blocking I/O without timeout because hangs cause failures
- You SHOULD use efficient algorithms (no O(n²) where avoidable) because slow hooks degrade experience
- You SHOULD load context minimally (just-in-time) because excessive loading wastes resources

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
- You SHOULD review similar hooks in project for patterns because consistency aids maintenance
- You MUST verify hooks.json syntax is valid JSON because invalid JSON breaks loading
- You SHOULD test in actual Claude Code session because real testing catches issues
- You MUST confirm 100% of checklist items because partial compliance causes failures
- You MUST stake professional reputation on correctness because this is the standard

**Sign-off**: Only deliver when ALL constraints satisfied.

---

## Troubleshooting

### Hook Not Triggering

If hook is not invoked when expected:
- You SHOULD verify hook is registered in hooks.json
- You SHOULD check event type matches expected trigger
- You SHOULD verify matcher pattern matches expected input
- You MUST check file is executable

### Input/Output Issues

If hook receives or produces unexpected data:
- You SHOULD verify JSON parsing handles edge cases
- You SHOULD check stdout/stderr usage is correct
- You MUST verify exit codes match intended behavior

### Performance Issues

If hook causes delays:
- You SHOULD profile hook execution time
- You SHOULD reduce context loading to minimum
- You MUST NOT use blocking I/O without timeouts

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
