# Evidence Documentation Standard

## Confidence Ratings

| Rating | Criteria |
|--------|----------|
| **High** | 3+ Tier 1/2 sources agree, recent data, no conflicts |
| **Medium** | 2+ sources agree, some Tier 3, minor conflicts resolved |
| **Low** | Limited sources, older data, or unresolved minor conflicts |
| **Uncertain** | Conflicting authoritative sources, insufficient data |

## Per-Claim Format

```
[Statement] | Source: [URL] | Date: [YYYY-MM-DD] | Tier: [1/2/3] | Confidence: [H/M/L/U]
Cross-validation: [Confirming URLs] | Conflicts: [If any]
```

Example:
```
Global AI market size reached $196.6B in 2024
| Source: https://www.grandviewresearch.com/industry-analysis/artificial-intelligence-ai-market
| Date: 2025-01-15
| Tier: 2 (Industry Research)
| Confidence: High
| Cross-validation: Statista ($184B), IDC ($189B) - consistent range
| Conflicts: None
```

## Report Template

```markdown
# Research Report: [Topic]

## Executive Summary
[2-3 paragraphs: Key findings, confidence levels, actionable recommendations]

## Methodology & Source Verification
- **Sources consulted**: [N total, breakdown by tier]
- **Search iterations**: [N passes]
- **Coverage assessment**: [gaps identified]
- **Limitations**: [explicit constraints]

## Key Findings

### Finding 1: [Title] [Confidence: High/Medium/Low]
[Content with inline citations]

**Sources**:
- [Source 1] | [URL] | [Date] | Tier [N]

## Disputed/Uncertain Points

| Point | Source A Says | Source B Says | Assessment |
|-------|---------------|---------------|------------|

## Risk Assessment & Recommendations

### Risks Identified
| Risk | Likelihood | Impact | Mitigation |

### Strategic Recommendations
1. [Recommendation] [Priority: High]

## Appendix: Complete Source Log
| # | URL | Accessed | Tier | Claims Extracted |
```

## Quality Gates

| Criterion | Requirement |
|-----------|-------------|
| **Factual grounding** | Every claim sourced |
| **Source diversity** | No over-reliance on single source |
| **Recency** | Prefer sources < 12 months old |
| **Uncertainty transparency** | Gaps explicitly declared |
| **Actionability** | Recommendations provided |

Report NOT ready if: any material claim lacks citation, confidence ratings missing, known conflicts undocumented, no methodology section, no limitations stated.

## Error Handling

| Condition | Action |
|-----------|--------|
| **Source unavailable** | Log, try archive.org, move to next source |
| **Paywall encountered** | Note limitation, seek alternative source |
| **Conflicting authoritative sources** | Document both, mark as Uncertain |
| **Insufficient sources found** | Expand to Tier 3, note coverage gap |
| **Browser navigation fails** | Use `--headed` to debug, retry |
