# Research Question Patterns

## Characteristics of Effective Sub-Questions

Good sub-questions are:

1. **Falsifiable** — Can be answered with evidence that could prove them wrong. "Is React faster than Vue?" is falsifiable; "Is React good?" is not.
2. **Scoped** — Bounded by time, context, or domain. "What is Prisma's query performance on PostgreSQL with 10K+ rows?" vs. "How does Prisma perform?"
3. **Independent** — Answerable without first resolving other sub-questions. If SQ-3 requires SQ-1's answer, merge them or sequence explicitly.
4. **Perspective-rich** — Naturally invite multiple viewpoints. "How does X handle Y?" can be asked from performance, DX, maintenance, and ecosystem perspectives.

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| "Is X good?" | Unfalsifiable, no criteria | Define "good" -> "Does X meet criteria A, B, C?" |
| "Tell me about X" | Unbounded, invites rambling | Decompose into specific aspects |
| "What do experts think?" | Authority laundering | "What does [specific source] report about [specific metric]?" |
| "What's the best Y?" | Subjective without criteria | "Which Y has lowest latency for use case Z?" |
| "How does X compare to Y?" | Too broad without dimensions | Split into: performance, DX, ecosystem, cost dimensions |

## Decomposition Heuristics

Start with the factual core, then layer constraints and judgment:

1. **Factual core first** — What can be verified with primary sources?
2. **Constraints second** — What requirements narrow the answer? (scale, team size, existing stack)
3. **Judgment last** — What requires weighing tradeoffs? (recommendations, risk assessment)

### Decomposition by research type:

- **API/Framework**: capabilities -> limitations -> migration path -> ecosystem health
- **Technology Decision**: requirements match -> performance -> DX -> ecosystem -> cost -> migration
- **Architecture**: constraints -> patterns that fit -> tradeoffs -> prior art -> failure modes
- **Market/Industry**: current state -> trends -> drivers -> risks -> projections
- **Current Events**: what happened -> timeline -> who's affected -> implications -> what's next

## Worked Example

**Topic**: "Should we migrate from Express to Fastify for our Node.js API?"

**Decomposition:**

| # | Sub-Question | Type | Perspectives |
|---|-------------|------|-------------|
| SQ-1 | What is Fastify's request throughput vs Express on comparable workloads? | Factual | Benchmark authors, framework maintainers |
| SQ-2 | What Express middleware do we use and what are Fastify equivalents? | Factual | Ecosystem, migration guides |
| SQ-3 | What is the typical migration effort (team-weeks) for a mid-size Express API? | Factual | Case studies, migration reports |
| SQ-4 | What are Fastify's known limitations or breaking changes in recent versions? | Factual | GitHub issues, changelog, community reports |
| SQ-5 | Does Fastify's plugin architecture fit our authentication and validation patterns? | Constraint | Architecture, DX, security |
| SQ-6 | Given SQ-1 through SQ-5, is the migration worth the investment for our context? | Judgment | Performance, team capacity, risk tolerance |

Note: SQ-6 depends on SQ-1-5 and is explicitly judgment. It will not be answered with evidence alone — this is documented upfront.

---

*Reference for: deep-research skill, Step 1 (Planning)*
