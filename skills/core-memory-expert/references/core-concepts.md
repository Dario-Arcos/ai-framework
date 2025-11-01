# RedPlanet Core - Architecture & Concepts

Comprehensive reference for Core's memory architecture, data model, and operational mechanics.

## What is Core?

Core (Contextual Observation & Recall Engine) is a unified memory system that persists context across multiple AI tools through a temporal knowledge graph.

**Problem Solved:** AI tools operate in isolation without shared context or persistent memory.

**Solution:** Portable memory layer accessible via Model Context Protocol (MCP) enabling context sharing across Claude, Cursor, VS Code, and other tools.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ AI TOOLS (Claude, Cursor, VS Code, etc.)                │
└───────────────────┬─────────────────────────────────────┘
                    │ MCP Protocol
┌───────────────────▼─────────────────────────────────────┐
│ CORE MCP SERVER                                         │
│  ├─ memory_search (retrieval)                           │
│  └─ memory_ingest (storage)                             │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ MEMORY CREATION PIPELINE                                │
│  1. Normalization    → Contextualize & standardize      │
│  2. Extraction       → Identify entities/relationships  │
│  3. Resolution       → Handle contradictions            │
│  4. Graph Integration → Connect temporal graph          │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ TEMPORAL KNOWLEDGE GRAPH                                │
│  Entities + Relationships + Provenance + Time           │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│ MEMORY RECALL SYSTEM                                    │
│  Keyword → Semantic → Graph Traversal → Re-rank         │
└─────────────────────────────────────────────────────────┘
```

## Memory Creation Pipeline

### Phase 1: Normalization

**Purpose:** Contextualize new information and standardize terminology.

**Process:**
- Adds contextual metadata (timestamp, source, conversation ID)
- Standardizes terminology across different inputs
- Resolves abbreviations and aliases

**Example:**
```
Input: "I prefer TS"
Normalized: "User prefers TypeScript for development (timestamp: 2025-10-31, source: Claude-conversation-abc)"
```

### Phase 2: Extraction

**Purpose:** Identify entities, statements, and relationships from normalized text.

**Entities Extracted:**
- People (users, developers, team members)
- Technologies (languages, frameworks, tools)
- Projects (repositories, applications, features)
- Concepts (patterns, practices, decisions)

**Relationships Extracted:**
- Uses (User → TypeScript)
- Works_On (User → Project)
- Prefers (User → Tool)
- Decided (Team → Architecture)

**Example:**
```
Input: "We're building TaskMaster with React and TypeScript"
Entities: [TaskMaster:Project, React:Framework, TypeScript:Language]
Relationships: [TaskMaster-uses→React, TaskMaster-uses→TypeScript]
```

### Phase 3: Resolution

**Purpose:** Detect contradictions and preserve multiple perspectives with provenance.

**Contradiction Handling:**
- **Track evolution:** "Previously preferred Vue, now prefers React (changed: 2025-10-30)"
- **Preserve context:** Multiple valid perspectives with timestamps
- **Reliability scoring:** Recent statements weighted higher

**Example:**
```
Old: "Prefer Vue for frontend" (2025-09-01)
New: "Prefer React for frontend" (2025-10-31)
Resolution: Update preference, keep history with timeline
```

### Phase 4: Graph Integration

**Purpose:** Connect data into temporal knowledge graph.

**Graph Structure:**
```
Node: Entity
  ├─ Type (Person, Technology, Project, Concept)
  ├─ Properties (name, description, metadata)
  └─ Timestamp (first seen, last updated)

Edge: Relationship
  ├─ Type (uses, works_on, prefers, decided)
  ├─ Properties (strength, confidence)
  ├─ Provenance (source, conversation ID)
  └─ Timestamp (when established, last confirmed)
```

**Temporal Tracking:**
- Who said what
- When it was said
- Why it was said
- What changed over time

## Memory Recall System

### Multi-Angle Search

**1. Keyword Search**
- Exact string matching
- Fast, deterministic
- Use for: names, IDs, specific terms

**2. Semantic Search**
- Conceptual similarity via embeddings
- Finds related ideas
- Use for: "similar to X", conceptual queries

**3. Graph Traversal**
- Follows entity connections
- Discovers relationships
- Use for: "what's related to X", "dependencies of Y"

### Re-Ranking

**Factors:**
- **Relevance:** How closely matches query
- **Recency:** Newer information preferred
- **Reliability:** Source trust + confirmation frequency
- **Relationship strength:** Direct > indirect connections

### Filtering

**Temporal Filtering:**
- Last week, last month, all time
- Before/after specific dates

**Reliability Filtering:**
- High confidence (confirmed multiple times)
- Medium confidence (single source)
- Low confidence (contradicts other data)

## Data Model

### What Core Stores

**✅ Store:**
- Conversation insights (decisions, explanations)
- User preferences (tools, patterns, standards)
- Technical context (architecture, schemas, APIs)
- Project status (features, blockers, goals)
- Conceptual knowledge (how things work, why chosen)

**❌ Don't Store:**
- Code blocks (use git instead)
- Logs/outputs (transient)
- Sensitive data (credentials, PII)
- File contents (use version control)

### Storage Granularity

**Optimal level:** Conceptual insights, not raw transcripts

**Too granular:**
```
"User typed 'npm install'"
"User ran tests"
"Tests passed"
```

**Right level:**
```
"Project uses npm for package management. Testing with Jest configured for TypeScript with coverage thresholds of 80%."
```

## Performance Characteristics

**Benchmarks (LoCoMo Dataset):**
- **Average accuracy:** 88.24%
- **Single-hop reasoning:** High accuracy
- **Multi-hop reasoning:** High accuracy
- **Open-domain knowledge:** High accuracy
- **Temporal reasoning:** High accuracy

**Scale:**
- Handles 300+ turn conversations
- Maintains context across sessions
- Supports multiple concurrent projects

## Integration Patterns

### Observation Streams

**1. Environment Monitoring**
- GitHub: commits, PRs, issues
- Slack: messages, threads
- Linear: tasks, status updates
- Notion: pages, databases

**2. Conversation Capture**
- Claude conversations
- Cursor interactions
- VS Code sessions

**3. Manual Input**
- Direct chat with Core
- Explicit "add to memory" commands
- Reflective notes

### Tool Access Pattern

**Single MCP URL:**
```
https://core.heysol.ai/api/v1/mcp?source=[Tool-Name]
```

**Per-tool configuration:**
- `?source=Claude-Code` (mandatory)
- `&integrations=github,linear` (optional)
- `&no_integrations=true` (Core tools only)

## Security Model

**Authentication:**
- OAuth 2.0 (recommended for production)
- API Keys (development only)

**Encryption:**
- TLS 1.3 in transit
- AES-256 at rest

**Access Control:**
- Workspace-based isolation
- Role-based permissions
- User owns their memory graph

## Best Practices

### Memory Hygiene

**Regular review:** Audit what's stored monthly
**Prune outdated:** Remove obsolete information
**Update contradictions:** Keep memory current
**Verify sensitive data:** Ensure no credentials stored

### Query Strategy

**Be specific:** "Authentication approach for API" > "tell me everything"
**Use temporal filters:** "decisions made last week"
**Follow relationships:** "what depends on X"

### Storage Strategy

**Focus on why:** Rationale > implementation details
**Include context:** When, why, trade-offs
**Update > duplicate:** Revise existing over creating new
**Quality > quantity:** 10 high-value insights > 100 trivial facts

## Troubleshooting Concepts

**Memory not updating:**
- Check if memory_ingest tool is active
- Verify conversation contains storable insights
- Review agent configuration for auto-storage

**Search returns nothing:**
- Information may not be stored yet
- Try broader queries
- Check temporal filters

**Contradictory results:**
- Expected behavior (Core tracks evolution)
- Review timeline to see what changed when
- Update if outdated information is wrong

## Further Reading

- MCP Configuration: mcp-configuration.md
- Troubleshooting Guide: troubleshooting.md
- Integration Catalog: integrations.md
- Official docs: docs.heysol.ai
