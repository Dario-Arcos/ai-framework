"""SDD file classification, coverage state, parsers, diff-coverage engine.

Extracted from _sdd_detect.py — pure refactor, zero behavior change.
"""
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows — file locking skipped
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

from _sdd_state import (
    _tmp,
    _read_json_with_ttl,
    _write_json_atomic,
    _parse_utc_timestamp,
    project_hash,
    coverage_path,
)


# ─────────────────────────────────────────────────────────────────
# FILE CLASSIFICATION — centralized source/test/exempt detection
# ─────────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".java", ".kt", ".rb", ".swift", ".c", ".cpp", ".cs",
    ".vue", ".svelte",          # frontend frameworks
    ".mts", ".cts", ".mjs",    # ES module variants
    ".graphql", ".gql",         # schemas with logic
    ".prisma",                  # ORM schemas
    ".proto",                   # protobuf
    ".sql",                     # database
    ".sh", ".bash",             # shell scripts
})

# Compound extensions that look like source but are generated artifacts
GENERATED_COMPOUND_RE = re.compile(r"\.(?:d\.ts|min\.js|min\.css)$")

TEST_FILE_RE = re.compile(
    r"(?:test|spec|__tests__)[/\\]|"
    r"\.(?:test|spec)\.|"
    r"_tests?\.|"
    r"test_"
)

EXEMPT_RE = re.compile(
    r"(?:^|/)(?:"
    r"__init__\.py|conftest\.py|setup\.py|"
    r"index\.(?:ts|js|tsx|jsx)|"
    r"types\.(?:ts|d\.ts)|"
    r"constants?\.(?:ts|js|py)|"
    r"config[^/]*\.(?:ts|js|py|json|ya?ml|toml)"
    r")$|"
    r"(?:^|/)(?:migrations?|generated|vendor|scripts|docs?|\.ralph)/"
)


def is_source_file(path):
    """Check if path is a source file worth triggering tests for."""
    if not path:
        return False
    if GENERATED_COMPOUND_RE.search(path):
        return False
    return Path(path).suffix in SOURCE_EXTENSIONS


def is_test_file(path):
    """Check if path matches common test file patterns."""
    if not path:
        return False
    return bool(TEST_FILE_RE.search(path))


def is_exempt_from_tests(path):
    """Check if a source file is exempt from coverage requirements.

    Exempt: __init__.py, conftest.py, index.ts, types.ts, constants.ts,
    config files, migrations/, generated/, vendor/, scripts/, docs/.
    """
    if not path:
        return False
    return bool(EXEMPT_RE.search(path))


# ─────────────────────────────────────────────────────────────────
# COVERAGE TRACKING STATE — anti reward-hacking by omission
# ─────────────────────────────────────────────────────────────────

def record_file_edit(cwd, file_path, sid=None):
    """Atomic append: add file to source_files or test_files set.

    Uses LOCK_EX read-modify-write. ~1ms.
    """
    cp = coverage_path(cwd, sid)
    try:
        # Ensure file exists
        cp.touch(exist_ok=True)
        with open(cp, "r+", encoding="utf-8") as f:
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_EX)
            raw = f.read()
            try:
                data = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                data = {}

            source_files = set(data.get("source_files", []))
            test_files = set(data.get("test_files", []))

            if is_test_file(file_path):
                test_files.add(file_path)
            else:
                source_files.add(file_path)

            data["source_files"] = sorted(source_files)
            data["test_files"] = sorted(test_files)
            data["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            # Record edit time unconditionally — sub-agents without a sid
            # also need stale-report detection; missing it lets stale
            # coverage reports pass freshness checks vacuously.
            data["last_edit_time"] = time.time()

            f.seek(0)
            f.truncate()
            json.dump(data, f)
            f.write("\n")
    except OSError:
        pass


def read_coverage(cwd, max_age_seconds=14400, sid=None):
    """Read coverage state with LOCK_SH + TTL (4h). Returns dict or None."""
    return _read_json_with_ttl(coverage_path(cwd, sid), max_age_seconds, use_flock=True)


def clear_coverage(cwd, sid=None):
    """Remove coverage state file."""
    try:
        coverage_path(cwd, sid).unlink(missing_ok=True)
    except OSError:
        pass


def parse_lcov(lcov_path):
    """Parse lcov.info file → {abs_path: {line_no: hit_count}}.

    lcov format (simplified):
      SF:<relative-or-absolute-path>
      DA:<line_number>,<hit_count>[,<optional_checksum>]
      ...
      end_of_record

    Tolerant: malformed DA lines are skipped; path normalization resolves
    relative paths against the lcov file's parent directory. Returns
    empty dict on missing file or IO errors.
    """
    result = {}
    try:
        content = Path(lcov_path).read_text(encoding="utf-8", errors="replace")
    except (OSError, FileNotFoundError):
        return result

    base_dir = Path(lcov_path).parent
    current_file = None
    current_lines = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("SF:"):
            current_file = line[3:].strip()
            current_lines = {}
        elif line.startswith("DA:") and current_file:
            try:
                parts = line[3:].split(",")
                line_no = int(parts[0])
                hits = int(parts[1])
                current_lines[line_no] = hits
            except (ValueError, IndexError):
                continue
        elif line == "end_of_record" and current_file:
            p = Path(current_file)
            if not p.is_absolute():
                p = (base_dir / p).resolve()
            else:
                p = p.resolve()
            result[str(p)] = current_lines
            current_file = None
            current_lines = {}
    return result


def parse_go_cover(cover_path):
    """Parse Go coverprofile file → {abs_path: {line_no: hit_count}}.

    Go cover format:
      mode: set|count|atomic
      <file>:<startLine>.<startCol>,<endLine>.<endCol> <numStmt> <count>

    Each range expands to all lines in [startLine, endLine]. Tolerant
    of malformed lines. Returns empty dict on missing file.
    """
    result = {}
    try:
        content = Path(cover_path).read_text(encoding="utf-8", errors="replace")
    except (OSError, FileNotFoundError):
        return result

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("mode:"):
            continue
        try:
            # Split from the right — count is always last, numStmt second-to-last
            file_part, rest = line.split(":", 1)
            spec, num_stmt, count = rest.rsplit(" ", 2)
            # spec is "startLine.startCol,endLine.endCol"
            start_spec, end_spec = spec.split(",", 1)
            start_line = int(start_spec.split(".", 1)[0])
            end_line = int(end_spec.split(".", 1)[0])
            hits = int(count)
        except (ValueError, IndexError):
            continue
        p = Path(file_part).resolve()
        key = str(p)
        if key not in result:
            result[key] = {}
        for ln in range(start_line, end_line + 1):
            prev = result[key].get(ln, 0)
            result[key][ln] = prev + hits
    return result


def find_test_for_source(source_path, test_files):
    """Convention match: find a test file for a source file by basename.

    Matches:
    - foo.py → test_foo.py, foo_test.py
    - foo.ts → foo.test.ts, foo.spec.ts
    - foo.go → foo_test.go

    Returns matching path or None.
    """
    p = Path(source_path)
    stem = p.stem
    for tf in test_files:
        tf_name = Path(tf).name
        # Python: test_foo.py, foo_test.py
        if tf_name == f"test_{stem}.py" or tf_name == f"{stem}_test.py":
            return tf
        # JS/TS: foo.test.ts, foo.spec.ts, foo.test.js, foo.spec.js, etc.
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            if tf_name == f"{stem}.test{ext}" or tf_name == f"{stem}.spec{ext}":
                return tf
        # Go: foo_test.go
        if tf_name == f"{stem}_test.go":
            return tf
    return None


def has_test_on_disk(source_path, cwd):
    """Check if a test file exists on disk for a given source file.

    Convention-based lookup: same directory, __tests__/, project-level tests/.
    Returns True if any matching test file exists on the filesystem.
    """
    p = Path(source_path)
    stem = p.stem

    # Resolve relative paths against cwd
    if not p.is_absolute():
        p = Path(cwd) / p
    parent = p.parent

    candidates = []

    # Python: test_foo.py, foo_test.py
    candidates.append(parent / f"test_{stem}.py")
    candidates.append(parent / f"{stem}_test.py")

    # JS/TS: foo.test.ts, foo.spec.ts, etc.
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        candidates.append(parent / f"{stem}.test{ext}")
        candidates.append(parent / f"{stem}.spec{ext}")

    # Go: foo_test.go
    candidates.append(parent / f"{stem}_test.go")

    # __tests__ sibling directory
    tests_dir = parent / "__tests__"
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        candidates.append(tests_dir / f"{stem}.test{ext}")
        candidates.append(tests_dir / f"{stem}.spec{ext}")

    # Project-level test directories (tests/, test/)
    cwd_path = Path(cwd)
    for test_dir_name in ("tests", "test"):
        test_dir = cwd_path / test_dir_name
        candidates.append(test_dir / f"test_{stem}.py")
        candidates.append(test_dir / f"{stem}_test.py")
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            candidates.append(test_dir / f"{stem}.test{ext}")
            candidates.append(test_dir / f"{stem}.spec{ext}")

    return any(c.exists() for c in candidates)


def _session_max_edit_time(cwd, sid=None):
    """Max last_edit_time for this session's coverage state.

    Session-scoped: when sid is provided, reads only sdd-coverage-{hash}-{sid}.json,
    avoiding cross-contamination from parallel teammates whose edit timestamps
    are unrelated to this gate's freshness check.

    When sid is None (legacy/non-teammate), falls back to the project-wide glob
    to preserve old behavior for solo runs.
    """
    if sid:
        # Use shared lock to avoid reading partial JSON from a concurrent
        # record_file_edit() that holds LOCK_EX and is truncating/rewriting.
        data = _read_json_with_ttl(coverage_path(cwd, sid), max_age_seconds=-1,
                                   use_flock=True)
        if data is None:
            return None
        try:
            t = float(data.get("last_edit_time", 0))
            return t if t > 0 else None
        except (ValueError, TypeError):
            return None
    # Legacy path: no sid → project-wide glob
    hash_ = project_hash(cwd)
    max_t = 0.0
    try:
        for p in Path(tempfile.gettempdir()).glob(f"sdd-coverage-{hash_}*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                t = float(data.get("last_edit_time", 0))
                if t > max_t:
                    max_t = t
            except (OSError, json.JSONDecodeError, ValueError):
                pass
    except OSError:
        pass
    return max_t if max_t > 0 else None


def _build_basename_index(report):
    """Build {basename: [keys]} from a coverage report. O(N) once.

    Used by _match_path_in_report to convert tier-2/tier-3 lookups from
    O(N) walks per source file into O(1) candidate set + O(k) suffix check
    over typically small k. At monorepo scale (10k+ entries) this turns
    seconds of matching into milliseconds.
    """
    index = {}
    for key in report:
        bn = Path(key).name
        index.setdefault(bn, []).append(key)
    return index


def _match_path_in_report(report, target_abs, basename, basename_index=None):
    """Three-tier path matching against coverage report keys.

    1. Exact realpath match
    2. Suffix-unique match (for monorepo path skew)
    3. Basename-unique match (last resort)

    Returns the hits dict for the matched path, or None.

    basename_index ({basename: [keys]}) is optional but recommended — it
    constrains tier-2/tier-3 walks to candidates sharing the source file's
    basename instead of scanning every report entry.
    """
    # Tier 1: exact
    if target_abs in report:
        return report[target_abs]

    # Constrain candidate set via basename index when available
    candidates = (basename_index.get(basename, [])
                  if basename_index is not None else list(report))

    # Tier 2: suffix match (unique only)
    target_parts = Path(target_abs).parts
    matches = []
    for path_key in candidates:
        key_parts = Path(path_key).parts
        if len(key_parts) > len(target_parts):
            continue
        if len(key_parts) > 0 and key_parts == target_parts[-len(key_parts):]:
            matches.append(path_key)
    if len(matches) == 1:
        return report[matches[0]]

    # Tier 3: basename match (unique only) — already bounded by candidates
    if basename_index is not None:
        if len(candidates) == 1:
            return report[candidates[0]]
    else:
        bn_matches = [k for k in report if Path(k).name == basename]
        if len(bn_matches) == 1:
            return report[bn_matches[0]]

    return None


def _git_changed_lines(cwd):
    """Parse `git diff HEAD` output → {abs_path: set(line_numbers)}.

    Returns None if git is unavailable or the repo has no HEAD (new repo).
    Used to restrict coverage check to lines actually edited in this change.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--unified=0", "--no-color"],
            capture_output=True, text=True, timeout=5, cwd=cwd,
        )
        if result.returncode != 0:
            return None
    except (OSError, subprocess.TimeoutExpired):
        return None

    changed = {}
    current_file = None
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            rel = line[6:]
            current_file = str((Path(cwd) / rel).resolve())
            if current_file not in changed:
                changed[current_file] = set()
        elif line.startswith("@@") and current_file:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2) or "1")
                for i in range(start, start + count):
                    changed[current_file].add(i)
    return changed


def _load_coverage_report(cwd, coverage_spec=None, sid=None):
    """Load the project's coverage report if available and fresh.

    Returns {abs_path: {line_no: hit_count}} dict, or None if unavailable
    or stale. Stale = older than any session edit in this project.

    When sid is provided, freshness check is scoped to this session only
    (avoids cross-contamination from parallel teammates).
    """
    # Import here to avoid circular dependency — detect_coverage_command
    # lives in _sdd_detect which imports from us via the facade
    from _sdd_detect import detect_coverage_command

    if coverage_spec is None:
        coverage_spec = detect_coverage_command(cwd)
    if coverage_spec is None:
        return None
    _cmd, fmt, rel_path = coverage_spec
    full_path = Path(cwd) / rel_path
    if not full_path.is_file():
        return None

    try:
        report_mtime = full_path.stat().st_mtime
    except OSError:
        return None

    edit_time = _session_max_edit_time(cwd, sid=sid)
    if edit_time is not None and report_mtime < edit_time - 5:
        # 5s clock-skew grace window
        return None

    if fmt == "lcov":
        return parse_lcov(str(full_path))
    if fmt == "go-cover":
        return parse_go_cover(str(full_path))
    return None


def _diff_coverage_uncovered(cwd, source_files, report):
    """Flag source files not exercised by the coverage report.

    Per file:
      - If git diff is available: uncovered = any edited line has 0 hits.
      - Else: uncovered = no line has any hit (file-level check).
    """
    cwd_path = Path(cwd).resolve()
    changed_lines = _git_changed_lines(cwd) or {}
    bn_index = _build_basename_index(report)
    uncovered = []

    for sf in source_files:
        p = Path(sf)
        if not p.is_absolute():
            p = (cwd_path / p).resolve()
        else:
            p = p.resolve()
        file_key = str(p)

        hits = _match_path_in_report(report, file_key, p.name, bn_index)
        if hits is None:
            # Not in report → test suite didn't touch this file
            uncovered.append(sf)
            continue

        file_changed = changed_lines.get(file_key)
        if file_changed:
            # Line-level: any edited line with 0 hits → uncovered
            if any(hits.get(ln, 0) == 0 for ln in file_changed):
                uncovered.append(sf)
        else:
            # File-level fallback: need at least one executed line
            if not any(count > 0 for count in hits.values()):
                uncovered.append(sf)

    return uncovered


def _basename_uncovered(cwd, source_files, test_files):
    """Legacy basename + disk heuristic. Fallback when no coverage report."""
    uncovered = []
    for sf in source_files:
        if find_test_for_source(sf, test_files):
            continue
        if has_test_on_disk(sf, cwd):
            continue
        uncovered.append(sf)
    return uncovered


def compute_uncovered(cwd, state, coverage_spec=None, sid=None):
    """Return source files without corresponding tests.

    Strategy (first applicable wins):
      1. Coverage report (diff-coverage) — if detected and fresh, use line/file
         hit data from the test runner's own report. Stack-agnostic and
         anti-reward-hacking (line must actually execute, not just "a test
         file exists").
      2. Basename + disk heuristic — fallback when no coverage report is
         available. Checks session test_files + convention-matched files
         on disk.

    Exempt files and test files misclassified as source are always excluded.
    When sid is provided, the coverage report freshness check is session-scoped.
    """
    source_files = [
        sf for sf in state.get("source_files", [])
        if not is_exempt_from_tests(sf) and not is_test_file(sf)
    ]
    if not source_files:
        return []

    report = _load_coverage_report(cwd, coverage_spec, sid=sid)
    if report is not None:
        return _diff_coverage_uncovered(cwd, source_files, report)

    return _basename_uncovered(cwd, source_files, state.get("test_files", []))
