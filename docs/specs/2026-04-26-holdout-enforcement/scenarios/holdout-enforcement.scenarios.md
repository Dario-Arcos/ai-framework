---
name: holdout-enforcement
created_by: manual
created_at: 2026-04-26T00:00:00Z
---

## SCEN-401: one skill invocation covers exactly one commit (P0 — F1 close)
**Given**: scenarios exist under discovery roots; skill `verification-before-completion` was invoked once
**When**: agent runs `git commit -m "first"` then immediately `git commit -m "second"` (no re-invocation between)
**Then**: first commit passes; second commit BLOCKS with `[SDD:POLICY]` exit 2 stderr
**Evidence**: subprocess test invokes skill via writer helper, runs two consecutive git-commit pre-tool-use checks, asserts rc=0 then rc=2. Counter-test: re-invocation between commits → both pass.

## SCEN-402: editing scenario file after invocation invalidates evidence (P0 — F2 close)
**Given**: skill invoked at T0 (evidence records hash of `foo.scenarios.md`); user edits the file at T1 (hash changes)
**When**: `git commit` is attempted at T2
**Then**: commit BLOCKS — evidence stale, scenario hashes do not match current
**Evidence**: write evidence file with hash H1, mutate scenario content (hash becomes H2), assert gate rejects. Counter-test: scenario file untouched between invocation and commit → passes.

## SCEN-403: `--no-verify` continues to bypass with telemetry (P1)
**Given**: scenarios pending, no evidence file
**When**: `git commit --no-verify -m "emergency"`
**Then**: rc=0 (allow), AND `.claude/scenarios/.bypass-log.jsonl` appended with timestamp + scenario-hash list
**Evidence**: subprocess test confirms exit code AND log file has new line. Counter-test: same command without `--no-verify` → rc=2.

## SCEN-404: Ralph mode preserves behavior (mode parity)
**Given**: cwd contains `.ralph/specs/auth/scenarios/auth.scenarios.md`
**When**: skill invoked → git commit → second git commit
**Then**: same behavior as non-Ralph — first passes, second blocks
**Evidence**: parametrized test with `.ralph/specs` discovery root.

## SCEN-405: non-Ralph mode preserves behavior (mode parity)
**Given**: cwd contains `docs/specs/foo/scenarios/foo.scenarios.md`
**When**: skill invoked → git commit → second git commit
**Then**: same behavior as Ralph — first passes, second blocks
**Evidence**: parametrized test with `docs/specs` discovery root.

## SCEN-406: TaskUpdate(completed) no longer separately gated (F4 alignment)
**Given**: scenarios pending, no evidence file
**When**: `TaskUpdate(taskId=X, status=completed)` is invoked
**Then**: rc=0 (allow) — task tracker actions are NOT gated; only durable history-changing commands (git commit/merge/push) are
**Evidence**: subprocess test on the TaskUpdate hook path, asserts no policy block. Counter-test: `git commit` without evidence STILL blocks.

## SCEN-407: stale evidence file (older than current commit's scenarios) blocks
**Given**: evidence written at T0 covering scenarios A and B; new scenario file C added at T1; commit at T2
**When**: gate runs at T2
**Then**: BLOCK — current scenarios `{A, B, C}` not subset-equal to evidence `{A, B}`
**Evidence**: subprocess test creates A.scenarios.md and B.scenarios.md, invokes skill, adds C.scenarios.md, asserts gate rejects.

## SCEN-408: removed scenario does NOT invalidate evidence
**Given**: evidence written at T0 covering `{A, B}`; user deletes B.scenarios.md at T1; commit at T2
**When**: gate runs at T2
**Then**: PASS — current scenarios `{A}` is subset of evidence `{A, B}`. Removal is not a new claim; it's a contract reduction.
**Evidence**: subprocess test creates A and B, invokes skill, deletes B, asserts gate passes. Counter-test: SCEN-407 (added scenario) still blocks.
