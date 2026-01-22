#!/bin/bash
# Extract all iteration outputs (compressed + uncompressed)
# Usage: ./extract-history.sh [dest_dir]

set -euo pipefail

OUTPUT_DIR="claude_output"
DEST="${1:-/tmp/ralph-history-$(date +%Y%m%d-%H%M%S)}"

mkdir -p "$DEST"

echo "Extracting to: $DEST"

# Decompress .gz files
for f in "$OUTPUT_DIR"/iteration_*.txt.gz; do
    [ -f "$f" ] || continue
    gzip -dc "$f" > "$DEST/$(basename "${f%.gz}")"
done

# Copy uncompressed files
for f in "$OUTPUT_DIR"/iteration_*.txt; do
    [ -f "$f" ] || continue
    cp "$f" "$DEST/"
done

COUNT=$(ls -1 "$DEST"/iteration_*.txt 2>/dev/null | wc -l | tr -d ' ')
SIZE=$(du -sh "$DEST" | cut -f1)

echo "Extracted: $COUNT files"
echo "Total size: $SIZE"
echo ""
echo "View all:"
echo "  cat $DEST/iteration_*.txt | less"
echo ""
echo "View specific:"
echo "  cat $DEST/iteration_005.txt"
