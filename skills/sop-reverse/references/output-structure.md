# Output Structure Reference

Complete directory structure and file templates for investigation output.

## Directory Structure

```
{output_dir}/
├── investigation.md           # Raw findings and analysis
├── specs-generated/          # Structured specs by category
│   └── [type-specific specs]
├── recommendations.md        # Improvement suggestions
├── summary.md                # Overview and next steps
└── artifacts/                # Supporting materials
    ├── diagrams/             # Generated mermaid diagrams
    ├── examples/             # Code samples, configs
    └── references/           # External docs, links
```

## Investigation.md Template

```markdown
# Investigation: [Artifact Name]

**Target**: [path/url/description]
**Type**: [codebase|api|documentation|process|concept]
**Date**: [generated date]

## Executive Summary
[High-level overview of findings]

## Detailed Findings

### [Category 1]
[Findings with evidence]

### [Category 2]
[Findings with evidence]

## Observations
[Patterns, anomalies, notable items]

## Questions for Refinement
[Items needing clarification]

## Diagrams
[Mermaid diagrams where applicable]
```

## Recommendations.md Template

```markdown
# Recommendations for [Artifact Name]

## Executive Summary
[High-level assessment and top 3 recommendations]

## Improvements
- Modernization opportunities
- Technical debt to address
- Missing capabilities
- Performance optimizations

## Risks & Technical Debt
- Security vulnerabilities
- Deprecated dependencies
- Scalability concerns
- Maintainability issues

## Migration Paths
[If applicable]
- Upgrade strategies
- Refactoring approaches
- Migration to new stack

## Next Steps
1. Priority 1: [Action with rationale]
2. Priority 2: [Action with rationale]
3. Priority 3: [Action with rationale]

## Forward Flow Option
Ready to plan improvements? Use sop-planning with these specs as input.
```

## Spec Format Requirements

- Clear, structured markdown
- Mermaid diagrams for flows, architectures, relationships
- Code examples where applicable
- Cross-references between specs
- Versioning information if applicable
- Date generated and source artifact
