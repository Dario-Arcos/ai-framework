# Questioning Protocol

## Core Discipline

When gathering information from the user during discovery:

### Constraints

1. **ONE question per message** - Never batch multiple questions together
2. **Wait for response** - Do not proceed until user answers
3. **Append immediately** - Add Q&A to discovery document after each answer
4. **Confirm success** - Verify append before asking next question

### Flow

```text
Ask question → Wait for answer → Append to document → Confirm → Next question
```

### Example

**CORRECT:**
```text
Claude: "What technology constraints exist for this project?"
User: "Must use Python 3.9+, no external API calls"
[Appends to discovery.md]
Claude: "Got it, added to discovery. Next: What are the performance requirements?"
```

**INCORRECT:**
```text
Claude: "What are the constraints? And the risks? And prior art you know of?"
```

### Why This Matters

- Users can think deeply about one question
- Answers are captured immediately (no lost information)
- Discovery document stays synchronized with conversation
- Prevents overwhelming users with multiple questions

---

*This protocol applies to ALL discovery steps that involve user questioning.*
