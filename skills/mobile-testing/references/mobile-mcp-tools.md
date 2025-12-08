# mobile-mcp Tools Reference

## Table of Contents
1. [Device Management](#device-management)
2. [App Lifecycle](#app-lifecycle)
3. [Screen Capture](#screen-capture)
4. [UI Interaction](#ui-interaction)
5. [Debugging Workflow](#debugging-workflow)

---

## Device Management

### mobile_list_available_devices

List all available simulators, emulators, and connected devices.

```
Returns: List of devices with:
- deviceId: Unique identifier
- name: Device name (e.g., "iPhone 15 Pro")
- platform: "ios" or "android"
- state: "Booted", "Shutdown", etc.
```

### mobile_get_screen_size

Get current device screen dimensions.

```
Returns: { width: number, height: number }
```

### mobile_get_orientation

Get current device orientation.

```
Returns: "portrait" or "landscape"
```

### mobile_set_orientation

Set device orientation.

```
Parameters:
- orientation: "portrait" | "landscape"
```

---

## App Lifecycle

### mobile_list_apps

List installed applications on device.

```
Returns: List of apps with bundle IDs
```

### mobile_launch_app

Start an application.

```
Parameters:
- appId: Bundle identifier (e.g., "com.myapp")
```

### mobile_terminate_app

Stop a running application.

```
Parameters:
- appId: Bundle identifier
```

### mobile_install_app

Install an application.

```
Parameters:
- appPath: Path to .app (iOS) or .apk (Android)
```

### mobile_uninstall_app

Remove an application.

```
Parameters:
- appId: Bundle identifier
```

---

## Screen Capture

### mobile_take_screenshot

Capture current screen as image.

```
Returns: Base64 encoded image or image data
Use for: Visual debugging, documenting UI state
```

### mobile_save_screenshot

Save screenshot to file.

```
Parameters:
- path: File path to save image
```

### mobile_list_elements_on_screen

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

Tap at specific screen coordinates.

```
Parameters:
- x: Horizontal position (pixels)
- y: Vertical position (pixels)
```

### mobile_double_tap_on_screen

Double tap at coordinates.

```
Parameters:
- x: Horizontal position
- y: Vertical position
```

### mobile_long_press_on_screen_at_coordinates

Long press at coordinates.

```
Parameters:
- x: Horizontal position
- y: Vertical position
- duration: Press duration in ms (optional)
```

### mobile_swipe_on_screen

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

Enter text (requires focused text field).

```
Parameters:
- text: Text to type
```

### mobile_press_button

Press hardware button.

```
Parameters:
- button: "home" | "back" | "menu" | "volumeUp" | "volumeDown"
```

### mobile_open_url

Open URL in device browser or deep link.

```
Parameters:
- url: URL or deep link (e.g., "myapp://screen")
```

---

## Debugging Workflow

### Step-by-Step Debug Process

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
```
1. mobile_list_elements_on_screen
2. Find button in tree
3. Check: enabled: true? visible: true?
4. If enabled: false → validation issue
5. If not in tree → rendering issue
```

**Text not appearing:**
```
1. mobile_list_elements_on_screen
2. Search for text element
3. Check parent container visibility
4. Verify text content matches expected
```

**Navigation not working:**
```
1. mobile_take_screenshot (before)
2. mobile_click_on_screen_at_coordinates
3. mobile_take_screenshot (after)
4. Compare: did screen change?
5. mobile_list_elements_on_screen → verify new screen elements
```
