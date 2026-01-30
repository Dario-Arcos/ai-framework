# Implementation Plan: Ralph Supervision Dashboard

**Created**: 2026-01-30
**Design Reference**: `design/detailed-design.md`
**Status**: Ready for task generation

---

## Implementation Checklist

- [x] Step 01: Configure server to serve static files from public/
- [ ] Step 02: Create HTML structure with semantic markup
- [ ] Step 03: Implement CSS design system with tokens and components
- [ ] Step 04: Build status card UI with state-based styling
- [ ] Step 05: Build progress display with visual indicator
- [ ] Step 06: Build activity log component with expand/collapse
- [ ] Step 07: Implement StatusPoller with adaptive interval
- [ ] Step 08: Implement StateManager with status translation
- [ ] Step 09: Implement UIRenderer with efficient DOM updates
- [ ] Step 10: Add empty state and error handling UI
- [ ] Step 11: Implement dark mode and responsive design
- [ ] Step 12: Add accessibility features (ARIA, focus, keyboard)
- [ ] Step 13: Write unit tests for Poller and StateManager
- [ ] Step 14: Manual verification and polish

---

## Prerequisites

**Dependencies**:
- Existing `dashboard/server.js` (already present)
- Existing `dashboard/lib/readers.js` (already present)
- Node.js 18+

**Environment Setup**:
- None required (uses existing infrastructure)

**Access Requirements**:
- File system write access to `dashboard/public/`

---

## Implementation Steps

### Step 01: Configure server to serve static files

**Complexity**: S

**Description**: Update `dashboard/server.js` to serve static files from `dashboard/public/` directory and route `/` to `public/index.html`.

**Acceptance Criteria**:
- [ ] `GET /` returns `public/index.html`
- [ ] Static files in `public/` accessible via HTTP
- [ ] Existing `/api/status` endpoint unchanged
- [ ] Server tests still pass

**TDD Approach**:
1. Write test: `GET /` returns HTML with content-type text/html
2. Verify test fails (currently returns placeholder HTML)
3. Implement static file serving
4. Verify test passes

**Dependencies**: None

---

### Step 02: Create HTML structure with semantic markup

**Complexity**: S

**Description**: Create `dashboard/public/index.html` with semantic HTML5 structure for the dashboard layout (header, main content areas, footer).

**Acceptance Criteria**:
- [ ] File exists at `dashboard/public/index.html`
- [ ] Valid HTML5 document with proper doctype
- [ ] Semantic elements: header, main, article, section, footer
- [ ] Placeholder content for each section
- [ ] Meta viewport for mobile
- [ ] Page title set

**HTML Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ralph Dashboard</title>
  <style>/* Step 03 */</style>
</head>
<body>
  <header><!-- Header with title and connection status --></header>
  <main>
    <article id="status-card"><!-- Status display --></article>
    <article id="logs-card"><!-- Activity log --></article>
  </main>
  <footer><!-- Last update and refresh --></footer>
  <script>/* Steps 07-09 */</script>
</body>
</html>
```

**Dependencies**: Step 01

---

### Step 03: Implement CSS design system with tokens and components

**Complexity**: M

**Description**: Add inline CSS with design tokens (custom properties) and base component styles following the design specification.

**Acceptance Criteria**:
- [ ] CSS custom properties defined for colors, spacing, typography
- [ ] Base reset/normalize styles
- [ ] Container and card component styles
- [ ] Status indicator styles (colors for each state)
- [ ] Dark mode support via prefers-color-scheme
- [ ] Mobile-first base styles

**Key CSS Classes**:
- `.container` - Main layout wrapper
- `.card` - Content card with shadow and border radius
- `.status-indicator` - Colored status dot/badge
- `.status-text` - Status description text
- `.progress-bar` - Visual progress indicator

**Dependencies**: Step 02

---

### Step 04: Build status card UI with state-based styling

**Complexity**: M

**Description**: Implement the main status card showing status indicator, current task, and elapsed time with appropriate styling for each status state.

**Acceptance Criteria**:
- [ ] Status indicator shows colored dot + text
- [ ] Current task description displayed
- [ ] Elapsed time formatted (e.g., "5 min")
- [ ] Different colors for each status (running/complete/error/etc.)
- [ ] Loading state shown initially
- [ ] Responsive on mobile

**HTML Template**:
```html
<article id="status-card" class="card">
  <div class="status-header">
    <span class="status-indicator" data-status="running"></span>
    <span class="status-text">Working...</span>
  </div>
  <div class="task-info">
    <span class="task-label">Task 3 of 7:</span>
    <span class="task-description">Creating API endpoint</span>
  </div>
  <div class="progress-container">
    <div class="progress-bar" style="--progress: 42%"></div>
  </div>
  <div class="elapsed-time">5 min elapsed</div>
</article>
```

**Dependencies**: Step 03

---

### Step 05: Build progress display with visual indicator

**Complexity**: S

**Description**: Implement visual progress bar that shows task completion percentage with smooth transitions.

**Acceptance Criteria**:
- [ ] Progress bar fills based on percentage
- [ ] Percentage calculated from current/total tasks
- [ ] Smooth CSS transition on updates
- [ ] Accessible (aria-valuenow, aria-valuemax)
- [ ] Works when total tasks unknown (indeterminate)

**CSS Implementation**:
```css
.progress-bar {
  width: var(--progress, 0%);
  height: 4px;
  background: var(--color-primary);
  transition: width 0.3s ease;
}
```

**Dependencies**: Step 04

---

### Step 06: Build activity log component with expand/collapse

**Complexity**: M

**Description**: Implement the activity log section showing recent events with timestamps, collapsible for space efficiency.

**Acceptance Criteria**:
- [ ] Shows last 5 log entries by default
- [ ] Expand button reveals full log (last 20)
- [ ] Each entry has timestamp and message
- [ ] Different styling for info/warn/error levels
- [ ] Auto-scroll to bottom when expanded
- [ ] Preserve scroll position on update

**HTML Template**:
```html
<article id="logs-card" class="card">
  <header class="logs-header">
    <h2>Recent Activity</h2>
    <button id="logs-toggle" aria-expanded="false">Expand</button>
  </header>
  <div id="logs-list" class="logs-collapsed">
    <div class="log-entry log-info">
      <time>10:23</time>
      <span>✓ Completed: Task 2</span>
    </div>
  </div>
</article>
```

**Dependencies**: Step 03

---

### Step 07: Implement StatusPoller with adaptive interval

**Complexity**: M

**Description**: Implement the StatusPoller class that fetches `/api/status` with adaptive polling interval and error handling.

**Acceptance Criteria**:
- [ ] Polls `/api/status` at configurable interval
- [ ] Increases interval (up to 30s) when no changes
- [ ] Resets to 2s interval on status change
- [ ] Exponential backoff on consecutive errors
- [ ] Emits updates via callback
- [ ] Can be started/stopped
- [ ] Handles visibility change (pause when hidden)

**Interface**:
```javascript
class StatusPoller {
  constructor(url, onUpdate) { }
  start() { }
  stop() { }
  async poll() { }
}
```

**Test Cases**:
1. Interval increases when data unchanged
2. Interval resets on data change
3. Backoff on fetch failure
4. Callback receives data and connection status

**Dependencies**: Step 02

---

### Step 08: Implement StateManager with status translation

**Complexity**: M

**Description**: Implement StateManager that transforms API responses into UI state with human-readable status translations.

**Acceptance Criteria**:
- [ ] Translates status codes to plain language
- [ ] Maps status to colors (blue/green/yellow/red/gray)
- [ ] Calculates progress percentage
- [ ] Formats elapsed time (seconds → "5 min")
- [ ] Tracks state changes for efficient rendering
- [ ] Handles null/missing data gracefully

**Status Translation Map**:
```javascript
const STATUS_MAP = {
  running:          { text: 'Working...',              color: 'blue' },
  complete:         { text: 'Done!',                   color: 'green' },
  circuit_breaker:  { text: 'Paused for safety',       color: 'yellow' },
  // ... etc
};
```

**Test Cases**:
1. Each status code maps correctly
2. Unknown status handled gracefully
3. Progress % calculated correctly
4. Time formatted correctly (1min, 5min, 1hr 5min)

**Dependencies**: None (pure logic)

---

### Step 09: Implement UIRenderer with efficient DOM updates

**Complexity**: M

**Description**: Implement UIRenderer that updates the DOM based on state, minimizing unnecessary updates.

**Acceptance Criteria**:
- [ ] Updates status indicator color and text
- [ ] Updates task info and progress bar
- [ ] Updates elapsed time
- [ ] Updates log entries
- [ ] Only touches DOM elements that changed
- [ ] Preserves log scroll position

**Interface**:
```javascript
class UIRenderer {
  constructor(elements) { }
  render(state) { }
  showLoading() { }
  showError(message) { }
}
```

**Dependencies**: Steps 04-06

---

### Step 10: Add empty state and error handling UI

**Complexity**: S

**Description**: Implement UI states for when no loop is running or when connection fails.

**Acceptance Criteria**:
- [ ] Empty state shows friendly message when `active: false`
- [ ] Instructions on how to start a loop
- [ ] Connection error shows warning banner
- [ ] Last known data preserved during errors
- [ ] Automatic recovery when connection restored

**Empty State Content**:
```html
<div class="empty-state">
  <h2>No active process</h2>
  <p>Start a loop with:</p>
  <code>./loop.sh specs/your-feature/</code>
</div>
```

**Dependencies**: Step 09

---

### Step 11: Implement dark mode and responsive design

**Complexity**: S

**Description**: Add dark mode support via prefers-color-scheme and ensure responsive layout on all screen sizes.

**Acceptance Criteria**:
- [ ] Dark mode activates based on system preference
- [ ] All colors have dark mode variants
- [ ] Layout stacks vertically on mobile (< 640px)
- [ ] Touch targets minimum 44x44px
- [ ] Text readable at all sizes
- [ ] Tested on 375px viewport (iPhone SE)

**Dependencies**: Step 03

---

### Step 12: Add accessibility features (ARIA, focus, keyboard)

**Complexity**: S

**Description**: Ensure dashboard is fully accessible per WCAG 2.1 AA guidelines.

**Acceptance Criteria**:
- [ ] ARIA labels on interactive elements
- [ ] ARIA live region for status updates
- [ ] Focus indicators visible
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Color not sole indicator (icons + text)
- [ ] Screen reader announces status changes

**Key ARIA Additions**:
```html
<div role="status" aria-live="polite" aria-atomic="true">
  <span class="status-text">Working...</span>
</div>
<button aria-expanded="false" aria-controls="logs-list">Expand</button>
```

**Dependencies**: Steps 04-06

---

### Step 13: Write unit tests for Poller and StateManager

**Complexity**: S

**Description**: Add unit tests for business logic in StatusPoller and StateManager.

**Acceptance Criteria**:
- [ ] Tests for StatusPoller interval logic
- [ ] Tests for StateManager status translation
- [ ] Tests for time formatting
- [ ] Tests for progress calculation
- [ ] All tests pass
- [ ] Test file at `dashboard/__tests__/dashboard.test.js`

**Test Framework**: Node.js native test runner (no deps)

**Dependencies**: Steps 07-08

---

### Step 14: Manual verification and polish

**Complexity**: S

**Description**: Final manual testing and visual polish.

**Verification Checklist**:
- [ ] Load dashboard, verify status displays
- [ ] Watch real loop, verify updates
- [ ] Test on mobile (Chrome DevTools)
- [ ] Test dark mode
- [ ] Test keyboard navigation
- [ ] Check Lighthouse score (> 90)
- [ ] Visual inspection and polish

**Dependencies**: All previous steps

---

## Testing Strategy

### Unit Tests (Step 13)
- StatusPoller: interval adjustment, backoff logic
- StateManager: status translation, time formatting, progress calculation

### Integration Tests
- Server serves index.html correctly
- Full flow: start dashboard → receive updates → display status

### Manual Tests (Step 14)
- Real loop monitoring
- Mobile viewport
- Accessibility audit

---

## Rollout Plan

**Deployment Steps**:
1. Merge changes to main branch
2. Dashboard available at `http://localhost:3456`
3. Document in human-handbook

**Rollback Plan**:
- Revert server.js changes
- Remove public/index.html
- API endpoint unchanged, no data migration needed

---

## Notes for Task Generator

- Each step is independently testable
- Steps build sequentially (no forward dependencies)
- Complexity estimates: S = < 1hr, M = 1-2hrs
- TDD approach: test → fail → implement → pass
- Single HTML file: all code inline

---

*Plan complete. Ready for sop-task-generator.*
