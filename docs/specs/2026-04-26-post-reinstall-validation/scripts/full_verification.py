"""Post-reinstall full verification — run from repo root.

Loads hooks from the INSTALLED plugin (CLAUDE_PLUGIN_ROOT or known path),
runs every adversarial probe of v2026.5.0:
  - Bundle 1: A1+A2+A3+E (sdd-test-guard.py)
  - Bundle 5: A3 hardening (cross-statement + comment FPs)
  - Bundle 2 P0: B1 rename evasion + B2 plural tests/
  - Bundle 3: C1+C2+D1
  - Bundle 4 P0: D2 log evasion + D3 normalize gitignore
  - Holdout F1: consume one-shot
  - Holdout F2: edited scenario invalidates
  - Holdout F3: skill writes hashes
  - Holdout F4: TaskUpdate gate removed
  - Backward compat: sop-code-assist persistent

Exits 0 on `0 failures`, 1 otherwise.
"""
import os
import sys
import importlib.util as _u
import tempfile
import shutil
from pathlib import Path

INSTALLED_PLUGIN = (
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or "/Users/dariarcos/.claude/plugins/cache/ai-framework-marketplace/ai-framework/2026.5.0"
)
HOOK_DIR = os.path.join(INSTALLED_PLUGIN, "hooks")

if not os.path.exists(HOOK_DIR):
    print(f"[FATAL] Plugin hooks not found at {HOOK_DIR}")
    print("Reinstall plugin or set CLAUDE_PLUGIN_ROOT to the v2026.5.0 install.")
    sys.exit(1)

sys.path = [p for p in sys.path if "/tmp" not in p]
sys.path.insert(0, HOOK_DIR)


def _load(rel, name):
    path = os.path.join(HOOK_DIR, rel)
    s = _u.spec_from_file_location(name, path)
    m = _u.module_from_spec(s)
    s.loader.exec_module(m)
    return m


guard = _load("sdd-test-guard.py", "guard")
auto = _load("sdd-auto-test.py", "auto")
tc = _load("task-completed.py", "tc")
ss = _load("session-start.py", "ss")
import _amend_protocol as ap
from _sdd_coverage import is_test_file
from _sdd_state import (
    consume_skill_invoked, read_skill_invoked, skill_invoked_path, write_skill_invoked,
)
from _sdd_scenarios import current_scenario_hashes, has_pending_scenarios

cwd = "/Users/dariarcos/G-Lab/IA-First-Development/prod/ai-framework"
failures = []


def assert_eq(label, actual, expected):
    if actual != expected:
        failures.append(f"  [FAIL] {label}: expected={expected!r} actual={actual!r}")
    else:
        print(f"  [OK] {label}")


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ─── Bundle 1 + Bundle 5 ───
section("Bundle 1 + 5 — sdd-test-guard.py")
assert_eq("A1 raw assert True (TP)",
          guard._find_tautological_test_addition("def test_x():\n    assert True\n    pass"),
          "assert True")
assert_eq("A1 assert True == X (FP closed)",
          guard._find_tautological_test_addition("def t():\n    assert True == cfg\n"), None)
assert_eq("A1 assert True is not None (FP closed)",
          guard._find_tautological_test_addition("def t():\n    assert True is not None\n"), None)
assert_eq("A1 # comment (FP closed)",
          guard._find_tautological_test_addition("# do not use assert True\n"), None)
assert_eq("A1 string literal (FP closed)",
          guard._find_tautological_test_addition('msg = "expect(true).toBe(true) demo"\n'), None)
assert_eq("A2 real git commit (TP)", guard._bash_is_git_commit("git commit -m fix"), True)
assert_eq("A2 heredoc body git commit (FP)",
          guard._bash_is_git_commit("cat > N <<EOF\nrecorda git commit\nEOF"), False)
assert_eq("A2 git commit-tree lookalike (FP)", guard._bash_is_git_commit("git commit-tree"), False)
assert_eq("A3 sed scenarios TP",
          guard._bash_writes_scenarios(
              "sed -i 's/x/y/' docs/specs/foo/scenarios/foo.scenarios.md", cwd), True)
assert_eq("A3 unrelated cleanup FP",
          guard._bash_writes_scenarios("rm -rf cache/.ralph/specs/leftover", cwd), False)
assert_eq("Bundle5 cross-stmt FP",
          guard._bash_writes_scenarios(
              "rm /tmp/foo && echo 'docs/specs/x/scenarios/x.scenarios.md'", cwd), False)
assert_eq("Bundle5 rm in comment FP",
          guard._bash_writes_scenarios(
              "grep 'docs/specs/x/scenarios/x.scenarios.md' src/  # rm hint", cwd), False)
assert_eq("Bundle5 tee after pipe TP",
          guard._bash_writes_scenarios(
              "cat config | tee docs/specs/foo/scenarios/foo.scenarios.md", cwd), True)
assert_eq("E bare pass TP",
          guard._find_tautological_test_addition("def test_x():\n    pass\n"),
          "empty test function")
assert_eq("E @pytest.mark.skip FP",
          guard._find_tautological_test_addition(
              "@pytest.mark.skip\ndef test_x():\n    pass\n"), None)
assert_eq("E @unittest.skipIf FP",
          guard._find_tautological_test_addition(
              "@unittest.skipIf(c,'r')\ndef test_x():\n    pass\n"), None)

# ─── Bundle 2 P0 ───
section("Bundle 2 P0 — B1 rename evasion + B2 plural tests/")
for path in ["attest_logger.py", "fastest_loader.py", "prod_test_data.py",
             "contest_winner.py", "manifest_data.py", "latest_release.py"]:
    assert_eq(f"B1 P0 {path} (rename FP)", is_test_file(path), False)
for path in ["test_login.py", "src/test_helper.py", "foo_test.py",
             "foo.test.ts", "__tests__/foo.js", "test/foo.py"]:
    assert_eq(f"B1 TP {path}", is_test_file(path), True)
for path in ["tests/conftest.py", "tests/foo.py", "src/tests/helper.py"]:
    assert_eq(f"B2 plural {path}", is_test_file(path), True)

# ─── Bundle 3 ───
section("Bundle 3 — C1, C2, D1")
assert_eq("C2 _INJECTION_TOKENS missing premortem",
          "<premortem>" in ap._INJECTION_TOKENS, False)
for t in ("<scenario_original>", "<unified_diff>", "<evidence_artifact_content>"):
    assert_eq(f"C2 _INJECTION_TOKENS contains {t}", t in ap._INJECTION_TOKENS, True)


def fb(state):
    return auto.format_feedback(state) or ""


assert_eq("D1 desync False+pure-pass repaired",
          fb({"passing": False, "summary": "13 passed"}).startswith("SDD Auto-Test [PASS]"), True)
assert_eq("D1 real failure preserved",
          fb({"passing": False, "summary": "13 passed, 1 failed"}).startswith("SDD Auto-Test [FAIL]"), True)
assert_eq("D1 timeout preserved",
          fb({"passing": False, "summary": "tests timed out"}).startswith("SDD Auto-Test [FAIL]"), True)

# ─── Bundle 4 P0 ───
section("Bundle 4 P0 — D2 log evasion + D3 normalize")
for s in ["All assertions pass: 100% confidence", "100% certain about this fix",
          "All passed: 100%", "Test suite: all green at 100%",
          "100% of cookies eaten", "Overall accuracy: 95%"]:
    assert_eq(f"D2 P0 reject {s!r}", tc.extract_coverage_pct(s), None)
assert_eq("D2 TP Total coverage: 85%", tc.extract_coverage_pct("Total coverage: 85%"), 85.0)
assert_eq("D2 TP Line coverage: 72%", tc.extract_coverage_pct("Line coverage: 72%"), 72.0)
assert_eq("D2 TP Statements : 85.71%", tc.extract_coverage_pct("Statements : 85.71%"), 85.71)
assert_eq("D3 trailing slash normalized",
          ss._normalize_gitignore_rule("/.claude/*/"), "/.claude/*")
assert_eq("D3 leading-/ semantics preserved",
          ss._normalize_gitignore_rule("/path"), "/path")

# ─── Holdout ───
section("Holdout — F1, F2, F3, F4")


def with_tmp(fn):
    td = tempfile.mkdtemp(prefix="post-reinstall-")
    try:
        return fn(td)
    finally:
        try:
            os.unlink(skill_invoked_path(td, "verification-before-completion"))
        except FileNotFoundError:
            pass
        shutil.rmtree(td, ignore_errors=True)


def setup_scen(td, content=None):
    if content is None:
        content = ("---\nname: x\n---\n## SCEN-001: x\n**Given**: x\n**When**: x\n"
                   "**Then**: x\n**Evidence**: x\n")
    sd = Path(td) / "docs" / "specs" / "x" / "scenarios"
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "x.scenarios.md").write_text(content, encoding="utf-8")


def f1_test(td):
    setup_scen(td)
    write_skill_invoked(td, "verification-before-completion")
    first = consume_skill_invoked(td, "verification-before-completion")
    second = consume_skill_invoked(td, "verification-before-completion")
    return first is not None and second is None


assert_eq("F1 one-shot consume", with_tmp(f1_test), True)


def f2_test(td):
    setup_scen(td)
    h = current_scenario_hashes(td)
    write_skill_invoked(td, "verification-before-completion", scenario_hashes=h)
    setup_scen(td, content="---\nname: x\n---\n## SCEN-001b: tampered\n**Given**: x\n"
                            "**When**: x\n**Then**: x\n**Evidence**: x\n")
    return has_pending_scenarios(td, sid="t1", consume=True)


assert_eq("F2 edited scenario invalidates", with_tmp(f2_test), True)


def f3_test(td):
    setup_scen(td)
    h = current_scenario_hashes(td)
    write_skill_invoked(td, "verification-before-completion", scenario_hashes=h)
    state = consume_skill_invoked(td, "verification-before-completion")
    return state.get("scenario_hashes") == h


assert_eq("F3 skill writes hashes", with_tmp(f3_test), True)

gtxt = open(os.path.join(HOOK_DIR, "sdd-test-guard.py")).read()
assert_eq("F4 TaskUpdate(completed) block REMOVED",
          "TaskUpdate(completed) blocked" in gtxt, False)

# ─── Backward compat ───
section("Backward compat — sop-code-assist persistent")


def bc_test(td):
    write_skill_invoked(td, "sop-code-assist")
    a = read_skill_invoked(td, "sop-code-assist")
    b = read_skill_invoked(td, "sop-code-assist")
    return a is not None and b is not None


assert_eq("sop-code-assist persistent (a + b both readable)", with_tmp(bc_test), True)

# ─── Final ───
print()
print("=" * 70)
if failures:
    print(f"** {len(failures)} FAILURES **")
    for f in failures:
        print(f)
    print()
    print("VERDICT: NO-GO")
    sys.exit(1)
print("ALL VERIFIED — 0 failures")
print()
print("VERDICT: GO (subject to live phases 2, 3, 7, 9, 10 — see test-plan.md)")
sys.exit(0)
