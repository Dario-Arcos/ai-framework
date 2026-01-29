# Output Structure Reference

## Overview

This reference defines the complete directory structure and file templates for sop-reverse investigation output. Understanding output structure is essential for consistent spec generation and forward flow integration.

---

## Directory Structure

**Constraints:**
- You MUST create all standard directories because forward flow expects this structure
- You MUST place investigation.md at root because this is the primary findings document
- You SHOULD organize supporting materials in artifacts/ because this maintains clarity

```text
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

---

## Investigation.md Template

**Constraints:**
- You MUST include all template sections because this ensures completeness
- You MUST include target and type metadata because this provides context
- You SHOULD include diagrams where applicable because visual aids improve understanding

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

---

## Recommendations.md Template

**Constraints:**
- You MUST include executive summary because readers need quick orientation
- You MUST include prioritized next steps because actionability matters
- You SHOULD include forward flow option because this guides continuation

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

---

## Spec Format Requirements

**Constraints:**
- You MUST use clear, structured markdown because this enables parsing
- You MUST include mermaid diagrams for flows and architectures because visual documentation aids understanding
- You MUST include cross-references between specs because this maintains coherence
- You SHOULD include versioning information because this tracks evolution
- You SHOULD include date generated because this provides temporal context
- You MAY include code examples where applicable because concrete samples aid implementation

---

## Troubleshooting

### Output Directory Not Created

If output directory structure is incomplete:
- You SHOULD verify write permissions because access issues prevent creation
- You SHOULD check parent directory exists because nested creation may fail
- You MUST create missing directories manually if needed because incomplete structure breaks forward flow

### Investigation.md Missing Sections

If investigation document lacks expected sections:
- You SHOULD verify artifact was fully analyzed because partial analysis produces incomplete docs
- You SHOULD add N/A for truly inapplicable sections because structure must be consistent
- You MUST NOT skip required sections because downstream processing expects them

### Specs Not Generated for Type

If specs-generated/ is empty or incomplete:
- You SHOULD verify artifact type was correctly identified because wrong type skips relevant specs
- You SHOULD check analysis found sufficient content because sparse artifacts produce sparse specs
- You MUST document why specs were not generated because this informs manual completion

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
