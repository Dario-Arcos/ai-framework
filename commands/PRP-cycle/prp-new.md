---
description: Create Product Requirements Prompt (minimal, business-focused) from natural language, GitHub issues, or context files
argument-hint: [natural-language] or [from Github issue #N] or [from document path]
allowed-tools: Bash(date -u +"%Y-%m-%dT%H:%M:%SZ"), Read, Write, LS, WebFetch
---

# PRP New

Create minimal, business-focused Product Requirements Prompt.

## Usage Examples

**Natural language:**
```
/PRP-cycle:prp-new Implement real-time notifications for user actions with email delivery
```

**GitHub issue:**
```
/PRP-cycle:prp-new from Github issue #456
```

**Context file:**
```
/PRP-cycle:prp-new from document research/notifications-proposal.md
```

**Short prompt (will ask questions):**
```
/PRP-cycle:prp-new notification system
```

## Required Rules

**IMPORTANT:** Read and follow:
- `.claude/rules/datetime.md` - For current date/time

## User Input

```text
$ARGUMENTS
```

Input can be:
- **Natural language**: "Implement real-time notifications"
- **GitHub Issue**: "from Github issue #123" or URL
- **Context file**: "from document <path>"
- **Short name**: "user-notifications" (will prompt for details)

## Instructions

### Step 1: Parse and Load Context

**Identify input type and load context:**

**If natural language:**
- Proceed to Step 2

**If GitHub issue** (contains "github.com" or "issue #"):
- Extract URL or number
- WebFetch issue content
- Extract title, body, labels
- Proceed with loaded context

**If context file** (contains "from document"):
- Extract file path
- Read file content
- Proceed with loaded context

**If short/empty:**
- Note: Will ask comprehensive questions
- Proceed to Step 2

### Step 2: Generate Short Name

Create kebab-case name (2-4 words):
- Extract meaningful keywords from input
- Use action-noun format (e.g., "add-user-auth", "fix-payment-bug")
- Preserve technical terms (OAuth2, API, JWT)
- Keep concise but descriptive

**Examples:**
- "Implement real-time notifications" → "realtime-notifications"
- "Add OAuth2 integration" → "oauth2-integration"
- "Fix payment timeout" → "fix-payment-timeout"

Store as `$SHORT_NAME`.

### Step 3: Validate and Check

**Silently validate:**

1. **Format validation:**
   - Lowercase letters, numbers, hyphens only
   - Must start with letter
   - If invalid: "❌ Feature name must be kebab-case. Examples: user-auth, payment-v2"

2. **Check existing:**
   - If `prps/$SHORT_NAME/prp.md` exists
   - Ask: "⚠️ PRP '$SHORT_NAME' exists. Overwrite? (yes/no)"
   - If no: "Use different name or sync: `/PRP-cycle:prp-sync $SHORT_NAME`"

3. **Directory check:**
   - Ensure `prps/$SHORT_NAME/` can be created
   - If fails: "❌ Cannot create PRP directory. Check permissions."

### Step 4: Discovery Session

Ask clarifying questions **only if critical info missing**. Limit: 3-4 questions.

**Priority 1 (always ask if unclear):**
- **Problem**: What problem? Why now?
- **Users**: Who affected? Primary personas?
- **Success**: How measure if works?

**Priority 2 (ask if impacts scope):**
- **Impact**: What if we DON'T solve?
- **Constraints**: Budget, timeline, compliance?
- **Scope**: What NOT building in V1?

**Make informed guesses** for non-critical details based on:
- Industry standards
- Context from input
- Common patterns

### Step 5: Create PRP Content

**Philosophy: "Simplicity is the ultimate sophistication"**

- Describe WHAT and WHY, not HOW
- Target: 50-100 lines
- No implementation details (stack, architecture, config)
- Focus on user value and business outcomes

**PRP Structure (5 sections only):**

#### 1. Problem Statement (5-10 lines)

Structured format:
- **Problem**: What exists today?
- **Affected Users**: Who experiences this?
- **Frequency**: How often?
- **Current Cost**: Time/money wasted?
- **Why Now**: Why important NOW?
- **Risk of Inaction**: What if we don't solve?

#### 2. User Impact (10-20 lines)

**Primary Users:**
- Persona 1: Need in one sentence
- Persona 2: Need in one sentence

**User Journey:**
1. User does X
2. System provides Y
3. User achieves Z

**Pain Points:**
- Current friction 1
- Current friction 2

#### 3. Success Criteria (5-10 lines)

**Quantitative:**
- [ ] Metric 1: Baseline → Target (Measured by: method)
- [ ] Metric 2: Baseline → Target (Measured by: method)

**Qualitative:**
- [ ] Observable 1 (Verified by: method)
- [ ] Observable 2 (Verified by: method)

#### 4. Constraints (5-10 lines)

- **Budget**: $X or "zero cost"
- **Timeline**: Deadline or "immediate"
- **Team**: Size/skills available
- **Compliance**: Regulatory requirements if any
- **Complexity**: S (≤80 LOC), M (≤250 LOC), L (≤600 LOC)

#### 5. Out of Scope V1 (5-10 lines)

Explicitly list what NOT building:
- Feature X: Why excluded (defer V2, complexity, etc.)
- Feature Y: Why excluded

**Exclusions (belong in SDD-cycle):**
- ❌ Stack decisions ("Use React")
- ❌ Architecture diagrams
- ❌ Data models, API endpoints
- ❌ Performance targets ("<200ms")
- ❌ Edge cases, error handling details

**Keep business-level:**
- ✅ "Users find docs quickly"
- ❌ "Algolia search <200ms"

### Step 6: Save PRP with Frontmatter

Save to `prps/$SHORT_NAME/prp.md`:

```markdown
---
name: $SHORT_NAME
description: [One-line PRP description]
status: backlog
created: [ISO timestamp]
complexity_budget: S|M|L
priority: P1|P2|P3
---

# PRP: $SHORT_NAME

[5 sections from Step 5]

---

**Next Steps**: `/PRP-cycle:prp-sync $SHORT_NAME`
```

**Frontmatter:**
- `name`: Exact feature name
- `description`: Concise summary
- `status`: Always "backlog"
- `created`: !bash date -u +"%Y-%m-%dT%H:%M:%SZ"
- `complexity_budget`: S/M/L estimate
- `priority`: P1 (Critical), P2 (Important), P3 (Nice-to-have)

### Step 7: Quality Validation

**Verify before saving:**
- [ ] Length: 50-100 lines (excluding frontmatter)
- [ ] No implementation details
- [ ] Problem statement uses structured format
- [ ] Success criteria have checkboxes + measurement methods
- [ ] Problem and user impact clear
- [ ] Out of scope defined
- [ ] No placeholders (no "TBD")
- [ ] Written for business stakeholders (non-technical)
- [ ] Frontmatter complete

### Step 8: Confirm Creation

**After successful creation:**

1. Confirm: "✅ PRP created: prps/$SHORT_NAME/prp.md"
2. Summary:
   - Problem: [One sentence]
   - Target: [Primary metric]
   - Complexity: S/M/L
   - Priority: P1/P2/P3
3. Next: "Sync to GitHub? `/PRP-cycle:prp-sync $SHORT_NAME`"

## Error Recovery

**If any step fails:**
- Explain what went wrong
- Provide fix steps
- Never leave partial/corrupted files

**Target**: Lean, business-focused PRP (100-200 lines). Technical details → SDD-cycle.
