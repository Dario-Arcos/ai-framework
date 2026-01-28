#!/bin/bash
# Ralph Memories CLI
# Manage persistent learnings in memories.md
#
# Usage:
#   ./memories.sh add pattern "Pattern description" --tags tag1,tag2
#   ./memories.sh add decision "Decision description" --reason "Reasoning" --tags tag1
#   ./memories.sh add fix "Fix description" --tags tag1
#   ./memories.sh search "query"
#   ./memories.sh list [--type pattern|decision|fix] [--limit N]

set -euo pipefail

MEMORIES_FILE="${MEMORIES_FILE:-memories.md}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Generate memory ID: mem-[timestamp]-[4char-hash]
generate_id() {
    local content="$1"
    local timestamp=$(date +%s)
    local hash=$(echo "$content" | md5 -q 2>/dev/null || echo "$content" | md5sum | cut -c1-4)
    hash="${hash:0:4}"
    echo "mem-${timestamp}-${hash}"
}

# Add a memory
cmd_add() {
    local type="$1"
    local content="$2"
    shift 2

    local tags=""
    local reason=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --tags) tags="$2"; shift 2 ;;
            --reason) reason="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    [ -z "$tags" ] && tags="general"

    local id=$(generate_id "$content")
    local date=$(date +%Y-%m-%d)

    # Build entry
    local entry="### $id"
    entry+="\n> $content"
    [ -n "$reason" ] && entry+="\n> Reason: $reason"
    entry+="\n<!-- tags: $tags | created: $date -->"

    # Determine section
    local section
    case "$type" in
        pattern) section="## Patterns" ;;
        decision) section="## Decisions" ;;
        fix) section="## Fixes" ;;
        context) section="## Context" ;;
        *) echo -e "${RED}Unknown type: $type${NC}"; exit 1 ;;
    esac

    # Check memories.md exists
    if [ ! -f "$MEMORIES_FILE" ]; then
        echo -e "${RED}Error: $MEMORIES_FILE not found${NC}"
        exit 1
    fi

    # Insert after section header using temp file
    awk -v section="$section" -v entry="$entry" '
        $0 == section { print; print ""; print entry; next }
        { print }
    ' "$MEMORIES_FILE" > "${MEMORIES_FILE}.tmp"
    mv "${MEMORIES_FILE}.tmp" "$MEMORIES_FILE"

    echo -e "${GREEN}Memory added:${NC} $id"
    echo -e "  Type: $type"
    echo -e "  Tags: $tags"
}

# Search memories
cmd_search() {
    local query="$1"

    if [ ! -f "$MEMORIES_FILE" ]; then
        echo -e "${RED}Error: $MEMORIES_FILE not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}Searching for:${NC} $query"
    echo ""

    local results=$(grep -i "$query" "$MEMORIES_FILE" -A2 -B1 2>/dev/null || true)
    if [ -n "$results" ]; then
        echo "$results"
    else
        echo -e "${YELLOW}No matches found${NC}"
    fi
}

# List memories
cmd_list() {
    local type=""
    local limit=10

    while [ $# -gt 0 ]; do
        case "$1" in
            --type) type="$2"; shift 2 ;;
            --limit) limit="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    if [ ! -f "$MEMORIES_FILE" ]; then
        echo -e "${RED}Error: $MEMORIES_FILE not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}Recent memories:${NC}"
    echo ""

    if [ -n "$type" ]; then
        grep "^### mem-" "$MEMORIES_FILE" -A1 | grep -i "$type" -B1 | head -n "$limit"
    else
        grep "^### mem-" "$MEMORIES_FILE" | head -n "$limit"
    fi
}

# Show usage
cmd_help() {
    echo "Ralph Memories CLI"
    echo ""
    echo "Usage:"
    echo "  ./memories.sh add <type> \"<content>\" [--tags tags] [--reason reason]"
    echo "  ./memories.sh search \"<query>\""
    echo "  ./memories.sh list [--type <type>] [--limit <n>]"
    echo ""
    echo "Types:"
    echo "  pattern   - Recurring architecture approaches"
    echo "  decision  - Tech choices with reasoning"
    echo "  fix       - Solutions to persistent problems"
    echo "  context   - Confession records"
    echo ""
    echo "Examples:"
    echo "  ./memories.sh add pattern \"All APIs return Result<T>\" --tags api,error-handling"
    echo "  ./memories.sh add decision \"Chose PostgreSQL\" --reason \"ACID compliance\" --tags db"
    echo "  ./memories.sh search \"database\""
    echo "  ./memories.sh list --type pattern --limit 5"
}

# Main dispatch
case "${1:-help}" in
    add) shift; cmd_add "$@" ;;
    search) shift; cmd_search "$@" ;;
    list) shift; cmd_list "$@" ;;
    help|--help|-h) cmd_help ;;
    *) echo -e "${RED}Unknown command: $1${NC}"; cmd_help; exit 1 ;;
esac
