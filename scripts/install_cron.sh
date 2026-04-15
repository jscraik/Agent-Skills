#!/usr/bin/env bash
# Install cron job for skill genome loop

set -euo pipefail

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/cron_genome_loop.sh"
CRON_ENTRY="0 4 * * * $SCRIPT_PATH"

# Check if already installed
if crontab -l 2>/dev/null | grep -q "cron_genome_loop.sh"; then
    echo "Cron job already installed."
    echo "Current entry:"
    crontab -l | grep "cron_genome_loop.sh"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✓ Cron job installed successfully"
echo "  Schedule: Daily at 4:00 AM UTC"
echo "  Script: $SCRIPT_PATH"
echo ""
echo "To view: crontab -l"
echo "To remove: crontab -e (then delete the line)"
echo ""
echo "Current crontab:"
crontab -l 2>/dev/null || echo "(empty)"
