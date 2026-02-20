# Context Management

## Research State as Backbone

The `research-state.md` file (created from `templates/research-state.md.template`) is the single source of truth during investigation. It follows Context Engineering Law 3: Retrieve Don't Remember.

**Why**: The context window is finite. Raw HTML pages, full Context7 responses, and unprocessed tool output consume attention budget rapidly. After ~10 sources, the model's attention to earlier claims degrades. The research state file persists findings to disk where they cannot be lost to context compression.

**How**: Every finding goes to disk immediately. The context window holds only the current working set (active sub-question + recent tool output). When switching sub-questions, the model reads the relevant section from research-state.md rather than relying on what it "remembers."

## Extraction Discipline

When processing a source (browser page or Context7 response):

1. **Extract claims** — Identify 3-10 specific, citable statements per source
2. **Write to research-state.md** — Record each claim with URL, date, tier, confidence, perspective
3. **Discard raw output** — Do not retain the full HTML, full API response, or full page text in context

### Extraction template per source:

```
Source: [URL]
Date: [YYYY-MM-DD]
Tier: [1/2/3]

Claims:
1. [Specific statement] — Confidence: [H/M/L/U/I]
2. [Specific statement] — Confidence: [H/M/L/U/I]
...

Relevance to sub-questions: SQ-[N], SQ-[M]
```

### What NOT to retain:
- Full HTML or rendered page content
- Complete Context7 query responses (extract relevant snippets only)
- Navigation logs (keep only final URLs, not click sequences)
- Duplicate information already recorded in research-state.md

## Checkpoint Cadence

Update research-state.md at these points:

| Trigger | Action |
|---------|--------|
| **Every 3 sources processed** | Write all new claims, update sub-question status |
| **Phase boundary** (Planning → Investigation, etc.) | Update Phase Log, verify convergence gate |
| **Contradiction found** | Record both positions immediately in Conflicts section |
| **Approaching token limit** | Full checkpoint: summarize active work, write everything to state, clear intermediates from context |
| **Switching sub-questions** | Write current SQ findings, read next SQ section from state |

## Multi-Agent Context

When sub-agents investigate in parallel:

1. **Each sub-agent owns specific sub-questions** — Assigned in Step 1 planning
2. **Each sub-agent writes to its own SQ sections** — No contention on shared sections
3. **Lead agent merges results** — Reads all SQ sections during Step 3 (Cross-Validation)
4. **Conflict resolution is centralized** — Only the lead agent resolves cross-SQ contradictions

### Sub-agent prompt template:

```
Investigate sub-questions [SQ-N, SQ-M] for research on "[topic]".
- Read research-state.md for context and assigned perspectives
- Use [assigned tool] as primary, [fallback tool] as fallback
- Write findings directly to SQ-[N] and SQ-[M] sections in research-state.md
- Mark sub-questions as Confirmed, Insufficient, or flag contradictions
- Do NOT investigate sub-questions outside your assignment
```

---

*Reference for: deep-research skill, all Steps*
