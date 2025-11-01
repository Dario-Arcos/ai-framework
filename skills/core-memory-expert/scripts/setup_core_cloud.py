#!/usr/bin/env python3
"""
Setup RedPlanet Core Cloud MCP Server for Claude Code

Automates the complete setup process:
1. Registers Core MCP server via claude mcp add command
2. Provides authentication instructions
3. Verifies connection status
4. Reports setup completion

Usage:
    python3 setup_core_cloud.py [--integrations github,linear,slack] [--no-integrations]

Examples:
    python3 setup_core_cloud.py
    python3 setup_core_cloud.py --integrations github,linear
    python3 setup_core_cloud.py --no-integrations

Stdlib only - no external dependencies required.
"""

import sys
import subprocess
import json
import time
from pathlib import Path


def run_command(cmd_list, description, capture_output=True):
    """Execute command with error handling. cmd_list must be a list of strings."""
    try:
        if capture_output:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd_list, timeout=30)
            return result.returncode == 0, "", ""
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out: {description}"
    except Exception as e:
        return False, "", f"Error executing {description}: {e}"


def build_mcp_url(integrations=None, no_integrations=False):
    """Build Core MCP URL with optional integrations parameter."""
    base_url = "https://core.heysol.ai/api/v1/mcp?source=Claude-Code"

    if no_integrations:
        return f"{base_url}&no_integrations=true"
    elif integrations:
        return f"{base_url}&integrations={integrations}"
    else:
        return base_url


def check_claude_cli():
    """Verify claude CLI is available."""
    success, stdout, stderr = run_command(["which", "claude"], "Check Claude CLI")
    if not success:
        print("❌ ERROR: claude CLI not found in PATH")
        print("   Install Claude Code CLI first: https://docs.claude.com/")
        return False
    print("✅ Claude CLI found")
    return True


def register_mcp_server(url):
    """Register Core MCP server using claude mcp add."""
    print("\n📝 Registering Core MCP server...")

    cmd_list = ["claude", "mcp", "add", "--transport", "http", "core-memory", url]
    print(f"   Running: {' '.join(cmd_list)}")

    success, stdout, stderr = run_command(cmd_list, "Register MCP server")

    if not success:
        print(f"❌ Failed to register MCP server")
        if stderr:
            print(f"   Error: {stderr}")
        return False

    print("✅ MCP server registered successfully")
    if stdout:
        print(f"   Output: {stdout.strip()}")
    return True


def get_mcp_config_path():
    """Find .mcp.json file in current project."""
    # Check current directory and parent directories
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        mcp_file = parent / ".mcp.json"
        if mcp_file.exists():
            return mcp_file
    return None


def verify_mcp_registration():
    """Verify Core MCP server appears in .mcp.json."""
    print("\n🔍 Verifying MCP configuration...")

    mcp_file = get_mcp_config_path()
    if not mcp_file:
        print("⚠️  WARNING: .mcp.json not found in project")
        print("   Server may be registered in global config")
        return True

    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)

        if "mcpServers" not in config:
            print("⚠️  WARNING: .mcp.json has no 'mcpServers' field")
            return False

        if "core-memory" in config["mcpServers"]:
            print(f"✅ core-memory found in {mcp_file}")
            server_config = config["mcpServers"]["core-memory"]
            if "url" in server_config:
                print(f"   URL: {server_config['url']}")
            return True
        else:
            print("⚠️  WARNING: core-memory not found in .mcp.json")
            print("   Server may be registered in global config")
            return True

    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in .mcp.json: {e}")
        return False
    except Exception as e:
        print(f"⚠️  WARNING: Could not read .mcp.json: {e}")
        return True


def print_auth_instructions():
    """Display authentication next steps."""
    print("\n" + "="*60)
    print("🔐 AUTHENTICATION REQUIRED")
    print("="*60)
    print("\nNext steps to authenticate:")
    print()
    print("1. Restart Claude Code CLI (if currently running)")
    print("2. Start a new conversation")
    print("3. Type: /mcp")
    print("4. Select 'core-memory' from the list")
    print("5. Browser will open automatically")
    print("6. Sign in to Core (core.heysol.ai)")
    print("7. Grant permissions when prompted")
    print()
    print("Alternative: Use verify_connection.py to check status")
    print()
    print("="*60)


def print_success_summary(url):
    """Display setup completion summary."""
    print("\n" + "="*60)
    print("✅ SETUP COMPLETED")
    print("="*60)
    print()
    print("Core MCP Server Configuration:")
    print(f"  Name: core-memory")
    print(f"  URL: {url}")
    print()
    print("What was configured:")
    if "no_integrations=true" in url:
        print("  • Core memory tools only (no external integrations)")
    elif "integrations=" in url:
        integrations = url.split("integrations=")[1].split("&")[0]
        print(f"  • Integrations: {integrations}")
    else:
        print("  • All available integrations enabled")
    print()
    print("="*60)


def main():
    """Main setup workflow."""
    print("🚀 RedPlanet Core Cloud Setup")
    print("="*60)

    # Parse arguments
    integrations = None
    no_integrations = False

    if "--no-integrations" in sys.argv:
        no_integrations = True
    elif "--integrations" in sys.argv:
        try:
            idx = sys.argv.index("--integrations")
            integrations = sys.argv[idx + 1]
        except IndexError:
            print("❌ ERROR: --integrations requires a value (e.g., github,linear)")
            sys.exit(1)

    # Step 1: Check Claude CLI
    if not check_claude_cli():
        sys.exit(1)

    # Step 2: Build MCP URL
    url = build_mcp_url(integrations, no_integrations)
    print(f"\n🔗 MCP URL: {url}")

    # Step 3: Register MCP server
    if not register_mcp_server(url):
        sys.exit(1)

    # Step 4: Verify registration
    time.sleep(1)  # Give filesystem time to update
    verify_mcp_registration()

    # Step 5: Print next steps
    print_auth_instructions()
    print_success_summary(url)

    print("\n✅ Setup completed successfully!")
    print("   Run verify_connection.py after authenticating to test")


if __name__ == "__main__":
    main()
