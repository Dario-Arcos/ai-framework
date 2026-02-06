# Long-Horizon Context Patterns

## Contents

- Strategy Selection
- Compaction (implementation, tuning, tool result clearing)
- Structured Note-Taking (patterns, hygiene, anti-patterns)
- Sub-Agent Architectures (pattern, token economics, prompt template)
- Compressed Index Pattern (format, implementation)
- Combining Strategies

## Overview

Three strategies for tasks that exceed context window limits: compaction, structured note-taking, and sub-agent architectures. They are not mutually exclusive. Choose based on task characteristics, combine for very long sessions.

## Strategy Selection

| Task Characteristic | Best Strategy | Why |
|---|---|---|
| Extensive back-and-forth | Compaction | Maintains conversational flow without losing thread |
| Iterative development with milestones | Structured notes | Tracks progress across phases, survives compaction |
| Complex research / parallel exploration | Sub-agents | Clean context per branch, no cross-contamination |
| Navigation of large codebases | Compressed index | Passive map eliminates search decisions |
| Very long tasks (hours) | Combine all three | Each addresses a different constraint |

## Compaction

### Implementation

- Pass full message history to model with a compaction prompt
- **Preserve**: architectural decisions, unresolved issues, implementation details, file paths, variable/function names, error states
- **Discard**: redundant tool outputs, old search results, verbose error logs, superseded plans
- Keep 5 most recently accessed files alongside summary

### Compaction Prompt Template

```
Summarize this conversation for context reinitiation.

Preserve:
- Architectural decisions and their rationale
- Unresolved issues, blockers, open questions
- File paths, function/variable names, line numbers referenced
- Error states and their diagnosis
- Current task progress and next steps

Discard:
- Raw tool outputs (keep only conclusions drawn from them)
- Superseded plans or abandoned approaches
- Verbose error logs (keep only root cause)
- Redundant search results

Format: Bullet points grouped by topic. Include the 5 most recently accessed file paths.
Target: Under 2000 tokens.
```

### Tuning the Compaction Prompt

1. **Start by maximizing recall** -- capture everything that could be relevant. Over-inclusion is cheaper than lost context.
2. **Iterate to improve precision** -- eliminate content that never gets referenced after compaction.
3. **Test on complex agent traces**, not simple conversations. Simple exchanges compress trivially; the hard cases reveal prompt weaknesses.

### Lightest-Touch: Tool Result Clearing

Before full compaction, try clearing old tool call results. Once a tool was called deep in history, the raw output is rarely needed again -- only the conclusion drawn from it matters. This is the safest first step because it removes bulk without touching reasoning.

```
Before: [tool_call: grep "auth" → 200 lines of results] → [analysis: "auth handled in middleware/auth.ts"]
After:  [tool_call: grep "auth" → <cleared>] → [analysis: "auth handled in middleware/auth.ts"]
```

The analysis line carries the signal. The raw grep output is dead weight.

### Compaction Trigger Heuristics

- **Token threshold**: Trigger when context reaches ~80% of window limit
- **Turn count**: After N tool-heavy turns, evaluate whether clearing results is sufficient
- **Signal decay**: If the agent starts repeating searches or forgetting prior conclusions, context is degraded -- compact immediately
- **Manual trigger**: User or orchestrator explicitly requests compaction

### Warning

Overly aggressive compaction loses subtle context whose importance emerges later. A design constraint mentioned in turn 3 might become critical in turn 40. Better to over-include than under-include. You can always compact again; you cannot recover lost context.

## Structured Note-Taking

### Patterns

- **Todo list**: Track progress, completed items, blockers. Maps directly to task management tools (TaskCreate, TaskUpdate).
- **NOTES.md / scratchpad**: Architectural decisions, key findings, dependency relationships. Free-form but scannable.
- **Structured state file**: JSON/YAML with current state, counters, checkpoints. Machine-readable for automated resumption.

### When Notes Beat Context

- Task spans multiple compaction cycles (notes survive compaction)
- Critical decisions made early affect later work (notes are always retrievable)
- Progress tracking across hundreds of steps (counters, checklists)
- Multiple agents working on related tasks (shared state file)

### Example

```markdown
## Session Notes
- Architecture: event-driven with Redis pub/sub
- Blocker: auth service returns 401 on refresh tokens (see middleware/auth.ts:47)
- Completed: user model, API routes for /users/*, input validation
- Next: implement token refresh flow
- Decision: chose JWT over session cookies (stateless, scales horizontally)
- Files modified: src/models/user.ts, src/routes/users.ts, src/middleware/auth.ts
```

### Note Hygiene

- Keep notes scannable: bullet points, not paragraphs
- Date or phase-stamp entries so stale notes are identifiable
- Prune completed items periodically (move to "done" section, do not delete)
- Include file paths and line numbers -- vague references lose value after compaction

### Anti-Pattern

Writing notes that duplicate what is already in context. Notes should capture what will be lost on compaction, not echo the current conversation. If it is visible in the current window and will survive until next compaction, do not write it down.

## Sub-Agent Architectures

### Pattern

```
Main Agent (coordinator)
├── Sub-agent A: deep research task    → returns 1-2K summary
├── Sub-agent B: code implementation   → returns result + key decisions
└── Sub-agent C: validation/testing    → returns pass/fail + issues found
```

### Key Principles

- Each sub-agent starts with **clean context** (only the information it needs for its task)
- Sub-agents may use 10K+ tokens internally for exploration, reasoning, tool calls
- Returns **condensed summary** (1-2K tokens typically) -- the distilled output
- Separation of concerns: search context, error traces, and intermediate results stay isolated
- Main agent synthesizes results without carrying the weight of each exploration
- Failed sub-agent paths do not pollute the main agent's context

### When to Use Sub-Agents

- Task naturally decomposes into independent subtasks
- Deep exploration needed without polluting main context
- Parallel work on different aspects of a problem
- Research tasks where most retrieved content is discarded after analysis

### Token Economics

```
Without sub-agents:
  Main context: 50K research + 30K implementation + 20K validation = 100K tokens

With sub-agents:
  Main context: 2K research summary + 2K impl summary + 1K validation = 5K tokens
  Sub-agents: 50K + 30K + 20K (each isolated, each discarded after summary)
```

### Sub-Agent Prompt Template

```
You are a focused sub-agent. Your task: {task_description}

Context:
{only_relevant_context}

Constraints:
- Complete the task using available tools
- Return a summary of: findings, decisions made, files changed, open questions
- Keep your summary under 1500 tokens
- Do NOT include raw tool outputs in your summary
```

The constraint on summary length forces the sub-agent to distill. Without it, sub-agents return full transcripts that defeat the purpose.

## Compressed Index Pattern

### Format

```
[Domain Docs Index]|root: ./docs
|IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning
|section-a:{file1.md,file2.md,file3.md}
|section-b/subsection:{fileA.md,fileB.md}
|section-c:{config.md,deploy.md,troubleshoot.md}
```

### Implementation

1. Use pipe-delimited format for maximum compression
2. Group files by domain or feature
3. Include root path so the agent resolves reads without guessing
4. Add the retrieval-led reasoning instruction at the top of the index
5. Update the index when files are added or removed

### When NOT to Use

- Small projects where full docs fit comfortably in context
- Rapidly changing file structures (index goes stale)
- Tasks where the agent needs every file simultaneously (just inline them)

## Combining Strategies

For tasks spanning hours or multiple sessions, layer all three strategies:

1. **Compressed index** as permanent passive context (always present, never compacted)
2. **Structured notes** for decisions, progress, and state that must survive indefinitely
3. **Sub-agents** for deep exploration phases that would bloat the main context
4. **Compaction** as the periodic maintenance step that resets the conversation while preserving thread

Sequencing: the compressed index is set once at session start. Notes accumulate throughout. Sub-agents spin up for intensive phases. Compaction fires when context approaches limits, using notes as an anchor to validate the summary.

### Failure Mode

Running all strategies simultaneously from the start adds overhead to simple tasks. Start with compaction alone. Add notes when you hit your first compaction cycle. Spin up sub-agents when a subtask is clearly isolatable. The strategies are responses to specific pressures, not upfront configuration.

The goal is not minimal context. The goal is **maximal signal density** -- every token in the window earns its place.
