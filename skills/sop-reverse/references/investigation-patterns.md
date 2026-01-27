# Investigation Patterns Reference

Detailed investigation process, question strategies, and quality standards.

## Question Guidelines

### One Question at a Time
- **Never** ask multiple questions in one message
- Wait for response before asking next question
- Prefer multiple choice when possible

### Question Categories

**Priority Questions**:
- What aspect is most important?
- Should I dig deeper into X or Y?

**Clarification Questions**:
- Is this pattern intentional or legacy?
- Are there specific flows to document?

**Scope Questions**:
- Should I focus on specific areas?
- Is the full analysis needed?

## Error Handling

### Target Not Found
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
```
Cannot determine target type from: {target}

Could be:
- [Option 1 with evidence]
- [Option 2 with evidence]

Which type should I investigate?
```

### Insufficient Access
```
Cannot fully analyze target due to:
- [Access issue 1]
- [Access issue 2]

I can proceed with partial analysis of:
- [What's accessible]

Continue with limited analysis? (yes/no)
```

### Large Scope
```
This is a large artifact ({size} files / {endpoints} endpoints).

Recommend focusing on:
- [Priority area 1]
- [Priority area 2]

Or proceed with full analysis? (This may take longer)
```

## Quality Gates

Before completing, verify:
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

## Anti-Patterns

### Do NOT:
- Assume artifact type without confirmation
- Ask multiple questions in one message
- Generate specs before user confirms refinement complete
- Auto-invoke sop-planning without asking
- Skip batch analysis to ask questions first
- Limit investigation to just code
- Provide vague recommendations

### DO:
- Confirm target type with evidence
- Ask ONE question at a time
- Complete batch analysis before questions
- Wait for explicit user approval at each gate
- Support ALL artifact types equally
- Generate actionable, specific recommendations
- Use mermaid diagrams to visualize findings

## Example Interactions

### Codebase Investigation
```
User: Investigate /path/to/legacy-api
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

### Process Investigation
```
User: Investigate our deployment process
You: Target: "deployment process"
     Detected type: process

     Proceed with process investigation?
User: Yes
You: Please describe the process or point me to documentation.
User: [describes process]
You: [Performs analysis, asks one clarifying question]
```

## Success Criteria

A successful investigation produces:
1. Clear, accurate understanding of artifact
2. Structured specs ready for forward flow
3. Actionable recommendations
4. User feels confident in findings
5. Specs are detailed enough to build from
6. Diagrams clarify complex relationships
7. Next steps are obvious
