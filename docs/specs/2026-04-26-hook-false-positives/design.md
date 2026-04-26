---
name: hook-false-positives
created_at: 2026-04-26
revision: R1
strategic_intent: |
  Software factory loops break when guards misfire. False positives force agents
  into workarounds that bypass observability; false negatives open reward-hacking
  vectors. This spec closes 11 verified hook misfires across 4 lifecycle hooks
  and 2 shared modules. Two findings (B1, D2) are P0 because they contradict the
  holdout principle: a determined agent today can rename a source file to contain
  `test_` and skip coverage entirely, OR emit logs with "100% confidence" to
  satisfy the coverage gate without writing tests.
---

# Hook False-Positive Closure

## Mission

Tighten 11 patterns across the lifecycle and shared modules. No new features.
No design changes. Pure precision fixes verified with adversarial regression
tests, parametrized Ralph + non-Ralph where mode-relevant.

## Findings (verified live)

| ID | Sev | Hook / Module | Pattern | Failure mode |
|----|-----|---------------|---------|--------------|
| **B1** | **P0** | `_sdd_coverage.py:52` `TEST_FILE_RE` | `test_` substring no boundary | `attest_logger.py`, `fastest_loader.py`, `prod_test_data.py` classified as test → exempt from coverage. Reward hacking by rename. |
| **D2** | **P0** | `task-completed.py:231` `extract_coverage_pct` | Catch-all `total\|overall\|all.*?(\d+)%` | `All assertions pass: 100% confidence` parsed as 100% coverage. Reward hacking by log crafting. |
| **A1** | P1 | `sdd-test-guard.py:78-95` `_TAUTOLOGICAL_PATTERNS` | Strip only triple-quoted | `assert True == X`, `assert True is not None`, `# assert True` comments, `"expect(true)..."` strings all flagged. |
| **A2** | P1 | `sdd-test-guard.py:133` `_BASH_GIT_COMMIT_RE` + quote stripper | Heredoc bodies + escaped quotes not stripped | `cat > foo <<EOF\n...git commit...\nEOF` triggers verification gate. |
| **A3** | P1 | `sdd-test-guard.py:163` `_bash_writes_scenarios` | `any(root in command)` substring + write-verb anywhere | `rm -rf cache/.ralph/specs/leftover` blocked. |
| **B2** | P1 | `_sdd_coverage.py:52` `TEST_FILE_RE` | Plural `tests/` not enumerated | `tests/conftest.py`, `tests/foo.py` classified as source → false uncovered. |
| **E**  | P1 | `sdd-test-guard.py:83-88` empty-test pattern | Decorator above `pass` not honored | `@pytest.mark.skip\ndef test_x(): pass` blocked. |
| **C1** | P2 | `_amend_protocol.py:848` `verify_proposal_received_at` | `isinstance(x, (int, float))` accepts `bool` | `_received_at: true` passes type check, `float(True)=1.0`. HMAC still gates; type leak only. |
| **C2** | P2 | `_amend_protocol.py:85` `_INJECTION_TOKENS` | `<premortem>` rejected by pre-gate, but Gate-2 template doesn't substitute it | Meta-scenarios mentioning `<premortem>` literal cannot be amended. |
| **D1** | P2 | `sdd-auto-test.py:152` `format_feedback` | `passing` flag desync vs summary | Reports `[FAIL]: 14 passed — fix implementation` (contradictory). |
| **D3** | P3 | `session-start.py:55` `ensure_gitignore_rules` | Exact-string set membership | `/.claude/*/` vs `/.claude/*` re-appended on every session. |

Two P3 cleanup-only items deferred (dead `_SCEN_HEADER_RE`, `EXIT_SUPPRESSION_RE` in quoted strings — neither blocks work).

## Components

| File | Bundle | Change shape |
|------|--------|--------------|
| `hooks/sdd-test-guard.py` | 1 | Tighten `_TAUTOLOGICAL_PATTERNS` strip; fix `_BASH_GIT_COMMIT_RE` quote/heredoc handling; rewrite `_bash_writes_scenarios` to require root in target arg; skip empty-test on `@pytest.mark.skip` decorator. |
| `hooks/_sdd_coverage.py` | 2 | `TEST_FILE_RE`: anchor `test_` to filename start; add `tests?` plural; preserve all true positives. |
| `hooks/_amend_protocol.py` | 3 | `verify_proposal_received_at`: exclude `bool` from numeric check; drop `<premortem>` from `_INJECTION_TOKENS`. |
| `hooks/sdd-auto-test.py` | 3 | Audit `passing` setting; ensure `[PASS]/[FAIL]` matches summary. |
| `hooks/task-completed.py` | 4 | `extract_coverage_pct`: drop catch-all 5th pattern OR anchor on `coverage\|line\|stmt` keyword. |
| `hooks/session-start.py` | 4 | `ensure_gitignore_rules`: normalize before set membership. |

## Bundles (ordered)

**Bundle 0** — Merge already-fixed branch
- Branch: `fix/bash-scenarios-regex-false-positive` (commit `1f0b014e`, +25 tests, 0 regressions)
- Action: `git merge --no-ff` to `main` after a fresh `pytest hooks/ -q` confirms parity.

**Bundle 1** — `sdd-test-guard.py` regex tightening (A1 + A2 + A3 + E)
- 4 P1 fixes, single commit, single test file `test_hook_false_positives_sdd_guard.py`.
- Mode parity: A3 parametrize Ralph + non-Ralph.

**Bundle 2** — `_sdd_coverage.py` test-file detection (B1 + B2)
- 1 P0 + 1 P1, single commit. **Critical**: B1 closes a reward-hacking surface.
- Test file `test_hook_false_positives_coverage.py`. Adversarial cases: `attest_logger.py`, `prod_test_data.py`, `tests/conftest.py`, `src/tests/helper.py`.

**Bundle 3** — `_amend_protocol.py` + `sdd-auto-test.py` (C1 + C2 + D1)
- 3 P2 fixes, single commit.

**Bundle 4** — `task-completed.py` + `session-start.py` (D2 + D3)
- 1 P0 + 1 P3, single commit. **D2 critical**: coverage gate must not be game-able by log content.

## Iron rules

1. **SDD red-green per fix**: every test must fail before the fix and pass after; verify by `git stash` of the fix and rerunning.
2. **Mode parity**: every check that consults a discovery root parametrizes both `.ralph/specs` and `docs/specs`.
3. **No scope creep**: this spec fixes patterns. Do not refactor surrounding code, add features, or change unrelated regex.
4. **Verify true positives**: every fix must include a test that proves the intended-detection case is still caught. No weakening.
5. **Pytest baseline**: 1129 → final must be ≥ 1170 (11 fixes × ~3 tests each + B1/D2 adversarial sets). Zero regressions.

## Out of scope

- `_SCEN_HEADER_RE` dead-code removal (cosmetic).
- `EXIT_SUPPRESSION_RE` quoted-string false positive (P3, contrived, non-realistic).
- `_bash_is_git_commit` command-substitution false NEGATIVE (`bash -c "git commit..."` bypass) — separate audit class, deserves its own spec.
- Refactoring `_strip_quoted` to a real shell parser (out of proportion to fix scope).

## Acceptance

- 11 SCEN-301..311 satisfied (see scenarios file)
- `pytest hooks/ -q` ≥ 1170 passed, 0 failures
- Live-repro evidence: each P0/P1 captured in commit body via the same command shape that originally misfired
- 4 commits to `main` (Bundles 1-4); Bundle 0 merge separate
