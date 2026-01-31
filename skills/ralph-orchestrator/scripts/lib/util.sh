#!/bin/bash
# Ralph Loop - Utility Functions
# Common helpers used across modules

[[ -n "${_RALPH_UTIL_LOADED:-}" ]] && return 0
_RALPH_UTIL_LOADED=1

# ─────────────────────────────────────────────────────────────────
# ATOMIC FILE OPERATIONS
# ─────────────────────────────────────────────────────────────────

# Write content to file atomically (prevents corruption on crash)
ralph_atomic_write() {
    local file="$1"
    local content="$2"
    local tmp="${file}.tmp.$$"

    echo "$content" > "$tmp"
    mv "$tmp" "$file"
}

# ─────────────────────────────────────────────────────────────────
# LOG ROTATION
# ─────────────────────────────────────────────────────────────────

# Rotate logs if they exceed max size
ralph_rotate_logs() {
    local logs_dir="${1:-logs}"
    local max_size="${2:-$((10 * 1024 * 1024))}"  # 10MB default
    local max_files="${3:-20}"

    # Rotate main logs if too large
    for logfile in "${logs_dir}/iteration.log" "errors.log"; do
        if [[ -f "$logfile" ]]; then
            local size
            size=$(stat -f%z "$logfile" 2>/dev/null || stat -c%s "$logfile" 2>/dev/null || echo "0")
            if [[ "$size" -gt "$max_size" ]]; then
                mv "$logfile" "${logfile}.old"
                touch "$logfile"
                echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Log rotated (was ${size} bytes)" >> "$logfile"
            fi
        fi
    done

    # Clean old iteration output files (keep last N)
    if ls "${logs_dir}"/iteration-*-output.log 1>/dev/null 2>&1; then
        ls -t "${logs_dir}"/iteration-*-output.log 2>/dev/null | tail -n +$((max_files + 1)) | xargs rm -f 2>/dev/null || true
    fi
}

# ─────────────────────────────────────────────────────────────────
# TIMESTAMP HELPERS
# ─────────────────────────────────────────────────────────────────

ralph_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# ─────────────────────────────────────────────────────────────────
# FILE HELPERS
# ─────────────────────────────────────────────────────────────────

ralph_ensure_dir() {
    local dir="$1"
    [[ -d "$dir" ]] || mkdir -p "$dir"
}
