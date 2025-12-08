# Maestro YAML Patterns

## Table of Contents
1. [Flow Structure](#flow-structure)
2. [Selectors](#selectors)
3. [Commands Reference](#commands-reference)
4. [AI Assertions](#ai-assertions)
5. [Common Patterns](#common-patterns)

---

## Flow Structure

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

```yaml
- doubleTapOn: "Element"
- longPressOn: "Element"
- longPressOn:
    id: "element"
    duration: 2000             # Hold for 2 seconds
```

### Text Input

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

```yaml
- startRecording: video-name
- stopRecording
- takeScreenshot: screenshot-name
```

### State Management

```yaml
- clearState                   # Clear app data
- clearKeychain                # iOS: clear keychain
```

### Scripting

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

```yaml
- scrollUntilVisible:
    element:
      text: "Item 50"
    direction: DOWN
    timeout: 30000
- tapOn: "Item 50"
```

### Modal Handling

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
