> **Status: IMPLEMENTED** — All changes in this document have been applied. This file is kept as historical reference.

# Windows Compatibility for Hooks

All Python hooks fail silently on Windows due to three root causes. This document describes the required changes and the rationale behind each one.

## Root Causes

| # | Problem | Impact |
|---|---------|--------|
| 1 | `python3` does not exist on Windows | All 8 hook commands in `hooks.json` use `python3 -B` but Windows only has `python`. The `python3` alias from the Microsoft Store is a broken stub that silently fails. |
| 2 | `/tmp/` paths hardcoded | `_sdd_detect.py` builds state file paths using `/tmp/` which does not exist on Windows (temp dir is `C:\Users\<user>\AppData\Local\Temp`). |
| 3 | Unix-only modules and syscalls | `fcntl` (file locking), `os.kill(pid, 0)` (process check), and `os.rename` (atomic replace) behave differently or don't exist on Windows. |

`notify.sh` already handles Windows correctly (exits 0 on non-darwin) and requires no changes.

---

## Step 1: Create `hooks/_run.sh`

**New file** — cross-platform Python runner.

```bash
#!/bin/bash
# Cross-platform Python runner for hooks
[ -f "$1" ] || exit 0
if python3 --version >/dev/null 2>&1; then
  exec python3 -B "$@"
else
  exec python -B "$@"
fi
```

**Why this works:**
- `python3 --version` validates that the executable actually works (not just that it exists in PATH). On Windows, the Microsoft Store stub exists at `WindowsApps/python3` but fails to execute.
- `exec` replaces the shell process to avoid zombie shells.
- `[ -f "$1" ] || exit 0` absorbs the file-existence guard that was previously duplicated in every `hooks.json` command.
- Uses `"$@"` instead of `"$1"` to forward all arguments (needed for `sdd-auto-test.py --run-tests` worker mode).
- Follows the `_prefix` naming convention for private shared modules.

---

## Step 2: Update `hooks/hooks.json`

Replace all 8 Python hook commands. The pattern is:

**Before:**
```json
"command": "[ -f ${CLAUDE_PLUGIN_ROOT}/hooks/X.py ] || exit 0; python3 -B ${CLAUDE_PLUGIN_ROOT}/hooks/X.py"
```

**After:**
```json
"command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/_run.sh ${CLAUDE_PLUGIN_ROOT}/hooks/X.py"
```

**All 8 hooks to update:**

| Hook Event | Script |
|------------|--------|
| SessionStart | `session-start.py` |
| SessionStart | `agent-browser-check.py` |
| SessionStart | `memory-check.py` |
| TeammateIdle | `teammate-idle.py` |
| TaskCompleted | `task-completed.py` |
| PreToolUse | `sdd-test-guard.py` |
| PostToolUse | `sdd-auto-test.py` |
| SubagentStart | `subagent-start.py` |

The `Stop` and `Notification` hooks already use `bash notify.sh` and need no changes.

---

## Step 3: Replace `/tmp/` with `tempfile.gettempdir()` in `hooks/_sdd_detect.py`

### 3a. Add the `_tmp()` helper

After the existing imports, add:

```python
def _tmp(*parts):
    """Cross-platform temp directory."""
    return Path(tempfile.gettempdir(), *parts)
```

`tempfile` is already imported in this file. `tempfile.gettempdir()` returns `/tmp` on Unix and `C:\Users\<user>\AppData\Local\Temp` on Windows.

### 3b. Update the 4 path functions

| Function | Before | After |
|----------|--------|-------|
| `state_path()` | `Path(f"/tmp/sdd-test-state-{...}.json")` | `_tmp(f"sdd-test-state-{...}.json")` |
| `pid_path()` | `Path(f"/tmp/sdd-test-run-{...}.pid")` | `_tmp(f"sdd-test-run-{...}.pid")` |
| `skill_invoked_path()` | `Path(f"/tmp/sdd-skill-{...}.json")` | `_tmp(f"sdd-skill-{...}.json")` |
| `coverage_path()` | `Path(f"/tmp/sdd-coverage-{...}.json")` | `_tmp(f"sdd-coverage-{...}.json")` |

### 3c. Update `tempfile.mkstemp()` calls

In `write_state()` and `write_skill_invoked()`, replace:

```python
# Before
fd, tmp = tempfile.mkstemp(dir="/tmp", prefix="sdd-state-")
fd, tmp = tempfile.mkstemp(dir="/tmp", prefix="sdd-skill-")

# After
fd, tmp = tempfile.mkstemp(dir=tempfile.gettempdir(), prefix="sdd-state-")
fd, tmp = tempfile.mkstemp(dir=tempfile.gettempdir(), prefix="sdd-skill-")
```

---

## Step 4: Make `fcntl` import conditional

`fcntl` is a Unix-only module. Three files import it directly.

### Files to update

**`hooks/_sdd_detect.py`**, **`hooks/task-completed.py`**, **`hooks/teammate-idle.py`**

In each file, replace:

```python
# Before
import fcntl

# After
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows — file locking skipped
```

Then guard every `fcntl.flock()` call:

```python
# Before
fcntl.flock(f, fcntl.LOCK_SH)

# After
if fcntl:
    fcntl.flock(f, fcntl.LOCK_SH)
```

**All `fcntl.flock()` call sites:**

| File | Function | Lock type |
|------|----------|-----------|
| `_sdd_detect.py` | `read_state()` | `LOCK_SH` |
| `_sdd_detect.py` | `read_skill_invoked()` | `LOCK_SH` |
| `_sdd_detect.py` | `record_file_edit()` | `LOCK_EX` |
| `_sdd_detect.py` | `read_coverage()` | `LOCK_SH` |
| `task-completed.py` | `_increment_failures()` | `LOCK_EX` |
| `teammate-idle.py` | `_read_failures()` | `LOCK_SH` + `LOCK_UN` |

File locking is a concurrency safety measure for multi-teammate scenarios. On Windows single-user setups this is not a concern. If Windows multi-teammate support is needed later, replace `fcntl` with `msvcrt.locking()`.

---

## Step 5: Fix `os.rename()` → `os.replace()`

`os.rename()` fails on Windows when the target file already exists. `os.replace()` (Python 3.3+) atomically replaces on both platforms.

In `_sdd_detect.py`, two call sites in `write_state()` and `write_skill_invoked()`:

```python
# Before
os.rename(tmp, str(sp))

# After
os.replace(tmp, str(sp))
```

---

## Step 6: Fix `os.kill(pid, 0)` exception handling

In `_sdd_detect.py`, the `is_test_running()` function uses `os.kill(pid, 0)` to check if a process exists. On Unix this raises `ProcessLookupError` for non-existent PIDs. On Windows it raises `OSError` (`[WinError 87]`).

```python
# Before
except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):

# After
except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError, OSError):
```

`OSError` is the parent class of `ProcessLookupError`, so on Unix this is a no-op broadening that remains safe.

---

## Step 7: Update tests

### `hooks/test_sdd_detect.py`

The path format assertions use hardcoded `/tmp/` prefixes:

```python
# Before
self.assertTrue(str(sp).startswith("/tmp/sdd-test-state-"))
self.assertTrue(str(pp).startswith("/tmp/sdd-test-run-"))

# After
expected_prefix = os.path.join(tempfile.gettempdir(), "sdd-test-state-")
self.assertTrue(str(sp).startswith(expected_prefix))
expected_prefix = os.path.join(tempfile.gettempdir(), "sdd-test-run-")
self.assertTrue(str(pp).startswith(expected_prefix))
```

### `hooks/test_sdd_integration.py`

The `_cleanup_state()` helper uses hardcoded `/tmp/` paths:

```python
# Before
for pattern in [f"/tmp/sdd-test-state-{h}.json",
                f"/tmp/sdd-test-run-{h}.pid",
                f"/tmp/sdd-test-lock-{h}"]:

# After
tmp = tempfile.gettempdir()
for pattern in [os.path.join(tmp, f"sdd-test-state-{h}.json"),
                os.path.join(tmp, f"sdd-test-run-{h}.pid"),
                os.path.join(tmp, f"sdd-test-lock-{h}")]:
```

### `hooks/test_sdd_auto_test.py`

The cleanup glob in `TestSkillTracking.tearDown`:

```python
# Before
for f in g.glob("/tmp/sdd-skill-invoked-*.json"):

# After
for f in g.glob(os.path.join(tempfile.gettempdir(), "sdd-skill-invoked-*.json")):
```

---

## Files Changed Summary

| File | Type | Changes |
|------|------|---------|
| `hooks/_run.sh` | New | Cross-platform Python runner (8 lines) |
| `hooks/hooks.json` | Modified | 8 commands simplified to use `_run.sh` |
| `hooks/_sdd_detect.py` | Modified | `_tmp()` helper, conditional `fcntl`, `os.replace`, `OSError` catch |
| `hooks/task-completed.py` | Modified | Conditional `fcntl` import + guard |
| `hooks/teammate-idle.py` | Modified | Conditional `fcntl` import + guard |
| `hooks/test_sdd_detect.py` | Modified | 2 path assertions use `tempfile.gettempdir()` |
| `hooks/test_sdd_integration.py` | Modified | Cleanup paths use `tempfile.gettempdir()` |
| `hooks/test_sdd_auto_test.py` | Modified | Glob pattern uses `tempfile.gettempdir()` |

---

## Verification

Run in order:

```bash
# 1. Verify _sdd_detect.py imports cleanly
python hooks/_sdd_detect.py

# 2. Verify _run.sh detects the correct Python
bash hooks/_run.sh hooks/session-start.py

# 3. Verify a hook runs end-to-end through _run.sh
echo '{}' | bash hooks/_run.sh hooks/memory-check.py

# 4. Run all affected tests
python -m pytest hooks/test_sdd_detect.py hooks/test_sdd_integration.py hooks/test_sdd_auto_test.py -v
```

Expected: 141 tests pass on both macOS/Linux and Windows.

## Step 8: Statusline Rewrite

Replaces `jq` dependency with Python `json` stdlib:

- **`template/.claude.template/statusline.py`** — Python rewrite of statusline.sh (same visual output)
- **`template/.claude.template/statusline.sh`** — Thin wrapper that delegates to statusline.py
- **`.claude/statusline.py`** + **`.claude/statusline.sh`** — Plugin's own copies

### Session-start.py Template Sync

Added `".claude.template/statusline.py"` to `ALLOWED_TEMPLATE_PATHS` in `hooks/session-start.py` so the Python statusline syncs to target projects.

### Updated Files Summary

| File | Type | Changes |
|------|------|---------|
| `template/.claude.template/statusline.py` | New | Python statusline (~90 lines, stdlib only) |
| `template/.claude.template/statusline.sh` | Rewritten | Thin wrapper (6 lines) |
| `.claude/statusline.py` | New | Plugin copy of Python statusline |
| `.claude/statusline.sh` | Rewritten | Plugin copy of thin wrapper |
| `hooks/session-start.py` | Modified | Added statusline.py to ALLOWED_TEMPLATE_PATHS |
