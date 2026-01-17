# Workflow Examples

Complete workflow examples for common Xcode CLI tasks.

## Contents

- [Complete Build and Run Workflow](#complete-build-and-run-workflow)

## Complete Build and Run Workflow

```bash
#!/bin/bash
set -e

# Configuration
WORKSPACE="/path/to/App.xcworkspace"
SCHEME="App"
BUNDLE_ID="com.example.app"
DERIVED_DATA="/tmp/build"

# 1. Find simulator
echo "Finding simulator..."
UDID=$(xcrun simctl list devices --json | \
  jq -r '.devices | .[].[] | select(.name=="iPhone 16 Pro" and .isAvailable==true) | .udid' | head -1)

if [ -z "$UDID" ]; then
  echo "Error: No simulator found"
  exit 1
fi
echo "Using simulator: $UDID"

# 2. Boot simulator
echo "Booting simulator..."
xcrun simctl boot "$UDID" 2>/dev/null || true
sleep 3

# 3. Build
echo "Building..."
xcodebuild \
  -workspace "$WORKSPACE" \
  -scheme "$SCHEME" \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath "$DERIVED_DATA" \
  -configuration Debug \
  build

# 4. Find app
APP_PATH=$(find "$DERIVED_DATA" -name "*.app" -type d | head -1)
echo "Found app: $APP_PATH"

# 5. Install
echo "Installing..."
xcrun simctl install "$UDID" "$APP_PATH"

# 6. Launch with logging
echo "Launching..."
xcrun simctl launch --console "$UDID" "$BUNDLE_ID"
```
