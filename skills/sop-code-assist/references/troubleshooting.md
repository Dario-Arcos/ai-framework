# Troubleshooting

## Overview

This reference covers common issues encountered during sop-code-assist execution and their solutions.

---

## Test fails after SATISFY phase

**Symptom:** Tests passed, but after refactoring they fail

**Cause:** Refactoring changed behavior, not just structure

**Fix:** Revert to last passing state, make smaller refactoring steps

**Prevention:**
- Run tests after EVERY refactoring change
- Commit before refactoring to enable easy revert
- Follow the mantra: "Refactoring changes structure, not behavior"

---

## Cannot find task file

**Symptom:** Path to .code-task.md returns file not found

**Cause:** Incorrect path or file doesn't exist yet

**Fix:** Verify path, use sop-task-generator to create tasks first

**Diagnostic Steps:**
1. Check if path is absolute or relative
2. Verify file exists: `ls -la <path>`
3. Check for typos in filename (especially step/task numbers)
4. Ensure sop-task-generator completed successfully

---

## Build fails after implementation

**Symptom:** Tests pass but build/typecheck fails

**Cause:** Type errors, missing imports, incompatible changes

**Fix:** Check .ralph/guardrails.md for last known good state, fix incrementally

**Common Build Failures:**

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| Type mismatch | Return type changed | Update function signature |
| Missing import | New dependency used | Add import statement |
| Circular import | Cross-module dependency | Restructure imports |
| Missing dependency | Package not installed | Add to requirements/package.json |

---

## Interactive mode not asking questions

**Symptom:** Expected prompts for feedback not appearing

**Cause:** Mode set to 'autonomous' instead of 'interactive'

**Fix:** Restart with `mode="interactive"` parameter

**Verification:**
```bash
/sop-code-assist task_description="..." mode="interactive"
```

---

## Tests pass immediately (no SCENARIO phase)

**Symptom:** New test passes without implementation

**Cause:** Test is not testing what you think, or implementation already exists

**Fix:** Fix the test, not the code

**Diagnostic Steps:**
1. Check if function already exists (may be testing wrong function)
2. Verify test assertions are correct
3. Check test is actually being run (naming convention)
4. Ensure test file is in correct location

---

## Context.md missing key information

**Symptom:** Implementation decisions made without sufficient context

**Cause:** Explore phase incomplete or rushed

**Fix:** Re-run explore phase, use CODEASSIST.md for guidance

**What .code-task.md MUST contain:**
- [ ] Project structure overview
- [ ] Relevant existing patterns
- [ ] Dependencies and their versions
- [ ] Related code locations
- [ ] Acceptance criteria mapping

---

## Commit fails pre-commit hooks

**Symptom:** `git commit` rejected by hooks

**Cause:** Code doesn't meet project standards (lint, format, tests)

**Fix:** Run failing check manually, fix issues, retry

**Common Pre-commit Fixes:**

| Hook | Fix |
|------|-----|
| lint | Run linter with auto-fix flag |
| format | Run formatter |
| type-check | Fix type annotations |
| test | Ensure all tests pass |

---

## Autonomous mode stuck in loop

**Symptom:** Same error keeps occurring, no progress

**Cause:** Cannot resolve issue without user input

**Fix:** Check .ralph/guardrails.md for documented challenge, provide guidance

**Escalation Triggers:**
- 3 failed attempts at same issue
- Conflicting requirements discovered
- Security-sensitive change required
- Breaking change to public API

---

## Wrong conventions applied

**Symptom:** Code doesn't match project style

**Cause:** Explored wrong files or missed CODEASSIST.md

**Fix:** Check CODEASSIST.md, refactor to match conventions

**Convention Checklist:**
- [ ] Naming (camelCase vs snake_case)
- [ ] File structure (where tests go)
- [ ] Error handling patterns
- [ ] Import style
- [ ] Documentation format

---

## Progress.md not tracking changes

**Symptom:** .ralph/guardrails.md empty or outdated

**Cause:** Autonomous mode not logging, or file write failed

**Fix:** Verify write permissions, manually update if needed

**Progress.md MUST track:**
- Each SDD cycle (SCENARIO, SATISFY, REFACTOR)
- Decisions made and rationale
- Challenges encountered
- Current checklist status
