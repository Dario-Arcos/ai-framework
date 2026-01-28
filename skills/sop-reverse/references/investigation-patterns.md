# Investigation Patterns Reference

## Overview

This reference defines investigation process, question strategies, and quality standards for the sop-reverse skill. Use this when conducting artifact investigations to ensure consistent, high-quality analysis.

---

## Question Guidelines

### One Question at a Time

**Constraints:**
- You MUST ask only one question per message because multiple questions overwhelm users and reduce response quality
- You MUST wait for user response before asking the next question because proceeding without confirmation may lead to misaligned analysis
- You SHOULD prefer multiple choice questions when possible because they reduce cognitive load and accelerate the investigation

### Question Categories

**Priority Questions:**
- What aspect is most important?
- Should I dig deeper into X or Y?

**Clarification Questions:**
- Is this pattern intentional or legacy?
- Are there specific flows to document?

**Scope Questions:**
- Should I focus on specific areas?
- Is the full analysis needed?

---

## Error Handling

### Target Not Found

**Constraints:**
- You MUST present clear options when target cannot be found because users need guidance to resolve the issue

**Template:**
```
Target not found: {target}

Please verify:
- Path exists and is readable
- URL is accessible
- Description is clear

Would you like to:
1. Specify different target
2. Provide more context
3. Cancel investigation
```

### Ambiguous Type

**Constraints:**
- You MUST present evidence for each detected type because users need context to make informed decisions
- You MUST NOT proceed without user confirmation because incorrect type selection invalidates the entire analysis

**Template:**
```
Cannot determine target type from: {target}

Could be:
- [Option 1 with evidence]
- [Option 2 with evidence]

Which type should I investigate?
```

### Insufficient Access

**Constraints:**
- You MUST clearly state what is and is not accessible because partial analysis may still provide value
- You MUST request explicit approval before proceeding with limited analysis because incomplete data may lead to incorrect conclusions

**Template:**
```
Cannot fully analyze target due to:
- [Access issue 1]
- [Access issue 2]

I can proceed with partial analysis of:
- [What's accessible]

Continue with limited analysis? (yes/no)
```

### Large Scope

**Constraints:**
- You SHOULD recommend focused analysis for large artifacts because full analysis may exceed reasonable time bounds
- You MUST present the scope explicitly because users need to understand the time/effort tradeoff

**Template:**
```
This is a large artifact ({size} files / {endpoints} endpoints).

Recommend focusing on:
- [Priority area 1]
- [Priority area 2]

Or proceed with full analysis? (This may take longer)
```

---

## Quality Gates

**Constraints:**
- You MUST verify all quality gates before completing because incomplete investigations produce unreliable specs

**Checklist:**
- [ ] Target type confirmed with user
- [ ] Batch analysis completed and documented
- [ ] Questions asked ONE at a time
- [ ] User confirmed refinement complete
- [ ] Specs generated in correct format
- [ ] Mermaid diagrams included where appropriate
- [ ] Recommendations are actionable
- [ ] Summary clearly states next steps
- [ ] All files written to output_dir
- [ ] User asked about forward flow

---

## Anti-Patterns

**Constraints:**
- You MUST NOT assume artifact type without confirmation because incorrect assumptions invalidate subsequent analysis
- You MUST NOT ask multiple questions in one message because users can only effectively answer one question at a time
- You MUST NOT generate specs before user confirms refinement complete because premature specs may not match user intent
- You MUST NOT auto-invoke sop-planning without asking because the user may want to review or modify findings first
- You MUST NOT skip batch analysis to ask questions first because analysis provides context for meaningful questions
- You MUST NOT limit investigation to just code because documentation, processes, and other artifacts provide critical context
- You SHOULD NOT provide vague recommendations because they don't give users clear next steps

**Positive Patterns:**
- You MUST confirm target type with evidence
- You MUST ask ONE question at a time
- You MUST complete batch analysis before questions
- You MUST wait for explicit user approval at each gate
- You MUST support ALL artifact types equally
- You SHOULD generate actionable, specific recommendations
- You SHOULD use mermaid diagrams to visualize findings

---

## Examples

### Example 1: Codebase Investigation

**Input:**
```
User: Investigate /path/to/legacy-api
```

**Expected Process:**
```
You: Based on analysis:
     - Target: /path/to/legacy-api
     - Detected type: codebase
     - Evidence: Contains package.json, Express app in src/

     Proceed with codebase investigation?
User: Yes
You: [Performs batch analysis, presents findings]
     What aspect is most important for your needs?
     a) API endpoints and data model
     b) Authentication and security
     c) Database schema
     d) Overall architecture
```

### Example 2: Process Investigation

**Input:**
```
User: Investigate our deployment process
```

**Expected Process:**
```
You: Target: "deployment process"
     Detected type: process

     Proceed with process investigation?
User: Yes
You: Please describe the process or point me to documentation.
User: [describes process]
You: [Performs analysis, asks one clarifying question]
```

---

## Success Criteria

A successful investigation produces:
1. Clear, accurate understanding of artifact
2. Structured specs ready for forward flow
3. Actionable recommendations
4. User feels confident in findings
5. Specs are detailed enough to build from
6. Diagrams clarify complex relationships
7. Next steps are obvious

---

## Troubleshooting

### User Provides Incomplete Information
If the user's description lacks sufficient detail:
- You SHOULD ask clarifying questions one at a time
- You SHOULD offer multiple choice options when possible
- You MAY provide examples of the information you need

### Analysis Takes Too Long
If investigation exceeds reasonable time bounds:
- You SHOULD pause and summarize progress
- You SHOULD ask if user wants to continue or focus on specific areas
- You MUST NOT claim completion without finishing quality gates because incomplete investigations produce unreliable specs that undermine forward flow

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
