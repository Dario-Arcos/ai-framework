# mobile-mcp Tools Reference

## Overview

This reference defines mobile-mcp tools for interactive mobile debugging. Understanding these tools is essential for effective mobile app inspection and troubleshooting.

---

## Table of Contents
1. [Device Management](#device-management)
2. [App Lifecycle](#app-lifecycle)
3. [Screen Capture](#screen-capture)
4. [UI Interaction](#ui-interaction)
5. [Debugging Workflow](#debugging-workflow)

---

## Device Management

### mobile_list_available_devices

**Constraints:**
- You MUST call this first to discover available devices because device ID is required for all other calls
- You MUST let user select device if multiple are available because assuming wrong device causes confusion

List all available simulators, emulators, and connected devices.

```
Returns: List of devices with:
- deviceId: Unique identifier
- name: Device name (e.g., "iPhone 15 Pro")
- platform: "ios" or "android"
- state: "Booted", "Shutdown", etc.
```

### mobile_get_screen_size

**Constraints:**
- You SHOULD get screen size for coordinate calculations because size varies by device
- You MUST NOT hardcode coordinates because they differ across devices

Get current device screen dimensions.

```
Returns: { width: number, height: number }
```

### mobile_get_orientation

**Constraints:**
- You SHOULD check orientation before coordinate-based interactions because x/y swap in landscape

Get current device orientation.

```
Returns: "portrait" or "landscape"
```

### mobile_set_orientation

**Constraints:**
- You SHOULD test both orientations because UI may behave differently
- You MUST wait after orientation change because rotation animation takes time

Set device orientation.

```
Parameters:
- orientation: "portrait" | "landscape"
```

---

## App Lifecycle

### mobile_list_apps

**Constraints:**
- You SHOULD use this to find correct bundle ID because names and IDs often differ

List installed applications on device.

```
Returns: List of apps with bundle IDs
```

### mobile_launch_app

**Constraints:**
- You MUST use correct bundle ID because wrong ID fails silently
- You SHOULD wait after launch because app startup takes time

Start an application.

```
Parameters:
- appId: Bundle identifier (e.g., "com.myapp")
```

### mobile_terminate_app

**Constraints:**
- You SHOULD terminate between tests because this ensures clean state
- You MUST use correct bundle ID because wrong ID does nothing

Stop a running application.

```
Parameters:
- appId: Bundle identifier
```

### mobile_install_app

**Constraints:**
- You MUST use correct file type for platform because .app for iOS, .apk for Android
- You SHOULD verify install succeeded because corrupted files fail silently

Install an application.

```
Parameters:
- appPath: Path to .app (iOS) or .apk (Android)
```

### mobile_uninstall_app

**Constraints:**
- You SHOULD uninstall before reinstall because this clears all data
- You MUST NOT uninstall system apps because this causes errors

Remove an application.

```
Parameters:
- appId: Bundle identifier
```

---

## Screen Capture

### mobile_take_screenshot

**Constraints:**
- You MUST take screenshot to see current state because this is primary visual debugging tool
- You SHOULD take before and after screenshots because this shows state changes

Capture current screen as image.

```
Returns: Base64 encoded image or image data
Use for: Visual debugging, documenting UI state
```

### mobile_save_screenshot

**Constraints:**
- You SHOULD save screenshots for documentation because transient screenshots are lost
- You MUST use valid file path because invalid paths fail silently

Save screenshot to file.

```
Parameters:
- path: File path to save image
```

### mobile_list_elements_on_screen

**Constraints:**
- You MUST use this for debugging selectors because it reveals actual identifiers
- You MUST NOT cache results because UI changes frequently
- You SHOULD call after navigation because element tree changes between screens

Get accessibility tree of current screen.

```
Returns: Hierarchical structure with:
- type: Element type (Button, TextField, etc.)
- label: Accessibility label
- identifier: testID or accessibility identifier
- enabled: Boolean
- visible: Boolean
- frame: { x, y, width, height }
- children: Nested elements
```

**Key for debugging**: This reveals testIDs, accessibility labels, and element states.

---

## UI Interaction

### mobile_click_on_screen_at_coordinates

**Constraints:**
- You MUST use coordinates from element tree because guessing fails
- You SHOULD tap center of element because edge taps may miss

Tap at specific screen coordinates.

```
Parameters:
- x: Horizontal position (pixels)
- y: Vertical position (pixels)
```

### mobile_double_tap_on_screen

**Constraints:**
- You MUST use for double-tap interactions because single tap has different behavior

Double tap at coordinates.

```
Parameters:
- x: Horizontal position
- y: Vertical position
```

### mobile_long_press_on_screen_at_coordinates

**Constraints:**
- You MUST set appropriate duration because too short doesn't trigger long press
- You SHOULD use for context menus because this is standard pattern

Long press at coordinates.

```
Parameters:
- x: Horizontal position
- y: Vertical position
- duration: Press duration in ms (optional)
```

### mobile_swipe_on_screen

**Constraints:**
- You MUST calculate start and end coordinates because swipe needs direction
- You SHOULD use for scrolling and dismissing because this simulates finger gesture

Perform swipe gesture.

```
Parameters:
- startX: Start horizontal position
- startY: Start vertical position
- endX: End horizontal position
- endY: End vertical position
- duration: Swipe duration in ms (optional)
```

### mobile_type_keys

**Constraints:**
- You MUST focus text field first because typing without focus fails
- You SHOULD use for text input because this simulates keyboard

Enter text (requires focused text field).

```
Parameters:
- text: Text to type
```

### mobile_press_button

**Constraints:**
- You MUST use correct button name because invalid names fail
- You SHOULD use for hardware buttons because this simulates physical press

Press hardware button.

```
Parameters:
- button: "home" | "back" | "menu" | "volumeUp" | "volumeDown"
```

### mobile_open_url

**Constraints:**
- You MUST use for deep links because this is how to navigate within app
- You SHOULD use for testing URL handling because this validates deep linking

Open URL in device browser or deep link.

```
Parameters:
- url: URL or deep link (e.g., "myapp://screen")
```

---

## Debugging Workflow

### Step-by-Step Debug Process

**Constraints:**
- You MUST follow this sequence for systematic debugging because random exploration wastes time
- You MUST compare screenshot with element tree because this correlates visual and structural data
- You SHOULD take screenshots before and after interactions because this shows cause and effect

```
1. DISCOVER DEVICE
   mobile_list_available_devices
   → Identify target simulator/emulator

2. LAUNCH APP
   mobile_launch_app(appId: "com.myapp")
   → Start the application

3. CAPTURE STATE
   mobile_take_screenshot
   → Visual context of current screen

   mobile_list_elements_on_screen
   → Accessibility tree with all elements

4. ANALYZE
   Compare screenshot with element tree:
   - Find element by visual position
   - Check enabled/visible states
   - Identify missing testIDs
   - Discover accessibility issues

5. INTERACT (if needed)
   mobile_click_on_screen_at_coordinates
   mobile_type_keys
   → Reproduce user actions

6. VERIFY
   mobile_take_screenshot
   mobile_list_elements_on_screen
   → Confirm state changes
```

### Common Debug Scenarios

**Button not responding:**

**Constraints:**
- You MUST check enabled state because disabled buttons don't respond
- You SHOULD verify element is in tree because missing elements can't be tapped

```
1. mobile_list_elements_on_screen
2. Find button in tree
3. Check: enabled: true? visible: true?
4. If enabled: false → validation issue
5. If not in tree → rendering issue
```

**Text not appearing:**

**Constraints:**
- You MUST search element tree because text may be in unexpected location
- You SHOULD check parent visibility because hidden parents hide children

```
1. mobile_list_elements_on_screen
2. Search for text element
3. Check parent container visibility
4. Verify text content matches expected
```

**Navigation not working:**

**Constraints:**
- You MUST take before/after screenshots because this proves whether navigation occurred
- You SHOULD verify new screen elements because partial navigation is possible

```
1. mobile_take_screenshot (before)
2. mobile_click_on_screen_at_coordinates
3. mobile_take_screenshot (after)
4. Compare: did screen change?
5. mobile_list_elements_on_screen → verify new screen elements
```

---

## Troubleshooting

### Device Not Found

If mobile_list_available_devices returns empty:
- You SHOULD verify simulator/emulator is running because stopped devices don't appear
- You SHOULD check mobile-mcp server is running because connection may be lost
- You MUST restart mobile-mcp if connection issues persist because this resets state

### App Launch Fails

If mobile_launch_app returns error:
- You SHOULD verify app is installed because uninstalled apps can't launch
- You SHOULD check bundle ID is correct because typos cause failures
- You MUST reinstall if app is corrupted because damaged apps fail silently

### Elements Not Appearing in Tree

If mobile_list_elements_on_screen misses elements:
- You SHOULD wait for screen to settle because mid-animation trees are incomplete
- You SHOULD check accessibility settings because some elements may be hidden from accessibility
- You MUST ensure testID is set because elements without identifiers are harder to find

---

*Version: 1.1.0 | Updated: 2026-01-27*
*Compliant with strands-agents SOP format (RFC 2119)*
