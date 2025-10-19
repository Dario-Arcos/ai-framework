---
description: Detect and install missing project dependencies
allowed-tools: Read, Grep, Bash(*)
---

# Setup Dependencies

Intelligent dependency detection and installation through documentation analysis and code scanning.

## Step 1: Analyze Project Documentation

**Read and analyze these files in order:**

1. **README.md** — Extract requirements section
   - Look for "Requirements", "Prerequisites", "Dependencies" sections
   - Identify tools mentioned with version numbers
   - Note which are marked as "required", "essential", "optional"

2. **package.json** (if exists) — Extract npm dependencies
   - Read `dependencies` and `devDependencies`
   - Identify tools that need global installation (used in scripts)

3. **.specify/memory/project-context.md** (if exists) — Check documented stack
   - Extract critical dependencies listed
   - Note platform-specific requirements

**Output:** Summarize findings in a structured list:

```
Critical Tools:
- tool-name (purpose) [source: README.md]

Essential Tools:
- tool-name (purpose) [source: package.json]

Optional Tools:
- tool-name (purpose) [source: README.md]
```

## Step 2: Scan Codebase for Hidden Dependencies

**Use Grep to find tools called in code:**

1. **Python subprocess calls** — Find external tools called via subprocess:

   ```
   Grep for: subprocess\.(run|call|Popen)
   In: hooks/, commands/, scripts/
   Pattern: Look for first argument in list (the command being called)
   ```

2. **npx commands in configs** — Find npm packages executed with npx:

   ```
   Grep for: "npx"
   In: .claude/, template/.claude.template/
   Pattern: Extract package names after @ symbol
   ```

3. **Shell scripts** — Find commands called in .sh files:
   ```
   Grep for common tools: gh, git, jq, curl, wget
   In: scripts/, .specify/scripts/
   ```

**Output:** Add any NEW dependencies not found in Step 1 to the list:

```
Hidden Dependencies (found in code):
- tool-name (found in: file.py:line)
```

## Step 3: Classify and Map to Installers

**For each dependency identified, determine:**

1. **Installer:** Which package manager installs it?
   - Homebrew (brew) → macOS CLI tools (gh, terminal-notifier, jq)
   - npm → Node.js packages (global: npm install -g)
   - pip → Python packages (pip install or pip3 install)

2. **Platform:** Which platforms need it?
   - darwin (macOS only) → terminal-notifier
   - linux (Linux only) → apt/yum packages
   - all → gh, black, npm packages

3. **Priority:** How critical is it?
   - Critical → Framework won't work without it
   - Essential → Major features disabled without it
   - Optional → Nice-to-have enhancements

**Known Mappings:**

- `terminal-notifier` → brew (darwin only, optional)
- `gh` → brew (all platforms, essential)
- `black` / `ruff` / `autopep8` → pip (all platforms, optional)
- `jq` → brew (all platforms, optional)
- `prettier` → npm (all platforms, optional)

**Output:** Generate installation manifest:

```
Installation Plan:

Homebrew (macOS):
  essential: gh
  optional: terminal-notifier, jq

npm (Global):
  optional: prettier

pip (Python):
  optional: black, ruff
```

## Step 4: Check Installation Status

**For each tool in the manifest, check if already installed:**

Execute bash for EACH tool individually:

```bash
command -v tool-name
```

If command succeeds (exit code 0) → installed ✅
If command fails (exit code 1) → missing ❌

**Output:** Display status report:

```
Dependency Status:

✅ gh (installed)
❌ terminal-notifier (missing)
✅ black (installed)
❌ jq (missing)

Summary: 2 installed, 2 missing
```

If all installed → Stop here with success message.

## Step 5: User Confirmation

**Present installation plan to user:**

```
📦 Missing dependencies to install:

Homebrew:
  • terminal-notifier → Desktop notifications for completed tasks
  • jq → JSON processing in scripts

Total: 2 dependencies

Proceed with installation? (Y/n):
```

**Wait for user input.**

If user responds "n" or "N" → Show manual installation instructions and exit:

```
Cancelled. Install manually:

  macOS:
    brew install terminal-notifier jq

  Linux:
    # terminal-notifier not available on Linux
    apt install jq

  Python:
    pip install black ruff
```

If user responds "Y", "y", or just presses Enter → Continue to installation.

## Step 6: Execute Installation

**Group dependencies by package manager and install:**

### For Homebrew dependencies:

1. Check if brew is installed:

   ```bash
   command -v brew
   ```

2. If not installed → Display error:

   ```
   ❌ Homebrew not found

   Install Homebrew first:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   Then skip to next package manager.

3. If installed → Run installation:
   ```bash
   brew install tool1 tool2 tool3
   ```

### For npm dependencies:

1. Check if npm is installed:

   ```bash
   command -v npm
   ```

2. If not installed → Display error and skip:

   ```
   ❌ npm not found (comes with Node.js)

   Install Node.js first: https://nodejs.org/
   ```

3. If installed → Run installation:
   ```bash
   npm install -g package1 package2
   ```

### For pip dependencies:

1. Try pip3 first:

   ```bash
   command -v pip3
   ```

2. If not found, try pip:

   ```bash
   command -v pip
   ```

3. If neither found → Display error and skip:

   ```
   ❌ pip not found

   Install Python 3.8+: https://www.python.org/downloads/
   ```

4. If found → Run installation:
   ```bash
   pip3 install package1 package2
   # or
   pip install package1 package2
   ```

## Step 7: Verification

**After all installations, verify each tool:**

For each tool that was attempted:

```bash
command -v tool-name
```

**Display results:**

```
Installation Results:

✅ terminal-notifier
✅ jq
❌ some-tool (failed)

Summary: 2 succeeded, 1 failed
```

If all succeeded:

```
✅ All dependencies installed successfully

Framework features now fully enabled.
```

If some failed:

```
⚠️  Some installations failed

Successfully installed: terminal-notifier, jq
Failed: some-tool

Try manual installation for failed dependencies.
```

## Important Notes

- **No complex bash scripts** — Each bash command is simple and atomic
- **Read files first** — Analyze documentation before scanning code
- **One tool at a time** — Check installation status individually
- **User confirmation required** — Never install without asking
- **Graceful degradation** — Skip missing package managers, don't fail
- **Clear output** — Show what's happening at each step

## Example Flow

```
Step 1: Analyzing README.md...
Found: Git (critical), GitHub CLI (essential), terminal-notifier (optional)

Step 2: Scanning code for hidden dependencies...
Found in hooks/ccnotify.py: terminal-notifier

Step 3: Generating installation plan...
✅ Git (already installed)
❌ GitHub CLI (missing, installer: brew)
❌ terminal-notifier (missing, installer: brew)

Step 4: Checking status...
2 dependencies missing

Step 5: Confirm installation? Y

Step 6: Installing via Homebrew...
brew install gh terminal-notifier
✓ gh installed
✓ terminal-notifier installed

Step 7: Verification...
✅ All 2 dependencies installed successfully
```
