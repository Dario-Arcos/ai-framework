---
description: Sync PRP to GitHub as parent issue for SDD workflow tracking
argument-hint: [feature-name] or [empty for auto-detect]
allowed-tools: Read, Edit, Write, Bash(gh), Bash(date), Glob
---

# PRP Sync

Sync PRP to GitHub as parent issue for SDD workflow tracking.

## Usage Examples

**Auto-detect unsynced PRP:**
```
/PRP-cycle:prp-sync
```

**Sync specific PRP:**
```
/PRP-cycle:prp-sync realtime-notifications
```

**List all PRPs:**
```
/PRP-cycle:prp-sync --list
```

## User Input

```text
$ARGUMENTS
```

## Instructions

### Step 1: Identify PRP to Sync

**1. If feature-name provided:**
   - Use it directly
   - Proceed to Step 2

**2. If empty arguments:**
   - Use Glob to list `prps/*/prp.md`
   - Read frontmatter of each PRP
   - Filter PRPs without `github_synced` field
   - **If 1 unsynced found**:
     - Use automatically
     - Show: "🔍 Auto-detected: `<feature-name>`"
   - **If multiple unsynced found**:
     - List with descriptions
     - Ask: "Which PRP to sync?"
     - Wait for selection
   - **If none unsynced**:
     - Show: "✅ All PRPs synced to GitHub"
     - Stop

**3. If `--list` flag:**
   - List all PRPs with status:
     ```
     PRPs in prps/:
     ✅ realtime-notifications (synced: 2025-01-15, #123)
     ⏸️  payment-gateway (not synced)
     ✅ user-auth (synced: 2025-01-10, #89)
     ```
   - Ask which to sync
   - Wait for selection

**4. Store as `$FEATURE_NAME`**

### Step 2: Validate PRP File

**Check file exists:**
- Verify `prps/$FEATURE_NAME/prp.md` exists
- If missing, show:
  ```
  ❌ PRP not found: prps/$FEATURE_NAME/prp.md

  Available PRPs:
  [list prps/ directories]
  ```
- Stop if not found

### Step 3: Check Existing Sync

**Read frontmatter:**
- Parse `prps/$FEATURE_NAME/prp.md` frontmatter
- Extract `name`, `description`, `github` fields
- **If `github` field exists**:
  - Show: "⚠️ Already synced: [URL]"
  - Ask: "Create duplicate? (yes/no)"
  - Stop if user says no

### Step 4: Create GitHub Issue

**Prepare content:**
1. Read `prps/$FEATURE_NAME/prp.md`
2. Strip frontmatter (between `---` delimiters)
3. Use clean content as body

**Create issue:**
```bash
gh issue create \
  --title "PRP: $FEATURE_NAME" \
  --body "$BODY_CONTENT" \
  --label prp,parent-issue,sdd
```

**Capture output:**
- Extract issue number and URL
- Store as `$ISSUE_NUM`, `$ISSUE_URL`

### Step 5: Update PRP Frontmatter

**Add fields to `prps/$FEATURE_NAME/prp.md`:**
- `github: $ISSUE_URL`
- `github_issue: $ISSUE_NUM`
- `github_synced: <timestamp>`

Use ISO format: `YYYY-MM-DDTHH:MM:SSZ`

**Implementation:**
- Use Edit tool for surgical update
- Preserve existing fields
- Maintain frontmatter structure

### Step 6: Create Mapping File

**Create `prps/$FEATURE_NAME/github-mapping.md`:**

```markdown
# GitHub Issue Mapping

Parent Issue: #$ISSUE_NUM - $FEATURE_NAME
URL: $ISSUE_URL

Sub-issues created by SDD workflow:
/SDD-cycle:speckit.specify from Github issue $ISSUE_NUM

Synced: <timestamp>
```

### Step 7: Display Results

**Success message:**
```
✅ PRP synced to GitHub

📋 Parent Issue: #$ISSUE_NUM - $FEATURE_NAME
   URL: $ISSUE_URL
   Labels: prp, parent-issue, sdd

Next steps:
  • Create spec: /SDD-cycle:speckit.specify from Github issue $ISSUE_NUM
  • View issue: $ISSUE_URL
```

## Error Handling

- **PRP not found**: Show available PRPs
- **Already synced**: Warn and confirm before duplicate
- **Issue creation fails**: Report error, don't rollback
- **File update fails**: Report specific failure

## Important Notes

- Trust GitHub CLI authentication
- Don't pre-check for duplicates
- Update files after successful GitHub ops
- Keep operations simple
- Sub-issues handled by SDD workflow
- Auto-detection reduces friction

## Implementation Approach

Uses natural language processing via Claude Code:

1. **Parse arguments** from `$ARGUMENTS`
2. **Auto-detect PRP** if empty
3. **Read PRP** via Read tool
4. **Create issue** via gh CLI
5. **Update files** via Edit/Write tools

**Benefits:**
- No variable persistence issues
- No temporary files
- Natural language processing
- Intelligent edge case handling
- Maintainable and debuggable

## Workflow Integration

**PRP as Parent Issue:**
- PRP = business requirement
- GitHub issue = hub for technical sub-issues
- SDD creates spec + implementation tasks
- Stakeholders track via parent issue
- Tech team tracks via sub-issues

**Flow:**
```
PRP.md → [prp-new] → Business brainstorming
   ↓
PRP.md → [prp-sync] → GitHub Parent Issue
   ↓
GitHub Issue → [speckit.specify] → Spec + Sub-issues
```

**Example:**

1. **PM**: `/PRP-cycle:prp-new Implement notifications`
   - Creates `prps/realtime-notifications/prp.md`

2. **PM**: `/PRP-cycle:prp-sync`
   - Auto-detects unsynced PRP
   - Creates GitHub issue #123

3. **Tech Lead**: `/SDD-cycle:speckit.specify from Github issue 123`
   - Creates spec
   - Creates sub-issues
   - Links to parent #123

4. **Team**: Tracks progress via parent issue #123
