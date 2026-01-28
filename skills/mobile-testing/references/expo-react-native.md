# Expo & React Native Testing Reference

## Overview

This reference defines testing patterns for Expo and React Native applications. Understanding these patterns is essential for effective mobile testing with Maestro and mobile-mcp.

---

## Table of Contents
1. [Development Builds vs Expo Go](#development-builds-vs-expo-go)
2. [testID Implementation](#testid-implementation)
3. [Deep Links](#deep-links)
4. [Common Issues](#common-issues)
5. [CI/CD Integration](#cicd-integration)

---

## Development Builds vs Expo Go

### The Problem with Expo Go

**Constraints:**
- You MUST NOT use Expo Go for E2E testing because Maestro cannot control apps inside Expo Go container
- You MUST use Development Builds for proper testing because these provide direct app control
- You SHOULD build development clients early because build time affects workflow

Maestro cannot launch apps via bundle ID when using Expo Go because:
- App runs inside Expo Go container
- Bundle ID points to Expo Go, not your app
- No direct app control

### Solution: Development Builds

**Constraints:**
- You MUST install expo-dev-client because this enables development builds
- You MUST build for target platform because cross-platform testing needs both
- You SHOULD use EAS Build because this simplifies the build process

Development Builds create a standalone app with your code:

```bash
# Create development build
npx expo install expo-dev-client
eas build --profile development --platform ios
eas build --profile development --platform android
```

**Benefits:**
- Direct bundle ID access
- Full native module support
- Proper E2E testing environment

---

## testID Implementation

### React Native Components

**Constraints:**
- You MUST add testID to all interactive elements because Maestro needs stable selectors
- You MUST use descriptive, unique IDs because ambiguous IDs cause selector failures
- You SHOULD include screen context in testID because this prevents collisions

```tsx
// Button
<Pressable testID="login-button">
  <Text>Login</Text>
</Pressable>

// TextInput
<TextInput
  testID="email-input"
  placeholder="Email"
/>

// View containers
<View testID="profile-screen">
  ...
</View>
```

### Best Practices

**Constraints:**
- You MUST use descriptive IDs because clarity prevents maintenance issues
- You MUST include context in list items because indices change
- You SHOULD follow naming convention because consistency aids debugging

```tsx
// Use descriptive, unique IDs
testID="auth-login-button"      // Good
testID="btn1"                    // Bad

// Include screen context
testID="profile-edit-name-input" // Good
testID="name-input"              // Ambiguous

// Lists: use index or item ID
testID={`todo-item-${item.id}`}
testID={`list-item-${index}`}
```

### Maestro Selectors for testID

**Constraints:**
- You MUST prefer testID selectors because these are most stable
- You SHOULD use text fallback only when testID unavailable because text changes more often
- You MAY use index for duplicate text because this resolves ambiguity

```yaml
# By testID (preferred)
- tapOn:
    id: "login-button"

# Fallback to text
- tapOn:
    text: "Login"
```

---

## Deep Links

### Expo Development Build

**Constraints:**
- You MUST use correct deep link format because wrong format fails to launch
- You MUST use 10.0.2.2 for Android emulator because localhost doesn't resolve
- You SHOULD add extended wait after deep link because app load takes time

```yaml
# Standard deep link format
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"

# For iOS simulator
- openLink: "exp+com.myapp://expo-development-client/?url=http://localhost:8081"

# After opening, wait for app load
- extendedWaitUntil:
    visible:
      text: "Welcome"
    timeout: 15000
```

### Custom Deep Links (app.json)

**Constraints:**
- You MUST configure scheme in app.json because this enables custom deep links
- You SHOULD use app-specific scheme because this prevents conflicts with other apps

```json
{
  "expo": {
    "scheme": "myapp"
  }
}
```

```yaml
# Navigate to specific screen
- openLink: "myapp://profile"
- openLink: "myapp://product/123"
```

### Expo Go (not recommended)

**Constraints:**
- You MUST NOT use Expo Go for E2E testing because control is limited
- You MAY use only for quick manual testing because automated testing fails

```yaml
# Only if absolutely necessary
- openLink: "exp://127.0.0.1:19000"
```

---

## Common Issues

### "Development Build" Screen Appears

**Constraints:**
- You MUST use openLink instead of launchApp because launchApp shows connection screen
- You MUST wait for home screen because proceeding too fast causes failures

**Cause:** Maestro launches app but dev client shows connection screen.

**Fix:**
```yaml
# Use openLink instead of launchApp
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
- extendedWaitUntil:
    visible:
      text: "Your App Home Screen"
    timeout: 20000
```

### Element Not Found

**Constraints:**
- You MUST verify testID is set because missing IDs cause failures
- You MUST use mobile_list_elements_on_screen for debugging because this reveals actual identifiers

**Cause:** testID not set or wrong selector.

**Debug:**
```
1. mobile_list_elements_on_screen
2. Search for element in tree
3. Verify identifier matches testID
```

**Fix:**
```tsx
// Add testID to component
<Button testID="submit-btn" title="Submit" />
```

### Timing Issues

**Constraints:**
- You MUST add explicit waits for async operations because race conditions cause flaky tests
- You SHOULD wait for animations to complete because tapping during animation fails

**Cause:** Assertions run before async operations complete.

**Fix:**
```yaml
# Add explicit wait
- extendedWaitUntil:
    visible:
      id: "data-loaded"
    timeout: 10000

# Or wait for animation
- waitForAnimationToEnd
```

### Navigation Not Working

**Constraints:**
- You MUST verify element is tappable because disabled elements don't respond
- You SHOULD check element coordinates because off-screen elements can't be tapped

**Cause:** Tap coordinates off or element not tappable.

**Debug:**
```
1. mobile_take_screenshot
2. mobile_list_elements_on_screen
3. Check element frame coordinates
4. Verify enabled: true
```

### Android Emulator Network

**Constraints:**
- You MUST use 10.0.2.2 for localhost on Android because emulator network is isolated
- You MUST NOT use localhost in Android deep links because this fails to resolve

**Cause:** `localhost` doesn't work in Android emulator.

**Fix:**
```yaml
# Use 10.0.2.2 for Android emulator
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
```

---

## CI/CD Integration

### GitHub Actions

**Constraints:**
- You MUST install Maestro in CI because it's not pre-installed
- You MUST boot simulator before running tests because tests require running device
- You SHOULD upload test results as artifacts because this enables post-run analysis

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on: [push]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Install Maestro
        run: curl -fsSL "https://get.maestro.mobile.dev" | bash

      - name: Start iOS Simulator
        run: |
          xcrun simctl boot "iPhone 15"
          xcrun simctl install booted app.app

      - name: Run E2E Tests
        run: |
          export PATH=$PATH:$HOME/.maestro/bin
          maestro test flows/ --format junit --output results.xml

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: results.xml
```

### EAS Workflows (Expo)

**Constraints:**
- You MUST use simulator build for iOS E2E because real device builds require signing
- You SHOULD use APK for Android E2E because this simplifies installation

```yaml
# eas.json workflow
build:
  e2e:
    distribution: internal
    ios:
      simulator: true
    android:
      buildType: apk

workflows:
  e2e-tests:
    jobs:
      - build:
          profile: e2e
      - custom:
          name: Run Maestro
          run: maestro test flows/
```

### Maestro Cloud

**Constraints:**
- You SHOULD use Maestro Cloud for parallel testing because this reduces total time
- You MUST set API key environment variable because authentication is required

```bash
# Upload and run in cloud
maestro cloud --app-file app.apk flows/

# With API key
MAESTRO_CLOUD_API_KEY=xxx maestro cloud flows/
```

---

## Troubleshooting

### Development Build Won't Install

If development build fails to install:
- You SHOULD verify build completed successfully because failed builds can't install
- You SHOULD check simulator/emulator is running because installation needs target
- You MUST match build architecture to device because ARM vs x86 causes failures

### testID Not Appearing in Element Tree

If testID is missing from accessibility tree:
- You SHOULD verify component supports testID because not all components do
- You SHOULD check for wrapper components because they may not forward testID
- You MUST use accessible={true} on custom components because this enables accessibility

### Deep Links Not Working

If deep links fail to open app:
- You SHOULD verify scheme is registered because unregistered schemes fail silently
- You SHOULD rebuild app after changing scheme because config changes need rebuild
- You MUST check URL encoding because special characters need escaping

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
