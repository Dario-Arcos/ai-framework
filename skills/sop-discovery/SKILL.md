---
name: sop-discovery
description: Use when starting a new goal or project to brainstorm constraints, risks, and prior art before detailed planning
---

# SOP: Discovery Phase

## Overview

This skill implements the Discovery phase of Amazon's agent-sop methodology. It helps explore new goals or ideas by systematically identifying constraints, risks, and prior art before moving to detailed planning.

The discovery process is conversational and iterative. You will ask questions one at a time to gather context about the problem space, technical constraints, resource limitations, potential risks, and relevant patterns from existing work. The output is a structured discovery document that serves as input for the planning phase.

**When to use this skill:**
- Starting a new project or major feature
- Exploring a new technical direction
- Before creating detailed implementation plans
- When stakeholder requirements are unclear
- To align on scope and success criteria before committing resources

**Keywords for Claude Search Optimization (CSO)**:
- Error messages/symptoms: "unclear requirements", "undefined scope", "stakeholder alignment needed", "what are the constraints", "need risk assessment"
- Synonyms: "requirements gathering", "problem definition", "scope definition", "brainstorm constraints", "discovery phase", "requirements elicitation"
- Use cases: "new project planning", "feature exploration", "feasibility study", "constraint analysis", "risk identification", "prior art research"
- Alternative terminology: "pre-planning", "scoping session", "requirements workshop", "discovery workshop", "problem framing"

## Parameters

### Required Parameters

**goal_description** (string)
- A brief description of the goal or idea to explore
- Examples: "Add real-time collaboration to the editor", "Migrate from REST to GraphQL", "Implement automated testing pipeline"

### Optional Parameters

**project_dir** (string, default: "specs")
- Directory where the discovery document will be stored
- Created if it doesn't exist
- Full path: `{project_dir}/discovery.md`

## Steps

### Step 1: Setup and Context Gathering

**You MUST perform these actions:**

1. Create the project directory if it doesn't exist
2. Check for existing project documentation (README, architecture docs, recent specs)
3. Review recent git commits to understand current development focus
4. Initialize the discovery document with the goal description

**You MUST NOT:**
- Skip context gathering even if the goal seems simple
- Make assumptions about the existing codebase without verification

### Step 2: Problem Definition

**Objective:** Understand what job needs to be done and who benefits.

**You MUST ask the following questions, ONE AT A TIME:**

1. **Job to Be Done (JTBD):**
   - "What specific job does this solve for users/developers?"
   - Wait for response, append to discovery.md

2. **Beneficiaries:**
   - "Who are the primary beneficiaries of this work? (e.g., end users, developers, operations, business stakeholders)"
   - Wait for response, append to discovery.md

3. **Success Metrics:**
   - "How will we measure success? What would 'done and successful' look like?"
   - Wait for response, append to discovery.md

**You MUST:**
- Ask ONLY ONE question per message
- Wait for the user's response before proceeding
- Append each question and answer to the discovery document
- Confirm successful append before asking the next question

**You MUST NOT:**
- List all questions at once for the user to answer
- Proceed to the next question without receiving a response
- Skip any of these questions

### Step 3: Constraints Identification

**Objective:** Identify technical and resource constraints that will shape the solution.

**You MUST ask the following questions, ONE AT A TIME:**

1. **Technical Constraints:**
   - "What are the technical constraints we must work within? (e.g., existing architecture, technology choices, compatibility requirements, performance requirements)"
   - Wait for response, append to discovery.md

2. **Time/Resource Constraints:**
   - "What are the time and resource constraints? (e.g., deadlines, team size, budget, opportunity costs)"
   - Wait for response, append to discovery.md

3. **Non-Negotiables:**
   - "What aspects are non-negotiable or fixed? (e.g., must use existing auth system, cannot break API compatibility)"
   - Wait for response, append to discovery.md

**You MUST:**
- Ask ONLY ONE question per message
- Wait for the user's response before proceeding
- Append each question and answer to the discovery document
- Confirm successful append before asking the next question

**You MUST NOT:**
- Present multiple questions for batch answering
- Make assumptions about constraints

### Step 4: Risk Analysis

**Objective:** Identify potential risks and mitigation strategies.

**You MUST ask the following questions, ONE AT A TIME:**

1. **Technical Risks:**
   - "What are the technical risks? (e.g., scalability concerns, integration challenges, performance bottlenecks)"
   - For each risk identified, ask: "What would be the mitigation strategy for [specific risk]?"
   - Wait for response, append to discovery.md

2. **Integration Risks:**
   - "What integration risks exist with other systems or components?"
   - For each risk identified, ask: "What would be the mitigation strategy for [specific risk]?"
   - Wait for response, append to discovery.md

3. **Unknown Unknowns:**
   - "What areas have significant uncertainty or missing information?"
   - Wait for response, append to discovery.md

4. **Recommended Spikes:**
   - "Based on the unknowns identified, what time-boxed spikes or proof-of-concepts should we do before committing to the full plan?"
   - Wait for response, append to discovery.md

**You MUST:**
- Ask ONLY ONE question per message
- For risks, follow up with mitigation questions
- Wait for the user's response before proceeding
- Append each question and answer to the discovery document
- Confirm successful append before asking the next question

**You SHOULD:**
- Probe deeper on risks that seem vague or incomplete
- Suggest potential risks based on context if the user's list seems incomplete
- Challenge optimistic risk assessments

**You MAY:**
- Skip spike recommendations if there are no significant unknowns

### Step 5: Prior Art and Patterns

**Objective:** Learn from existing patterns and avoid known anti-patterns.

**You MUST ask the following questions, ONE AT A TIME:**

1. **Existing Patterns:**
   - "What patterns from our existing codebase or past projects should we follow? (e.g., architecture patterns, coding conventions, workflow patterns)"
   - Wait for response, append to discovery.md

2. **External Inspiration:**
   - "Are there external examples or prior art we should consider? (e.g., how other teams solved similar problems, industry best practices)"
   - Wait for response, append to discovery.md

3. **Anti-patterns:**
   - "What anti-patterns should we explicitly avoid? (e.g., past mistakes, known pitfalls, technical debt patterns)"
   - Wait for response, append to discovery.md

**You MUST:**
- Ask ONLY ONE question per message
- Wait for the user's response before proceeding
- Append each question and answer to the discovery document
- Confirm successful append before asking the next question

**You SHOULD:**
- Search the codebase for relevant patterns if the user seems unsure
- Reference specific files or commits as examples

### Step 6: Generate Discovery Summary

**You MUST perform these actions:**

1. Review all gathered information from the discovery document
2. Identify the single most constraining factor
3. Identify the highest-impact risk
4. Generate a structured summary using the template from `templates/discovery-output.md.template`
5. Write the complete discovery document to `{project_dir}/discovery.md`
6. Display the summary to the user for review

**Summary structure (from template):**
```markdown
# Discovery: {goal_name}

## Summary
- **Goal**: [One sentence]
- **Main Constraint**: [The most limiting factor]
- **Biggest Risk**: [Highest-impact risk]
- **Ready for**: Planning phase

## Problem Statement

### Job to Be Done
[Answer from Step 2.1]

### Beneficiaries
[Answer from Step 2.2]

### Success Metrics
[Answer from Step 2.3]

## Constraints

### Technical Constraints
[Answer from Step 3.1]

### Time/Resource Constraints
[Answer from Step 3.2]

### Non-Negotiables
[Answer from Step 3.3]

## Risks

### Technical Risks
[Risks from Step 4.1 with mitigations]
- **[Risk Name]**: [Description]
  - *Mitigation*: [Strategy]

### Integration Risks
[Risks from Step 4.2 with mitigations]
- **[Risk Name]**: [Description]
  - *Mitigation*: [Strategy]

### Open Questions
[Unknowns from Step 4.3]

### Recommended Spikes
[Spikes from Step 4.4, if any]

## Prior Art

### Patterns to Follow
[Patterns from Step 5.1 and 5.2]

### Anti-patterns to Avoid
[Anti-patterns from Step 5.3]
```

**You MUST:**
- Generate a complete, well-formatted discovery document
- Highlight the main constraint and biggest risk in the summary
- Use the template structure exactly

**You SHOULD:**
- Ask the user if they want to proceed to planning phase
- Offer to commit the discovery document to git

**You MUST NOT:**
- Skip any sections in the final document
- Leave placeholder text without real content
- Claim the discovery is complete if any section is missing

## Key Principles

1. **One Question at a Time** - Never present multiple questions for the user to answer in one go. This ensures focused, thoughtful responses.

2. **Incremental Documentation** - Append each question and answer to the discovery document as you go. This creates a narrative trail and prevents information loss.

3. **Conversational Depth** - If an answer seems incomplete or vague, ask follow-up questions before moving on.

4. **No Assumptions** - Don't assume you know the constraints or risks. Always ask, even if it seems obvious.

5. **Challenge Optimism** - If risk assessments seem overly optimistic or constraint lists seem incomplete, probe deeper.

6. **Context-Aware** - Reference specific files, commits, or patterns from the codebase when discussing prior art.

7. **Outcome-Focused** - The discovery document should provide clear direction for the planning phase. It's not just documentation—it's a decision-making tool.

## After Discovery

Once the discovery document is complete, you **SHOULD** suggest one of the following next steps:

1. **Proceed to Planning** - Use the `sop-planning` skill to create a detailed Problem Definition Document (PDD)
2. **Execute Spikes** - Time-box exploration of high-uncertainty areas before planning
3. **Refine Scope** - If constraints or risks suggest the goal is too large, work with the user to decompose it

**You MUST NOT:**
- Jump directly to implementation without planning
- Proceed without user confirmation on next steps

## Quality Checks

Before marking the discovery phase complete, verify:

- [ ] All required questions have been asked and answered
- [ ] Discovery document exists at `{project_dir}/discovery.md`
- [ ] Summary section clearly identifies main constraint and biggest risk
- [ ] All sections follow the template structure
- [ ] Risks include mitigation strategies
- [ ] Prior art references specific examples or patterns
- [ ] User has reviewed and approved the discovery document
- [ ] Next steps are clearly communicated

## Example Discovery Session

**User:** "I want to add real-time collaboration to our document editor."

**Assistant:** "I'll help you explore this through a discovery process. We'll identify constraints, risks, and prior art before moving to detailed planning.

Let me start by understanding the problem better.

**Question 1 of 12:** What specific job does this solve for users/developers?"

**User:** "Users want to see each other's edits in real-time, like Google Docs."

**Assistant:** *[Appends to discovery.md]*

"Got it. I've recorded that.

**Question 2 of 12:** Who are the primary beneficiaries of this work? (e.g., end users, developers, operations, business stakeholders)"

*[...continues one question at a time...]*

---

## Related Skills

- **sop-planning** - Next phase: create detailed Problem Definition Document
- **sop-task-generator** - After planning: generate implementation tasks
- **brainstorming** - Alternative exploratory approach for simpler features
- **ralph-loop** - Autonomous implementation after planning

---

## References

This skill implements concepts from:
- Amazon's agent-sop methodology
- Jobs to Be Done (JTBD) framework
- Risk-first software development
- Agile spike methodology
