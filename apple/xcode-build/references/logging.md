# Logging Reference

Complete reference for logging with `/usr/bin/log` and finding built apps.

## Contents

- [Streaming Logs](#streaming-logs)
- [Common Predicates](#common-predicates)
- [Finding Built App Path](#finding-built-app-path)

## Streaming Logs

```bash
# Stream logs for specific app
/usr/bin/log stream \
  --predicate 'processImagePath CONTAINS[cd] "AppName"' \
  --level debug

# Stream with JSON output
/usr/bin/log stream \
  --predicate 'processImagePath CONTAINS[cd] "AppName"' \
  --style json

# Stream with timeout
/usr/bin/log stream \
  --predicate 'processImagePath CONTAINS[cd] "AppName"' \
  --timeout 60s

# Filter by message content
/usr/bin/log stream \
  --predicate 'eventMessage CONTAINS[cd] "error"' \
  --level debug

# Save to file (background)
/usr/bin/log stream \
  --predicate 'processImagePath CONTAINS[cd] "AppName"' \
  --style json > /tmp/logs.json &
LOG_PID=$!

# Stop logging
kill $LOG_PID
```

## Common Predicates

| Predicate | Description |
|-----------|-------------|
| `processImagePath CONTAINS[cd] "App"` | Filter by app name |
| `eventMessage CONTAINS[cd] "error"` | Filter by message |
| `category == "network"` | Filter by category |
| `subsystem == "com.apple.xxx"` | Filter by subsystem |
| `messageType == error` | Only errors |

## Finding Built App Path

```bash
# If using -derivedDataPath
find /tmp/build -name "*.app" -type d | head -1

# Default derived data location
find ~/Library/Developer/Xcode/DerivedData -name "*.app" -path "*Debug-iphonesimulator*" | head -1

# Get from build settings
xcodebuild -workspace App.xcworkspace -scheme App -showBuildSettings | grep "BUILT_PRODUCTS_DIR"
```
