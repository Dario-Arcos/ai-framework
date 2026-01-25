# Supervision Modes Reference

Two approaches based on human involvement level.

## HITL (Human-in-the-Loop)

### Use For

- Learning how Ralph handles your codebase
- Risky tasks (auth, payments, migrations)
- Architectural decisions that need approval
- First-time setup of a new project

### Configuration

```bash
./loop.sh 1     # Single iteration, review after
./loop.sh 5     # Few iterations, frequent review
```

### Behavior

- Short runs (1-5 iterations)
- Human reviews after each batch
- Adjust Signs and specs between runs
- High confidence before AFK mode

---

## AFK (Away-From-Keyboard)

### Use For

- Bulk implementation work
- Low-risk, well-defined tasks
- Overnight batch processing
- Tasks with strong test coverage

### Configuration

```bash
./loop.sh 20    # Medium batch
./loop.sh 50    # Long overnight run
./loop.sh       # Unlimited (until complete)
```

### Behavior

- Long runs (10-50+ iterations)
- Circuit breaker handles failures
- Review aggregated results
- Trust backpressure gates

---

## Progression Path

```
First project    -> HITL (1-5)    -> Learn patterns
Stable codebase  -> AFK (10-20)   -> Bulk work
High test coverage -> AFK (50+)  -> Overnight runs
Full confidence  -> AFK (unlimited) -> Until complete
```

**Recommendation:** Start HITL, graduate to AFK as confidence grows.

---

## Security Considerations

**Use protection:**
- Run with `--dangerously-skip-permissions` in sandbox only
- "It's not if it gets popped, it's when"
- Isolated environment (Docker/VM) recommended for AFK

### Docker Sandbox Setup (Optional)

```bash
# Create isolated container
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  node:20 bash

# Inside container
npm install
./loop.sh
```

This prevents any filesystem damage outside the mounted volume.
