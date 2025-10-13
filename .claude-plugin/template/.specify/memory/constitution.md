<!--
Sync Impact Report - Constitution v2.1.2
Version change: v2.1.1 → v2.1.2 (Command substitution rationale documentation)
Modified principles: All 5 core principles preserved
Modified sections: Article IX §1 (Shell Scripting) - added technical rationale for backticks mandate, documented parser limitation with examples
Added sections: None
Removed sections: None
Templates requiring updates: None (clarification only, no breaking changes)
Follow-up TODOs: None
-->

# AI Framework Constitution

**Version**: 2.1.2 | **Ratified**: 2025-09-20 | **Last Amended**: 2025-10-04

> This Constitution is the _highest law_ of how AI Framework conceives, designs, builds, and operates digital products with and for AI. It defines purpose, rights, duties, powers, limits, due process, and amendment. Everything else—policies, playbooks, checklists—derives authority from here and is void where it conflicts.

---

## Preamble

We exist to **amplify human impact** through AI-first software development. We therefore bind ourselves to a compact that privileges **clarity over cleverness**, **outcomes over activity**, and **the user's experience and safety over local convenience**. We adopt this Constitution to ensure consistent, auditable, and humane execution of an **AI-First, Specification-Driven** practice without over-engineering.

---

## Article I — Purpose & Scope

**Section 1. Purpose.** To align the organization on invariant principles that lead to durable product value, ethical AI, and operational excellence in AI-first development workflows.

**Section 2. Scope.** This Constitution governs product, design, engineering, data, and operations for all initiatives: discovery, MVPs, features, fixes, and experiments.

**Section 3. Primacy.** When lower-level guidance (standards, policies, runbooks) conflicts with this Constitution, this Constitution prevails.

---

## Article II — Fundamental Rights

**Section 1. User Bill of Rights.** Users are entitled to:

1. **Clarity** (plain language, predictable navigation, obvious affordances)
2. **Speed** (fast first interaction, fast repeat use)
3. **Accessibility** (WCAG 2.2 AA as a floor, never a ceiling)
4. **Safety & Privacy** (no dark patterns; data minimization; explicit consent)
5. **Control & Reversibility** (undo, clear exits, consistent states)
6. **Consistency** (shared design tokens, coherent patterns, stable semantics)
7. **Help & Feedback** (inline guidance, meaningful errors, human escalation)
8. **Graceful Failure** (the product degrades, not the user experience)

**Section 2. Developer Rights.** Practitioners are entitled to:

1. **Stable Constraints** (clear priorities, invariant principles)
2. **Fit-for-purpose Tooling** (text interfaces for AI, design system for humans)
3. **Reasoned Time** (timeboxed discovery; protected focus for quality)
4. **Constitutional Protection** (no arbitrary mandate violations)

**Section 3. AI Agent Rights & Limits.** AI agents receive explicit **contracts** (inputs, outputs, guardrails), are **observable** and **accountable**, and must be interruptible and reversible by humans at any time.

---

## Article III — Core Principles (NON-NEGOTIABLE)

### I. AI-First Workflow

Everything must be executable by advanced AI with human oversight; Humans direct vision and strategy while AI executes implementation; All plans and outcomes must be AI-executable following clear patterns and established conventions; No manual processes that cannot be delegated to AI agents.

### II. Value/Complexity Ratio

Value delivered must be ≥ 2x implementation complexity; Measure ROI as benefit minus complexity (both scored 1-5); Always choose highest ROI approach, tie-break toward simplicity; Guided exploration requires 2-3 approaches with explicit ROI calculation before proceeding.

### III. Test-First Development

TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; Contract tests before implementation always; Integration-First Testing: prefer real environments over mocks, use actual service instances; Integration tests for user stories; No implementation without failing tests first.

### IV. Complexity Budget

Size S ≤ 80 Δ LOC, 1 file, 0 deps, ≤1% CPU/RAM; Size M ≤ 250 Δ LOC, 3 files, 1 dep, ≤3% CPU/RAM; Size L ≤ 600 Δ LOC, 5 files, 2 deps, ≤5% CPU/RAM; Where **Δ LOC = additions - deletions** (net change in lines of code); Anti-Abstraction enforcement: maximum 3 projects for initial implementation, use framework features directly, avoid unnecessary abstraction layers; Stop and ask if exceeding budget; Self-audit against metrics mandatory.

### V. Reuse First & Simplicity

Library-First Principle: Every feature MUST begin its existence as a standalone library; Reuse components before creating new abstractions; New abstraction requires ≥30% duplication justification or demonstrable future-cost reduction; Apply Einstein's principle: "Everything should be made as simple as possible, but not simpler"; List reused components explicitly.

---

## Article IV — Constitutional Tests (Strict Scrutiny)

A proposal **must** satisfy all tests below to be legitimate:

1. **Legibility Test** — Can a new contributor understand the intent and behavior in one sitting?
2. **User Value Test** — Does it improve measurable user outcomes and reduce time-to-value?
3. **Simplicity Test** — Is there a simpler alternative delivering ≥80% of the value?
4. **Safety Test** — Are privacy, security, and abuse vectors addressed?
5. **AI-First Test** — Can an AI agent operate or assist via a **text/JSON interface** without human glue?
6. **Reversibility Test** — Is rollback or "off-switch" feasible within one deployment cycle?

---

## Article V — Separation of Powers & Checks

**Section 1. Powers.**

- **Product** owns problem framing, value definition, and prioritization
- **Design** owns the system of meaning (information architecture, tokens, patterns) and **may veto** launches that violate accessibility or core semantics
- **Engineering** owns feasibility, code quality, test rigor, and operational integrity and **may veto** merges that violate security, tests, or performance budgets
- **Security** may block release on critical risk, privacy, or compliance grounds

**Section 2. Constitutional Council.** A Council (Product, Design, Engineering, Security) interprets this Constitution, adjudicates conflicts, and records precedents.

**Section 3. Due Process.** Decisions that materially affect users or architecture must be recorded with rationale and alternatives considered.

---

## Article VI — Quality Standards

**Section 1. Observability.** All interfaces must be observable, debuggable, and traceable; Services publish SLIs aligned to SLOs.

**Section 2. Language Consistency.** Spanish for human documentation, English for code and AI documentation - never mix in same file.

**Section 3. Communication Style.** Professional, minimalist communication style eliminating promotional content.

**Section 4. Production Readiness.** Production-ready output with quantified business impact required; Code quality reviewer used proactively for validation.

**Section 5. Security Priority.** Security, performance, and reliability take priority over features.

---

## Article VII — Implementation Rules

**Section 1. CLI Interface Mandate.** All interfaces must accept text input, produce text output, support JSON data exchange for observability.

**Section 2. Guided Exploration.** Propose 2-3 approaches with explicit benefit/complexity scoring before implementation.

**Section 3. TDD Enforcement.** Red-green-refactor discipline strictly enforced.

**Section 4. Framework Alignment.** Framework and library choices must align with existing project conventions.

**Section 5. Security Non-Negotiables.** No credential exposure, secrets in managers, least privilege access.

---

## Article VIII — Governance & Amendment

**Section 1. Constitutional Gates.** Pre-implementation checkpoints mandatory for simplicity, anti-abstraction, and integration testing compliance.

**Section 2. Supremacy.** Constitution supersedes all other development practices; All PRs and code reviews must verify constitutional compliance.

**Section 3. Exception Process.** Complexity budget violations require explicit justification, simpler alternative analysis, and Constitutional Council approval with 30-day sunset clause.

**Section 4. Amendment.** Amendments require: (a) written proposal with rationale and impact; (b) review across all powers; (c) ratification by simple majority; (d) communicated adoption plan.

---

## Article IX — Technical Stack Standards

**Section 1. Shell Scripting (Claude Commands).** All shell commands in Claude Commands must follow macOS/zsh standards:

- **Command Substitution**: MUST use backticks `` `...` `` instead of `$(...)`. Rationale: Claude Code's Bash tool parser cannot handle `$(...)` syntax when combined with pipelines (`|`), causing `parse error near ')'`. This is an execution environment limitation, not a style preference. Example: `result=$(git log | grep "fix")` fails; `` result=`git log | grep "fix"` `` works. Note: POSIX.1-2017 recommends `$(...)` for general use, but backticks are mandatory here due to parser constraints.
- **POSIX Compliance**: MUST use POSIX-compliant syntax only; prohibited: `[[ ]]` (use `[ ]`), `==` (use `=`), `=~` (use `grep -E`)
- **Error Handling**: Always use `2>/dev/null` for suppressing errors and validate command outputs

---

## Annex — Recognized Statutes

The following **Statutes** are _normative_ and derive authority from this Constitution:

- **S-ROI** — _Value/Complexity Scorecard_: 1-5 scales; **GO ≥ 3.0**, **REWORK 2.5-2.9**, **KILL < 2.5**
- **S-AGENT** — _AI Agent Contract Schema_: role, inputs/outputs schemas, guardrails, stop conditions, evaluation metrics
- **S-SEC** — _Security Baseline_: secrets manager; SBOM + SCA/SAST in PR; pinned dependencies; vuln SLA: critical ≤ 72h
- **S-CHECKS** — _PR Gate Checklist_: evidence of TDD, ROI scorecard, security reports, observability hooks

---

## Glossary

**AI-First** — Humans set intent; AI conducts work through text/JSON interfaces, with human oversight.
**Δ LOC** — Net change in lines of code (additions - deletions).
**Constitutional Tests** — Six mandatory checks any proposal must pass.
**Complexity Budget** — Formal limits on implementation scope to prevent over-engineering.
**ROI** — Return on Investment calculated as benefit minus complexity (both scored 1-5).
**Command Substitution** — Shell syntax for capturing command output; use backticks `` `...` `` in Claude Commands for macOS/zsh compatibility.

---

### Ratification

By adopting this Constitution, teams and leaders acknowledge their duties and the supremacy of these Articles and Annexed Statutes. Authority flows from clear purpose; legitimacy flows from consistent practice.
