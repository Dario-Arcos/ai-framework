# Expo & React Native Testing Guide

## Table of Contents
1. [Development Builds vs Expo Go](#development-builds-vs-expo-go)
2. [testID Implementation](#testid-implementation)
3. [Deep Links](#deep-links)
4. [Common Issues](#common-issues)
5. [CI/CD Integration](#cicd-integration)

---

## Development Builds vs Expo Go

### The Problem with Expo Go

Maestro cannot launch apps via bundle ID when using Expo Go because:
- App runs inside Expo Go container
- Bundle ID points to Expo Go, not your app
- No direct app control

### Solution: Development Builds

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

```yaml
# Only if absolutely necessary
- openLink: "exp://127.0.0.1:19000"
```

---

## Common Issues

### "Development Build" Screen Appears

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

**Cause:** Tap coordinates off or element not tappable.

**Debug:**
```
1. mobile_take_screenshot
2. mobile_list_elements_on_screen
3. Check element frame coordinates
4. Verify enabled: true
```

### Android Emulator Network

**Cause:** `localhost` doesn't work in Android emulator.

**Fix:**
```yaml
# Use 10.0.2.2 for Android emulator
- openLink: "exp+com.myapp://expo-development-client/?url=http://10.0.2.2:8081"
```

---

## CI/CD Integration

### GitHub Actions

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

```bash
# Upload and run in cloud
maestro cloud --app-file app.apk flows/

# With API key
MAESTRO_CLOUD_API_KEY=xxx maestro cloud flows/
```
