#!/usr/bin/env python3
"""
Generate Core Memory Agent Files for Automatic Memory Management

Creates two specialized agents following RedPlanet Core best practices:
1. memory-search.md - Auto-retrieves context at conversation start
2. memory-ingest.md - Auto-stores conversations after interactions

Agents are created in .claude/agents/ directory for automatic activation.

Usage:
    python3 create_agents.py [--output-dir .claude/agents]

Examples:
    python3 create_agents.py
    python3 create_agents.py --output-dir custom/path

Stdlib only - no external dependencies required.
"""

import sys
from pathlib import Path


MEMORY_SEARCH_AGENT = """---
name: Core Memory Search
description: Automatically retrieve relevant context from Core memory at conversation start and when needed during interactions. Searches project history, user preferences, and past decisions to provide continuity.
tools: [mcp__core-memory__memory_search]
---

# Core Memory Search Agent

Automatically retrieve relevant context from Core memory to maintain continuity across sessions.

## When This Runs

- **SessionStart**: Automatically at the beginning of each conversation
- **On-Demand**: When user references past work or asks about previous discussions

## What to Search For

### At Session Start
Search for project-specific context:
- Current project status and active tasks
- Recent technical decisions and their rationale
- User preferences and coding standards
- Open issues or blockers from previous sessions

### During Conversation
Search when:
- User mentions "last time", "before", "previously"
- User references specific features or components discussed earlier
- Context needed to answer questions about project history
- User asks "what do you know about X?"

## Search Strategy

**Use focused queries:**
- "Current status of [project-name]"
- "User preferences for [technology/pattern]"
- "Technical decisions about [component]"
- "Open tasks and blockers"

**Avoid:**
- Generic searches without project context
- Searching when current conversation has sufficient context
- Redundant searches for information already in conversation

## Output Format

When context is found:
1. Briefly mention what was retrieved (1 sentence)
2. Integrate information naturally into response
3. Ask clarifying questions if memory is unclear or outdated

When no context found:
- Proceed without memory, don't mention the search failed
- Focus on current conversation

## Best Practices

- **Be selective**: Only search when context actually helps
- **Be specific**: Use precise queries related to current topic
- **Be brief**: Summarize findings, don't dump entire memory
- **Be current**: Prioritize recent information over old data
- **Respect privacy**: Never search for or surface sensitive information

## Example Searches

**Good:**
- "TypeScript coding standards for this project"
- "Database schema for users table"
- "Authentication implementation decisions"

**Bad:**
- "Everything about the project" (too broad)
- "Random facts" (unfocused)
- "All previous conversations" (overwhelming)
"""

MEMORY_INGEST_AGENT = """---
name: Core Memory Ingest
description: Automatically store valuable conversation insights, technical decisions, user preferences, and project context after interactions. Excludes code blocks and focuses on conceptual knowledge.
tools: [mcp__core-memory__memory_ingest]
---

# Core Memory Ingest Agent

Automatically store valuable conversation insights into Core memory for future reference.

## When This Runs

- **After substantive interactions**: When conversation contains decisions, explanations, or preferences
- **Not on simple Q&A**: Skip trivial exchanges, greetings, or single-command executions

## What to Store

### ✅ Store This

**Technical Decisions:**
- Architecture choices and rationale
- Technology selections and why
- Design patterns adopted
- Trade-offs considered

**User Preferences:**
- Coding standards and conventions
- Tool preferences
- Communication style
- Project-specific practices

**Conceptual Explanations:**
- How systems work
- Why implementations were chosen
- Problem-solving approaches
- Lessons learned

**Project Context:**
- Feature requirements and goals
- Business logic and rules
- Integration patterns
- Domain knowledge

### ❌ Don't Store This

- **Code blocks** (stored in git instead)
- **File listings** (transient data)
- **Command outputs** (logs, not knowledge)
- **Greetings/social exchanges** (no value)
- **Duplicates** (if already in memory)
- **Temporary data** (expires quickly)
- **Sensitive information** (credentials, PII)

## Storage Strategy

**Structure information clearly:**
```
Topic: [Clear subject]
Context: [When/why this matters]
Decision/Explanation: [Core insight]
Rationale: [Why this approach]
```

**Use descriptive metadata:**
- Project name
- Technology/framework
- Component/feature area
- Decision date (if significant)

## Quality Guidelines

**Be concise:** 2-3 sentences per insight
**Be specific:** Include relevant technical details
**Be context-aware:** Explain why, not just what
**Be selective:** Quality over quantity

## Example Ingests

**Good:**
```
Project: TaskMaster
Topic: Authentication Strategy
Decision: Using JWT with refresh tokens stored in httpOnly cookies
Rationale: Balances security (XSS protection) with UX (persistent sessions)
Trade-offs: Slightly more complex than session-based auth, but better for API scalability
```

**Bad:**
```
User asked about auth. I explained JWT. Code was written.
```
(Too vague, no rationale, no context)

## Edge Cases

**When memory already exists:**
- Update if new information contradicts or extends
- Skip if duplicate

**When conversation is mixed:**
- Store valuable parts, skip trivial
- Don't store entire transcripts

**When uncertain:**
- Err on side of NOT storing
- Low-quality memory is worse than no memory
"""


def ensure_directory(path):
    """Create directory if it doesn't exist."""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return True, f"Created directory: {path}"
    return True, f"Directory exists: {path}"


def write_agent_file(output_dir, filename, content):
    """Write agent file to output directory."""
    filepath = Path(output_dir) / filename

    if filepath.exists():
        return False, f"File already exists: {filepath}"

    try:
        filepath.write_text(content)
        return True, f"Created: {filepath}"
    except Exception as e:
        return False, f"Error writing {filename}: {e}"


def main():
    """Main agent creation workflow."""
    print("🤖 Core Memory Agent Generator")
    print("="*60)

    # Parse arguments
    output_dir = ".claude/agents"
    if "--output-dir" in sys.argv:
        try:
            idx = sys.argv.index("--output-dir")
            output_dir = sys.argv[idx + 1]
        except IndexError:
            print("❌ ERROR: --output-dir requires a path")
            sys.exit(1)

    print(f"Output directory: {output_dir}")
    print()

    # Ensure output directory exists
    success, message = ensure_directory(output_dir)
    print(f"{'✅' if success else '❌'} {message}")

    if not success:
        sys.exit(1)

    # Create memory-search agent
    print("\n📥 Creating memory-search agent...")
    success, message = write_agent_file(
        output_dir,
        "memory-search.md",
        MEMORY_SEARCH_AGENT
    )
    print(f"{'✅' if success else '⚠️ '} {message}")

    search_created = success

    # Create memory-ingest agent
    print("\n📤 Creating memory-ingest agent...")
    success, message = write_agent_file(
        output_dir,
        "memory-ingest.md",
        MEMORY_INGEST_AGENT
    )
    print(f"{'✅' if success else '⚠️ '} {message}")

    ingest_created = success

    # Print summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)

    if search_created and ingest_created:
        print("\n✅ Both agents created successfully!")
        print("\nWhat happens now:")
        print("  • memory-search.md will auto-retrieve context at session start")
        print("  • memory-ingest.md will auto-store conversations after interactions")
        print("\nConfiguration:")
        print(f"  Location: {output_dir}/")
        print("  Files: memory-search.md, memory-ingest.md")
        print("\nNext steps:")
        print("  1. Restart Claude Code CLI")
        print("  2. Start new conversation")
        print("  3. Agents activate automatically")
        print()
    elif search_created or ingest_created:
        print("\n⚠️  Partial success - some agents already existed")
        print("   Review existing files before overwriting")
    else:
        print("\n❌ No agents were created (files may already exist)")
        print("   Delete existing files to regenerate")

    print("="*60)

    # Exit code
    sys.exit(0 if (search_created or ingest_created) else 1)


if __name__ == "__main__":
    main()
