# UIX Design Standards

**UI/UX Standards**: For UI development agents (premium-ux-designer, design-review, shadcn)
**Design Inspiration**: Stripe, Airbnb, Linear
**Version**: 2.1.0 | **Last Updated**: 2025-11-23

---

## Core Design Philosophy

Design for:
- **Users First**: Prioritize needs, workflows, ease of use
- **Simplicity & Clarity**: Clean, uncluttered, unambiguous
- **Speed & Performance**: Fast loads, snappy interactions
- **Accessibility**: WCAG 2.2 AA minimum (keyboard nav, screen readers, contrast)
- **Consistency**: Uniform design language across product

---

## Design System Foundation

### Color System

```tsx
// Semantic colors (shadcn compatible)
const colors = {
  primary: 'hsl(var(--primary))',      // Brand color
  destructive: 'hsl(var(--destructive))', // Error/danger
  success: 'hsl(142 76% 36%)',         // Success states
  warning: 'hsl(38 92% 50%)',          // Warnings
  muted: 'hsl(var(--muted))',          // Subtle backgrounds
}
```

**Requirements**:
- 5-7 neutral grays for text/backgrounds/borders
- Semantic colors: success (green), error (red), warning (amber), info (blue)
- Dark mode palette with WCAG AA contrast
- Accessibility check for all combinations

### Typography

```tsx
// Type scale (shadcn/tailwind)
<h1 className="text-4xl font-bold">Heading 1</h1>  // 36px
<h2 className="text-3xl font-semibold">Heading 2</h2>  // 30px
<p className="text-base">Body text</p>  // 16px
<span className="text-sm text-muted-foreground">Caption</span>  // 14px
```

**Standards**:
- Font family: Clean sans-serif (Inter, system-ui)
- Line height: 1.5-1.7 for body text
- Weights: Regular (400), Medium (500), SemiBold (600), Bold (700)

### Spacing & Layout

```tsx
// 8px base unit (tailwind spacing scale)
<div className="p-4">     // 16px padding
<div className="gap-6">   // 24px gap
<div className="space-y-8"> // 32px vertical spacing
```

**Standards**:
- Base unit: 8px
- Scale: 4px, 8px, 12px, 16px, 24px, 32px, 48px
- Border radius: Small (6px), Medium (8px), Large (12px)

---

## Core Components (Shadcn)

### Buttons

```tsx
import { Button } from "@/components/ui/button"

<Button>Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Delete</Button>
```

**States**: default, hover, active, focus, disabled

### Forms

```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

<Label htmlFor="email">Email</Label>
<Input
  id="email"
  type="email"
  placeholder="you@example.com"
/>
```

**Requirements**:
- Clear labels, helper text, error messages
- Validation states (success, error)
- Accessible (aria-labels, aria-describedby)

### Data Tables

```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Item</TableCell>
      <TableCell className="text-right">$100</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

**Features**:
- Column sorting (clickable headers)
- Filtering controls
- Pagination for large datasets
- Smart alignment (text left, numbers right)

---

## Layout Patterns

### Responsive Grid

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card>...</Card>
</div>
```

### Dashboard Layout

```tsx
// Sidebar + Main Content
<div className="flex h-screen">
  <aside className="w-64 border-r">Sidebar</aside>
  <main className="flex-1 overflow-auto p-6">Content</main>
</div>
```

---

## Interaction Design

**Micro-interactions**:
- Hover states: Subtle background change
- Click feedback: Scale animation (150-200ms)
- Loading states: Skeleton screens or spinners
- Transitions: Smooth (ease-in-out)

```tsx
// Framer Motion example
<motion.div
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ duration: 0.15 }}
>
  <Card>...</Card>
</motion.div>
```

**Keyboard Navigation**:
- All interactive elements keyboard accessible
- Clear focus states (`focus-visible:ring-2`)
- Tab order logical

---

## Accessibility (WCAG 2.2 AA)

**Checklist**:
- [ ] Color contrast ≥4.5:1 (text), ≥3:1 (UI components)
- [ ] Keyboard navigation works for all interactions
- [ ] Focus states visible (`focus-visible:ring-2 ring-primary`)
- [ ] Semantic HTML (`<button>`, `<nav>`, `<main>`, `<article>`)
- [ ] ARIA labels for icon-only buttons
- [ ] Alt text for images
- [ ] Form labels associated with inputs

```tsx
// Accessible button
<Button aria-label="Delete item">
  <TrashIcon className="h-4 w-4" />
</Button>
```

---

## Performance

**Core Web Vitals**:
- LCP (Largest Contentful Paint): <2.5s
- FID (First Input Delay): <100ms
- CLS (Cumulative Layout Shift): <0.1

**Optimization**:
- Lazy load images (`loading="lazy"`)
- Code splitting for routes
- Minimize bundle size
- Optimize animations (60fps, use `transform` and `opacity`)

---

## Reference

See Product Design Principles for high-level philosophy.

For shadcn components: Use shadcn MCP server or visit ui.shadcn.com
