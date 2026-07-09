#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE="$SCRIPT_DIR/Sources/ImproveAgentNativeMenuBar/App.swift"
BUILD_ROOT="${IMPROVE_AGENT_NATIVE_MENUBAR_BUILD_ROOT:-/Users/jamiecraik/.codex/usage-data/improve-agent-native-menubar}"
APP_DIR="$BUILD_ROOT/ImproveAgentNativeMenuBar.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
EXECUTABLE="$MACOS_DIR/ImproveAgentNativeMenuBar"
MODULE_CACHE="$BUILD_ROOT/clang-module-cache"
SWIFTPM_BUILD="$BUILD_ROOT/swiftpm-build"
LAUNCH_RECEIPT="$BUILD_ROOT/ImproveAgentNativeMenuBar.launch-receipt.json"

rm -rf "$APP_DIR" "$MODULE_CACHE"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$MODULE_CACHE"

stop_existing() {
  if command -v pkill >/dev/null 2>&1; then
    pkill -x ImproveAgentNativeMenuBar >/dev/null 2>&1 || true
    pkill -f "ImproveAgentNativeMenuBar.app/Contents/MacOS/ImproveAgentNativeMenuBar" >/dev/null 2>&1 || true
    sleep 0.4
  fi
}

stop_existing

cat > "$CONTENTS_DIR/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>ImproveAgentNativeMenuBar</string>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleIdentifier</key>
  <string>local.jscraik.improve-agent-native-menubar</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>Improve Agent Native</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>0.1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>14.0</string>
  <key>LSUIElement</key>
  <true/>
  <key>NSHumanReadableCopyright</key>
  <string>Local prototype</string>
  <key>NSPrincipalClass</key>
  <string>NSApplication</string>
</dict>
</plist>
PLIST
printf 'APPL????' > "$CONTENTS_DIR/PkgInfo"

pushd "$SCRIPT_DIR" >/dev/null
HOME="$BUILD_ROOT/home" \
XDG_CACHE_HOME="$BUILD_ROOT/xdg-cache" \
XDG_STATE_HOME="$BUILD_ROOT/xdg-state" \
MISE_CACHE_DIR="$BUILD_ROOT/mise-cache" \
MISE_STATE_DIR="$BUILD_ROOT/mise-state" \
CLANG_MODULE_CACHE_PATH="$MODULE_CACHE" \
swift build --build-system native --disable-sandbox --build-path "$SWIFTPM_BUILD"
popd >/dev/null
BUILD_EXECUTABLE="$SWIFTPM_BUILD/debug/ImproveAgentNativeMenuBar"
if [[ ! -x "$BUILD_EXECUTABLE" ]]; then
  BUILD_EXECUTABLE="$(find "$SWIFTPM_BUILD" -path "*/debug/ImproveAgentNativeMenuBar" -type f -perm -111 -print -quit)"
fi
if [[ -z "$BUILD_EXECUTABLE" || ! -x "$BUILD_EXECUTABLE" ]]; then
  echo "SwiftPM build completed but ImproveAgentNativeMenuBar executable was not found under $SWIFTPM_BUILD" >&2
  exit 1
fi
cp "$BUILD_EXECUTABLE" "$EXECUTABLE"
chmod +x "$EXECUTABLE"
cp "$SCRIPT_DIR/Sources/ImproveAgentNativeMenuBar/Resources/TesslLogo.png" "$RESOURCES_DIR/TesslLogo.png"
cp "$SCRIPT_DIR/Sources/ImproveAgentNativeMenuBar/Resources/SkillsSDKIcon.png" "$RESOURCES_DIR/SkillsSDKIcon.png"
/usr/bin/codesign --force --sign - "$APP_DIR" >/dev/null

echo "Built $APP_DIR"

if [[ "${NO_OPEN:-0}" == "1" ]]; then
  exit 0
fi

echo "Opening menu-bar prototype..."
OPEN_OUTPUT="$BUILD_ROOT/ImproveAgentNativeMenuBar.open.log"
if /usr/bin/open -n "$APP_DIR" >"$OPEN_OUTPUT" 2>&1; then
  cat > "$LAUNCH_RECEIPT" <<JSON
{
  "schema_version": "improve-agent-native-menubar-launch/v1",
  "status": "launched",
  "launch_method": "launchservices_open",
  "app_path": "$APP_DIR",
  "executable_path": "$EXECUTABLE"
}
JSON
  exit 0
fi

OPEN_ERROR="$(tr '\n' ' ' < "$OPEN_OUTPUT" | sed 's/"/\\"/g')"
cat > "$LAUNCH_RECEIPT" <<JSON
{
  "schema_version": "improve-agent-native-menubar-launch/v1",
  "status": "blocked_launchservices",
  "launch_method": "launchservices_open",
  "app_path": "$APP_DIR",
  "executable_path": "$EXECUTABLE",
  "open_error": "$OPEN_ERROR",
  "manual_open_command": "open -n '$APP_DIR'"
}
JSON

echo "LaunchServices open failed; app bundle was built but not launched." >&2
cat "$OPEN_OUTPUT" >&2
echo "" >&2
echo "Try from a normal macOS Terminal or Finder session:" >&2
echo "  open -n '$APP_DIR'" >&2
echo "Launch receipt: $LAUNCH_RECEIPT" >&2
exit 1
