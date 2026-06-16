#!/bin/bash
# Export Apple Notes modified in the last 24 hours into one daily YYYY-MM-DD.md file.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
EXPORT_DIR="/Users/zhaowenlong/workspace/myblog/_posts/new-apple-notes"
SCRIPT="$DIR/export-notes.applescript"
DATE_STR="$(date +%Y-%m-%d)"
FILE_PATH="$EXPORT_DIR/$DATE_STR.md"

COUNT=$(osascript "$SCRIPT" "$FILE_PATH")

if [[ "$COUNT" -eq 0 ]]; then
    echo "No notes modified in the last 24 hours."
else
    python3 "$DIR/clean-export.py" "$FILE_PATH"
    echo "Exported $COUNT note(s) to $FILE_PATH"
fi
