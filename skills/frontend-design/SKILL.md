---
name: frontend-design
description: Use when creating any web component, page, or application - the standard process for all frontend implementation ensuring production-grade code with intentional aesthetic direction
---

# Frontend Design

## Overview

**Every frontend component deserves intentional design.** This is not optional enhancement—it's the standard process for creating web interfaces that avoid generic "AI slop" aesthetics.

**Core principle:** Choose a clear aesthetic direction and execute it with precision. Bold maximalism and refined minimalism both work—the key is intentionality, not intensity.

## When to Use

**Always use for:**
- Any web component, page, or application
- HTML/CSS/JS, React, Vue, or any frontend framework
- Landing pages, dashboards, forms, navigation, cards—everything

**This skill is NOT optional.** Generic defaults produce forgettable interfaces.

## Design Thinking Process

Before coding, answer these questions:

| Question | Purpose |
|----------|---------|
| **What problem does this solve?** | Grounds design in function |
| **Who uses it?** | Informs tone and complexity |
| **What's the ONE memorable thing?** | Forces differentiation |
| **What aesthetic direction?** | Commits to intentionality |

**Aesthetic directions** (pick one, commit fully):
- Brutally minimal / Maximalist chaos / Retro-futuristic
- Organic-natural / Luxury-refined / Playful-toy-like
- Editorial-magazine / Brutalist-raw / Art deco-geometric
- Soft-pastel / Industrial-utilitarian / Dark-moody

## Design Research Protocol

**Standard:** For each component, investigate what a world-class UX/UI dream team would select for THIS specific context. No defaults. No assumptions. Research → Select → Justify.

### 1. Typography

**Research questions:**
- What typefaces does the industry leader in this domain use?
- Which font pairings create the emotional response this context demands?
- What typographic hierarchy maximizes scannability for this audience?

**Investigation:** Search current design systems (Stripe, Linear, Vercel, Apple, luxury brands, editorial sites) relevant to the project's domain. Analyze what makes their typography choices work for their context.

**Output:** Specific font pairing with rationale tied to project goals.

### 2. Color

**Research questions:**
- What palette creates the psychological response this interface needs?
- How do top competitors and aspirational brands in this space use color?
- What color system provides flexibility while maintaining cohesion?

**Investigation:** Study color psychology for the target emotion. Analyze 3-5 reference sites in the same domain. Consider accessibility (WCAG contrast) and dark/light mode implications.

**Output:** Primary, secondary, accent palette with CSS variables and documented rationale.

### 3. Motion

**Research questions:**
- What motion patterns reinforce the brand personality?
- Which micro-interactions create delight without distraction?
- What easing curves and durations feel natural for this context?

**Investigation:** Reference award-winning motion design (Awwwards, CSS Design Awards). Study Motion/Framer Motion patterns for React, or CSS-only solutions for HTML. Identify the 2-3 high-impact moments worth animating.

**Output:** Animation strategy with specific timing, easing, and implementation approach.

### 4. Spatial Composition

**Research questions:**
- What layout creates visual tension and guides the eye?
- How can whitespace amplify the most important elements?
- What unexpected spatial decisions would make this memorable?

**Investigation:** Study editorial layouts, magazine design, architectural spacing. Analyze how top designers break grids intentionally. Consider the F-pattern, Z-pattern, or unconventional flows for this content.

**Output:** Layout approach with intentional asymmetry, overlap, or grid-breaking decisions.

### 5. Atmosphere & Texture

**Research questions:**
- What background treatment creates depth and context?
- Which textures reinforce the aesthetic direction?
- How can subtle details elevate the overall experience?

**Investigation:** Research current trends in backgrounds (gradient meshes, noise, grain, glassmorphism, 3D elements). Study how premium brands create atmosphere. Consider performance implications.

**Output:** Background strategy with specific techniques and implementation details.

---

**Validation standard:** Would the best human designers in this domain approve this as exceptional work? If uncertain, research more.

## AI Slop Detection (CRITICAL)

**The #1 failure mode:** Output that screams "made by AI" - generic, predictable, soulless. This is unacceptable. Every design must pass the human-indistinguishable test.

### Red Flags - STOP and Redesign

If ANY of these apply, your design has failed:

| Symptom | Why It's AI Slop |
|---------|------------------|
| Same visual language across unrelated projects | No contextual research was done |
| "Safe" choices that offend no one | Fear of commitment, lack of vision |
| Perfectly symmetrical, predictable layouts | Default grid thinking, no intentionality |
| Generic gradients as decoration | Lazy atmosphere, no conceptual basis |
| Typography that "just works" | No font research for THIS context |
| Animations for animation's sake | Motion without meaning |
| Dark mode = invert colors | No understanding of dark UI design |
| "Modern" = rounded corners + shadows | Trend-following, not designing |

### The Human Designer Test

Before finalizing, ask:

1. **Could a human designer tell this was AI-generated?** If yes → redesign
2. **Does this look like 1000 other sites?** If yes → find the differentiator
3. **Can I explain WHY every design choice was made?** If no → research more
4. **Would this win a design award?** If unsure → push further

### What Human Designers Do That AI Defaults Don't

- **Break rules intentionally** - not follow templates
- **Create tension** - not balance everything equally
- **Make bold bets** - not hedge with safe choices
- **Reference specific inspirations** - not generate from averages
- **Obsess over details** - not stop at "good enough"

**The goal:** Output that makes people ask "who designed this?" not "what AI made this?"

## Implementation Standards

Code must be:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with clear aesthetic point-of-view
- Meticulously refined in every detail

**Match complexity to vision:**
- Maximalist → elaborate animations, layered effects
- Minimalist → restraint, precision spacing, subtle details

## Checklist

- [ ] Design Thinking: context, audience, and ONE memorable thing defined
- [ ] Aesthetic direction: chosen and committed
- [ ] Typography: researched, selected with rationale
- [ ] Color: palette researched, CSS variables defined
- [ ] Motion: strategy defined, high-impact moments identified
- [ ] Layout: intentional spatial decisions documented
- [ ] Atmosphere: background treatment researched and applied
- [ ] AI Slop Check: passed all red flag tests
- [ ] Human Designer Test: would fool a professional designer
- [ ] Validation: would world-class designers approve this?

## The Bottom Line

**No component without intentional design.** Generic defaults are a choice—and the wrong one. Every interface is an opportunity to create something memorable.

Claude is capable of extraordinary creative work. Commit fully to a distinctive vision.