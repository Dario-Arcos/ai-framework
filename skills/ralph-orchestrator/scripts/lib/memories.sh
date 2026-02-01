#!/bin/bash
# Memories module: parsing and injection for structured guardrails

# Memory format detection
ralph_detect_memory_format() {
    local file="$1"
    [[ ! -f "$file" ]] && echo "none" && return

    if grep -q "^## Fixes\|^## Decisions\|^## Patterns" "$file" 2>/dev/null; then
        echo "structured"
    elif grep -q "^### Sign:" "$file" 2>/dev/null; then
        echo "legacy"
    else
        echo "empty"
    fi
}

# Count memories in file
ralph_count_memories() {
    local file="$1"
    [[ ! -f "$file" ]] && echo "0" && return

    local format
    format=$(ralph_detect_memory_format "$file")

    case "$format" in
        structured)
            grep -c "^### [a-z]*-[0-9]*-" "$file" 2>/dev/null || echo "0"
            ;;
        legacy)
            grep -c "^### Sign:" "$file" 2>/dev/null || echo "0"
            ;;
        *)
            echo "0"
            ;;
    esac
}

# Generate memory ID
ralph_generate_memory_id() {
    local type="$1"
    local timestamp
    local hex
    timestamp=$(date +%s)
    hex=$(printf '%04x' $((RANDOM % 65536)))
    echo "${type}-${timestamp}-${hex}"
}

# Add a memory to guardrails.md
ralph_add_memory() {
    local file="${1:-guardrails.md}"
    local type="$2"      # fix, decision, pattern
    local content="$3"
    local tags="$4"

    [[ ! -f "$file" ]] && return 1

    local id
    local date
    local section

    id=$(ralph_generate_memory_id "$type")
    date=$(date +%Y-%m-%d)

    case "$type" in
        fix) section="## Fixes" ;;
        decision) section="## Decisions" ;;
        pattern) section="## Patterns" ;;
        *) section="## Fixes" ;;
    esac

    # Find section and append memory
    local memory_block
    memory_block=$(cat <<EOF

### ${id}
> ${content}
<!-- tags: ${tags} | created: ${date} -->
EOF
)

    # Insert after section header
    if grep -q "^${section}$" "$file"; then
        sed -i.bak "/^${section}$/a\\
${memory_block}
" "$file" && rm -f "${file}.bak"
    fi
}

# Parse memories from file (returns JSON-like format for processing)
ralph_parse_memories() {
    local file="$1"
    local filter_type="${2:-}"
    local filter_tags="${3:-}"

    [[ ! -f "$file" ]] && return

    local format
    format=$(ralph_detect_memory_format "$file")

    [[ "$format" != "structured" ]] && return

    # Extract memory blocks
    awk -v ftype="$filter_type" '
    /^### [a-z]+-[0-9]+-[a-f0-9]+$/ {
        if (id != "") { print id "|" type "|" content "|" tags }
        id = $2
        split(id, parts, "-")
        type = parts[1]
        content = ""
        tags = ""
        next
    }
    /^> / {
        sub(/^> /, "")
        content = $0
        next
    }
    /^<!-- tags:/ {
        match($0, /tags: ([^|]+)/, t)
        tags = t[1]
        next
    }
    END {
        if (id != "") { print id "|" type "|" content "|" tags }
    }
    ' "$file" | while IFS='|' read -r id type content tags; do
        # Apply type filter
        if [[ -n "$filter_type" && "$type" != "$filter_type" ]]; then
            continue
        fi
        # Apply tag filter (any tag match)
        if [[ -n "$filter_tags" ]]; then
            local match=0
            IFS=',' read -ra FTAGS <<< "$filter_tags"
            for ftag in "${FTAGS[@]}"; do
                if [[ "$tags" == *"$ftag"* ]]; then
                    match=1
                    break
                fi
            done
            [[ $match -eq 0 ]] && continue
        fi
        echo "$id|$type|$content|$tags"
    done
}

# Get memory summary for context injection
ralph_get_memory_summary() {
    local file="$1"
    local budget="${2:-2000}"

    [[ ! -f "$file" ]] && return

    local format
    format=$(ralph_detect_memory_format "$file")

    case "$format" in
        structured)
            # Return raw file content up to budget (chars * 4 ~ tokens)
            local char_budget=$((budget * 4))
            head -c "$char_budget" "$file"
            ;;
        legacy)
            # Return as-is for legacy format
            local char_budget=$((budget * 4))
            head -c "$char_budget" "$file"
            ;;
        *)
            return
            ;;
    esac
}

# Validate memory format integrity
ralph_validate_memories() {
    local file="$1"
    local errors=0

    [[ ! -f "$file" ]] && return 0

    local format
    format=$(ralph_detect_memory_format "$file")

    [[ "$format" != "structured" ]] && return 0

    # Check for orphaned content (content without ID)
    if grep -q "^> " "$file"; then
        local orphans
        orphans=$(awk '/^### [a-z]+-[0-9]+-[a-f0-9]+$/{inmem=1;next} /^## /{inmem=0} /^> / && !inmem{print NR}' "$file")
        if [[ -n "$orphans" ]]; then
            ralph_log_warn "Orphaned memory content at lines: $orphans"
            ((errors++))
        fi
    fi

    # Check for duplicate IDs
    local dupes
    dupes=$(grep "^### [a-z]*-[0-9]*-" "$file" | sort | uniq -d)
    if [[ -n "$dupes" ]]; then
        ralph_log_warn "Duplicate memory IDs: $dupes"
        ((errors++))
    fi

    return $errors
}
