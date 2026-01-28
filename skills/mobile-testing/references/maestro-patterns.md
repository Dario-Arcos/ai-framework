# Maestro YAML Patterns Reference

## Overview

This reference defines Maestro YAML patterns for mobile E2E testing. Understanding these patterns is essential for writing reliable and maintainable test flows.

---

## Table of Contents
1. [Flow Structure](#flow-structure)
2. [Selectors](#selectors)
3. [Commands Reference](#commands-reference)
4. [AI Assertions](#ai-assertions)
5. [Common Patterns](#common-patterns)

---

## Flow Structure

**Constraints:**
- You MUST organize flows by feature because this aids maintainability
- You MUST include appId in flows because this ensures correct app targeting
- You SHOULD separate smoke tests because quick validation is valuable

```
flows/
├── smoke/
│   └── app-launch.yaml
├── auth/
│   ├── login.yaml
│   └── validation.yaml
└── [feature]/
    ├── happy-path.yaml
    └── edge-cases.yaml
```

**Flow Template:**

```yaml
appId: com.myapp.bundleid
---
- launchApp
# ... commands
```

---

## Selectors

**Constraints:**
- You MUST prefer testID selectors because these are most stable across app changes
- You MUST NOT rely solely on text because text is localized and changes frequently
- You SHOULD use index only for duplicates because explicit IDs are better

All commands that interact with elements accept these selectors:

| Selector | Description | Example |
|----------|-------------|---------|
| `id` | testID/accessibilityIdentifier | `id: "login-btn"` |
| `text` | Visible text content | `text: "Sign In"` |
| `enabled` | Element enabled state | `enabled: true` |
| `checked` | Checkbox/toggle state | `checked: true` |
| `focused` | Has keyboard focus | `focused: true` |
| `selected` | Selection state | `selected: true` |

**Priority (most to least stable):**

```yaml
# 1. testID (most stable)
- tapOn:
    id: "login-button"

# 2. Text content
- tapOn:
    text: "Sign In"

# 3. Text with index (for duplicates)
- tapOn:
    text: "Item"
    index: 0

# 4. Regex pattern
- tapOn:
    id: ".*floating_action.*"

# 5. Combined conditions
- tapOn:
    text: "Submit"
    enabled: true
```

---

## Commands Reference

### App Lifecycle

**Constraints:**
- You MUST use launchApp at flow start because app must be running
- You SHOULD use clearState for isolation because state from previous tests causes flaky results
- You MAY use killApp for cleanup because this ensures clean slate

```yaml
# Basic launch
- launchApp

# Launch specific app
- launchApp: com.example.app

# Full options
- launchApp:
    appId: "com.example.app"
    clearState: true           # Clear app data
    clearKeychain: true        # iOS: clear keychain
    stopApp: false             # Don't stop before launch (bring to foreground)
    permissions:
      all: deny                # deny/allow/unset
    arguments:                 # Launch arguments
      key: "value"
      enabled: true

# Stop/kill app
- stopApp                      # Background app
- killApp                      # Force terminate
```

### Tap Interactions

**Constraints:**
- You MUST wait for elements before tapping because race conditions cause failures
- You SHOULD use retryTapIfNoChange for unreliable buttons because this handles timing issues
- You MAY use point for precise positioning because some elements need specific tap location

```yaml
# Simple tap
- tapOn: "Button Text"

# By ID
- tapOn:
    id: "element-id"

# Advanced options
- tapOn:
    text: "Button"
    repeat: 3                  # Tap 3 times
    delay: 500                 # 500ms between taps
    retryTapIfNoChange: true   # Retry if screen unchanged
    waitToSettleTimeoutMs: 500 # Wait for UI to settle

# Tap at specific point
- tapOn:
    point: "50%,50%"           # Center of screen
- tapOn:
    point: "100,200"           # Absolute pixels

# Tap within element
- tapOn:
    text: "Link text"
    point: "90%,50%"           # Tap right side of element
```

### Other Gestures

**Constraints:**
- You MUST use appropriate gesture for interaction type because wrong gesture fails
- You SHOULD specify duration for long press because default may not trigger action

```yaml
- doubleTapOn: "Element"
- longPressOn: "Element"
- longPressOn:
    id: "element"
    duration: 2000             # Hold for 2 seconds
```

### Text Input

**Constraints:**
- You MUST focus input before typing because unfocused inputs don't receive text
- You SHOULD erase existing text before input because appending to existing text is usually wrong
- You SHOULD hide keyboard after input because keyboard may obscure next element

```yaml
- inputText: "hello@email.com"
- eraseText: 5                 # Delete 5 characters
- eraseText                    # Delete all
- copyTextFrom:
    id: "display-field"
- pasteText
- hideKeyboard
```

### Navigation

**Constraints:**
- You MUST wait after navigation because screen transition takes time
- You SHOULD use scrollUntilVisible for off-screen elements because direct tap fails
- You MAY use back for Android back button because this is common navigation

```yaml
- back
- scroll
- scroll:
    direction: UP              # UP/DOWN/LEFT/RIGHT
- swipe:
    direction: LEFT
    duration: 500
- scrollUntilVisible:
    element:
      text: "Target"
    direction: DOWN
    timeout: 30000
- openLink: "https://example.com"
- openLink: "myapp://deep/link"
```

### Assertions

**Constraints:**
- You MUST use assertions to verify expected state because tests without assertions don't validate
- You MUST use assertNotVisible for absence checks because assertVisible with negative is wrong
- You SHOULD combine selectors for precision because loose selectors match wrong elements

```yaml
# Basic visibility
- assertVisible: "Welcome"
- assertVisible:
    id: "home-screen"
- assertVisible:
    text: "Button"
    enabled: true

# Not visible
- assertNotVisible: "Error"
- assertNotVisible:
    id: "loading-spinner"

# Condition
- assertTrue: ${condition}
```

### Waiting

**Constraints:**
- You MUST use explicit waits for async operations because implicit waits are unreliable
- You MUST set reasonable timeouts because too short causes flaky tests
- You SHOULD wait for animations because tapping during animation fails

```yaml
# Wait for element to appear
- extendedWaitUntil:
    visible:
      text: "Loaded"
    timeout: 10000

# Wait for element to disappear
- extendedWaitUntil:
    notVisible:
      id: "loading"
    timeout: 10000

# Wait for animations
- waitForAnimationToEnd
```

### Device Control

**Constraints:**
- You SHOULD use pressKey for hardware buttons because this simulates real user interaction
- You MAY set location for geo-dependent features because this enables location testing

```yaml
- pressKey: Home
- pressKey: Enter
- pressKey: Back
- setLocation:
    latitude: 40.7128
    longitude: -74.0060
- setAirplaneMode: true
- toggleAirplaneMode
```

### Recording & Screenshots

**Constraints:**
- You SHOULD use screenshots for debugging because visual evidence aids diagnosis
- You MAY use recording for complex flows because video captures full sequence

```yaml
- startRecording: video-name
- stopRecording
- takeScreenshot: screenshot-name
```

### State Management

**Constraints:**
- You MUST clear state between test runs because leftover state causes flaky tests
- You SHOULD clear keychain on iOS because credentials persist across installs

```yaml
- clearState                   # Clear app data
- clearKeychain                # iOS: clear keychain
```

### Scripting

**Constraints:**
- You MAY use runScript for complex logic because YAML has limited expressiveness
- You SHOULD use runFlow for reusable sequences because this promotes DRY
- You MAY use repeat for iteration because this avoids duplication

```yaml
- runScript: path/to/script.js
- evalScript: ${output.result}
- runFlow: path/to/other-flow.yaml
- repeat:
    times: 5
    commands:
      - tapOn: "Button"
```

---

## AI Assertions

**Constraints:**
- You SHOULD use AI assertions for visual validation because pixel-perfect assertions are brittle
- You MAY use text extraction for dynamic content because this handles variable data

**Visual Defect Detection:**

```yaml
- assertNoDefectsWithAI
```

**Semantic Validation:**

```yaml
- assertWithAI: "The login form displays email and password fields correctly"
```

**Text Extraction:**

```yaml
- extractTextWithAI:
    prompt: "What is the total price displayed?"
    output: totalPrice
- assertTrue: ${totalPrice == "$99.00"}
```

---

## Common Patterns

### Login Flow

**Constraints:**
- You MUST clear state before login because cached credentials skip login
- You MUST wait for home screen because navigation takes time

```yaml
appId: com.myapp
---
- launchApp:
    clearState: true
- tapOn:
    id: "email-input"
- inputText: "user@example.com"
- tapOn:
    id: "password-input"
- inputText: "SecurePass123"
- tapOn:
    id: "login-button"
- extendedWaitUntil:
    visible:
      id: "home-screen"
    timeout: 10000
```

### Form Validation

**Constraints:**
- You MUST test validation messages because user feedback is important
- You SHOULD test multiple invalid inputs because single test is insufficient

```yaml
appId: com.myapp
---
- launchApp
- tapOn:
    id: "submit-button"
- assertVisible: "Email is required"
- tapOn:
    id: "email-input"
- inputText: "invalid-email"
- tapOn:
    id: "submit-button"
- assertVisible: "Invalid email format"
```

### List Scroll & Select

**Constraints:**
- You MUST use scrollUntilVisible because direct tap fails for off-screen items
- You SHOULD set reasonable timeout because long lists take time to scroll

```yaml
- scrollUntilVisible:
    element:
      text: "Item 50"
    direction: DOWN
    timeout: 30000
- tapOn: "Item 50"
```

### Modal Handling

**Constraints:**
- You MUST wait for modal to appear because animation takes time
- You MUST wait for modal to disappear because closing has animation too

```yaml
- tapOn: "Show Modal"
- extendedWaitUntil:
    visible:
      id: "modal-container"
    timeout: 5000
- tapOn:
    id: "modal-close"
- extendedWaitUntil:
    notVisible:
      id: "modal-container"
    timeout: 3000
```

### Run Commands

**Constraints:**
- You MUST use --format junit for CI because this produces parseable results
- You SHOULD use --continuous for development because this speeds iteration

```bash
# All flows
maestro test flows/

# Single flow
maestro test flows/auth/login.yaml

# With recording
maestro record flows/auth/login.yaml

# CI/CD output
maestro test flows/ --format junit --output results.xml

# Continuous mode (re-run on file change)
maestro test flows/ --continuous
```

---

## Troubleshooting

### Selector Not Finding Element

If selector fails to find element:
- You SHOULD verify testID is set correctly because typos cause failures
- You SHOULD check element is visible because hidden elements aren't findable
- You MUST use mobile_list_elements_on_screen to debug because this shows actual identifiers

### Test Flaky

If test passes sometimes and fails sometimes:
- You SHOULD add explicit waits because race conditions cause flakiness
- You SHOULD use retryTapIfNoChange because timing issues cause missed taps
- You MUST NOT use fixed sleep because this is slow and still flaky

### Flow Hangs

If flow stops making progress:
- You SHOULD check for unexpected dialogs because system dialogs block tests
- You SHOULD verify app is responsive because crashed apps don't respond
- You MUST add timeouts to waits because missing timeout causes infinite hang

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
