---
name: git-pullrequest
allowed-tools: Bash(git *), Bash(gh *), Task, AskUserQuestion, Skill
description: Create PR with intelligent pre-review using Contextual Observations
---

# Pull Request v2.0

Automated workflow to create PR with quality gate based on contextual observations.

**Input**: `$ARGUMENTS` = target branch (e.g., "main")

---

## PHASE 1: Validation + Context

### Step 1.1: Validate and Extract Metadata

Execute in bash (single consolidated block):

```bash
#!/bin/bash
set -e

# Parse target branch
target_branch="$ARGUMENTS"
target_branch=$(echo "$target_branch" | xargs)

# Validations
if [ -z "$target_branch" ]; then
  echo "❌ Error: No target branch specified"
  echo "   Usage: /git-pullrequest main"
  exit 1
fi

if ! echo "$target_branch" | grep -Eq '^[a-zA-Z0-9/_-]+$'; then
  echo "❌ Error: Invalid branch name format"
  exit 1
fi

if echo "$target_branch" | grep -Eq '^--'; then
  echo "❌ Error: Branch name cannot start with --"
  exit 1
fi

# Fetch and validate target branch exists
echo "🔍 Validating target branch..."
git fetch origin --quiet

if ! git rev-parse --verify "origin/$target_branch" >/dev/null 2>&1; then
  echo "❌ Error: Branch origin/$target_branch does not exist"
  exit 1
fi

# Count commits
commit_count=$(git rev-list --count "origin/$target_branch..HEAD" --)

if [ "$commit_count" -eq 0 ]; then
  echo "❌ Error: No commits to create PR"
  exit 1
fi

# Extract metadata
current_branch=$(git branch --show-current)

echo ""
echo "📊 PR Context:"
echo "   From: $current_branch"
echo "   To: $target_branch"
echo "   Commits: $commit_count"
echo ""

# Get commit list
echo "Commits to include:"
git log --pretty=format:'  %h %s' "origin/$target_branch..HEAD" --
echo ""
echo ""

# Get first commit for format detection
first_commit=$(git log --pretty=format:'%s' "origin/$target_branch..HEAD" -- | head -1)

# Detect format (corporate vs conventional)
if echo "$first_commit" | grep -Eq '^[a-z]+\|[A-Z]+-[0-9]+\|[0-9]{8}\|'; then
  commit_format="corporate"
  primary_type=$(echo "$first_commit" | cut -d'|' -f1)
else
  commit_format="conventional"
  primary_type=$(echo "$first_commit" | grep -oE '^[a-z]+' | head -1)
  if [ -z "$primary_type" ]; then
    primary_type="feat"
  fi
fi

# Get statistics
stats=$(git diff --shortstat "origin/$target_branch..HEAD" --)

if [ -z "$stats" ]; then
  files_changed=0
  additions=0
  deletions=0
else
  files_changed=$(echo "$stats" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo "0")
  additions=$(echo "$stats" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
  deletions=$(echo "$stats" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")
fi

delta_loc=$((additions - deletions))

echo "📈 Statistics:"
echo "   Files changed: $files_changed"
echo "   Lines: +$additions -$deletions (Δ$delta_loc)"
echo "   Format: $commit_format"
echo "   Type: $primary_type"
echo ""

# Check for breaking changes
breaking=$(git log --pretty=format:'%B' "origin/$target_branch..HEAD" -- | grep -iE 'BREAKING' || echo "")
```

**Store in model context (no git config):**
- `target_branch`, `current_branch`, `commit_count`
- `first_commit`, `commit_format`, `primary_type`
- `files_changed`, `additions`, `deletions`, `delta_loc`
- `breaking` (if any)

**All commits from current branch to target will be included in PR.**

---

## PHASE 2: Review + Decision (Loop)

### Step 2.1: Invoke requesting-code-review Skill

Load the skill:

```
Skill: requesting-code-review
```

Prepare context for code-reviewer:

```
WHAT_WAS_IMPLEMENTED: "{commit_count} commits for {primary_type}: {commit_summary}"
PLAN_OR_REQUIREMENTS: "Pre-PR quality gate for merge to {target_branch}"
BASE_SHA: "origin/{target_branch}"
HEAD_SHA: "HEAD"
DESCRIPTION: "PR validation - {files_changed} files, ΔLOC={delta_loc}"
```

Dispatch code-reviewer subagent using Task tool:

```
subagent_type: code-reviewer
description: "Pre-PR Review: {target_branch}"
prompt: [Use template from skills/requesting-code-review/code-reviewer.md with filled placeholders]
```

### Step 2.2: Generate Contextual Observations

**A) Transform code-reviewer output**

Map severity:
- Critical (Must Fix) → 🔴 Requiere
- Important (Should Fix) → ⚠️ Atención
- Minor (Nice to Have) → 💡 Sugerencia
- No issues → ✅ OK

**B) Auto-detect additional observations**

Execute bash to detect:

```bash
#!/bin/bash

# 1. Test Coverage
test_files=$(git diff --name-only "origin/$target_branch..HEAD" -- | grep -E '(test|spec)\.' | wc -l | tr -d ' ')
src_files=$(git diff --name-only "origin/$target_branch..HEAD" -- | grep -vE '(test|spec)\.' | grep -E '\.(ts|js|py|go|rs)$' | wc -l | tr -d ' ')

if [ "$src_files" -gt 0 ] && [ "$test_files" -eq 0 ]; then
  obs_tests_status="⚠️"
  obs_tests_detail="$src_files archivos src modificados, 0 tests"
else
  obs_tests_status="✅"
  obs_tests_detail="$test_files tests modificados"
fi

# 2. Complexity Budget
if [ "$delta_loc" -le 80 ]; then
  size="S"; budget=80
elif [ "$delta_loc" -le 250 ]; then
  size="M"; budget=250
elif [ "$delta_loc" -le 600 ]; then
  size="L"; budget=600
else
  size="XL"; budget=1500
fi

if [ "$delta_loc" -gt "$budget" ]; then
  obs_complexity_status="⚠️"
else
  obs_complexity_status="✅"
fi

# 3. Secrets Detection
if git diff "origin/$target_branch..HEAD" -- | grep -iE '(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY|sk-|pk_|ghp_)' >/dev/null 2>&1; then
  obs_secrets_status="🔴"
else
  obs_secrets_status="✅"
fi

# 4. Public API Changes
if git diff --name-only "origin/$target_branch..HEAD" -- | grep -E '(api/|routes/|endpoints/)' >/dev/null 2>&1; then
  obs_api_status="⚠️"
  obs_api_files=$(git diff --name-only "origin/$target_branch..HEAD" -- | grep -E '(api/|routes/|endpoints/)' | wc -l | tr -d ' ')
else
  obs_api_status="✅"
  obs_api_files=0
fi

# 5. Breaking Changes
if [ -n "$breaking" ]; then
  obs_breaking_status="⚠️"
else
  obs_breaking_status="✅"
fi

echo "Observations detected:"
echo "  Tests: $obs_tests_status"
echo "  Complexity: $obs_complexity_status (Δ$delta_loc, budget $size: ≤$budget)"
echo "  Secrets: $obs_secrets_status"
echo "  API: $obs_api_status"
echo "  Breaking: $obs_breaking_status"
```

Store these variables for Step 2.3.

### Step 2.3: Present Observations

Construct and present observations to user:

```markdown
## Observaciones Pre-PR

### Complejidad [$obs_complexity_status]
ΔLOC = +$delta_loc (budget $size: ≤$budget)

### Tests [$obs_tests_status]
$obs_tests_detail
{IF ⚠️: Add "Por qué importa: Cambios sin tests aumentan riesgo de regresión"}

### Secrets [$obs_secrets_status]
{IF ✅: "No se detectaron patrones de secrets"}
{IF 🔴: Full context with Detectado/Por qué importa/Verificar}

### API Pública [$obs_api_status]
{IF ✅: "Sin cambios en API"}
{IF ⚠️: "$obs_api_files archivos API modificados" + context}

### Breaking Changes [$obs_breaking_status]
{IF ✅: "Sin breaking changes detectados"}
{IF ⚠️: Full context}

### Code Review [status from code-reviewer]
{Summary of code-reviewer findings: Critical/Important/Minor count}
**Assessment:** {code-reviewer assessment}

---

**Resumen:** {count_attention} observaciones requieren atención, {count_ok} OK.
```

**Calculate counters:**
```bash
count_ok=0
count_attention=0

for status in "$obs_complexity_status" "$obs_tests_status" "$obs_secrets_status" "$obs_api_status" "$obs_breaking_status"; do
  if [ "$status" = "✅" ]; then
    count_ok=$((count_ok + 1))
  else
    count_attention=$((count_attention + 1))
  fi
done

# Add code-reviewer findings to counts
# (Parse code-reviewer output and add to count_attention if Critical/Important exist)
```

**Format rules:**
- ✅ OK items: Single line, no "Por qué importa"
- ⚠️/🔴 Attention items: Full context with Detectado/Por qué importa/Verificar

### Step 2.4: User Decision

Use AskUserQuestion:

```
Question: "Observaciones completadas. ¿Cómo proceder?"

Options:
A) "Crear PR"
   Description: "Continuar con push y creación de PR. Observaciones se documentan en PR body."

B) "Fix automático"
   Description: "Subagent arregla todos los issues, luego re-review automático."

C) "Cancelar"
   Description: "Cancelar workflow. Arreglar manualmente y re-ejecutar después."
```

### Step 2.5: Handle User Choice

**If A (Crear PR):**
→ Proceed to PHASE 3

**If C (Cancelar):**
```bash
echo "✅ Workflow cancelado"
echo "   Branch actual: $(git branch --show-current)"
echo "   Para re-ejecutar: /git-pullrequest $target_branch"
exit 0
```

**If B (Fix automático):**

1. Load skill receiving-code-review:
```
Skill: receiving-code-review
```

2. Dispatch ONE general-purpose subagent:

```
subagent_type: general-purpose
description: "Fix pre-PR review findings"
prompt: """
Fix the following issues found in pre-PR review:

**Issues to fix:**
{formatted_list_of_issues_with_file_line_and_suggestions}

**Instructions (following receiving-code-review skill):**
1. Read each file to understand full context
2. Apply fixes in order: Critical → Important → Minor
3. Verify each fix doesn't break existing functionality
4. Run tests if they exist
5. Commit all fixes together: "fix: address pre-PR review findings"

**Report back:**
- Files modified
- Fixes applied
- Test results (if applicable)
- Any issues encountered or push-backs (with technical reasoning)
"""
```

3. AFTER fix completes → AUTOMATIC re-review:
   - Return to Step 2.1 (no user question)
   - Re-run code-reviewer subagent
   - Show new observations
   - Return to Step 2.4 (decision)

**Loop guarantee:** User can always exit via A or C.

---

## PHASE 3: Create PR

### Step 3.1: Push Branch

Execute in bash (uses variables from Phase 1):

```bash
#!/bin/bash
set -e

# Variables from Phase 1 context (already in scope)
# current_branch, target_branch, first_commit

echo "🚀 Preparing to push..."

# Check if current branch is protected
protected_branches="main|master|develop|staging|production"
if echo "$current_branch" | grep -Eq "^($protected_branches)$"; then
  echo "⚠️  Current branch is protected: $current_branch"

  # Generate temporary branch name
  timestamp=$(date +%Y%m%d%H%M%S)
  slug=$(echo "$first_commit" | tr '[:upper:]' '[:lower:]' | \
         sed 's/[^a-z0-9 ]/-/g' | awk '{for(i=1;i<=4 && i<=NF;i++) printf "%s-",$i}' | \
         sed 's/-$//' | cut -c1-30 | sed 's/-$//')
  slug="${slug:-feature}"

  temp_branch="pr/${slug}-${timestamp}"

  echo "   Creating temporary branch: $temp_branch"

  # Validate branch doesn't exist
  if git show-ref --verify --quiet "refs/heads/$temp_branch"; then
    echo "❌ Error: Branch $temp_branch already exists"
    exit 1
  fi

  # Create and push
  git checkout -b "$temp_branch"
  git push origin "$temp_branch" --set-upstream

  branch_to_pr="$temp_branch"
else
  # Push current branch
  branch_to_pr="$current_branch"

  echo "   Pushing branch: $branch_to_pr"

  # Check if has upstream
  if ! git rev-parse --abbrev-ref "$branch_to_pr@{upstream}" >/dev/null 2>&1; then
    git push origin "$branch_to_pr" --set-upstream
  else
    git push origin "$branch_to_pr"
  fi
fi

echo "✅ Branch pushed: $branch_to_pr"
```

### Step 3.2: Generate PR Body

Construct PR body with observations:

```markdown
## Summary

{primary_type} changes affecting **{files_changed}** files (Δ{delta_loc} LOC).

## Changes ({commit_count} commits)

{commit_list_formatted}

## Pre-PR Observations

{formatted_observations_from_step_2_3}

### Quality Gate Summary
- ✅ OK: {count_ok}
- ⚠️ Atención: {count_attention}
- 🔴 Requiere: {count_required}

## Test Plan

{test_items_based_on_primary_type}

{breaking_changes_section_if_applicable}
```

**Test items generated based on `primary_type`:**
- `feat` → Nueva funcionalidad probada, Tests agregados, Docs actualizada
- `fix` → Bug reproducido, Tests de regresión, Staging verificado
- `refactor` → Tests existentes pasan, Funcionalidad equivalente
- `default` → Cambios verificados, Build exitoso

### Step 3.3: Create PR with gh CLI

Execute in bash (uses variables from previous steps):

```bash
#!/bin/bash
set -e

# Variables in scope: first_commit, target_branch, branch_to_pr,
# commit_count, files_changed, additions, deletions, count_attention, count_ok

# Generate PR title (preserve format)
pr_title="$first_commit"

# Create temp file with body
temp_file=$(mktemp)
cat > "$temp_file" <<'EOF'
{GENERATED_PR_BODY}
EOF

# Create PR
echo "📝 Creating pull request..."

pr_url=$(gh pr create \
  --title "$pr_title" \
  --body-file "$temp_file" \
  --base "$target_branch" \
  --head "$branch_to_pr" \
  2>&1 | grep -oE 'https://github.com[^ ]+' || echo "")

rm "$temp_file"

if [ -z "$pr_url" ]; then
  echo "❌ Error: Failed to create PR"
  echo "   Run manually: gh pr create --base $target_branch --head $branch_to_pr"
  exit 1
fi

echo ""
echo "✅ PR created: $pr_url"
echo ""
echo "📊 Summary:"
echo "   Branch: $branch_to_pr → $target_branch"
echo "   Commits: $commit_count"
echo "   Files: $files_changed (+$additions -$deletions)"
echo "   Observations: $count_attention attention, $count_ok OK"
echo ""
```

---

## Security

**Command Injection Prevention:**

1. All variables quoted: `"$var"` never `$var`
2. Git commands with separator: `git cmd "ref" --`
3. Reject branches starting with `--`
4. Input validation via regex
5. No user input in eval or subshell without validation

---

## Error Handling

On any error during execution:

```bash
echo "❌ Error occurred during PR creation"
echo "   Current branch: $(git branch --show-current)"
echo "   To retry: /git-pullrequest $target_branch"
exit 1
```

If temporary branch was created but PR failed:

```bash
# User can manually delete: git branch -d pr/...
# Or re-run command from original branch
```

---

## Notes

- **No state persistence**: All context in model memory, not git config
- **Skills integration**: Uses `requesting-code-review` and `receiving-code-review`
- **Observations paradigm**: Reports facts with context, not accusations
- **Governance**: User always authorizes, mandatory re-validation after fixes
- **Format support**: Auto-detects conventional or corporate commit format
