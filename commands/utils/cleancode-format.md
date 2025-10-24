---
description: Format code files on-demand using appropriate formatters (prettier, black, shfmt)
argument-hint: "[file paths | directory | leave empty for git modified files]"
allowed-tools: Bash, Read, Glob
---

# Clean Code Format

**On-demand code formatting:** $ARGUMENTS

## Formatter Mapping

```
JavaScript/TypeScript: npx prettier --write (.js, .jsx, .ts, .tsx)
JSON/YAML/Markdown:    npx prettier --write (.json, .yml, .yaml, .md)
Python:                black --quiet (.py)
Shell:                 shfmt -w (.sh, .bash)
```

## Execution Protocol

### Step 1: Parse Input and Determine Target Files

**Parse $ARGUMENTS:**

- **Empty args**: Use git modified files (`git diff --name-only`)
- **File path(s)**: Process specific files (e.g., `src/auth.py src/utils.js`)
- **Directory**: Find all supported files recursively in directory (e.g., `src/`)

**Display**: "🔍 Analyzing files to format..."

### Step 2: Validate Targets

**For each target file:**

1. Execute: `test -f <file_path>` to verify file exists
2. Get file extension: `basename` + extract suffix
3. Match extension against formatter mapping (Step 3)
4. If unsupported extension: Skip silently, continue with next file
5. Build list of valid files to format

**Display**: "📋 Found <N> files to format: <file1, file2, ...>"

**If no valid files**: Show "ℹ️ No supported files found" and exit

### Step 3: Check Formatter Availability

**For each unique formatter required:**

Execute: `which <formatter_command>` (e.g., `which npx`, `which black`)

**If formatter not found**, display installation instructions:

```
⚠️ Formatter '<tool>' not installed

Installation commands:
- npx:   Comes with Node.js (https://nodejs.org)
- black: pip install black
- shfmt: brew install shfmt (macOS) | go install mvdan.cc/sh/v3/cmd/shfmt@latest
```

**Then exit** (do not proceed without required formatters)

### Step 4: Execute Formatting

**For each valid file:**

1. Determine formatter command from mapping:
   - `.js/.jsx/.ts/.tsx/.json/.md/.yml/.yaml` → `npx prettier --write <file>`
   - `.py` → `black --quiet <file>`
   - `.sh/.bash` → `shfmt -w <file>`

2. Execute: Formatter command with 10-second timeout

3. Capture result:
   - **Success (exit 0)**: Display "✅ <filename> formatted"
   - **Error (exit ≠ 0)**: Display "❌ <filename> failed: <error_output>"
   - **Timeout (>10s)**: Display "⏱️ <filename> timeout (>10s)"

4. Continue with next file (don't stop on individual failures)

### Step 5: Report Summary

**Display final results:**

```
✅ Formatting completed

Success: <N> files formatted
Errors:  <M> files failed
Skipped: <K> unsupported files

Files formatted: <list>
```

## Error Handling

- **Not a git repository** (when using git modified files): Show "⚠️ Not a git repo, specify files explicitly"
- **No files to format**: Show "ℹ️ No supported files found"
- **Formatter not installed**: Show installation instructions and exit
- **Individual file error**: Report error but continue with remaining files
- **Timeout**: Report timeout but continue with remaining files

## Important Notes

- Formatters must be pre-installed (no auto-installation)
- Formatting is idempotent (safe to run multiple times)
- Preserves file content and logic (only style changes)
- Works with staged and unstaged files
- Silent for unsupported file types
- Each formatter runs independently (one failure doesn't block others)

## Usage Examples

```bash
# Format all git modified files
/ai-framework:utils:cleancode-format

# Format specific files
/ai-framework:utils:cleancode-format src/auth.py src/utils.ts

# Format entire directory
/ai-framework:utils:cleancode-format src/

# Format multiple patterns
/ai-framework:utils:cleancode-format src/ tests/unit/
```
