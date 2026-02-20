---
name: brainstorming
description: Use when creating features, building components, adding functionality, or modifying behavior. Invoke FIRST — before any implementation skill.
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, observable scenarios
- Be ready to go back and clarify if something doesn't make sense

**Defining observable scenarios:**
- After architecture is validated, define 5-10 end-to-end scenarios that would satisfy the user
- Each scenario is a concrete user story with specific inputs and expected observable outcomes
- Scenarios use the user's language, not technical assertions
- Scenarios must include happy paths, edge cases, and error experiences
- Scenarios function as a holdout set: they define what "done" looks like before any code exists
- Present scenarios for validation one at a time, just like design sections
- Ask: "Would this scenario genuinely satisfy you?" — not "Is this correct?"

Scenario format:
```
SCENARIO: <short descriptive name>
Given <concrete initial state with specific values>
When <specific user action>
Then <observable outcome the user would see>
And <additional observable outcomes if needed>
```

These scenarios become the holdout set for implementation. They are NOT tests — they are specifications of what would satisfy the user. Implementation must converge until all scenarios are satisfied.

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Invoke humanizer on the design document to remove AI writing patterns before committing
- The design document MUST include an "Observable Scenarios" section with all validated scenarios
- Observable scenarios are the holdout set — they MUST NOT be modified during implementation without returning to brainstorming
- Commit the design document to git

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Invoke scenario-driven-development next — the observable scenarios from this design are its input
- The scenarios become the holdout set for the SCENARIO→SATISFY→REFACTOR convergence loop

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense
- **Scenarios before implementation** - Define observable scenarios as part of the design, not during coding. Scenarios are the bridge between "what to build" and "how to know it's done"

## Artifact Handoff

| Receives | Produces |
|---|---|
| User idea, feature request, or change requirement | Design document at `docs/plans/YYYY-MM-DD-<topic>-design.md` (humanized) |
| | Observable Scenarios section — the holdout set for implementation |

**→ Next:** scenario-driven-development receives the scenarios as input for the SCENARIO phase.
