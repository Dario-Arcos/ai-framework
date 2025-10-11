#!/usr/bin/env python3
"""
Security Guard Hook - PreToolUse Preventive Security Gate

PROBLEM SOLVED:
  Claude may inadvertently write code with security vulnerabilities:
  - Hardcoded credentials (API keys, passwords, tokens)
  - Dangerous code patterns (eval(), SQL injection, command injection)
  - Code quality issues (TypeScript 'any', debug statements)

SOLUTION:
  Scan tool parameters BEFORE execution (PreToolUse hook) to prevent
  vulnerable code from being written to files.

DESIGN RATIONALE:
  - PreToolUse (not PostToolUse): Block BEFORE writing to file
  - Real blocking: deny permission for critical security issues
  - Reduced false positives: Only block truly critical patterns
  - Clear user feedback: Show specific issues and line numbers

ARCHITECTURAL NECESSITY:
  Without preventive blocking, vulnerabilities would be written to files
  and require manual remediation. This hook stops them at the gate.
"""
import json
import re
import sys
import os
from datetime import datetime
from pathlib import Path


def find_project_root():
    """Find project root using current working directory (where Claude Code was started)"""
    # Start from current working directory (user's project directory)
    path = Path(os.getcwd()).resolve()

    # Check if current directory has .claude
    if (path / ".claude").exists() and (path / ".claude").is_dir():
        return path

    # Search upward for directory that CONTAINS .claude
    while path.parent != path:
        if (path / ".claude").exists() and (path / ".claude").is_dir():
            return path
        path = path.parent

    raise RuntimeError("Project root with .claude directory not found")


# Security patterns - CRITICAL issues block tool execution
# Aligned with official Claude Code security recommendations
CRITICAL_PATTERNS = [
    # Hardcoded credentials (only strings >= 16 chars to reduce false positives)
    {
        "regex": re.compile(
            r"(password|secret|api_?key|token|private_?key)\s*[=:]\s*['\"][\w\-/+=]{16,}['\"]",
            re.I,
        ),
        "message": "CRITICAL: Hardcoded credential detected (16+ chars)",
        "severity": "critical",
    },
    # eval() with variables (high injection risk)
    {
        "regex": re.compile(r"eval\s*\([^)]*[\w\[\]\.]+[^)]*\)", re.I),
        "message": "CRITICAL: eval() with variable input",
        "severity": "critical",
    },
    # SQL injection via f-strings (optimized to prevent ReDoS)
    {
        "regex": re.compile(
            r'f["\'][^"\']{0,200}(SELECT|INSERT|UPDATE|DELETE)[^"\']{0,100}(FROM|INTO|WHERE|SET)[^"\']{0,100}\{',
            re.I,
        ),
        "message": "CRITICAL: SQL injection risk (f-string in query)",
        "severity": "critical",
    },
    # Command injection via subprocess with variables
    {
        "regex": re.compile(
            r"subprocess\.(run|call|Popen|check_output)\s*\((?:[^)]*\{|[^)]*\w+\[|[^)]*\w+\.\w+|\s*\w+(?:\s|,|\)))",
            re.I,
        ),
        "message": "CRITICAL: Command injection risk (dynamic subprocess input)",
        "severity": "critical",
    },
    # Path traversal (recommended by official docs: "Block path traversal")
    {
        "regex": re.compile(
            r'\b(open|read|write|unlink|remove)\s*\([^)]{0,200}?f["\'][^"\']*\{', re.I
        ),
        "message": "CRITICAL: Path traversal risk (dynamic file path)",
        "severity": "critical",
    },
]

# Warning patterns - logged but don't block execution
WARNING_PATTERNS = [
    # TypeScript any
    {
        "regex": re.compile(r":\s*any\b"),
        "message": "WARNING: TypeScript 'any' type reduces type safety",
        "severity": "warning",
    },
    # TODO/FIXME
    {
        "regex": re.compile(r"(TODO|FIXME|HACK|XXX):", re.I),
        "message": "WARNING: Unresolved TODO/FIXME",
        "severity": "warning",
    },
    # Console statements
    {
        "regex": re.compile(r"console\.(log|warn|info|debug)", re.I),
        "message": "WARNING: Debug console statement",
        "severity": "warning",
    },
]


def analyze(content):
    """Analyze content against security patterns"""
    critical_issues = []
    warnings = []

    # Check critical patterns (will block execution)
    for pattern in CRITICAL_PATTERNS:
        matches = pattern["regex"].finditer(content)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            critical_issues.append(
                {
                    "line": line_num,
                    "message": pattern["message"],
                    "severity": pattern["severity"],
                    "match": match.group()[:50],  # Truncate for security
                }
            )

    # Check warning patterns (won't block execution)
    for pattern in WARNING_PATTERNS:
        matches = pattern["regex"].finditer(content)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            warnings.append(
                {
                    "line": line_num,
                    "message": pattern["message"],
                    "severity": pattern["severity"],
                    "match": match.group()[:30],  # Shorter truncation for warnings
                }
            )

    return critical_issues, warnings


def main():
    try:
        # Read input (max 1MB) from PreToolUse hook
        raw = sys.stdin.read(1048576)
        data = json.loads(raw) if raw else {}
    except (json.JSONDecodeError, MemoryError):
        # On error, allow tool execution
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": "Hook error - defaulting to allow",
                    }
                }
            )
        )
        sys.exit(0)

    # Extract tool information
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only analyze Edit, Write, and MultiEdit tools
    if tool_name not in ["Edit", "Write", "MultiEdit"]:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": f"Tool {tool_name} not analyzed",
                    }
                }
            )
        )
        sys.exit(0)

    # Extract content from tool parameters
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    file_path = tool_input.get("file_path", "unknown")

    if not content:
        # No content to analyze - allow
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": "No content to analyze",
                    }
                }
            )
        )
        sys.exit(0)

    # Analyze content
    critical_issues, warnings = analyze(content)

    # Logging (with stderr fallback for observability)
    try:
        project_root = find_project_root()
        log_dir = (
            Path(project_root)
            / ".claude"
            / "logs"
            / datetime.now().strftime("%Y-%m-%d")
        )
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "security.jsonl", "a") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "tool_name": tool_name,
                        "file_path": file_path,
                        "content_size": len(content),
                        "critical_issues": len(critical_issues),
                        "warnings": len(warnings),
                    }
                )
                + "\n"
            )
    except OSError as e:
        # Log to stderr for observability (similar to pre-tool-use.py)
        try:
            sys.stderr.write(
                f"HOOK_LOG_ERROR: {json.dumps({
                'timestamp': datetime.now().isoformat(),
                'hook': 'security_guard',
                'error': 'logging_failed',
                'reason': str(e)[:100]
            })}\n"
            )
        except:
            pass  # Ultimate fallback - only if stderr also fails

    # Block if critical security issues found
    if critical_issues:
        # Format issues for clear user feedback
        issues_summary = "\n".join(
            [
                f"  Line {issue['line']}: {issue['message']}"
                for issue in critical_issues[:5]  # Limit to 5 for readability
            ]
        )

        reason = (
            f"SECURITY BLOCK: {len(critical_issues)} critical issue(s) detected\n"
            f"{issues_summary}"
        )

        if len(critical_issues) > 5:
            reason += f"\n  ... and {len(critical_issues) - 5} more issue(s)"

        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
        sys.exit(1)  # Exit with error code to signal blocking

    # Allow if no critical issues (warnings are logged but don't block)
    reason = "No critical security issues detected"
    if warnings:
        reason += f" ({len(warnings)} warning(s) logged)"

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
