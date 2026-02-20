---
name: deep-research
description: Use when researching a topic in depth with verification — technology decisions, API comparisons, or architecture exploration.
---

# Deep Research

Systematic, tool-augmented research engine with multi-perspective investigation, incremental validation, and structured abstention.

## Iron Law

```
NO CLAIM WITHOUT CITATION.
NO CITATION WITHOUT NAVIGATION.
NO SYNTHESIS WITHOUT CROSS-VALIDATION.
INSUFFICIENT EVIDENCE → SAY SO.
```

## Parameters

- **research_topic** (required): The question or topic to investigate. Provided via $ARGUMENTS.
- **research_type** (optional, default: auto-classify): One of: api-framework, technology-decision, market-industry, architecture, current-events, exploratory.
- **output_format** (optional, default: auto): One of: direct-answer, comparison-table, formal-report, timeline, auto.
- **depth** (optional, default: standard): One of: quick (1-2 sources per question), standard (3+ sources), exhaustive (5+ sources, all perspectives).

**Constraints for parameter acquisition:**
- If research_topic is provided via $ARGUMENTS, You MUST proceed to Step 1
- If research_topic is empty, You MUST ask for it using AskUserQuestion before proceeding
- You MUST NOT ask for optional parameters unless the user's query is ambiguous because asking unnecessary questions delays research
- When asking, You MUST request all missing parameters in a single prompt

## Core Principles

| Principle | What It Means | How It Works |
|-----------|---------------|--------------|
| **Retrieval-Led** | Every factual claim requires a navigated source | Use Context7 or agent-browser before stating facts. Training knowledge is for planning only |
| **Multi-Perspective** | Single viewpoints miss half the evidence | Generate 2+ perspectives per sub-question (STORM pattern). Coverage nearly doubles (99.83 vs 39.56) |
| **Tool Routing** | Different questions need different tools | API questions → Context7 first. Complex navigation → agent-browser. See [source-routing.md](references/source-routing.md) |
| **Incremental Validation** | Validate claims as you find them, not just at the end | Record confidence per claim. Cross-validate every 3 sources. Flag contradictions immediately |
| **Explicit Abstention** | Stating "insufficient evidence" is a valid finding | Mark gaps with INSUFFICIENT rating and documented search attempts. Never fill gaps with reasoning |
| **Context as Backbone** | The research state file is the source of truth, not context memory | Write findings to research-state.md immediately. Read it back when switching sub-questions |

## Anti-Hallucination Protocol

| Risk | Signal | Countermeasure |
|------|--------|----------------|
| **Confabulation** | Claims without URLs, smooth unsourced narratives | MUST NOT state facts without a navigated URL |
| **Citation Fabrication** | 404 URLs, papers by wrong authors | MUST verify URL loads and contains the claimed information |
| **Plausible Interpolation** | "typically", "generally", "usually" as evidence | MUST NOT use hedging language as evidence — search for the specific claim |
| **Temporal Confusion** | Stats without dates, "currently" without timestamp | MUST record source date for every claim |
| **Authority Laundering** | Blog cites paper, you cite blog | MUST navigate to primary source when secondary cites it |

Read [references/anti-hallucination-protocol.md](references/anti-hallucination-protocol.md) for the full protocol with empirical data, detection signals, and pre-synthesis checklist.

## Research Type Classification

| Type | Signal Phrases | Primary Tool | Source Priority | Default Output |
|------|---------------|-------------|----------------|----------------|
| **api-framework** | "How does X work?", "X documentation", "X API" | Context7 | Official docs > GitHub issues > community | Direct Answer |
| **technology-decision** | "X vs Y", "Should we use X?", "Compare X and Y" | Context7 + agent-browser | Benchmarks > docs > case studies > blogs | Comparison Table |
| **market-industry** | "Market size", "Industry trends", "Competitive landscape" | agent-browser | Government/regulatory > research firms > financial press | Formal Report |
| **architecture** | "How to design", "System design for", "Architecture for" | Context7 + agent-browser | Source code > conference talks > blog posts | Formal Report |
| **current-events** | "Latest", "Recent changes", "What happened with" | agent-browser | Official announcements > news outlets > analysis | Timeline |
| **exploratory** | Broad topics, no clear classification | agent-browser | Varies — start with Tier 1 available, expand as needed | Formal Report |

## Steps

### 1. Planning

Classify the research type, generate sub-questions and perspectives, create the research state file, and plan tool routing.

**Constraints:**
- You MUST classify the research type using the Research Type Classification table before proceeding
- You MUST decompose the topic into 3-7 sub-questions following the heuristics in [references/research-question-patterns.md](references/research-question-patterns.md)
- You MUST generate minimum 2 perspectives per sub-question (STORM pattern: how would different stakeholders frame this question?)
- You MUST create `research-state.md` in the working directory from [templates/research-state.md.template](templates/research-state.md.template)
- You MUST assign primary and fallback tools per sub-question using [references/source-routing.md](references/source-routing.md)
- You MUST NOT proceed to Step 2 without completing all convergence gate items because incomplete planning leads to unfocused investigation
- You SHOULD display the research plan to the user before proceeding
- You MAY reclassify research type after Step 2 if initial results suggest a different type

**Sub-question quality check:**
- Each sub-question is falsifiable (can be proven wrong with evidence)
- Each sub-question is scoped (bounded by time, context, or domain)
- Each sub-question is independent (answerable without resolving others first, unless dependency is explicit)
- Factual questions come before judgment questions

**Convergence gate:**
- [ ] Research type classified with reasoning
- [ ] 3-7 sub-questions, each falsifiable and scoped
- [ ] 2+ perspectives per sub-question
- [ ] Tool routing assigned per sub-question (primary + fallback)
- [ ] research-state.md created with all planning data
- [ ] User has seen the research plan (SHOULD)

### 2. Parallel Investigation

Investigate each sub-question from assigned perspectives. Extract per-claim evidence. Manage context aggressively.

**Constraints:**
- You MUST use the tool assigned in Step 1 for each sub-question. Read [references/source-routing.md](references/source-routing.md) for tool-specific usage patterns
- You MUST record every claim immediately in research-state.md with: statement, URL, date, tier, confidence, perspective
- You MUST rate confidence using the criteria in [references/evidence-standard.md](references/evidence-standard.md)
- You MUST update research-state.md every 3 sources and discard raw tool output from context
- You MUST follow the extraction discipline in [references/context-management.md](references/context-management.md): extract 3-10 claims per source, write to state, discard raw
- You MUST NOT retain full HTML, full Context7 responses, or full page content in context because it exhausts the attention budget
- You MUST NOT state facts from training knowledge without navigating a source because reasoning models hallucinate >10% on factual extraction (Vectara 2026)
- You MUST mark sub-questions as INSUFFICIENT when fewer than 2 independent sources confirm the core claim
- You MUST NOT fill evidence gaps with reasoning because the abstention IS the finding
- You SHOULD skip remaining perspectives for a sub-question if 3+ Tier 1/2 sources already confirm with High confidence
- You SHOULD flag contradictions for Step 3 without attempting to resolve them yet
- You MAY return to Step 1 to add sub-questions if investigation reveals unexpected dimensions

**Context7 workflow (for api-framework, technology-decision):**
1. `resolve-library-id` with specific question context
2. `query-docs` with detailed query (not vague keywords)
3. Extract claims, write to research-state.md, discard raw response
4. Maximum 3 Context7 calls per sub-question

**agent-browser workflow (for market-industry, current-events, complex navigation):**
1. `agent-browser open [URL]` → navigate to source
2. `agent-browser snapshot -i` → understand page structure
3. Extract claims from snapshot, click for details if needed
4. `agent-browser screenshot [name].png` → capture visual evidence when relevant
5. Maximum 5 page navigations per sub-question before extracting

**Convergence gate:**
- [ ] Every sub-question investigated from 2+ perspectives (or marked INSUFFICIENT with documented searches)
- [ ] Every claim has: source URL, date, tier, confidence, perspective
- [ ] No raw HTML or full tool responses retained in context
- [ ] Contradictions flagged in research-state.md
- [ ] research-state.md fully updated with all findings

### 3. Merge & Cross-Validate

Group claims across perspectives, apply cross-validation rules, resolve conflicts, assess gaps.

**Constraints:**
- You MUST group all claims by sub-question across perspectives
- You MUST apply cross-validation rules from [references/evidence-standard.md](references/evidence-standard.md):
  - 3+ Tier 1/2 sources agree → High confidence
  - 2 sources agree → Medium confidence
  - 1 source only → Low confidence
  - Sources conflict → Uncertain, document both positions
  - No confirming sources → Insufficient, document search attempts
- You MUST document both positions when sources contradict, including the tier and perspective of each
- You MUST NOT silently pick one version of a contradicted claim because the user needs to see the disagreement
- You MUST attempt one additional targeted search for gaps with Low or Insufficient confidence
- You MUST accept and document gaps that persist after fallback search because the abstention is a valid finding
- You SHOULD return to Step 2 for focused investigation if more than 50% of sub-questions are Insufficient
- You MAY upgrade or downgrade confidence ratings based on cross-validation results

**Cross-validation procedure:**

```
For each sub-question:
  1. Collect all claims from all perspectives
  2. Group by factual assertion (same claim from different sources)
  3. Count independent sources per assertion
  4. Check tier distribution (High requires Tier 1/2 sources)
  5. Check for contradictions (same question, different answers)
  6. Assign cross-validated confidence rating
  7. Document conflicts with both positions and tier/perspective metadata
```

**Convergence gate:**
- [ ] All claims grouped by sub-question and cross-validated
- [ ] Contradictions documented with both positions, tiers, and perspectives
- [ ] Gaps documented with search attempts in Gaps section of research-state.md
- [ ] No High-confidence claim has fewer than 3 independent sources
- [ ] research-state.md updated with merged findings and final confidence ratings

### 4. Synthesis

Determine output format, assemble findings with citations, run quality gates, invoke humanizer.

**Constraints:**
- You MUST determine output format: use Research Type Classification defaults unless the user specified a format
- You MUST read [references/anti-hallucination-protocol.md](references/anti-hallucination-protocol.md) and run the pre-synthesis checklist before writing the output
- You MUST include inline citations at sentence level: `[statement] [Source: URL, Tier N, Confidence: H/M/L/U/I]`
- You MUST include a "Limitations & Gaps" section listing all Insufficient and Low-confidence findings with their documented search attempts
- You MUST separate recommendations (judgment based on evidence) from findings (evidence itself)
- You MUST NOT omit Insufficient findings from the output because omission is more dangerous than stated uncertainty
- You MUST invoke humanizer on the final output — research prose is especially vulnerable to inflated significance, vague attributions, and filler phrases
- You MUST NOT deliver without passing all quality gates from [references/evidence-standard.md](references/evidence-standard.md) because unvalidated research is worse than no research
- You SHOULD use the user-requested format if they specified one, regardless of research type default
- You MAY include a "Further Research" section suggesting focused follow-up investigations

**Output structure by format:**

| Format | Structure | When |
|--------|-----------|------|
| **Direct Answer** | Answer + code example + version note + source | API/framework questions with clear answers |
| **Comparison Table** | Criteria matrix + recommendation + caveats + sources | Technology decisions between options |
| **Formal Report** | Executive summary + methodology + findings + disputed points + limitations + recommendations + source log | Market/industry, architecture, exploratory |
| **Timeline** | Chronological events + current status + projected next + sources | Current events, recent developments |

See [references/evidence-standard.md](references/evidence-standard.md) for detailed templates per format.

**Quality gates (all must pass):**
- [ ] Every factual claim has inline citation with navigated URL
- [ ] Confidence ratings on all findings (H/M/L/U/I)
- [ ] Conflicts documented with both positions, not hidden
- [ ] Insufficient findings stated with documented search attempts
- [ ] Limitations & Gaps section present and substantive
- [ ] Recommendations separated from findings
- [ ] No INSUFFICIENT claim lacks documented search attempts
- [ ] Humanizer pass completed

## Red Flags — STOP

If you observe any of these, stop and correct before continuing:

| Red Flag | Violated Constraint | Correction |
|----------|-------------------|------------|
| Writing factual claims without opening a URL | Step 2: MUST NOT state facts without navigating a source | Navigate a source first, then state the claim |
| Citing a URL you haven't loaded in this session | Step 2: MUST verify URL loads | Load the URL, verify content matches claim |
| Using "typically" or "generally" as evidence | Step 2: MUST NOT use hedging language as evidence | Search for the specific claim or mark INSUFFICIENT |
| Retaining full page HTML in context | Step 2: MUST NOT retain full content | Extract claims, write to state, discard raw |
| Skipping a sub-question without documenting why | Step 2: MUST mark as INSUFFICIENT with search attempts | Document what you searched and what you found |
| Resolving a contradiction by picking one side | Step 3: MUST NOT silently pick one version | Document both positions with sources |
| Delivering without Limitations section | Step 4: MUST include Limitations & Gaps | Add the section with all Low/Insufficient findings |
| Delivering without humanizer pass | Step 4: MUST invoke humanizer | Run humanizer on the output before delivery |

## Human Partner Signals

| User Says | Likely Issue | Action |
|-----------|-------------|--------|
| "Where did you get that?" | Claim lacks citation | Return to Step 2, navigate source, add citation |
| "That doesn't sound right" | Possible confabulation or outdated info | Re-verify the specific claim with a fresh source |
| "You're missing X" | Planning gap — sub-question not covered | Return to Step 1, add sub-question, investigate in Step 2 |
| "This is too long/short" | Output format mismatch | Adjust format — may need to switch between report and direct answer |
| "Can you go deeper on Y?" | Insufficient depth on specific sub-question | Return to Step 2 for focused investigation on Y with exhaustive depth |

## Artifact Handoff

**Receives**: research_topic (required), research_type, output_format, depth (optional)

**Produces**:
- Humanized research output in the determined format (delivered to user)
- `research-state.md` in working directory (persistent state with all claims, sources, and validation status)

## References

| File | When to Read |
|------|-------------|
| [references/source-routing.md](references/source-routing.md) | Step 1 (tool assignment) and Step 2 (tool usage patterns) |
| [references/research-question-patterns.md](references/research-question-patterns.md) | Step 1 (sub-question decomposition) |
| [references/evidence-standard.md](references/evidence-standard.md) | Step 2 (confidence ratings), Step 3 (cross-validation), Step 4 (quality gates and output templates) |
| [references/anti-hallucination-protocol.md](references/anti-hallucination-protocol.md) | Step 2 (during investigation) and Step 4 (pre-synthesis checklist) |
| [references/context-management.md](references/context-management.md) | Step 2 (extraction discipline and checkpoint cadence) |
| [templates/research-state.md.template](templates/research-state.md.template) | Step 1 (create research-state.md from this template) |
