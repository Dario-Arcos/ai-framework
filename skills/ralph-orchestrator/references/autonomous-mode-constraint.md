# Autonomous Mode Constraints

**ALL autonomous-capable skills MUST follow these constraints:**

- NEVER use AskUserQuestion under any circumstance
- NEVER block waiting for user input
- If blocked by missing information or ambiguity:
  1. Document blocker in `{output_dir}/blockers.md` with full details
  2. Make reasonable assumption and document rationale
  3. Continue with remaining work
- Choose safest/simplest approach when ambiguous
- Document all assumptions in output artifacts

---

*Version: 2.0.0 | Updated: 2026-02-15*
