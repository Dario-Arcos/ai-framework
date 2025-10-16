# Changelog

All notable changes to AI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.1] - 2025-10-16

### Added

**Documentation Quality & Version Management** (PR #9)

- VersionBadge Vue component with Pure Text Minimal design for version comparison display
- Automated version synchronization script (sync-versions.cjs) triggered by npm version hooks
- Version Management section in README.md documenting release workflow
- Qualitative component descriptions replacing hardcoded counts with authoritative links

### Removed

**Visual Simplification** (PR #9)

- Redundant GitHub release badge from hero section (replaced by VersionBadge component)
- Decorative emojis from documentation headings and content (preserved functional: ✅❌⚠️➜)
- Broken markdown links from feature card details in homepage
- Hardcoded component counts throughout documentation

---

## [1.1.0] - 2025-10-15

### Added

**Monochrome Power Design System** (PR #8)

- Complete documentation site redesign with brutalist, Apple-inspired aesthetics
- Monochrome gradient theme (Black #18181B → Charcoal #52525B)
- Premium button animations: scale on hover + shine effect with Apple-standard easing
- New icon assets: `terminal.svg` (Commands), `zap.svg` (Pro Tips) from Lucide library
- Balanced 4-card features grid (2x2 layout) replacing unbalanced 5-card design

### Changed

**Visual Design System** (PR #8)

- Hero section: Removed redundant name field for minimalist approach
- Button hierarchy: Workflow as primary brand button, Quick Start/Changelog as secondary
- Brand color: Changed from GitHub blue (#0969da) to monochrome (#18181b)
- Release badge: Updated to monochrome color for visual consistency
- Typography: Enhanced with font-weight 800, tight letter-spacing (-0.5px) for authority
- Dark mode: Optimized with inverted gradients (White→Gray spectrum)

**Documentation Enhancement** (PR #8)

- Improved navigation structure across all documentation pages
- Enhanced content clarity and readability
- Reorganized homepage to emphasize value proposition: "AI development that works"

### Security

**Design Security Review** (PR #8)

- Passed security review with 0.95 confidence score
- No hardcoded credentials or secrets detected
- Safe SVG assets verified (no scripts or event handlers)
- Proper secret management guidance maintained in MCP documentation

---

## [1.0.0] - 2025-10-15

### Added

**Human Handbook Documentation** (GitHub Pages)

- Complete workflow documentation for PRP → SDD → GitHub ecosystem
- 6 comprehensive guides: Quickstart, AI-First Workflow, Commands Guide, Agents Guide, Pro Tips, MCP Servers
- Branch vs Worktree decision matrix with 4 usage scenarios
- Agent-assignment-analyzer workflow step (SDD-cycle paso 5) with parallel execution examples
- Workflow diagrams (Mermaid) for complete development cycle
- Cross-references between all documentation files

**Framework Components**

- 7 lifecycle hooks (Python): session-start, workspace-status, pre-tool-use, security_guard, clean_code, minimal_thinking, ccnotify
- 24 slash commands across 4 categories: PRP-cycle (2), SDD-cycle (9), git-github (5), utils (8)
- 45 specialized agents across 11 categories
- Constitutional governance framework with 5 non-negotiable principles
- Specification-Driven Development (SDD) workflow with artifact traceability

### Changed

**Command Syntax**

- Updated all command references to use full plugin namespace (`/ai-framework:category:command`)
- Corrected PRP-cycle terminology (was PRD-cycle) throughout documentation
- Updated command count from 22 to 24 commands across all docs

**SDD-Cycle Workflow**

- Documented correct execution order (9 steps): specify → clarify → plan → tasks → **agent-assignment** → analyze → implement → checklist → sync
- Added agent-assignment-analyzer as paso 5 (CRÍTICO - casi mandatorio) for parallel execution optimization
- Moved checklist to paso 8 (POST-implementation quality validation)
- Clarified that analyze and sync are optional but recommended

### Fixed

**Functional Behavior Documentation**

- Corrected `speckit.specify` behavior: creates branch in SAME directory (does NOT create worktree)
- Corrected `speckit.specify` behavior: does NOT open IDE automatically
- Clarified `worktree:create` as the ONLY command that creates isolated worktrees
- Fixed workflow examples to show correct command behavior
- Added explicit warnings about branch vs worktree differences

**Documentation Accuracy**

- Fixed 7 workflows with correct command sequences
- Fixed 191 command syntax references across 4 files
- Updated all dates to 2025-10-14
- Corrected agent count references (45 agents, not 44)

### Security

**Preventive Security**

- Security-first architecture with `security_guard.py` PreToolUse hook
- 5 critical patterns blocked: hardcoded credentials, eval injection, SQL injection, command injection, path traversal
- Security review BLOCKING in PR creation workflow

---

**Production Status**: ✅ READY FOR RELEASE

This release represents the complete, production-ready AI Framework with:

- Zero-config auto-installation
- Constitutional governance enforcement
- 45 specialized agents
- Complete documentation validated against source code
- All workflows tested and executable

**Breaking Changes**: None (initial release)

**Migration Guide**: Not applicable (initial release)

---

## Release Notes Format

When releasing, the `[Unreleased]` section will be replaced with:

```
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security vulnerability fixes
```

---

**Legend:**

- **Major (X.0.0):** Breaking changes, major new features
- **Minor (x.Y.0):** Backward-compatible new features
- **Patch (x.y.Z):** Backward-compatible bug fixes
