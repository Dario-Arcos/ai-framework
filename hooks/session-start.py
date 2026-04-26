#!/usr/bin/env python3
"""AI Framework auto-installer - Templates sync on SessionStart.

Also cleans up orphan SDD test workers and stale temp files from
previous sessions. Workers are detached (start_new_session=True)
and survive terminal close — cleanup here prevents accumulation.
"""
import filecmp
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path


def find_plugin_root():
    """Derive plugin root from this script's location."""
    return Path(__file__).resolve().parent.parent


def find_project_dir():
    """Find project directory (where Claude Code was started)."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()


ALLOWED_TEMPLATE_PATHS = [
    "CLAUDE.md.template",
    ".claude.template/critical-paths.md.template",
    ".claude.template/settings.json.template",
    ".claude.template/statusline.cmd",
    ".claude.template/statusline.py",
]

# Only framework internals that break if tracked. User-decidable rules
# (/.ralph/, /.research/, etc.) live in gitignore.template only — never
# re-enforced, so users can remove them without session-start re-adding.
#
# Phase 10 migration: scenarios will move to `.ralph/specs/*/scenarios/`
# and `docs/specs/*/scenarios/`. Until that migration ships (2026.4.0),
# the `!/.claude/scenarios/` un-ignore belongs to user choice via
# template/gitignore.template — NOT auto-re-enforced here. Auto-adding
# it caused working-tree drift on every SessionStart.
CRITICAL_GITIGNORE_RULES = [
    "/.claude/*",
    "!/.claude/rules/",
    "/CLAUDE.md",
    "/hooks/*.db",
    "/hooks/__pycache__/",
]


def active_gitignore_rules(content):
    """Return set of uncommented, non-empty rules from gitignore content."""
    return {
        line.strip() for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def _normalize_gitignore_rule(rule):
    """Canonicalise a gitignore rule for equivalence comparison.

    `path/*` and `path/*/` match the same set of paths under standard
    gitignore semantics (the `/*` glob already implies "contents of
    path"). Treating them as distinct caused the canonical form to be
    re-appended on every session — `.gitignore` grew indefinitely with
    redundant rules (D3, SCEN-312).

    Leading `/` semantics ARE preserved: `/.claude/*` (anchored to root)
    differs from `.claude/*` (matches at any depth) and must NOT be
    equated.
    """
    stripped = rule.strip()
    if stripped.endswith("/*/"):
        return stripped[:-1]  # `path/*/` -> `path/*`
    return stripped


def migrate_claude_gitignore(content):
    """Migrate old /.claude/ rule to /.claude/* so negation patterns work."""
    lines = content.splitlines(keepends=True)
    result = []
    for line in lines:
        if line.strip() == "/.claude/":
            result.append(line.replace("/.claude/", "/.claude/*"))
        else:
            result.append(line)
    return "".join(result)


def ensure_gitignore_rules(plugin_root, project_dir):
    """Ensure critical framework rules are in project .gitignore."""
    template_gitignore = plugin_root / "template" / "gitignore.template"
    project_gitignore = project_dir / ".gitignore"

    if not project_gitignore.exists():
        if template_gitignore.exists():
            try:
                shutil.copy2(template_gitignore, project_gitignore)
            except (OSError, IOError):
                pass
        return

    try:
        with open(project_gitignore, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        content = migrate_claude_gitignore(content)

        active = active_gitignore_rules(content)
        active_normalized = {_normalize_gitignore_rule(r) for r in active}
        appended = False
        for rule in CRITICAL_GITIGNORE_RULES:
            if _normalize_gitignore_rule(rule) in active_normalized:
                continue
            if not appended:
                if content and not content.endswith("\n"):
                    content += "\n"
                content += "\n# AI Framework runtime files (auto-added)\n"
                appended = True
            content += rule + "\n"
            active.add(rule)
            active_normalized.add(_normalize_gitignore_rule(rule))

        if content != original:
            with open(project_gitignore, "w", encoding="utf-8") as f:
                f.write(content)

    except (OSError, IOError):
        pass


def sync_template_gitignore_once(plugin_root, project_dir):
    """Add missing template gitignore rules once when the template changes."""
    template_gitignore = plugin_root / "template" / "gitignore.template"
    project_gitignore = project_dir / ".gitignore"

    if not template_gitignore.exists() or not project_gitignore.exists():
        return

    current_hash = hashlib.md5(template_gitignore.read_bytes()).hexdigest()
    hash_file = project_dir / ".claude" / ".gitignore-template-hash"

    try:
        stored_hash = hash_file.read_text(encoding="utf-8").strip()
    except (OSError, IOError):
        stored_hash = ""

    if current_hash == stored_hash:
        return

    try:
        template_content = template_gitignore.read_text(encoding="utf-8")
        project_content = project_gitignore.read_text(encoding="utf-8")

        project_rules = active_gitignore_rules(project_content)
        missing = list(dict.fromkeys(
            line.strip() for line in template_content.splitlines()
            if line.strip() and not line.strip().startswith("#")
            and line.strip() not in project_rules
        ))

        if missing:
            if project_content and not project_content.endswith("\n"):
                project_content += "\n"
            project_content += "\n# AI Framework template rules (one-time sync)\n"
            for rule in missing:
                project_content += rule + "\n"
            with open(project_gitignore, "w", encoding="utf-8") as f:
                f.write(project_content)

        hash_file.parent.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(current_hash, encoding="utf-8")
    except (OSError, IOError):
        pass


def remove_template_suffix(path_str):
    """Remove .template suffix from path components."""
    parts = Path(path_str).parts
    return str(Path(*(
        p.removesuffix(".template") for p in parts
    )))


def sync_all_files(plugin_root, project_dir):
    """Sync whitelisted template files to project (skip if identical)."""
    template_dir = plugin_root / "template"

    for template_path in ALLOWED_TEMPLATE_PATHS:
        src = template_dir / template_path
        if not src.is_file():
            continue

        target_path = remove_template_suffix(template_path)
        dst = project_dir / target_path

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                continue
            shutil.copy2(src, dst)
        except (OSError, IOError) as e:
            sys.stderr.write(
                f"WARNING: Failed to sync template\n\n"
                f"Target: {target_path}\n"
                f"Error: {e}\n"
            )


def cleanup_stale_sdd(max_age=86400):
    """Purge stale SDD temp files to prevent inode accumulation.

    Tests and SDD hooks create temp files keyed by project hash.
    Files older than max_age (default 24h) are removed. SDD workers
    are NOT killed — they self-terminate within 20 min (timeout 300s
    × 3 reruns max), and pkill cannot distinguish orphans from active
    workers in parallel sessions.
    """
    tmpdir = Path(tempfile.gettempdir())
    now = time.time()
    for f in tmpdir.glob("sdd-*"):
        if f.is_dir():
            continue
        try:
            if now - os.stat(f).st_mtime > max_age:
                f.unlink(missing_ok=True)
        except OSError:
            pass


def cleanup_resolved_amend_proposals(project_dir, max_age=86400):
    """Delete amend-proposals whose resolution lifecycle is complete.

    SCEN-213: an amend proposal is removable only when BOTH:
      * its mtime is older than `max_age` (default 24h), AND
      * a sibling `<stem>.resolved.json` exists (lifecycle complete).

    Both files (proposal + sibling) are deleted together so the audit
    trail is consistent. Unresolved proposals older than 24h are
    RETAINED — they are a debt signal visible to the human, not orphan
    state. The cleanup walks both Ralph and non-Ralph discovery roots
    so non-Ralph workflows that adopt the amend protocol get the same
    lifecycle hygiene.

    Idempotent: missing directories are skipped silently. Defensive
    against partial filesystem state — never crashes on permission
    errors or stale mounts.
    """
    if project_dir is None:
        return
    project_dir = Path(project_dir)
    now = time.time()
    discovery_roots = (".ralph/specs", "docs/specs")
    for root in discovery_roots:
        root_dir = project_dir / root
        if not root_dir.is_dir():
            continue
        for goal_dir in root_dir.iterdir():
            if not goal_dir.is_dir():
                continue
            proposals_dir = goal_dir / "amend-proposals"
            if not proposals_dir.is_dir():
                continue
            for proposal in proposals_dir.glob("*.json"):
                # Skip the resolved siblings themselves — we only
                # iterate proposal files and delete them together
                # with their sibling once both conditions hold.
                if proposal.name.endswith(".resolved.json"):
                    continue
                sibling = proposal.with_name(proposal.stem + ".resolved.json")
                if not sibling.exists():
                    continue
                try:
                    age = now - proposal.stat().st_mtime
                except OSError:
                    continue
                if age <= max_age:
                    continue
                for path in (proposal, sibling):
                    try:
                        path.unlink(missing_ok=True)
                    except OSError:
                        pass


def consume_stdin():
    """Consume stdin as required by hook protocol."""
    try:
        sys.stdin.read()
    except (IOError, OSError):
        pass


def output_hook_response(context_msg=""):
    """Output JSON response following hook protocol.

    Empty context_msg emits {} — no additionalContext injected into Claude.
    """
    if context_msg:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context_msg,
            }
        }))
    else:
        print(json.dumps({}))


def main():
    """Entry point."""
    consume_stdin()
    cleanup_stale_sdd()

    try:
        project_dir = find_project_dir()
        cleanup_resolved_amend_proposals(project_dir)
        plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
        plugin_root = Path(plugin_root_env) if plugin_root_env else find_plugin_root()

        if not plugin_root.exists():
            sys.stderr.write(
                "ERROR: Plugin root not found\n\n"
                "The AI Framework plugin directory does not exist.\n"
                "Verify CLAUDE_PLUGIN_ROOT or reinstall the plugin.\n"
            )
            output_hook_response("AI Framework: ✗ Plugin root not found")
            sys.exit(1)

        ensure_gitignore_rules(plugin_root, project_dir)
        sync_template_gitignore_once(plugin_root, project_dir)
        sync_all_files(plugin_root, project_dir)

        output_hook_response()
        sys.exit(0)

    except Exception as e:
        sys.stderr.write(
            f"ERROR: Installation failed\n\n"
            f"{e}\n"
        )
        output_hook_response(f"AI Framework: ✗ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
