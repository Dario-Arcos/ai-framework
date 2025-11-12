---
name: speckit.sync
allowed-tools: Read, Edit, Write, Bash(gh), Bash(date)
description: Push spec to GitHub as child issue linked to parent PRP
---

# Spec Sync

Push spec to GitHub as child issue linked to parent PRP.

**IMPORTANT:** This command REQUIRES a parent PRP issue. Specs must always be linked to a PRP. If you don't have a PRP issue yet, run `/PRP-cycle:prp-sync` first.

## Usage

```
/SDD-cycle:speckit.sync <parent_issue_number>
```

## User Input

$ARGUMENTS

## Instructions

### 1. Parse Arguments and Validate

**Parse parent issue number** from `$ARGUMENTS`:

- **Parent issue number**: Extract the issue number (REQUIRED)
- If no argument provided: Show error "❌ Parent issue number required. Usage: /SDD-cycle:speckit.sync <issue_number>" and stop

**Detect feature from current branch:**

- Get branch name via `git branch --show-current`
- Extract feature directory name (e.g., `001-documentation-changelog-visibility`)
- Or check `SPECIFY_FEATURE` environment variable if set

**Validate spec.md exists:**

- Check if `specs/<feature>/spec.md` exists
- If spec.md missing, show error "❌ Spec file not found: specs/<feature>/spec.md" and stop

**Verify not already synced (prevent duplicates):**

- Read frontmatter from `specs/<feature>/spec.md`
- Check if `github:` field exists in frontmatter
- If `github:` field exists:
  - Extract the GitHub issue URL from the field
  - Show error: "❌ Spec already synced to <issue_url>. To re-sync, manually remove the 'github:' line from spec.md frontmatter and re-run this command."
  - Stop execution

**Validate parent issue exists:**

- Run `gh issue view <parent_issue_number> --json number,title` to verify issue exists
- If issue doesn't exist: Show error "❌ Parent issue #<number> not found" and stop

**Validate optional files:**

- Check if `specs/<feature>/plan.md` exists (optional)
- Check if `specs/<feature>/tasks.md` exists (optional)

### 2. Prepare Issue Content

**Read spec artifacts:**

- Read `specs/<feature>/spec.md`
- Read `specs/<feature>/plan.md` if exists
- Read `specs/<feature>/tasks.md` if exists

**Strip frontmatter** from spec.md (everything between `---` lines at top)

**Format for GitHub Issue body:**

If only spec.md exists:

```markdown
# Feature Specification: <Title from spec>

**Parent PRD**: #<parent_number>

---

<spec.md content without frontmatter>

---

_Synced from local specs at <timestamp>_
```

If plan.md and/or tasks.md also exist, append:

```markdown
---
## Implementation Plan

<plan.md content>
---

## Task Breakdown

<tasks.md content>
```

**Write formatted body to temporary file:**

For safety with complex markdown content (quotes, special chars), write the formatted body to a temporary file instead of passing directly to `--body` flag.

### 3. Create GitHub Issue and Link to Parent

**Create GitHub issue:**

- **Title**: "Spec: <feature-name>" (convert kebab-case to Title Case)
- **Body**: Write formatted content to temporary file, use `--body-file`
- **Labels**: `spec`, `sdd`, `feature`

```bash
# Write body to temp file
temp_file=$(mktemp /tmp/spec-issue-XXXXXX.md)
echo "<formatted_body_content>" > "$temp_file"

# Create issue with body-file (safer for complex markdown)
gh issue create \
  --title "<title>" \
  --body-file "$temp_file" \
  --label spec,sdd,feature

# Cleanup temp file
rm "$temp_file"
```

**Notify parent PRD:**

- Add comment to parent issue:

```bash
gh issue comment <parent_number> \
  --body "📋 Technical specification created: #<spec_issue_number>"
```

### 4. Update Local Spec File

**Update** `specs/<feature>/spec.md` frontmatter with:

- `github: <issue_url>`
- `github_synced: <current_timestamp>`
- `parent_prd: #<parent_number>`

Use current timestamp in ISO format: `YYYY-MM-DDTHH:MM:SSZ`

**Preserve all other frontmatter fields** (Feature Branch, Created, Status, etc.)

### 5. Create GitHub Mapping File

**Create** `specs/<feature>/github-mapping.md` with this content:

```markdown
# GitHub Issue Mapping

Parent PRD: #<parent_number> - <parent_url>
Spec Issue: #<issue_number> - <issue_url>

Note: Implementation tasks tracked via this spec issue

Synced: <current_timestamp>
```

### 6. Output Results

**Display success message:**

```
✅ Spec synced to GitHub

  - Spec Issue: #<issue_number> - <feature_name>
  - Parent PRD: #<parent_number>
  - Files synced: spec.md[, plan.md][, tasks.md]

Documentation complete. Stakeholders can now review what was built.

Next steps:
  - View spec: <issue_url>
  - Close feature branch: Merge PR or delete branch
  - Start next feature: /PRP-cycle:prp-new <feature_name>
```

## Error Handling

- **If no parent issue number provided**: Show usage error and stop
- **If spec already synced**: Show error with existing issue URL and stop (prevents duplicates)
- **If parent issue doesn't exist**: Verify with `gh issue view` before proceeding and stop
- **If spec.md not found**: Show clear error message with correct path and stop
- **If issue creation fails**: Report what succeeded, don't rollback local changes
- **If file updates fail**: Report specific file and continue with others

## Important Notes

- **Parent PRD issue is REQUIRED** (enforces correct workflow: PRD → Spec)
- **Recommended timing: AFTER implementation** (documents what was built, not what was planned)
- **Single sync per feature** (run once at the end, eliminates re-sync complexity)
- **Duplicate prevention**: Command fails if spec already synced (checks frontmatter `github:` field)
- **Manual re-sync**: To re-sync, remove `github:` line from spec.md frontmatter first
- Trust GitHub CLI authentication (no pre-auth checks)
- Update files only after successful GitHub operations
- Keep operations atomic and simple
- Spec represents technical documentation, PRD represents business requirement
- All data in Issue body/labels (100% portable to Linear)

## Implementation Approach

This command uses **natural language instructions** processed by Claude Code's native capabilities rather than complex bash scripting. Claude will:

1. **Validate parent issue** exists via `gh issue view`
2. **Detect feature** from branch name
3. **Read spec artifacts** using the Read tool
4. **Execute GitHub operations** using simple Bash commands
5. **Update files** using Edit tool for surgical changes
6. **Create mapping file** using Write tool

This approach is more robust than bash scripting because:

- No variable persistence issues between commands
- No temporary file dependencies
- Leverages Claude's natural language processing
- More maintainable and debuggable
- Handles edge cases intelligently

## Relationship to PRP Workflow

**Recommended Flow (Sync After Implementation):**

```
PRP.md → [prp-sync] → GitHub Issue #247 (PRP - parent)
                           ↓
                    [speckit.specify --from-issue 247]
                           ↓
                    specs/001-feature/spec.md (local)
                           ↓
                    [speckit.plan] → plan.md (local)
                           ↓
                    [speckit.tasks] → tasks.md (local)
                           ↓
                    [speckit.implement] → CODE (validated)
                           ↓
                    [speckit.sync 247] ← SYNC AFTER IMPLEMENTATION
                           ↓
                    GitHub Issue #248 (Spec - documents what was built)
```

**Timing Recommendation:**

Run `/speckit.sync` AFTER implementation is complete and validated. This ensures:

- GitHub Issue documents what was actually built (not speculation)
- Spec + Plan + Tasks are 100% accurate with final code
- Stakeholders see results, not work-in-progress
- Zero need for re-sync or duplicate issues

**Stakeholder View:**

- Business team tracks PRP issue #247 (parent) - high-level requirements
- Tech team tracks Spec issue #248 (child) - technical documentation of what was built
- Parent-child relationship via "Parent PRP: #247" in spec body
- Clear separation of concerns: business requirements (PRP) vs technical implementation (Spec)

## Portability to Linear

Issues created by this command import cleanly to Linear with full context preserved. Zero lock-in to GitHub Projects.
