---
name: holdout-enforcement
created_at: 2026-04-26
revision: R1
strategic_intent: |
  The verification-before-completion holdout exists to block commits when
  scenarios are not satisfied. Today it is bypassable: a single skill
  invocation sets a 30-min flag covering ALL subsequent commits, and the
  gate trusts the flag without checking which scenarios were actually
  verified. Closing this is the difference between a holdout and security
  theater.
---

# Holdout Enforcement — close skill-flag bypass

## Mission

Make the verification-before-completion gate **non-decorative**. Today it
mistakes "skill was invoked once in the last 30 min" for "scenarios are
satisfied". Close the 4 bypass vectors with the smallest change that still
encodes best practice.

## Findings (verified live)

| ID | Sev | Module | Pattern | Bypass enabled |
|----|-----|--------|---------|----------------|
| **F1** | **P0** | `_sdd_state.py:707` `read_skill_invoked` | TTL-based, ignores `sid` | One skill call covers every commit for 30 min, across sessions/teammates. |
| **F2** | **P0** | `_sdd_scenarios.py:575` `has_pending_scenarios` | Checks flag, not scenario satisfaction | Skill invoked under spec A still clears gate when committing changes to spec B (or no spec at all). |
| **F3** | P1 | `verification-before-completion` skill | Writes flag without evidence | No scenario hashes recorded. Edits to scenario file after invocation are silently accepted. |
| **F4** | P2 | `sdd-test-guard.py:1102-1112` `TaskUpdate(completed)` gate | Redundant with git-commit gate, fires on different lifecycle | Skipping `TaskUpdate(completed)` (or using `deleted`/no-task workflow) avoids the symbolic gate. The substantive commit gate is the only one that matters. |

**Live proof of F1:** `/var/folders/.../sdd-skill-verification-before-completion-d999fca8122d.json` exists from a single skill invocation 1h ago. Every commit this session passed the gate without re-invocation: spec commit `d5f0655`, Bundle 0 merge `69427b3`, Bundle 1 commit `a5085f7`. Three commits, one stale flag.

## Design — one-shot, scenario-bound evidence

Replace the boolean flag with a **consumable, scenario-bound evidence file**:

1. **One-shot semantics.** The skill writes evidence. The git-commit gate **consumes** (deletes) the evidence on success. Next commit needs a new invocation. No 30-min coverage window.

2. **Scenario hash binding.** The evidence file records the SHA-256 of every `*.scenarios.md` under discovery roots **at invocation time**. The gate re-hashes at commit time. Any mismatch (added scenario, edited scenario, removed scenario) invalidates the evidence — caller must re-invoke skill against current scenarios.

3. **Single gate.** Remove the `TaskUpdate(completed)` gate. Keep the `Bash(git commit|merge|push)` gate. Symbolic task-tracker actions don't gate substantive history changes.

4. **Explicit bypass preserved.** `git commit --no-verify` continues to work — but the bypass log line escalates to a structured telemetry record (`.claude/scenarios/.bypass-log.jsonl` with timestamp + scenario hash list at bypass time). No silent escapes.

## Components

| File | Bundle | Change shape |
|------|--------|--------------|
| `hooks/_sdd_state.py` | A | New `read_evidence(cwd) → dict\|None` and `consume_evidence(cwd) → bool` (atomic delete-on-read). Deprecate `read_skill_invoked` for verification skill (keep for sop-code-assist/sop-reviewer). |
| `hooks/_sdd_scenarios.py` | A+B | `has_pending_scenarios` calls evidence check; new `current_scenarios_hashes(cwd)` enumerates `*.scenarios.md` and SHA-256s each. |
| `hooks/sdd-test-guard.py` | A+B | git-commit gate: read evidence, compare scenario-hash list to current, BLOCK if mismatch or absent. Atomic consume on PASS. Remove TaskUpdate(completed) gate. |
| `skills/verification-before-completion/SKILL.md` + helper | A+B | Skill execution writes evidence file with: invocation timestamp, scenario-hash list, optional per-SCEN execution evidence (deferred to C). |
| `hooks/test_holdout_enforcement.py` | A+B | NEW. Adversarial parametrized tests: stale flag, edited scenario, multi-commit reuse, Ralph + non-Ralph parity. |

## Bundles (ordered)

**Bundle A — One-shot consumption (closes F1)**
- Replace TTL flag with consumable evidence file
- git-commit gate atomic-deletes on PASS
- No scenario binding yet — evidence is a freshness signal only
- Estimated +8 tests

**Bundle B — Scenario-hash binding (closes F2 + F3)**
- Evidence records `[{path, sha256}]` for each `*.scenarios.md`
- Gate re-hashes at commit, requires set-equality
- Skill helper module computes hashes
- Estimated +10 tests

**Bundle C (deferred) — Per-SCEN execution evidence**
- Each SCEN id mapped to execution proof (command + output snippet)
- Skill produces; gate verifies coverage of changed files
- Out of scope for first pass — bigger redesign

## Iron rules

1. **Backwards compatible for Ralph + non-Ralph.** Both modes must continue to work end-to-end. Test parity required.
2. **No regression on legitimate commits.** A commit AFTER fresh skill invocation MUST pass; a commit without invocation MUST fail. No new false positives.
3. **`--no-verify` still works.** Explicit bypass remains the escape hatch. Telemetry escalation but no extra blocks.
4. **No scope creep.** Don't refactor unrelated state primitives. Touch only the verification skill, the gate logic, and the evidence path.
5. **SDD red-green per fix.** Adversarial bypass test fails before, passes after.

## Out of scope

- Per-SCEN execution evidence (Bundle C — deferred to its own spec).
- Structured telemetry consumer for `--no-verify` (logging exists; reader is a separate concern).
- Cryptographic signature on evidence (HMAC). Acceptable risk: agent has filesystem access already; trust boundary is the workflow, not the file.
- Replacing `read_skill_invoked` for sop-code-assist / sop-reviewer (different lifecycle, different semantics — keep TTL there).

## Acceptance

- 8 SCEN-401..408 satisfied (see scenarios file)
- `pytest hooks/ -q` ≥ baseline + 18, 0 failures
- Live proof of F1 closure: a single skill invocation followed by two `git commit` attempts MUST block the second
- Live proof of F2 closure: skill invoked → edit scenario file → git commit MUST block
- 2 commits to main (Bundle A, Bundle B)
