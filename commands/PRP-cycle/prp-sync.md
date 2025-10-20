---
allowed-tools: Read, Edit, Write, Bash(gh), Bash(date)
description: Push PRP to GitHub as parent issue with optional milestone assignment
---

# PRP Sync

Push PRP to GitHub as parent issue with optional milestone assignment.

## Usage

```
/PRP-cycle:prp-sync <feature_name>
/PRP-cycle:prp-sync <feature_name> --milestone <number>
```

## User Input

$ARGUMENTS

## Required Rules

**IMPORTANT:** Before executing this command, read and follow:

- `.claude/rules/datetime.md` - For getting real current date/time

## Instructions

### 1. Parse Arguments and Validate Files

**Parse the arguments** from `$ARGUMENTS`:

- **Feature name**: Extract the feature name (remove `--milestone <number>` if present)
- **Milestone mode**: Check if `--milestone <number>` is provided for reuse
- **Milestone number**: Extract number if provided

**Validate required files exist**:

- `prps/<feature_name>/prp.md`

If PRP file missing, show error and stop.

### 2. Milestone Handling

**If milestone number provided** (format: `--milestone 5`):

- Use existing milestone #5
- Get milestone details via GitHub API

**If no milestone provided**:

- Continue without milestone assignment
- Skip milestone-related operations

### 3. Create GitHub Issue

**Prepare issue content**:

- Read `prps/<feature_name>/prp.md`
- Strip the frontmatter (everything between `---` lines)
- Use clean PRP content as issue body

**Create GitHub issue**:

- Title: Extract from PRP frontmatter `name` field
- Body: Clean PRP content without frontmatter
- Labels: `prp`, `parent-issue`, `sdd`
- Assign to milestone only if milestone number was provided

```bash
# Create issue with natural language processing (Claude handles gh CLI syntax)
gh issue create \
  --title "<title>" \
  --body "<body_content>" \
  --label prp,parent-issue,sdd \
  [--milestone <milestone_number>]  # Only if milestone provided
```

### 4. Update PRP File

**Update** `prps/<feature_name>/prp.md` frontmatter with:

- `github: <issue_url>`
- `github_synced: <current_timestamp>`
- `milestone: <milestone_number>` (only if milestone provided)
- `milestone_url: <milestone_url>` (only if milestone provided)

Use current timestamp in ISO format: `YYYY-MM-DDTHH:MM:SSZ`

### 5. Create GitHub Mapping File

**Create** `prps/<feature_name>/github-mapping.md` with this content:

```markdown
# GitHub Issue Mapping

[If milestone provided] Milestone: #<milestone_number> - <milestone_url>
[If no milestone] No milestone assigned
Parent Issue: #<issue_number> - <issue_url>

Note: Sub-issues will be created by SDD workflow via /SDD-cycle:specify --from-issue <issue_number>

Synced: <current_timestamp>
```

### 6. Output Results

**Display success message**:

```
✅ PRP synced to GitHub
  [If milestone provided] - Milestone: #<milestone_number> - <milestone_title>
  - Parent Issue: #<issue_number> - <feature_name>
  [If milestone provided] - PRP issue created and assigned to milestone
  [If no milestone] - PRP issue created (no milestone assigned)

Next steps:
  - Technical specification: /SDD-cycle:specify --from-issue <issue_number>
  [If milestone provided] - View milestone: <milestone_url>
  - View PRP issue: <issue_url>
```

## Error Handling

- **If PRP.md not found**: Show clear error message with correct path
- **If milestone number invalid**: Show error that milestone doesn't exist
- **If issue creation fails**: Report what succeeded, don't rollback
- **If file updates fail**: Report specific file and continue with others

## Important Notes

- Trust GitHub CLI authentication (no pre-auth checks)
- Don't pre-check for duplicates (let GitHub handle conflicts)
- Update files only after successful GitHub operations
- Keep operations atomic and simple
- Sub-issues handled by SDD workflow, not this command
- Use `--milestone N` to assign PRP to existing milestone
- Milestones provide optional business-level progress tracking
- PRP represents business requirement, not technical implementation

## Implementation Approach

This command uses **natural language instructions** processed by Claude Code's native capabilities rather than complex bash scripting. Claude will:

1. **Parse arguments** intelligently from `$ARGUMENTS`
2. **Read PRP content** using the Read tool
3. **Execute GitHub operations** using simple Bash commands (issue creation, optional milestone assignment)
4. **Update files** using Edit tool for surgical changes
5. **Create new files** using Write tool when needed

This approach is more robust than bash scripting because:

- No variable persistence issues between commands
- No temporary file dependencies
- Leverages Claude's natural language processing
- More maintainable and debuggable
- Handles edge cases intelligently

## Relationship to SDD Workflow

**PRP as Parent Issue Strategy**:

- PRP represents the business requirement being tracked
- GitHub issue becomes the central hub for all technical sub-issues
- SDD workflow creates technical specification and implementation sub-issues
- Business stakeholders track progress via parent PRP issue
- Technical team tracks implementation via SDD sub-issues

**Workflow Integration**:

```
PRP.md → [prp-sync] → GitHub Parent Issue → [SDD-cycle:specify --from-issue] → Technical Spec + Sub-Issues
```
