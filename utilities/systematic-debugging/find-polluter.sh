#!/usr/bin/env bash
# Bisection script to find which test creates unwanted files/state
# Usage: ./find-polluter.sh <file_or_dir_to_check> <test_pattern>
# Example: ./find-polluter.sh '.git' 'src/**/*.test.ts'

set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  find-polluter.sh <file_to_check> <test_pattern>

Example:
  find-polluter.sh '.git' 'src/**/*.test.ts'
TXT
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == --* || "${1:-}" == -?* ]]; then
  echo "ERROR: unknown option: ${1:-}" >&2
  usage >&2
  exit 2
fi

if [ $# -ne 2 ]; then
  usage >&2
  exit 2
fi

POLLUTION_CHECK="$1"
TEST_PATTERN="$2"

echo "🔍 Searching for test that creates: $POLLUTION_CHECK"
echo "Test pattern: $TEST_PATTERN"
echo ""

# Get list of test files
TEST_FILES=()
if command -v fd >/dev/null 2>&1; then
  while IFS= read -r test_file; do
    [[ -n "$test_file" ]] || continue
    TEST_FILES+=("$test_file")
  done < <(fd -t f -g "$TEST_PATTERN" . | sort)
elif command -v rg >/dev/null 2>&1; then
  while IFS= read -r test_file; do
    [[ -n "$test_file" ]] || continue
    TEST_FILES+=("$test_file")
  done < <(rg --files -g "$TEST_PATTERN" . | sort)
else
  echo "❌ Missing dependency: fd or rg is required to enumerate test files." >&2
  exit 1
fi

TOTAL=${#TEST_FILES[@]}

if [ "$TOTAL" -eq 0 ]; then
  echo "❌ No test files matched pattern: $TEST_PATTERN"
  exit 2
fi

echo "Found $TOTAL test files"
echo ""

if ! command -v npm >/dev/null 2>&1; then
  echo "❌ Missing dependency: npm is required to run test files." >&2
  exit 1
fi

COUNT=0
for TEST_FILE in "${TEST_FILES[@]}"; do
  COUNT=$((COUNT + 1))

  # Skip if pollution already exists
  if [ -e "$POLLUTION_CHECK" ]; then
    echo "⚠️  Pollution already exists before test $COUNT/$TOTAL"
    echo "   Skipping: $TEST_FILE"
    continue
  fi

  echo "[$COUNT/$TOTAL] Testing: $TEST_FILE"

  # Run the test
  npm test -- "$TEST_FILE" > /dev/null 2>&1 || true

  # Check if pollution appeared
  if [ -e "$POLLUTION_CHECK" ]; then
    echo ""
    echo "🎯 FOUND POLLUTER!"
    echo "   Test: $TEST_FILE"
    echo "   Created: $POLLUTION_CHECK"
    echo ""
    echo "Pollution details:"
    ls -la "$POLLUTION_CHECK"
    echo ""
    echo "To investigate:"
    echo "  npm test $TEST_FILE    # Run just this test"
    echo "  cat $TEST_FILE         # Review test code"
    exit 1
  fi
done

echo ""
echo "✅ No polluter found - all tests clean!"
exit 0
