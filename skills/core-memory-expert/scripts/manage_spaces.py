#!/usr/bin/env python3
"""
Core Spaces Management Tool

CRUD operations for RedPlanet Core Spaces via REST API.
Spaces organize memory into logical containers (projects, contexts, etc.).

Usage:
    python3 manage_spaces.py list
    python3 manage_spaces.py create <name> [--description TEXT]
    python3 manage_spaces.py get <space-id>
    python3 manage_spaces.py update <space-id> --name NAME [--description TEXT]
    python3 manage_spaces.py delete <space-id>
    python3 manage_spaces.py assign <space-id> --statements stmt1,stmt2,stmt3

Examples:
    python3 manage_spaces.py list
    python3 manage_spaces.py create "Work Project" --description "Professional context"
    python3 manage_spaces.py get space-work
    python3 manage_spaces.py assign space-work --statements stmt_123,stmt_456
    python3 manage_spaces.py delete space-old

Environment Variables:
    CORE_API_KEY: API key for authentication (required)
    CORE_BASE_URL: Base URL (default: https://core.heysol.ai)

Stdlib only - no external dependencies required.
"""

import sys
import os
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def get_config():
    """Load configuration from environment."""
    api_key = os.getenv("CORE_API_KEY")
    base_url = os.getenv("CORE_BASE_URL", "https://core.heysol.ai")

    if not api_key:
        print("❌ ERROR: CORE_API_KEY environment variable not set")
        print("   Export your API key: export CORE_API_KEY='your-key-here'")
        print("   Get API key from: https://core.heysol.ai → Settings → API Keys")
        sys.exit(1)

    return {
        "api_key": api_key,
        "base_url": base_url.rstrip("/")
    }


def make_request(method, endpoint, config, data=None):
    """
    Make HTTP request to Core API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path
        config: Configuration dict with api_key and base_url
        data: Optional request body (dict)

    Returns:
        tuple: (success: bool, response_data: dict or None, error: str or None)
    """
    url = f"{config['base_url']}{endpoint}"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    request_data = None
    if data:
        request_data = json.dumps(data).encode('utf-8')

    try:
        req = Request(url, data=request_data, headers=headers, method=method)
        # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
        # Note: URL is constructed from user-controlled env var (CORE_BASE_URL) + hardcoded endpoint paths.
        # Risk is acceptable in this context (local development tool, user controls their own environment).
        with urlopen(req, timeout=30) as response:
            if response.status == 204:  # No Content
                return True, None, None

            response_data = json.loads(response.read().decode('utf-8'))
            return True, response_data, None

    except HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            error_msg = error_data.get('message', str(e))
        except:
            error_msg = str(e)
        return False, None, f"HTTP {e.code}: {error_msg}"

    except URLError as e:
        return False, None, f"Network error: {e.reason}"

    except Exception as e:
        return False, None, f"Request failed: {e}"


def list_spaces(config):
    """List all spaces."""
    print("📂 Listing spaces...\n")

    success, data, error = make_request("GET", "/api/v1/spaces", config)

    if not success:
        print(f"❌ Failed to list spaces: {error}")
        return False

    spaces = data.get("spaces", [])
    total = data.get("total", 0)

    if total == 0:
        print("No spaces found.")
        print("\nCreate your first space:")
        print('  python3 manage_spaces.py create "My First Space"')
        return True

    print(f"Found {total} space(s):\n")
    print(f"{'ID':<20} {'Name':<30} {'Statements':<12} {'Created'}")
    print("-" * 80)

    for space in spaces:
        space_id = space.get("id", "")
        name = space.get("name", "")
        count = space.get("statementCount", 0)
        created = space.get("createdAt", "")[:10]  # YYYY-MM-DD

        print(f"{space_id:<20} {name:<30} {count:<12} {created}")

    print()
    return True


def create_space(config, name, description=""):
    """Create new space."""
    print(f"➕ Creating space: {name}\n")

    payload = {"name": name}
    if description:
        payload["description"] = description

    success, data, error = make_request("POST", "/api/v1/spaces", config, payload)

    if not success:
        print(f"❌ Failed to create space: {error}")
        return False

    space_id = data.get("id", "")
    created_at = data.get("createdAt", "")

    print("✅ Space created successfully!")
    print(f"\nID: {space_id}")
    print(f"Name: {name}")
    if description:
        print(f"Description: {description}")
    print(f"Created: {created_at}")
    print()
    return True


def get_space(config, space_id):
    """Get space details."""
    print(f"🔍 Fetching space: {space_id}\n")

    success, data, error = make_request("GET", f"/api/v1/spaces/{space_id}", config)

    if not success:
        print(f"❌ Failed to get space: {error}")
        return False

    print("✅ Space details:\n")
    print(f"ID: {data.get('id', '')}")
    print(f"Name: {data.get('name', '')}")
    print(f"Description: {data.get('description', '(none)')}")
    print(f"Statements: {data.get('statementCount', 0)}")
    print(f"Created: {data.get('createdAt', '')}")
    print(f"Updated: {data.get('updatedAt', '')}")

    metadata = data.get("metadata", {})
    if metadata:
        print("\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

    print()
    return True


def update_space(config, space_id, name=None, description=None):
    """Update space metadata."""
    print(f"✏️  Updating space: {space_id}\n")

    payload = {}
    if name:
        payload["name"] = name
    if description is not None:  # Allow empty string
        payload["description"] = description

    if not payload:
        print("❌ No updates provided (use --name or --description)")
        return False

    success, data, error = make_request("PUT", f"/api/v1/spaces/{space_id}", config, payload)

    if not success:
        print(f"❌ Failed to update space: {error}")
        return False

    print("✅ Space updated successfully!")
    print(f"\nID: {data.get('id', '')}")
    if name:
        print(f"New name: {name}")
    if description is not None:
        print(f"New description: {description}")
    print(f"Updated: {data.get('updatedAt', '')}")
    print()
    return True


def delete_space(config, space_id):
    """Delete space."""
    print(f"🗑️  Deleting space: {space_id}")
    print("\n⚠️  WARNING: This will delete the space.")
    print("   Statements may become orphaned unless reassigned first.")
    print()

    confirm = input("Type 'yes' to confirm deletion: ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled")
        return False

    success, data, error = make_request("DELETE", f"/api/v1/spaces/{space_id}", config)

    if not success:
        print(f"❌ Failed to delete space: {error}")
        return False

    print("✅ Space deleted successfully")
    print()
    return True


def assign_statements(config, space_id, statement_ids):
    """Assign statements to space (bulk operation)."""
    print(f"📌 Assigning {len(statement_ids)} statement(s) to space: {space_id}\n")

    payload = {
        "intent": "assign_statements",
        "spaceId": space_id,
        "statementIds": statement_ids
    }

    success, data, error = make_request("PUT", "/api/v1/spaces", config, payload)

    if not success:
        print(f"❌ Failed to assign statements: {error}")
        return False

    modified = data.get("modified", 0)
    message = data.get("message", "")

    print("✅ Statements assigned successfully!")
    print(f"\nModified: {modified} statement(s)")
    print(f"Message: {message}")
    print()
    return True


def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python3 manage_spaces.py <command> [arguments]")
    print()
    print("Commands:")
    print("  list                           List all spaces")
    print("  create <name> [--description]  Create new space")
    print("  get <space-id>                 Get space details")
    print("  update <space-id> [--name] [--description]  Update space")
    print("  delete <space-id>              Delete space")
    print("  assign <space-id> --statements <ids>  Assign statements to space")
    print()
    print("Examples:")
    print('  python3 manage_spaces.py create "Work Project" --description "Professional context"')
    print("  python3 manage_spaces.py list")
    print("  python3 manage_spaces.py get space-work")
    print("  python3 manage_spaces.py assign space-work --statements stmt_1,stmt_2,stmt_3")
    print()
    print("Environment Variables:")
    print("  CORE_API_KEY    API key for authentication (required)")
    print("  CORE_BASE_URL   Base URL (default: https://core.heysol.ai)")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    # Special commands that don't need API key
    if command in ["help", "--help", "-h"]:
        print_usage()
        sys.exit(0)

    # Get configuration for all other commands
    config = get_config()

    # Route commands
    if command == "list":
        success = list_spaces(config)

    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ ERROR: Missing space name")
            print('Usage: python3 manage_spaces.py create "Space Name" [--description TEXT]')
            sys.exit(1)

        name = sys.argv[2]
        description = ""

        # Parse optional description
        if "--description" in sys.argv:
            idx = sys.argv.index("--description")
            if idx + 1 < len(sys.argv):
                description = sys.argv[idx + 1]

        success = create_space(config, name, description)

    elif command == "get":
        if len(sys.argv) < 3:
            print("❌ ERROR: Missing space ID")
            print("Usage: python3 manage_spaces.py get <space-id>")
            sys.exit(1)

        space_id = sys.argv[2]
        success = get_space(config, space_id)

    elif command == "update":
        if len(sys.argv) < 3:
            print("❌ ERROR: Missing space ID")
            print("Usage: python3 manage_spaces.py update <space-id> [--name NAME] [--description TEXT]")
            sys.exit(1)

        space_id = sys.argv[2]
        name = None
        description = None

        # Parse options
        if "--name" in sys.argv:
            idx = sys.argv.index("--name")
            if idx + 1 < len(sys.argv):
                name = sys.argv[idx + 1]

        if "--description" in sys.argv:
            idx = sys.argv.index("--description")
            if idx + 1 < len(sys.argv):
                description = sys.argv[idx + 1]

        success = update_space(config, space_id, name, description)

    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ ERROR: Missing space ID")
            print("Usage: python3 manage_spaces.py delete <space-id>")
            sys.exit(1)

        space_id = sys.argv[2]
        success = delete_space(config, space_id)

    elif command == "assign":
        if len(sys.argv) < 3:
            print("❌ ERROR: Missing space ID")
            print("Usage: python3 manage_spaces.py assign <space-id> --statements <comma-separated-ids>")
            sys.exit(1)

        space_id = sys.argv[2]

        if "--statements" not in sys.argv:
            print("❌ ERROR: Missing --statements argument")
            print("Usage: python3 manage_spaces.py assign <space-id> --statements stmt1,stmt2,stmt3")
            sys.exit(1)

        idx = sys.argv.index("--statements")
        if idx + 1 >= len(sys.argv):
            print("❌ ERROR: No statement IDs provided")
            sys.exit(1)

        statement_ids_str = sys.argv[idx + 1]
        statement_ids = [s.strip() for s in statement_ids_str.split(",") if s.strip()]

        if not statement_ids:
            print("❌ ERROR: No valid statement IDs provided")
            sys.exit(1)

        success = assign_statements(config, space_id, statement_ids)

    else:
        print(f"❌ ERROR: Unknown command: {command}")
        print()
        print_usage()
        sys.exit(1)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
