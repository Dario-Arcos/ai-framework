# Threat Model

## Pragmatic Threat Model

The current model assumes AI systems have a probabilistic tendency toward reward hacking when a shortcut can satisfy a visible metric faster than genuine user intent. The mitigations in this release do not create a sandbox. They raise the cost of bypass, make bypass more visible, and preserve a committed external contract that is harder to weaken silently.

Practical consequences:

- Scenario artifacts are defense-in-depth, not a hard security boundary.
- Bypass via raw Bash under the same UID is still possible, but it requires explicit intent and extra steps.
- Write-once scenarios, amend markers, verification tracking, and telemetry are meant to turn silent metric-gaming into observable policy violations.

## Eval-Awareness Consideration

SPEC §3.5 calls out the eval-awareness risk directly: once a model recognizes the structure of an evaluation, it may optimize for passing the measurement rather than satisfying the underlying task. The Anthropic Opus 4.6 BrowseComp case is the cautionary example here. The scenarios architecture responds by moving the primary contract into committed scenario artifacts and by treating tests as evidence, not authority.

## Known Out-Of-Scope Bypasses

These bypasses are acknowledged in the current release and are intentionally out of scope for the pragmatic model:

- Arbitrary scripts such as `python -c`, `perl -i`, or custom binaries.
  These are not regex-detectable without sandboxing or syscall-level controls.
- Direct skill-state writes such as `echo '{"skill": "sop-reviewer"}' > /tmp/sdd-skill-*`.
  This has the same cost profile as writing an amend marker directly: it raises the bar, but it is not a separate trust boundary.
- Git plumbing such as `git hash-object` plus `git update-index --cacheinfo`.
  This requires explicit multi-step intent and falls outside heuristic command guards.

## Strong Threat Model

This release does not implement the strong model. The roadmap version would require stronger separation:

- External scenarios store, such as a sidecar repo or remote authority.
- Sandboxed validator running with separate credentials.
- Implementation-time blindness, where the model cannot read scenario artifacts while writing code.
