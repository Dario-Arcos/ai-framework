<!--
Sync Impact Report - Constitution v2.3.0
Version change: v2.2.0 → v2.3.0 (Remove redundancies with CLAUDE.md)
Modified principles: All 5 core principles preserved - compressed to eliminate tactical detail duplication
Modified sections:
  - Article III §II (Value/Complexity): Removed ROI formula (→ CLAUDE.md §4)
  - Article III §III (TDD): Removed red-green-refactor details (→ CLAUDE.md §5)
  - Article III §IV (Complexity Budget): Removed S/M/L table (→ CLAUDE.md §3)
  - Article III §V (Reuse): Removed ≥30% threshold details (→ CLAUDE.md §5)
Added sections: None
Removed sections:
  - Annex (S-ROI, S-AGENT, S-SEC, S-CHECKS) - moved to operational docs
  - Glossary (redundant with inline definitions and CLAUDE.md)
Templates requiring updates: None
Rationale: Eliminate ~180 tokens of redundancy between constitution.md and CLAUDE.md. Constitution retains strategic governance authority; CLAUDE.md retains tactical implementation details.
-->

# AI Framework Constitution

**Version**: 2.3.0 | **Ratified**: 2025-09-20 | **Last Amended**: 2025-10-18

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

Value delivered must be ≥ 2x implementation complexity. Always choose highest ROI approach, tie-break toward simplicity. Guided exploration requires 2-3 approaches with explicit ROI calculation before proceeding.

_See CLAUDE.md §4 for ROI scoring formula (benefit 1-5, complexity 1-5)._

### III. Test-First Development

TDD mandatory: Tests written → User approved → Tests fail → Then implement. Contract tests before implementation always. Integration-First Testing: prefer real environments over mocks, use actual service instances. Integration tests for user stories. No implementation without failing tests first.

_See CLAUDE.md §5 for TDD loop (red → green → refactor)._

### IV. Complexity Budget

Formal limits on implementation scope to prevent over-engineering (**Δ LOC = additions - deletions**). Anti-Abstraction enforcement: maximum 3 projects for initial implementation, use framework features directly, avoid unnecessary abstraction layers. Stop and ask if exceeding budget. Self-audit against metrics mandatory.

_See CLAUDE.md §3 for size classes (S/M/L) with thresholds (lines, files, deps, CPU/RAM)._

### V. Reuse First & Simplicity

Library-First Principle: Every feature MUST begin its existence as a standalone library. Reuse components before creating new abstractions. New abstraction requires significant duplication (≥30%) OR demonstrable future-cost reduction. Apply Einstein's principle: "Everything should be made as simple as possible, but not simpler". List reused components explicitly.

_See CLAUDE.md §5 for implementation rules (reuse first, abstraction justification threshold)._

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

**Section 2. Communication Style.** Professional, minimalist communication style eliminating promotional content.

**Section 3. Production Readiness.** Production-ready output with quantified business impact required; Code quality reviewer used proactively for validation.

**Section 4. Security Priority.** Security, performance, and reliability take priority over features.

**Section 5. Documentation Language.** Human-facing documentation must be in Spanish. SDD artifacts (specifications, plans, tasks, research, data models, quickstarts, checklists) are Spanish. Code and AI agent instructions remain English. Technical terms (APIs, frameworks, commands) remain English as jargon within Spanish documentation.

---

## Article VII — Implementation Rules

**Section 1. CLI Interface Mandate.** All interfaces must accept text input, produce text output, support JSON data exchange for observability.

**Section 2. Guided Exploration.** Propose 2-3 approaches with explicit benefit/complexity scoring before implementation.

**Section 3. TDD Enforcement.** Red-green-refactor discipline strictly enforced.

**Section 4. Framework Alignment & Project Context.** Framework and library choices must align with existing project conventions:

- **MUST read** `.specify/memory/project-context.md` before making technology or architecture decisions
- **MUST respect** existing stack (languages, frameworks, databases, tools) unless explicit justification for change (security risk, EOL, performance bottleneck)
- **MAY suggest** strategic improvements or tactical optimizations if gaps, risks, or inefficiencies are identified, with documented rationale and ROI analysis

**Section 5. Security Non-Negotiables.** No credential exposure, secrets in managers, least privilege access.

**Section 6. Context Verification Protocol.** Before any implementation:
- Search Core Memory exhaustively for relevant context, decisions, and patterns
- Review local documentation (project files, specs, architectural docs) if memory insufficient
- Request user clarification if uncertainty remains
- Never proceed with unvalidated assumptions or incomplete information

---

## Article VIII — Governance & Amendment

**Section 1. Constitutional Gates.** Pre-implementation checkpoints mandatory for simplicity, anti-abstraction, and integration testing compliance.

**Section 2. Supremacy.** Constitution supersedes all other development practices; All PRs and code reviews must verify constitutional compliance.

**Section 3. Exception Process.** Complexity budget violations require explicit justification, simpler alternative analysis, and Constitutional Council approval with 30-day sunset clause.

**Section 4. Amendment.** Amendments require: (a) written proposal with rationale and impact; (b) review across all powers; (c) ratification by simple majority; (d) communicated adoption plan.

---

## Ratification

By adopting this Constitution, teams and leaders acknowledge their duties and the supremacy of these Articles. Authority flows from clear purpose; legitimacy flows from consistent practice.
