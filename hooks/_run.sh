#!/bin/bash
# Cross-platform Python runner for hooks
[ -f "$1" ] || exit 0
if python3 --version >/dev/null 2>&1; then
  exec python3 -B "$@"
else
  exec python -B "$@"
fi
