# xcodebuild Reference

Complete command reference for `xcodebuild`.

## Contents

- [Project Discovery](#project-discovery)
- [Building for iOS Simulator](#building-for-ios-simulator)
- [Building for Device](#building-for-device)
- [Building for macOS](#building-for-macos)
- [Archives and Distribution](#archives-and-distribution)
- [Testing](#testing)
- [Useful Flags](#useful-flags)

## Project Discovery

```bash
# List all schemes in workspace
xcodebuild -workspace /path/to/App.xcworkspace -list

# List all schemes in project
xcodebuild -project /path/to/App.xcodeproj -list

# Show available SDKs
xcodebuild -showsdks

# Show available destinations for a scheme
xcodebuild -workspace /path/to/App.xcworkspace -scheme SchemeName -showDestinations

# Show all build settings
xcodebuild -workspace /path/to/App.xcworkspace -scheme SchemeName -showBuildSettings

# Get specific build setting
xcodebuild -workspace /path/to/App.xcworkspace -scheme SchemeName \
  -showBuildSettings | grep PRODUCT_BUNDLE_IDENTIFIER
```

## Building for iOS Simulator

```bash
# Basic build
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,name=iPhone 16 Pro" \
  build

# Build with specific simulator UUID
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" \
  -configuration Debug \
  build

# Build with custom derived data path (recommended)
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath /tmp/build \
  build

# Clean build
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  clean build

# Build with specific iOS version
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,name=iPhone 16 Pro,OS=18.0" \
  build
```

## Building for Device

```bash
# Build for generic iOS device (no signing)
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "generic/platform=iOS" \
  -configuration Release \
  build

# Build for connected device
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS,id=DEVICE_UDID" \
  build
```

## Building for macOS

```bash
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme MacScheme \
  -destination "platform=macOS" \
  build
```

## Archives and Distribution

```bash
# Create archive
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "generic/platform=iOS" \
  -archivePath /tmp/App.xcarchive \
  archive

# Export IPA from archive
xcodebuild \
  -exportArchive \
  -archivePath /tmp/App.xcarchive \
  -exportPath /tmp/export \
  -exportOptionsPlist /path/to/ExportOptions.plist
```

## Testing

```bash
# Run all tests
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  test

# Run specific test class
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  -only-testing "AppTests/UserServiceTests" \
  test

# Run specific test method
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  -only-testing "AppTests/UserServiceTests/testLoginSuccess" \
  test

# Skip specific tests
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  -skip-testing "AppTests/SlowTests" \
  test

# Test with code coverage
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  -enableCodeCoverage YES \
  test

# Save test results
xcodebuild \
  -workspace /path/to/App.xcworkspace \
  -scheme SchemeName \
  -destination "platform=iOS Simulator,id=$UDID" \
  -resultBundlePath /tmp/TestResults.xcresult \
  test
```

## Useful Flags

| Flag | Description |
|------|-------------|
| `-workspace <path>` | Path to .xcworkspace |
| `-project <path>` | Path to .xcodeproj |
| `-scheme <name>` | Build scheme |
| `-destination <spec>` | Target device/simulator |
| `-configuration <name>` | Debug or Release |
| `-derivedDataPath <path>` | Where to put build products |
| `-quiet` | Suppress xcodebuild output |
| `-parallelizeTargets` | Build targets in parallel |
| `-jobs <n>` | Number of concurrent build jobs |
