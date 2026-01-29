# Research: {topic_name}

<!--
## Overview

Research document template for exploring options and making informed technical decisions.
Provides structured comparison of alternatives with clear recommendation.

## Usage Constraints

- You MUST define clear research question because this focuses investigation
- You MUST evaluate at least 2-3 options because single-option research is confirmation bias
- You MUST include pros/cons for each option because balanced analysis enables good decisions
- You MUST state clear recommendation because research without conclusion is incomplete
- You SHOULD include code examples because concrete examples aid understanding
- You SHOULD NOT research indefinitely because analysis paralysis blocks progress
-->

**Created**: {created_date}
**Last Updated**: {last_updated_date}
**Research Question**: {research_question}

---

## Executive Summary

**Constraints:**
- You MUST provide summary first because readers need quick orientation
- You MUST state clear recommendation because this is the primary output

{executive_summary}

**Recommendation**: {recommendation}

---

## Background

**Constraints:**
- You MUST explain why this research matters because context justifies effort
- You MUST define scope because unbounded research never completes

**Why This Research Matters**: {research_relevance}

**Scope**: {scope}

---

## Findings

### Option 1: {option_1_name}

**Description**: {option_1_description}

**Pros**:
- {option_1_pro_1}
- {option_1_pro_2}
- {option_1_pro_3}

**Cons**:
- {option_1_con_1}
- {option_1_con_2}
- {option_1_con_3}

**Use Cases**: {option_1_use_cases}

**Example**:
```text
{option_1_example}
```

**References**:
- {option_1_reference_1}
- {option_1_reference_2}

---

### Option 2: {option_2_name}

**Description**: {option_2_description}

**Pros**:
- {option_2_pro_1}
- {option_2_pro_2}
- {option_2_pro_3}

**Cons**:
- {option_2_con_1}
- {option_2_con_2}
- {option_2_con_3}

**Use Cases**: {option_2_use_cases}

**Example**:
```text
{option_2_example}
```

**References**:
- {option_2_reference_1}
- {option_2_reference_2}

---

### Option 3: {option_3_name}

{option_3_content}

---

## Comparison

**Constraints:**
- You MUST use consistent criteria because apples-to-apples comparison enables decision
- You SHOULD weight criteria by importance because not all factors are equal

| Criterion | Option 1 | Option 2 | Option 3 |
|-----------|----------|----------|----------|
| Complexity | {option_1_complexity} | {option_2_complexity} | {option_3_complexity} |
| Performance | {option_1_performance} | {option_2_performance} | {option_3_performance} |
| Maintainability | {option_1_maintainability} | {option_2_maintainability} | {option_3_maintainability} |
| Learning Curve | {option_1_learning_curve} | {option_2_learning_curve} | {option_3_learning_curve} |
| Community Support | {option_1_community_support} | {option_2_community_support} | {option_3_community_support} |
| Cost | {option_1_cost} | {option_2_cost} | {option_3_cost} |

**Legend**: S=Simple, M=Medium, L=Large, XL=Very Large

---

## Architecture Implications

**Constraints:**
- You MUST show how option fits into system because integration matters
- You SHOULD include diagram because visual aids comprehension

{architecture_implications_summary}

```mermaid
{architecture_diagram}
```

**Integration Points**: {integration_points}

**Dependencies**: {architecture_dependencies}

**Impact on Existing System**: {impact_on_existing_system}

---

## Recommendation

**Constraints:**
- You MUST state chosen option clearly because ambiguity blocks progress
- You MUST explain rationale because this enables informed disagreement
- You MUST acknowledge trade-offs because perfect options don't exist

**Chosen Option**: {chosen_option}

**Rationale**:
1. {rationale_1}
2. {rationale_2}
3. {rationale_3}

**Trade-offs Accepted**:
- {trade_off_1}
- {trade_off_2}

**Mitigation Strategies**:
- {mitigation_strategy}

---

## Implementation Considerations

**Constraints:**
- You MUST estimate complexity because this affects planning
- You MUST identify risks because these need mitigation

**Setup Requirements**:
- {setup_dependency}
- {setup_configuration}
- {setup_access_permissions}

**Estimated Complexity**: {estimated_complexity}

**Estimated Duration**: {estimated_duration}

**Risks**:
- {risk_1} - **Mitigation**: {risk_1_mitigation}
- {risk_2} - **Mitigation**: {risk_2_mitigation}

---

## Further Research Needed

**Constraints:**
- You MUST track open questions because they may affect decision
- You SHOULD time-box further research because diminishing returns apply

{further_research_summary}

- [ ] {further_research_question_1}
- [ ] {further_research_question_2}

---

## References

1. {reference_1_title} - {reference_1_url}
2. {reference_2_title} - {reference_2_url}
3. {reference_3_title} - {reference_3_url}

---

*This research document supports the PDD (Prompt-Driven Development) planning process.*

<!--
*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
-->
