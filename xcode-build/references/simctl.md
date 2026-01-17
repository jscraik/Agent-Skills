# xcrun simctl Reference

Complete command reference for `xcrun simctl`.

## Contents

- [Listing Simulators](#listing-simulators)
- [Extracting UDIDs with jq](#extracting-udids-with-jq)
- [Simulator Lifecycle](#simulator-lifecycle)
- [App Management](#app-management)
- [Screenshots and Video](#screenshots-and-video)
- [Location](#location)
- [Status Bar Overrides](#status-bar-overrides)
- [Push Notifications](#push-notifications)
- [Privacy Permissions](#privacy-permissions)
- [Pasteboard](#pasteboard)
- [URL Handling](#url-handling)
- [Keychain](#keychain)
- [Diagnostics](#diagnostics)

## Listing Simulators

```bash
# List all simulators (human readable)
xcrun simctl list devices

# List as JSON (better for parsing)
xcrun simctl list devices --json

# List only available simulators
xcrun simctl list devices available

# List simulators for specific OS
xcrun simctl list devices "iOS 18"

# List device types
xcrun simctl list devicetypes

# List runtimes
xcrun simctl list runtimes
```

## Extracting UDIDs with jq

```bash
# Get UDID of specific simulator
xcrun simctl list devices --json | \
  jq -r '.devices | .[].[] | select(.name=="iPhone 16 Pro") | .udid' | head -1

# Get all booted simulators
xcrun simctl list devices --json | \
  jq -r '.devices | .[].[] | select(.state=="Booted") | .udid'

# Get available simulators
xcrun simctl list devices --json | \
  jq -r '.devices | .[].[] | select(.isAvailable==true) | {name, udid}'
```

## Simulator Lifecycle

```bash
# Boot simulator
xcrun simctl boot $UDID

# Shutdown simulator
xcrun simctl shutdown $UDID

# Shutdown all simulators
xcrun simctl shutdown all

# Erase simulator (reset to clean state)
xcrun simctl erase $UDID

# Delete simulator
xcrun simctl delete $UDID

# Create new simulator
xcrun simctl create "My iPhone" \
  "com.apple.CoreSimulator.SimDeviceType.iPhone-16-Pro" \
  "com.apple.CoreSimulator.SimRuntime.iOS-18-0"
```

## App Management

```bash
# Install app
xcrun simctl install $UDID /path/to/App.app

# Uninstall app
xcrun simctl uninstall $UDID com.bundle.identifier

# Launch app
xcrun simctl launch $UDID com.bundle.identifier

# Launch with console output
xcrun simctl launch --console $UDID com.bundle.identifier

# Launch with stdout/stderr redirect
xcrun simctl launch \
  --stdout=/tmp/stdout.log \
  --stderr=/tmp/stderr.log \
  $UDID com.bundle.identifier

# Launch and wait for debugger
xcrun simctl launch -w $UDID com.bundle.identifier

# Terminate app
xcrun simctl terminate $UDID com.bundle.identifier

# List installed apps
xcrun simctl listapps $UDID

# Get app info
xcrun simctl appinfo $UDID com.bundle.identifier

# Get app container path
xcrun simctl get_app_container $UDID com.bundle.identifier
```

## Screenshots and Video

```bash
# Take screenshot
xcrun simctl io $UDID screenshot /tmp/screenshot.png

# Screenshot as JPEG
xcrun simctl io $UDID screenshot --type=jpeg /tmp/screenshot.jpg

# Record video
xcrun simctl io $UDID recordVideo /tmp/recording.mp4

# Record with codec
xcrun simctl io $UDID recordVideo --codec=h264 /tmp/recording.mp4

# Stop recording: Press Ctrl+C in the terminal running recordVideo
```

## Location

```bash
# Set custom location
xcrun simctl location $UDID set 37.7749,-122.4194

# Set location by name
xcrun simctl location $UDID set "San Francisco, CA"

# Reset location
xcrun simctl location $UDID clear
```

## Status Bar Overrides

```bash
# Override time
xcrun simctl status_bar $UDID override --time "9:41"

# Override battery
xcrun simctl status_bar $UDID override --batteryLevel 100 --batteryState charged

# Override network
xcrun simctl status_bar $UDID override --dataNetwork wifi --wifiBars 3

# Clear all overrides
xcrun simctl status_bar $UDID clear
```

## Push Notifications

```bash
# Send push notification
xcrun simctl push $UDID com.bundle.identifier /path/to/payload.json

# Payload example (payload.json):
# {
#   "aps": {
#     "alert": {
#       "title": "Test",
#       "body": "Hello from simctl"
#     }
#   }
# }
```

## Privacy Permissions

```bash
# Grant permission
xcrun simctl privacy $UDID grant photos com.bundle.identifier
xcrun simctl privacy $UDID grant camera com.bundle.identifier
xcrun simctl privacy $UDID grant microphone com.bundle.identifier
xcrun simctl privacy $UDID grant location com.bundle.identifier

# Revoke permission
xcrun simctl privacy $UDID revoke photos com.bundle.identifier

# Reset all permissions
xcrun simctl privacy $UDID reset all com.bundle.identifier
```

## Pasteboard

```bash
# Get pasteboard contents
xcrun simctl pbinfo $UDID

# Copy text to pasteboard
echo "Hello" | xcrun simctl pbcopy $UDID

# Paste from pasteboard
xcrun simctl pbpaste $UDID
```

## URL Handling

```bash
# Open URL in simulator
xcrun simctl openurl $UDID "https://example.com"

# Open deep link
xcrun simctl openurl $UDID "myapp://path/to/screen"
```

## Keychain

```bash
# Add certificate to keychain
xcrun simctl keychain $UDID add-root-cert /path/to/cert.pem

# Add CA certificate
xcrun simctl keychain $UDID add-ca-cert /path/to/ca.pem
```

## Diagnostics

```bash
# Collect diagnostic info
xcrun simctl diagnose

# Verbose logging
xcrun simctl logverbose $UDID enable
# ... reproduce issue ...
xcrun simctl logverbose $UDID disable

# Spawn process in simulator
xcrun simctl spawn $UDID log stream --predicate 'processImagePath CONTAINS "App"'
```
