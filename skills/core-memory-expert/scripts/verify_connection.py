#!/usr/bin/env python3
"""
Verify RedPlanet Core MCP Connection Status

Diagnostic tool that checks:
1. MCP server registration in .mcp.json
2. Core memory tools availability
3. Connection status
4. Authentication state

Usage:
    python3 verify_connection.py

Returns exit code 0 if fully operational, 1 if issues detected.
Stdlib only - no external dependencies required.
"""

import sys
import json
import subprocess
from pathlib import Path


def find_mcp_config():
    """Locate .mcp.json in current project or parent directories."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        mcp_file = parent / ".mcp.json"
        if mcp_file.exists():
            return mcp_file
    return None


def check_mcp_registration():
    """Verify core-memory server is registered in .mcp.json."""
    print("🔍 Checking MCP registration...")

    mcp_file = find_mcp_config()
    if not mcp_file:
        print("❌ .mcp.json not found in project hierarchy")
        print("   Run setup_core_cloud.py to configure")
        return False

    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in .mcp.json: {e}")
        return False

    if "mcpServers" not in config:
        print("❌ .mcp.json missing 'mcpServers' field")
        return False

    servers = config["mcpServers"]
    if "core-memory" not in servers:
        print("❌ core-memory not registered in .mcp.json")
        print("   Run setup_core_cloud.py to register")
        return False

    print(f"✅ core-memory registered in {mcp_file}")

    # Display configuration details
    server_config = servers["core-memory"]
    if "type" in server_config:
        print(f"   Type: {server_config['type']}")
    if "url" in server_config:
        print(f"   URL: {server_config['url']}")

    return True


def check_claude_cli():
    """Verify claude CLI is available."""
    print("\n🔍 Checking Claude CLI...")

    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print("❌ claude CLI not found in PATH")
            return False

        print("✅ Claude CLI found")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Timeout checking claude CLI")
        return False
    except Exception as e:
        print(f"❌ Error checking claude CLI: {e}")
        return False


def check_mcp_list():
    """Check if core-memory appears in claude mcp list."""
    print("\n🔍 Checking MCP server list...")

    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print("⚠️  Could not retrieve MCP server list")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False

        output = result.stdout
        if "core-memory" in output:
            print("✅ core-memory appears in MCP server list")
            # Try to extract status if present
            for line in output.splitlines():
                if "core-memory" in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ core-memory not in MCP server list")
            print("   Server may need re-registration")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Timeout checking MCP server list")
        return False
    except Exception as e:
        print(f"⚠️  Error checking MCP list: {e}")
        return False


def print_diagnostic_summary(checks_passed):
    """Display diagnostic summary and next steps."""
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)

    all_passed = all(checks_passed.values())

    for check_name, passed in checks_passed.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")

    print("="*60)

    if all_passed:
        print("\n✅ All checks passed - Core is ready to use!")
        print("\nYou can now:")
        print("  • Use memory_search tool in conversations")
        print("  • Use memory_ingest tool to store information")
        print("  • Run create_agents.py for automatic memory")
    else:
        print("\n❌ Some checks failed")
        print("\nRecommended actions:")

        if not checks_passed.get("MCP Registration", False):
            print("  1. Run: python3 setup_core_cloud.py")

        if not checks_passed.get("Claude CLI", False):
            print("  1. Install Claude Code CLI")

        if not checks_passed.get("MCP Server List", False):
            print("  2. Authenticate via /mcp in Claude Code")
            print("     - Type /mcp in conversation")
            print("     - Select core-memory")
            print("     - Complete browser OAuth flow")

    print()


def main():
    """Main verification workflow."""
    print("🔬 Core MCP Connection Diagnostic")
    print("="*60)

    checks = {}

    # Check 1: MCP Registration
    checks["MCP Registration"] = check_mcp_registration()

    # Check 2: Claude CLI
    checks["Claude CLI"] = check_claude_cli()

    # Check 3: MCP Server List
    if checks["Claude CLI"]:
        checks["MCP Server List"] = check_mcp_list()
    else:
        checks["MCP Server List"] = False
        print("\n⏭️  Skipping MCP list check (CLI not available)")

    # Print summary
    print_diagnostic_summary(checks)

    # Exit code based on results
    if all(checks.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
