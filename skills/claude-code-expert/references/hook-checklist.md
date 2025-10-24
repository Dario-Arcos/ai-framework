# Hook Validation Checklist

Use this checklist to validate hook implementations before delivery.

## File Structure

- [ ] File location: `hooks/[hook-name].py`
- [ ] Filename uses `snake_case.py`
- [ ] File encoding: UTF-8
- [ ] Shebang present: `#!/usr/bin/env python3`
- [ ] File is executable (`chmod +x`)

## Configuration Registration

- [ ] Hook registered in `hooks/hooks.json`
- [ ] Event type correct (SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, etc.)
- [ ] Matcher pattern correct (exact string, regex, or wildcard)
- [ ] Command path uses `${CLAUDE_PLUGIN_ROOT}` variable
- [ ] Timeout specified (if not default 60s)

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

## Python Implementation

### Dependencies

- [ ] **NO external dependencies** (stdlib only)
- [ ] Only uses: `sys`, `json`, `os`, `subprocess`, `pathlib`, etc.
- [ ] No `pip install` required

### Input Handling

- [ ] Reads JSON from `sys.stdin`
- [ ] Handles missing or malformed JSON gracefully
- [ ] Validates required fields in input JSON
- [ ] Uses try/except for JSON parsing

### Output Format

- [ ] Writes to `sys.stdout` (normal output)
- [ ] Writes errors to `sys.stderr` (error messages in Spanish)
- [ ] Output is valid JSON (if advanced control needed)
- [ ] No print statements outside of stdout/stderr

### Exit Codes

- [ ] `sys.exit(0)` for success
- [ ] `sys.exit(2)` for blocking errors (stops Claude)
- [ ] Other exit codes for non-blocking errors
- [ ] Exit code matches intended behavior

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

## Error Handling

- [ ] Try/except blocks for all I/O operations
- [ ] Graceful degradation (fails safely)
- [ ] Error messages are user-friendly and in Spanish
- [ ] No sensitive data in error output
- [ ] Logging to stderr, not stdout

## Security

- [ ] Input validation (no injection vulnerabilities)
- [ ] No eval() or exec() usage
- [ ] Subprocess calls use list args (not shell=True unless necessary)
- [ ] Path traversal prevention (validate paths)
- [ ] No hardcoded credentials

## Absolute Paths

- [ ] Uses `$CLAUDE_PROJECT_DIR` for project files
- [ ] Uses `$CLAUDE_PLUGIN_ROOT` for plugin files
- [ ] No relative paths that could fail in different contexts
- [ ] Path handling is cross-platform compatible

## Language Conventions

- [ ] User-facing messages in Spanish
- [ ] Code comments in English
- [ ] Technical error details in English (logs)
- [ ] Help text in Spanish

## Hook-Specific Logic

### SessionStart

- [ ] Performs initialization only
- [ ] Idempotent (safe to run multiple times)
- [ ] Fast execution (< 2 seconds)

### PreToolUse

- [ ] Validates tool parameters
- [ ] Returns `permissionDecision` in JSON output
- [ ] Blocks dangerous operations (returns exit code 2)

### PostToolUse

- [ ] Processes tool results
- [ ] Adds context if needed
- [ ] Does not modify tool output unless necessary

### UserPromptSubmit

- [ ] Injects additional context via `additionalContext` field
- [ ] Does not block user prompts unnecessarily
- [ ] Fast execution (< 500ms)

## Constitutional Compliance

- [ ] Value/Complexity ≥ 2 (simplest solution for purpose)
- [ ] Reuses existing hook patterns where applicable
- [ ] AI-First design (JSON I/O)
- [ ] No over-engineering

## Integration

- [ ] Hook event type matches use case
- [ ] Matcher pattern is specific enough (not too broad)
- [ ] No duplicate hooks for same event/matcher
- [ ] Tested with actual Claude Code session

## Performance

- [ ] Execution time < timeout (default 60s)
- [ ] No blocking I/O without timeout
- [ ] Efficient algorithms (no O(n²) where avoidable)
- [ ] Minimal context loading (just-in-time)

## Quality Gates

- [ ] Would pass code review by senior engineer
- [ ] Ready for production use without modifications
- [ ] All assumptions validated against official docs
- [ ] No TODO or FIXME comments left in code

## Final Verification

- [ ] WebFetch used to verify current official syntax
- [ ] Similar hooks in project reviewed for patterns
- [ ] hooks.json syntax validated (valid JSON)
- [ ] Tested in actual Claude Code session
- [ ] Checklist items 100% confirmed
- [ ] Professional reputation staked on correctness

**Sign-off**: Only deliver when ALL items checked.
