---
name: prp-new
description: Discovery Engine - Conversational process to define WHAT problem to solve and WHY it matters, before any technical consideration
argument-hint: [context source] or empty to start from scratch
---

# PRP: Product Requirement Prompt

## Philosophy

```
"We don't document requirements - we discover opportunities"
```

This is a **Discovery Engine**, not a document builder. Guide the user through 4 phases of progressive excavation to define the problem and opportunity before any technical solution.

**Responsibility Separation**:

| Role | Validates |
|------|-----------|
| **User** | "Did you understand MY problem correctly?" |
| **Claude** | "Does the output meet world-class methodological standards?" |

## Process Overview

```
Input (any context source or fresh start)
    ↓
PHASE 1: CONTEXT - Understand the situation
    ↓
PHASE 2: PROBLEM - Excavate to root cause (Five Whys)
    ↓
PHASE 3: IMPACT - Quantify business consequences
    ↓
PHASE 4: OPPORTUNITY - Define desired outcome (no technical solution)
    ↓
User Validation → Claude Validation → Output
```

## Execution Instructions

### Step 0: Context Detection

**If `$ARGUMENTS` contains context source** (document, URL, image, text):
- Extract relevant information
- Identify what's already known vs gaps
- Start discovery from gaps, not from zero

**If `$ARGUMENTS` is empty**:
- Start fresh with Phase 1

**If `$ARGUMENTS` is a short name** (e.g., "user-notifications"):
- Use as project name
- Start fresh with Phase 1

### Step 1: Generate Project Name

If not provided, derive kebab-case name (2-4 words) from conversation after Phase 1:
- Extract meaningful keywords
- Use action-noun format (e.g., "consolidate-reports", "reduce-onboarding-time")
- Store as `$PROJECT_NAME`

### Step 2: Execute 4 Phases

**CRITICAL RULES**:
- ONE question at a time - never overwhelm
- Use `AskUserQuestion` tool for multiple choice when options are clear
- Use open questions for deep exploration
- Do NOT advance until phase criteria is met
- ZERO technical solutions - only problem and opportunity

---

#### PHASE 1: CONTEXT

**Objective**: Understand the current situation (not the problem yet).

**Question Types**:
- "In what context does this need arise? What's happening today?"
- "Who is involved in this situation?"
- "How often does this occur?"

**Use AskUserQuestion when**:
- Clarifying stakeholder types
- Determining frequency ranges
- Identifying scope boundaries

**Advancement Criteria**: Clear understanding of situation/scenario.

---

#### PHASE 2: PROBLEM

**Objective**: Excavate to the real problem (not symptoms).

**Technique**: Adapted Five Whys - each answer generates the next question.

**Question Types**:
- "What happens when [situation]? What becomes difficult?"
- "Why is that a problem? What does it prevent?"
- "What have you tried before? Why didn't it work?"

**Advancement Criteria**: Underlying "Job to be Done" identified.

---

#### PHASE 3: IMPACT

**Objective**: Quantify/qualify business consequences.

**Question Types**:
- "What does this problem cost? (time, money, opportunity)"
- "What happens if this is NOT solved in the next 6 months?"
- "Who else suffers the consequences?"

**Use AskUserQuestion when**:
- Selecting impact severity levels
- Prioritizing affected stakeholders

**Advancement Criteria**: Business impact clearly articulated.

---

#### PHASE 4: OPPORTUNITY

**Objective**: Define desired outcome (without technical solution).

**Question Types**:
- "If this were magically solved, what would success look like?"
- "How would you know the problem no longer exists?"
- "What would change for [stakeholder]?"

**Advancement Criteria**: Measurable/observable outcome defined.

---

### Step 3: User Validation

Present the Opportunity Statement and ask for confirmation:

```
Based on our conversation, I understand:

**Opportunity Statement**:
"[Stakeholder] needs [desired outcome]
when [situation/context]
because currently [friction/pain]
which causes [business consequence]."

Does this correctly reflect your situation and need?
```

Use `AskUserQuestion`:
- Options: "Yes, correct" | "Needs adjustment" | "Start over"
- If adjustment needed: ask what specifically, return to relevant phase

### Step 4: Claude Internal Validation

**Silently evaluate** (do NOT show to user):

```
World-Class Methodology Checklist:
- [ ] Specific situation identified (not generic)?
- [ ] Job to be Done found (not symptom)?
- [ ] Business impact articulated (quantified or qualified)?
- [ ] Measurable/observable outcome defined?
- [ ] ZERO references to technical solutions?
- [ ] Evidence captured for each phase (user quotes)?
```

**If ANY item fails**: Return to relevant phase and ask clarifying questions.
**If ALL pass**: Proceed to output generation.

### Step 5: Generate Output

#### 5.1 Create Directory

```bash
mkdir -p prps/$PROJECT_NAME
```

#### 5.2 Write Discovery Document

Save to `prps/$PROJECT_NAME/discovery.md`:

```markdown
---
name: $PROJECT_NAME
status: discovered
created: [ISO timestamp from: date -u +"%Y-%m-%dT%H:%M:%SZ"]
---

# Discovery: $PROJECT_NAME

## Opportunity Statement

"[Stakeholder] needs [desired outcome]
when [situation/context]
because currently [friction/pain]
which causes [business consequence]."

## Context

**Synthesis**: [1-3 sentences summarizing Phase 1]

**Evidence**:
> "[Direct quote from user that captures the situation]"
> "[Another relevant quote if applicable]"

## Root Problem

**Synthesis**: [1-3 sentences - the Job to be Done identified]

**Evidence**:
> "[Quote showing the real underlying need]"
> "[Quote showing what they tried before / why it failed]"

## Impact

**Synthesis**: [1-3 sentences - business consequences]

**Evidence**:
> "[Quote quantifying or qualifying the cost]"
> "[Quote about consequences of inaction]"

## Desired Outcome

**Synthesis**: [1-3 sentences - success criteria]

**Evidence**:
> "[Quote describing what success looks like]"
> "[Quote about how they'd know it's solved]"

---

**Next**: Continue with systematic technical planning (specify, implementation plan, or other available workflow)
```

### Step 6: Confirm Completion

Display to user:

```
Discovery completed: prps/$PROJECT_NAME/discovery.md

**Opportunity Statement**:
"[The full statement]"

**Key Insights**:
- Root problem: [One sentence]
- Business impact: [One sentence]
- Success criteria: [One sentence]

Ready to proceed with technical planning when you are.
```

---

## Real-World Example

### Scenario: User invokes `/prp-new` with no arguments

**PHASE 1 - CONTEXT**:

Claude: "What situation or challenge brings you here today? Tell me what's happening."

User: "Every month closing our financial books is a nightmare. It takes forever."

Claude: "Who is involved in this monthly close process?"

User: "The finance team - 3 accountants and the CFO who needs to present to the board."

Claude: "How long does it currently take to close the books each month?"

User: "About 8-10 business days. Sometimes more if there are errors."

*[Criteria met: Situation clear - monthly financial close taking 8-10 days]*

---

**PHASE 2 - PROBLEM**:

Claude: "What makes the process take 8-10 days? What are the main blockers?"

User: "We have to pull data from 4 different systems - SAP, Salesforce, our billing system, and Excel spreadsheets from regional offices."

Claude: "Why can't this data be pulled faster? What happens when you try?"

User: "Each system has different formats. We spend days just cleaning and reconciling the data. And if someone finds an error, we have to start over."

Claude: "What have you tried to solve this?"

User: "We tried building some macros in Excel but they break constantly. We also looked at hiring more people but budget is tight."

*[Criteria met: Job to be Done = reliable, fast data consolidation across 4 systems]*

---

**PHASE 3 - IMPACT**:

Claude: "What does this 8-10 day delay cost the company?"

User: "The CFO can't make timely decisions. Last quarter we missed an investment window because we didn't have the numbers ready. That probably cost us $200K in returns."

Claude: "What happens if this isn't solved in the next 6 months?"

User: "The board is already frustrated. The CFO's job might be at risk honestly. And we're planning to acquire a smaller company - due diligence will be impossible at this pace."

*[Criteria met: Impact = delayed decisions, $200K+ opportunity cost, M&A risk, CFO job security]*

---

**PHASE 4 - OPPORTUNITY**:

Claude: "If this were magically solved tomorrow, what would success look like?"

User: "Close in 2-3 days max. The CFO gets reliable numbers by the 5th business day. No more fire drills."

Claude: "How would you know the problem is truly solved?"

User: "The CFO stops asking 'where are my numbers?' The team isn't working weekends at month-end. We can actually do the acquisition due diligence without panic."

*[Criteria met: Outcome = 2-3 day close, numbers by day 5, no weekend work, M&A capable]*

---

**OUTPUT GENERATED**:

```markdown
---
name: accelerate-month-close
status: discovered
created: 2025-12-05T15:30:00Z
---

# Discovery: accelerate-month-close

## Opportunity Statement

"The finance team needs to close monthly books in 2-3 days
when month-end arrives
because currently data consolidation from 4 systems takes 8-10 days with frequent errors
which causes delayed executive decisions, $200K+ missed opportunities, and M&A capability risk."

## Context

**Synthesis**: Monthly financial close involves 3 accountants and CFO, currently taking 8-10 business days due to multi-system complexity.

**Evidence**:
> "Every month closing our financial books is a nightmare. It takes forever."
> "The finance team - 3 accountants and the CFO who needs to present to the board."

## Root Problem

**Synthesis**: Data lives in 4 disconnected systems (SAP, Salesforce, billing, regional Excel files) requiring manual consolidation and reconciliation. Errors force complete restarts.

**Evidence**:
> "We have to pull data from 4 different systems - SAP, Salesforce, our billing system, and Excel spreadsheets from regional offices."
> "If someone finds an error, we have to start over."

## Impact

**Synthesis**: Delayed financial visibility costs $200K+ in missed investment opportunities, threatens CFO position, and blocks planned M&A activity.

**Evidence**:
> "Last quarter we missed an investment window because we didn't have the numbers ready. That probably cost us $200K in returns."
> "We're planning to acquire a smaller company - due diligence will be impossible at this pace."

## Desired Outcome

**Synthesis**: Close books in 2-3 days with reliable numbers available by business day 5, eliminating weekend work and enabling M&A due diligence.

**Evidence**:
> "Close in 2-3 days max. The CFO gets reliable numbers by the 5th business day."
> "The team isn't working weekends at month-end. We can actually do the acquisition due diligence without panic."

---

**Next**: Continue with systematic technical planning (specify, implementation plan, or other available workflow)
```

---

## Key Principles

1. **One question at a time** - Never overwhelm
2. **AskUserQuestion for choices** - Native UX when options are clear
3. **Open questions for depth** - Explore when space is undefined
4. **No advancement without clarity** - Return to phase if gaps exist
5. **Zero technical solutions** - Only problem and opportunity
6. **Synthesis + Evidence** - Preserve user's exact words
7. **User validates understanding** - Claude validates methodology
