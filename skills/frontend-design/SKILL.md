---
name: frontend-design
description: Use when building web components, pages, dashboards, landing pages, or styling any web UI. Invoke AFTER brainstorming, BEFORE scenario-driven-development for UI work.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

---

## Phase 0: Reference Research (MANDATORY)

**Before ANY design work, you MUST study real world-class references.**

AI generates generic designs because it optimizes for "statistical likelihood" — averaging thousands of designs into mediocrity. World-class design requires specific visual targets, not abstract concepts.

### Step 1: Research References

Use **agent-browser skill** to navigate and capture screenshots from:

1. **Awwwards.com** — Filter by category matching user's request
   - Prioritize "Site of the Day" winners
   - Capture 3-5 sites in the same industry/style

2. **Alternative sources** (if needed):
   - siteinspire.com — Clean, balanced designs
   - mobbin.com — Mobile UI patterns
   - dribbble.com — Specific component inspiration

**Invocation:**
```
Invoke skill: agent-browser

Task: Navigate to awwwards.com, filter by [category], capture full-page screenshots of 3-5 "Site of the Day" winners. For each site, also capture:
- Hero section close-up
- Typography samples
- Key interactive elements
```

**Fallback** (only if agent-browser unavailable): Use Chrome extension tools (mcp__claude-in-chrome__*) to navigate and take screenshots.

**Last resort** (only if browser tools fail): Use WebFetch to extract content, but acknowledge this provides inferior analysis.

### Step 2: Extract Design DNA

From each reference, document:

| Token | What to Extract |
|-------|-----------------|
| **Colors** | Primary, secondary, accent (exact hex values) |
| **Typography** | Font families, size ratios (h1/body), weights |
| **Spacing** | Base unit, section padding, element gaps |
| **Grid** | Columns, gutters, breakpoints |
| **Signature element** | What makes THIS site unforgettable? |

### Step 3: Synthesize Direction

Before proceeding to Design Thinking:
- Cherry-pick the best patterns from your references
- Define what YOUR design will do differently
- Commit to specific values, not vague concepts

**Example output:**
> "Inspired by [Reference A]'s bold typography scale (3.5x ratio) and [Reference B]'s restrained color palette (near-black + single accent), I'll create a design that combines editorial weight with surgical precision. The unforgettable element will be [specific technique]."

---

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

---

## Validation: Reference Comparison (MANDATORY)

**Before delivering, validate against your references.**

### Visual Tests

1. **Squint Test**: Blur to 5-10px — do priorities still read correctly?
2. **50ms Test**: First glance — is the hierarchy instant and obvious?
3. **Side-by-Side**: Compare with your 3 best references:
   - Is spacing as refined?
   - Is contrast as intentional?
   - Is symmetry/asymmetry purposeful?

### Design Token Audit

Compare your implementation against reference tokens:

| Aspect | Your Design | Reference Standard | Pass? |
|--------|-------------|-------------------|-------|
| Typography ratio | ? | ? | ✓/✗ |
| Color contrast | ? | ? | ✓/✗ |
| Spacing consistency | ? | ? | ✓/✗ |
| Visual weight balance | ? | ? | ✓/✗ |

### Symmetry Check

Asymmetry is a choice, not an accident. For each asymmetric element, answer:
- **Why** is this asymmetric?
- **What purpose** does it serve?
- Would symmetry work better here?

If you can't justify the asymmetry, fix it.

### Final Gate

Before delivery, capture a screenshot of your work and compare side-by-side with one reference. Ask:

> "Would a professional designer see this as peer-level to the reference, or clearly amateur?"

If amateur → iterate. If peer-level → deliver.