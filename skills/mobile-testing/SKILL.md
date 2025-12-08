---
name: mobile-testing
description: Use when testing mobile apps (React Native, Expo, Flutter, native iOS/Android), debugging UI on simulators/emulators, generating E2E test suites, or when user mentions mobile testing, Maestro, mobile-mcp, or asks to interact with a mobile app. Provides dual-stack integration with mobile-mcp (interactive debugging) and Maestro (E2E test generation).
---

# Mobile Testing

Dual-stack approach:
- **mobile-mcp**: Interactive debugging via MCP tools
- **Maestro**: E2E test suites via YAML flows

## Prerequisites Check

Before starting, verify:

```bash
# Required
node --version          # v22+
java --version          # 17+
maestro --version       # Latest

# Platform-specific
xcode-select -p         # iOS
adb --version           # Android
```

Enable MCP servers:

1. Add to project's `.mcp.json` (or copy from `.claude/.mcp.json.template`):
```json
{
  "mcpServers": {
    "mobile-mcp": { "command": "npx", "args": ["-y", "@mobilenext/mobile-mcp@latest"] },
    "maestro": { "command": "maestro", "args": ["mcp"] }
  }
}
```

2. Enable in `.claude/settings.local.json`:
```json
{ "enabledMcpjsonServers": ["mobile-mcp", "maestro"] }
```

## Workflow: Choose Your Path

```
Task type?
│
├─ DEBUGGING (UI issues, element inspection)
│   → Use mobile-mcp directly
│   → See: references/mobile-mcp-tools.md
│
├─ E2E TEST GENERATION
│   → Step 1: Explore with mobile-mcp
│   → Step 2: Generate Maestro YAML
│   → Step 3: Validate with maestro test
│   → See: references/maestro-patterns.md
│
└─ EXPO/REACT NATIVE specific
    → See: references/expo-react-native.md
```

## Quick Start: Debugging

```
1. mobile_list_available_devices    → Find device
2. mobile_launch_app(appId)         → Start app
3. mobile_take_screenshot           → Visual context
4. mobile_list_elements_on_screen   → Accessibility tree
5. Analyze tree for issues          → testIDs, enabled states
```

## Quick Start: E2E Test

**1. Explore and discover flows:**
```
mobile_launch_app → mobile_take_screenshot → mobile_list_elements_on_screen
Navigate through app, document flows
```

**2. Generate Maestro YAML:**
```yaml
appId: com.myapp
---
- launchApp
- tapOn:
    id: "login-button"
- inputText: "user@example.com"
- assertVisible: "Welcome"
```

**3. Validate:**
```bash
maestro test flows/auth/login.yaml
```

## Critical: Expo Apps

**Never use Expo Go for E2E testing.** Use Development Builds.

```yaml
# Launch Expo Development Build
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
- extendedWaitUntil:
    visible:
      text: "Home"
    timeout: 15000
```

See `references/expo-react-native.md` for complete guide.

## Selector Priority

```yaml
# 1. testID (most stable)
- tapOn:
    id: "submit-button"

# 2. Text (readable but fragile)
- tapOn:
    text: "Submit"
```

## Common Fixes

| Problem | Fix |
|---------|-----|
| Element not found | Add `extendedWaitUntil` before action |
| Wrong element tapped | Use `id:` instead of `text:` |
| Expo shows dev screen | Use `openLink` deep link |
| Flaky tests | Add explicit waits, use testIDs |

## Examples

Ready-to-use Maestro flow templates:

- `examples/login-flow.yaml` - Basic authentication flow
- `examples/form-validation.yaml` - Form validation testing
- `examples/expo-dev-build.yaml` - Expo Development Build launch pattern

Run with: `maestro test examples/login-flow.yaml`

## Reference Files

- **Maestro commands & patterns**: `references/maestro-patterns.md`
- **mobile-mcp tools**: `references/mobile-mcp-tools.md`
- **Expo/React Native**: `references/expo-react-native.md`
