---
name: hook-false-positives
created_by: manual
created_at: 2026-04-26T00:00:00Z
---

## SCEN-301: `is_test_file` rejects production substring (P0 — reward hacking close)
**Given**: production source files named `attest_logger.py`, `fastest_loader.py`, `prod_test_data.py`, `contest_winner.py`, `src/middleware/test_logger.ts`
**When**: `is_test_file(path)` is called for each
**Then**: every one returns `False` (production file, not a test)
**Evidence**: `python3 -c "from _sdd_coverage import is_test_file; assert not is_test_file('attest_logger.py')"` exits 0. True positives `test_login.py`, `foo.test.ts`, `__tests__/foo.js`, `foo_test.go` still return `True`.

## SCEN-302: `extract_coverage_pct` rejects non-coverage percentage phrases (P0 — reward hacking close)
**Given**: test runner output containing `All assertions pass: 100% confidence` (no coverage data)
**When**: `extract_coverage_pct(output)` is called
**Then**: returns `None` (no coverage detected; threshold check is skipped — fail-safe)
**Evidence**: live extraction from a synthetic output asserts `None`. True positive `Total coverage: 85%` still returns `85`.

## SCEN-303: tautology pre-strip handles comments and string literals
**Given**: a test file edit whose new content includes `# do NOT use assert True here` (comment) AND `msg = "expect(true).toBe(true) demo"` (string literal) AND zero real tautologies
**When**: PreToolUse `sdd-test-guard` evaluates the edit
**Then**: hook returns exit 0 (allow). True-positive case (raw `assert True\n` body line) still returns exit 2.
**Evidence**: subprocess hook invocation for both cases asserts the exit codes; stderr substring `[SDD:GATE]` only on the true-positive case.

## SCEN-304: `assert True == X` and `assert True is not None` allowed
**Given**: a test file edit with new content `def test_x():\n    assert True == self.config.enabled\n    assert True is not None\n`
**When**: PreToolUse `sdd-test-guard` evaluates
**Then**: hook returns exit 0 (these are real assertions, not tautologies)
**Evidence**: subprocess invocation asserts rc == 0; counter-test confirms `assert True\n    pass` (raw tautology) still rejects with rc == 2.

## SCEN-305: `git commit` mention inside heredoc bodies allowed
**Given**: a Bash command of shape `cat > NOTAS.md <<EOF\nrecordá hacer git commit luego\nEOF` with pending scenarios in cwd
**When**: PreToolUse `sdd-test-guard` evaluates the Bash payload
**Then**: hook returns exit 0 (no real `git commit` invocation, only literal text in heredoc)
**Evidence**: subprocess invocation asserts rc == 0; counter-test `git commit -m "fix"` with pending scenarios still returns rc == 2.

## SCEN-306: `_bash_writes_scenarios` blocks only when scenario path is the write target
**Given**: parametrized over (mode, command):
  - (ralph, `rm -rf cache/.ralph/specs/leftover`) — root in unrelated path
  - (nonralph, `grep -r 'docs/specs' src/`) — root mentioned for read
  - (ralph, `sed -i 's/x/y/' .ralph/specs/auth/scenarios/auth.scenarios.md`) — TRUE POSITIVE
  - (nonralph, `cat > docs/specs/foo/scenarios/foo.scenarios.md <<EOF\nx\nEOF`) — TRUE POSITIVE
**When**: PreToolUse `sdd-test-guard` evaluates each
**Then**: first two return rc == 0; last two return rc == 2 with `[SDD:SCENARIO]` stderr
**Evidence**: 4-case parametrized subprocess test asserts each rc.

## SCEN-307: `tests/` plural directory recognized as test layout
**Given**: file paths `tests/conftest.py`, `tests/foo.py`, `src/tests/helper.py`
**When**: `is_test_file(path)` is called for each
**Then**: every one returns `True` (pytest convention)
**Evidence**: live function call returns True for all three; `tests/` singular `test/foo.py` still returns True (true positive preserved).

## SCEN-308: empty test body honored when `@pytest.mark.skip` decorator present
**Given**: a test file edit with new content `@pytest.mark.skip(reason='wip')\ndef test_x():\n    pass`
**When**: PreToolUse `sdd-test-guard` evaluates
**Then**: hook returns exit 0 (skipped tests legitimately have empty body). True-positive `def test_x():\n    pass` (no decorator) still returns rc == 2.
**Evidence**: subprocess invocation asserts both cases.

## SCEN-309: `verify_proposal_received_at` rejects bool timestamp
**Given**: an `_received_at: true` (boolean) embedded in a proposal payload, with otherwise-valid HMAC
**When**: `verify_proposal_received_at(cwd, payload)` is called
**Then**: returns `None` (bool is not a legitimate timestamp type)
**Evidence**: live function call returns `None` for bool; integer `1234567890` and float `1234567890.5` still return their values when HMAC verifies.

## SCEN-310: meta-scenarios mentioning `<premortem>` are amendable
**Given**: an `amend_request` payload whose `proposed_content` contains the literal string `<premortem>` as documentation about the protocol itself
**When**: pre-Gate `_INJECTION_TOKENS` check runs
**Then**: the `<premortem>` token does NOT cause a `template_injection` rejection (the Gate-2 template substitutes only `<scenario_original>`, `<unified_diff>`, `<evidence_artifact_content>`)
**Evidence**: protocol invocation with such a payload returns a decision whose `failed_gate` is not `invariant_template_injection`. Counter-test: `<scenario_original>` literal IS still rejected.

## SCEN-311: `sdd-auto-test` reports `[PASS]` when all tests pass
**Given**: a test command that exits with rc=0 and stdout/stderr summary `14 passed in 0.5s`
**When**: `format_feedback(state)` renders the message
**Then**: the message is `SDD Auto-Test [PASS]: <summary>` (no `— fix implementation` tail). `passing` flag matches summary.
**Evidence**: unit test feeds rc=0 + summary into the worker write_state path, then asserts `format_feedback` output begins with `[PASS]` and contains no `fix implementation` substring.

## SCEN-312: `ensure_gitignore_rules` recognizes equivalent rules without re-append
**Given**: a `.gitignore` already containing `/.claude/*/` (trailing slash variant) and the framework expects `/.claude/*`
**When**: `ensure_gitignore_rules(cwd)` runs
**Then**: the file is NOT modified (the equivalent rule is honored)
**Evidence**: byte-identical hash before vs after; only TRUE missing rules trigger an append.
