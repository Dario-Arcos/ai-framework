---
outline: 2
---

# Phase 9 Silent Test Plan — Tech Lead Runbook

**Audience**: Claude Opus 4.7 acting as Tech Lead after session compaction.
**Goal**: validate Phase 9 in real use (Ralph + non-Ralph) without any push or release, then decide whether to proceed to official release.
**Mode**: silent — local cache swap, zero git push, fully reversible.
**Date authored**: 2026-04-22
**Baseline commit**: `3d1e843` (tip of Phase 9 work, 63 commits ahead of origin/main).

## 0. What was done before this document

Silent install already executed at end of previous session:

- Local clone at `/Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework` contains all Phase 8 + 8.1 + 9 commits.
- Claude Code plugin cache was replaced: `~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/` now holds the local-clone contents (minus dev artifacts). Original cache saved at `~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1.backup`.
- **Version mismatch on purpose**: cache directory name is `2026.3.1` (what Claude Code expects to load) but inside `plugin.json` version is `2026.3.2`. If Claude Code refuses to load due to mismatch, apply the hotfix in section 9.A.
- User will restart Claude Code before testing so hooks reload.
- No git push was performed. No tag was created on origin. Marketplace is unaffected.

## 1. Preflight — before touching anything

Run these first. If any fail, STOP and report to user.

```bash
# Repo state: should be clean, at 3d1e843, 63 ahead of origin
cd /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework
git status --short                # must be empty
git log --oneline -1              # must show 3d1e843 fix(hooks): Phase 9.5 ...
git rev-list --count origin/main..HEAD  # must show 63

# Cache state: must match local clone
diff -q \
  /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework/hooks/hooks.json \
  ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/hooks/hooks.json
# must print nothing (files identical)

# Backup exists
ls -d ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1.backup
# must exist
```

If any check fails, the silent install is broken. Follow §9.B REVERT before continuing.

## 2. Full-suite sanity check in the LOCAL CLONE (not cache)

This is the floor. Must pass before any real test.

```bash
cd /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework
python3 -m pytest hooks/ -q 2>&1 | tail -3
```

**Expected output (within 2-3%):**
```
1053 passed, 4 skipped, 3 xpassed, 44 subtests passed in 40s
```

- `1053 passed` is non-negotiable — zero regressions allowed
- `4 skipped` = perf benchmarks (opt-in), expected
- `3 xpassed` = quarantined flaky perf tests that happened to pass, expected

If the number is ≠ 1053 or there is any `failed`: abort test plan. Investigate regression first.

## 3. Test protocol — real-world execution

The user must have restarted Claude Code AT LEAST ONCE between silent install and these tests. Hooks reload only on restart.

### Test 3.1 — Non-Ralph interactive basics (~5 min)

**Setup** (user's OWN project, not this repo; any existing web/non-web project works):

```bash
cd <user's project with existing code>
mkdir -p .claude/scenarios
cat > .claude/scenarios/probe.scenarios.md <<'EOF'
---
name: phase9-silent-probe
created_by: tech-lead
created_at: 2026-04-22T00:00:00Z
---

## SCEN-001: phase 9 silent test verification
**Given**: user has installed Phase 9 via silent cache swap
**When**: user edits any source file in an interactive Claude Code session
**Then**: hooks fire correctly — cascade routes to Rung 1a/1b/2/3 per edit kind
**Evidence**: sdd-auto-test stderr shows scoped pytest/vitest command, not full suite
EOF
git add .claude/scenarios/probe.scenarios.md
git commit -m "seed probe scenarios"
```

**Execute** — ask user to perform these via Claude Code:

1. Ask Claude to edit one source file with a small change
2. Observe: after the edit, Claude Code should show something like `SDD Auto-Test [PASS/FAIL]: N passed in Xs` in the transcript. The command run should be **scoped** (e.g., `pytest <scoped-file>`) not `pytest` on everything.
3. Ask Claude to mark the task complete (or invoke `TaskUpdate(status="completed")`).
4. Observe: if the project has `package.json` with react/vue/etc, stderr should show:
   ```
   [SDD:DOGFOOD] Web project detected — code gates passed...
   ```
5. Invoke `/ai-framework:mission-report` directly.
6. Observe: file `.claude/mission-report-<timestamp>.md` appears with sections:
   - `## Convergence`
   - `## Cascade efficiency (Phase 8)`
   - `## Friction`
   - `## Evidence`

**Success criteria**:
- ✅ Cascade command is scoped (not full suite) when FAST_PATH_ENABLED=True (the default now)
- ✅ mission-report file is produced and readable
- ✅ Web projects show dogfood signal

**Failure mode**:
- ❌ Cascade runs full suite on every edit → `_detect_test_framework` returning None for this stack. Check stack detection for this project's manifest.
- ❌ mission-report file not produced → skill path broken. Check `~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/skills/mission-report/` exists.
- ❌ Dogfood signal on non-web project → over-reach. Check `_detect_web_project` logic.

### Test 3.2 — Write-once contract on committed scenarios (~3 min)

**Setup**: use the `.claude/scenarios/probe.scenarios.md` from Test 3.1.

**Execute**:
1. Ask Claude to edit the scenario file to change `"phase 9 silent test verification"` to something different (e.g., `"rewritten"`).
2. Observe: edit must be BLOCKED with stderr:
   ```
   [SDD:SCENARIO] SDD Guard: scenario write-once violation on .claude/scenarios/probe.scenarios.md
   ```

**Success criteria**: scenario edit denied, Phase 8.1 write-once works end-to-end including the MultiEdit/NotebookEdit matcher fix.

**Failure mode**: edit succeeds silently → hooks not reloaded OR matcher not updated. Verify:
```bash
cat ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/hooks/hooks.json | python3 -c "import sys,json; print(json.load(sys.stdin)['hooks']['PreToolUse'][0]['matcher'])"
```
Must print `Edit|Write|MultiEdit|NotebookEdit|TaskUpdate|Bash`.

### Test 3.3 — Ralph worktree enforcement (~5 min, requires git worktree)

**Setup** (in any git repo):
```bash
cd /tmp
rm -rf phase9-ralph-probe phase9-ralph-probe-wt
mkdir phase9-ralph-probe && cd phase9-ralph-probe
git init -q && git config user.email t@t.com && git config user.name t
echo seed > R && git add R && git commit -qm seed
git worktree add -b teammate-probe ../phase9-ralph-probe-wt -q
cd ../phase9-ralph-probe-wt
```

**Execute via Claude Code in `/tmp/phase9-ralph-probe-wt`**:
1. Ask Claude to create `.claude/scenarios/worktree-hack.scenarios.md` with any content.
2. Observe: Write/Edit must be BLOCKED with:
   ```
   [SDD:SCENARIO] SDD Guard: scenario parent-branch-only on .claude/scenarios/worktree-hack.scenarios.md
   First-write of a new scenario is not permitted inside a teammate worktree.
   ```

**Verify contrast in main clone** — in `/tmp/phase9-ralph-probe` (NOT the worktree):
1. Ask Claude to create `.claude/scenarios/leader.scenarios.md`.
2. Observe: Write must SUCCEED (no denial).

**Success criteria**: worktree denies first-write; main clone allows it.

**Cleanup after test**:
```bash
cd /tmp && rm -rf phase9-ralph-probe phase9-ralph-probe-wt
```

### Test 3.4 — Full Ralph autonomous run (30-60 min, most rigorous)

**Optional but strongly recommended before proceeding to release.**

**Setup**: user's real project with `.ralph/config.sh` + committed scenarios on main.

**Execute**:
1. User invokes `/ai-framework:ralph-orchestrator` with a small real task (e.g., "add a trivial utility function + tests").
2. Let it run until all teammates idle or circuit-breaker opens.
3. Verify artifacts at end:
   ```bash
   ls -la .ralph/mission-report-*.md   # must exist, latest timestamp
   cat .ralph/mission-report-*.md | head -40   # sections populated
   ```

**Success criteria**:
- mission-report auto-generated at end of run
- Rung distribution shows non-zero Rung 1a and/or Rung 1b (not 100% Rung 3)
- Tasks completed count > 0

**Failure mode**:
- Rung distribution 100% Rung 3: cascade is falling back. Either `_detect_test_framework` can't detect the stack, or the FAST_PATH config load failed. Inspect `.claude/metrics.jsonl` events to diagnose.

## 4. Success criteria — all three must be true before release

- Test 3.1 PASSED: cascade scopes correctly + mission-report generates + dogfood signals fire on web
- Test 3.2 PASSED: write-once contract enforced end-to-end
- Test 3.3 PASSED: worktree guard blocks; main clone allows
- (Optional but ideal) Test 3.4 PASSED: real Ralph run produces meaningful report

If all green → §5 (release). If any red → §6 (iterate).

## 5. Proceed to release — only after all success criteria met

**Requires explicit user authorization at each step.**

```bash
cd /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework

# Step A: promote [No Publicado] → [2026.4.0] in CHANGELOG
# Invoke: /ai-framework:changelog
# This rewrites CHANGELOG.md. Review before committing.

# Step B: bump version (npm version runs sync-versions.cjs + git tag)
npm version 2026.4.0 -m "chore(release): 2026.4.0"

# Step C: verify tag created locally
git tag | tail -3

# Step D: push (requires EXPLICIT user authorization per CLAUDE.md — ASK FIRST)
git push origin main
git push origin v2026.4.0

# Step E: marketplace sync workflow triggers on v* tag push; wait ~5 min
# Verify at https://github.com/Dario-Arcos/ai-framework/actions

# Step F: user installs 2026.4.0 via Claude Code's /plugin command
# Success: ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.4.0/ exists
```

**Before executing Step D (push)**, re-verify everything:
- Full suite still 1053 passed
- Working tree clean
- No uncommitted changes accidentally introduced during silent testing

## 6. Iterate on bugs found during silent test

If something breaks in Tests 3.1-3.4:

1. **Fix in local clone** (not in the cache):
   ```bash
   cd /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework
   # apply fix, author SCEN test, verify
   ```
2. **Re-sync cache** from local clone:
   ```bash
   rsync -a --exclude='.git/' --exclude='.pytest_cache/' --exclude='__pycache__/' \
     --exclude='node_modules/' --exclude='human-handbook/node_modules/' \
     --exclude='human-handbook/.vitepress/cache/' --exclude='.research/' \
     --exclude='.brainstorm/' --exclude='.visual-companion/' --exclude='.ralph/' \
     --exclude='.claude/metrics.jsonl' --exclude='.claude/mission-report-*.md' \
     --exclude='.claude/scenarios/' \
     /Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework/ \
     ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/
   ```
3. **User restarts Claude Code** to reload hooks.
4. **Re-run failing test**.
5. Loop until all success criteria met.

## 7. Observability during testing

Useful inspection commands while tests run:

```bash
# What events are firing during this session?
tail -20 <project>/.claude/metrics.jsonl | python3 -m json.tool 2>/dev/null || cat

# Any state from the cascade?
ls /tmp/sdd-state-*

# Has the guard fired?
grep -c 'guard_trigger' <project>/.claude/metrics.jsonl 2>/dev/null
```

## 8. Cleanup during compaction recovery

If the conversation was compacted and you need to resume mid-test:

1. Re-read this file (you are reading it now).
2. Run §1 preflight to verify state.
3. Check `.claude/metrics.jsonl` in the target project for evidence of what has already been tested.
4. Proceed from the last completed test.

## 9. Emergency procedures

### 9.A. Hotfix for plugin.json version mismatch

If Claude Code refuses to load due to `plugin.json` saying `2026.3.2` but directory is `2026.3.1`:

```bash
# Temporarily align plugin.json version with directory name
sed -i '' 's/"version": "2026.3.2"/"version": "2026.3.1"/' \
  ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/.claude-plugin/plugin.json

# Verify
grep '"version"' ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/.claude-plugin/plugin.json
# should show "version": "2026.3.1"

# User restarts Claude Code
```

Restore on release: the bumped version 2026.4.0 will be clean.

### 9.B. REVERT — if silent test reveals anything catastrophic

**Full revert to pre-Phase-9 state in 3 commands + 1 restart:**

```bash
rm -rf ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1
mv ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1.backup \
   ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1

# Verify original cache restored
cat ~/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.3.1/.claude-plugin/plugin.json | grep version
# Should show "version": "2026.3.1"

# User restarts Claude Code
```

The local clone is untouched — all 63 commits remain in git for later iteration.

### 9.C. If backup was lost or corrupted

Reinstall via Claude Code's `/plugin` command to pull fresh `2026.3.1` from the marketplace.

## 10. Contract summary (what this plan promises)

1. No git push executed by this plan
2. No marketplace release triggered
3. Full reversibility in <30 seconds via §9.B
4. The cache swap only affects this user's machine
5. Local clone remains the source of truth for any follow-up fixes
6. Official release in §5 requires explicit user authorization at every step

---

**If you (future Tech Lead Opus) are reading this after compaction**: welcome back. Run §1 preflight, then Test 3.1. The user has the authority to decide when to proceed to §5; you do not proceed without their explicit "procede con release".
