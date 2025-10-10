---
allowed-tools: Bash(date -u +"%Y-%m-%dT%H:%M:%SZ"), Read, Write, LS
model: claude-opus-4-1
---

# PRD New

Launch brainstorming for new product requirement document (minimalista, business-focused).

## Usage

```
/PRD-cycle:prd-new <feature_name>
```

## Required Rules

**IMPORTANT:** Before executing this command, read and follow:

- `.claude/rules/datetime.md` - For getting real current date/time

## Preflight Checklist

Before proceeding, complete these validation steps.
Do not bother the user with preflight checks progress ("I'm not going to ..."). Just do them and move on.

### Input Validation

1. **Validate feature name format:**
   - Must contain only lowercase letters, numbers, and hyphens
   - Must start with a letter
   - No spaces or special characters allowed
   - If invalid, tell user: "❌ Feature name must be kebab-case (lowercase letters, numbers, hyphens only). Examples: user-auth, payment-v2, notification-system"

2. **Check for existing PRD:**
   - Check if `.claude/prds/$ARGUMENTS/prd.md` already exists
   - If it exists, ask user: "⚠️ PRD '$ARGUMENTS' already exists. Do you want to overwrite it? (yes/no)"
   - Only proceed with explicit 'yes' confirmation
   - If user says no, suggest: "Use a different name or sync existing PRD: /PRD-cycle:prd-sync $ARGUMENTS"

3. **Verify directory structure:**
   - Ensure `.claude/prds/$ARGUMENTS/` directory exists or can be created
   - If cannot create, tell user: "❌ Cannot create PRD directory. Please check permissions."

## Instructions

You are a product manager creating a **lean, business-focused** Product Requirements Document (PRD) for: **$ARGUMENTS**

### Design Philosophy (Steve Jobs Principles)

**"Simplicity is the ultimate sophistication"**

- PRD describes WHAT and WHY, not HOW
- Target: 50-100 lines (vs typical 300+ line PRDs)
- Say NO to implementation details (stack, architecture, config)
- Focus on user value and business outcomes

### Discovery & Context

Ask clarifying questions about:

- **Problem**: What specific problem are we solving? Why now?
- **Users**: Who experiences this problem? Primary personas?
- **Impact**: What happens if we DON'T solve this?
- **Success**: How do we measure if this works?
- **Constraints**: Budget, timeline, compliance requirements?
- **Scope**: What are we explicitly NOT building in V1?

### PRD Structure (Minimalista)

Create a lean PRD with ONLY these sections:

#### 1. Problem Statement (5-10 lines)

- What problem exists today?
- Who experiences this problem?
- Why is it important to solve NOW?
- What's the cost of NOT solving it?

#### 2. User Impact (10-20 lines)

**Primary Users**

- [Persona 1]: [Their need in one sentence]
- [Persona 2]: [Their need in one sentence]

**User Journey (Happy Path)**

1. User does X
2. System provides Y
3. User achieves outcome Z

**User Pain Points**

- Current friction point 1
- Current friction point 2

#### 3. Success Criteria (5-10 lines)

**Quantitative**

- Metric 1: [Baseline] → [Target] (e.g., "Onboarding time: 30min → 5min")
- Metric 2: [Baseline] → [Target]

**Qualitative**

- Observable outcome 1 (e.g., "Zero Slack questions about 'where is X documented?'")
- Observable outcome 2

#### 4. Constraints (5-10 lines)

- **Budget**: $X or "zero cost"
- **Timeline**: [Deadline] or "immediate"
- **Team**: [Size/skills available]
- **Compliance**: [Regulatory requirements if any]
- **Complexity Budget**: Size S/M/L (S: ≤80 LOC, M: ≤250 LOC, L: ≤600 LOC)

#### 5. Out of Scope (V1) (5-10 lines)

Explicitly list what we're NOT building:

- [Feature X]: Why excluded (defer to V2, complexity, etc.)
- [Feature Y]: Why excluded
- [Feature Z]: Why excluded

### What NOT to Include (Critical)

**❌ DO NOT include these (belong in SDD-cycle):**

- Stack decisions (e.g., "Use Jekyll", "Use React")
- Architecture diagrams or technical design
- Domain entities and data models
- API endpoints or database schemas
- Configuration files (e.g., `_config.yml`)
- Performance targets (e.g., "<200ms latency") - keep high-level only
- Edge cases and error handling (technical details)
- Integration dependencies (technical details)

**✅ Keep it business-level:**

- "Users need to find documentation quickly" ✅
- "System must use Algolia search with <200ms response" ❌

### File Format with Frontmatter

Save the completed PRD to: `.claude/prds/$ARGUMENTS/prd.md` with this exact structure:

```markdown
---
name: $ARGUMENTS
description: [Brief one-line description of the PRD]
status: backlog
created: [Current ISO date/time]
---

# PRD: $ARGUMENTS

## Problem Statement

[Content...]

## User Impact

[Content...]

## Success Criteria

[Content...]

## Constraints

[Content...]

## Out of Scope (V1)

[Content...]

---

**Next Steps**: Run `/PRD-cycle:prd-sync $ARGUMENTS` to sync to GitHub as Parent Issue
```

### Frontmatter Guidelines

- **name**: Use the exact feature name (same as $ARGUMENTS)
- **description**: Write a concise one-line summary of what this PRD covers
- **status**: Always start with "backlog" for new PRDs
- **created**: !bash date -u +"%Y-%m-%dT%H:%M:%SZ"
  - Never use placeholder text
  - Must be actual system time in ISO 8601 format

### Quality Checks

Before saving the PRD, verify:

- [ ] Total length: 50-100 lines (excluding frontmatter)
- [ ] No implementation details (no stack, no config, no architecture)
- [ ] Problem and user impact are crystal clear
- [ ] Success criteria are measurable
- [ ] Out of scope explicitly defined
- [ ] All sections complete (no placeholder text like "TBD")
- [ ] Written for business stakeholders (non-technical language)

### Post-Creation

After successfully creating the PRD:

1. Confirm: "✅ PRD created: .claude/prds/$ARGUMENTS/prd.md"
2. Show brief summary:
   - Problem: [One sentence]
   - Target: [Primary metric]
   - Complexity: Size S/M/L
3. Suggest next step: "Ready to sync to GitHub? Run: `/PRD-cycle:prd-sync $ARGUMENTS`"

## Error Recovery

If any step fails:

- Clearly explain what went wrong
- Provide specific steps to fix the issue
- Never leave partial or corrupted files

**Target**: Create a lean, business-focused PRD that fits on one screen (50-100 lines). Technical details are handled by SDD-cycle, not here.

Conduct a thorough brainstorming session before writing the PRD. Ask questions, explore trade-offs, and ensure comprehensive coverage of the **business requirements** (not technical implementation) for "$ARGUMENTS".
