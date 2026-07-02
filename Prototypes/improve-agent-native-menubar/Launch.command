#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_ROOT="$SCRIPT_DIR/dist"
APP_DIR="$BUILD_ROOT/Improve Agent Native.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
EXECUTABLE="$MACOS_DIR/ImproveAgentNativeMenuBar"
MODULE_CACHE="$BUILD_ROOT/clang-module-cache"
SWIFTPM_BUILD="$BUILD_ROOT/swiftpm-build"
BUILD_RECEIPT="$BUILD_ROOT/ImproveAgentNativeMenuBar.build-receipt.json"
LAUNCH_RECEIPT="$BUILD_ROOT/ImproveAgentNativeMenuBar.launch-receipt.json"
OPEN_APP=0
SAFE_OPEN=0

usage() {
  cat <<'USAGE'
Usage: ./Launch.command [--open|--open-safe]

Builds and signs the Improve Agent Native menu-bar prototype.

Default: build only; do not launch.
--open: build, sign, then open the .app bundle with LaunchServices.
--open-safe: open with the Tessl CLI disabled for launch validation.

The launcher intentionally never starts the raw executable directly.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --open)
      OPEN_APP=1
      ;;
    --open-safe)
      OPEN_APP=1
      SAFE_OPEN=1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

rm -rf "$APP_DIR" "$MODULE_CACHE"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$MODULE_CACHE"

stop_existing() {
  /usr/bin/osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
tell application id "local.jscraik.improve-agent-native-menubar" to quit
APPLESCRIPT
  /usr/bin/osascript <<'APPLESCRIPT' >/dev/null 2>&1 || true
tell application "Improve Agent Native" to quit
APPLESCRIPT
  if command -v pkill >/dev/null 2>&1; then
    pkill -x ImproveAgentNativeMenuBar >/dev/null 2>&1 || true
    pkill -f "Improve Agent Native.app/Contents/MacOS/ImproveAgentNativeMenuBar" >/dev/null 2>&1 || true
    sleep 0.4
  fi
}

stop_existing

SAFE_ENV_PLIST=""
if [[ "$SAFE_OPEN" == "1" ]]; then
  SAFE_ENV_PLIST='  <key>LSEnvironment</key>
  <dict>
    <key>IMPROVE_AGENT_NATIVE_DISABLE_TESSL_CLI</key>
    <string>1</string>
  </dict>'
fi

cat > "$CONTENTS_DIR/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>ImproveAgentNativeMenuBar</string>
  <key>CFBundleIdentifier</key>
  <string>local.jscraik.improve-agent-native-menubar</string>
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
${SAFE_ENV_PLIST}
</dict>
</plist>
PLIST

pushd "$SCRIPT_DIR" >/dev/null
HOME="$BUILD_ROOT/home" \
XDG_CACHE_HOME="$BUILD_ROOT/xdg-cache" \
XDG_STATE_HOME="$BUILD_ROOT/xdg-state" \
MISE_CACHE_DIR="$BUILD_ROOT/mise-cache" \
MISE_STATE_DIR="$BUILD_ROOT/mise-state" \
CLANG_MODULE_CACHE_PATH="$MODULE_CACHE" \
swift build --build-system native --disable-sandbox --build-path "$SWIFTPM_BUILD"
popd >/dev/null

BUILT_EXECUTABLE="$SWIFTPM_BUILD/$(uname -m)-apple-macosx/debug/ImproveAgentNativeMenuBar"
if [[ ! -x "$BUILT_EXECUTABLE" ]]; then
  BUILT_EXECUTABLE="$(find "$SWIFTPM_BUILD" -type f -perm -111 -name ImproveAgentNativeMenuBar | head -n 1)"
fi
if [[ -z "${BUILT_EXECUTABLE:-}" || ! -x "$BUILT_EXECUTABLE" ]]; then
  echo "SwiftPM build did not produce ImproveAgentNativeMenuBar" >&2
  exit 1
fi

cp "$BUILT_EXECUTABLE" "$EXECUTABLE"
chmod +x "$EXECUTABLE"
cp "$SCRIPT_DIR/Sources/ImproveAgentNativeMenuBar/Resources/TesslLogo.png" "$RESOURCES_DIR/TesslLogo.png"
printf 'APPL????' > "$CONTENTS_DIR/PkgInfo"
/usr/bin/codesign --force --sign - "$APP_DIR" >/dev/null

EXECUTABLE_MTIME="$(stat -f '%Sm' -t '%Y-%m-%dT%H:%M:%S%z' "$EXECUTABLE")"
cat > "$BUILD_RECEIPT" <<JSON
{
  "schema_version": "improve-agent-native-menubar-build/v1",
  "status": "pass",
  "app_dir": "$APP_DIR",
  "built_executable": "$BUILT_EXECUTABLE",
  "bundle_executable": "$EXECUTABLE",
  "bundle_executable_mtime": "$EXECUTABLE_MTIME"
}
JSON

echo "Built $APP_DIR"
echo "Build receipt $BUILD_RECEIPT"

if [[ "${NO_OPEN:-0}" == "1" || "$OPEN_APP" != "1" ]]; then
  echo "Build-only mode; not launching. Use ./Launch.command --open or ./Launch.command --open-safe to launch deliberately."
  exit 0
fi

if [[ "$SAFE_OPEN" == "1" ]]; then
  echo "Opening menu-bar prototype with Tessl CLI disabled..."
else
  echo "Opening menu-bar prototype..."
fi
LOG_FILE="$BUILD_ROOT/ImproveAgentNativeMenuBar.log"
PID_FILE="$BUILD_ROOT/ImproveAgentNativeMenuBar.pid"
STARTUP_RECEIPT="$BUILD_ROOT/ImproveAgentNativeMenuBar.startup-receipt.json"
rm -f "$PID_FILE"
rm -f "$STARTUP_RECEIPT"
: > "$LOG_FILE"
if IMPROVE_AGENT_NATIVE_STARTUP_RECEIPT="$STARTUP_RECEIPT" /usr/bin/open -n "$APP_DIR"; then
  cat > "$LAUNCH_RECEIPT" <<JSON
{
  "schema_version": "improve-agent-native-menubar-launch/v1",
  "status": "requested",
  "launch_method": "LaunchServices",
  "app_dir": "$APP_DIR",
  "bundle_executable": "$EXECUTABLE",
  "safe_open": $SAFE_OPEN,
  "log_file": "$LOG_FILE",
  "startup_receipt": "$STARTUP_RECEIPT"
}
JSON
  echo "LaunchServices open requested for $APP_DIR"
  echo "Launch receipt $LAUNCH_RECEIPT"
  exit 0
else
  cat > "$LAUNCH_RECEIPT" <<JSON
{
  "schema_version": "improve-agent-native-menubar-launch/v1",
  "status": "failed",
  "launch_method": "LaunchServices",
  "app_dir": "$APP_DIR",
  "bundle_executable": "$EXECUTABLE",
  "safe_open": $SAFE_OPEN,
  "log_file": "$LOG_FILE",
  "startup_receipt": "$STARTUP_RECEIPT"
}
JSON
  echo "LaunchServices open failed; see $LOG_FILE" >&2
  exit 1
fi
