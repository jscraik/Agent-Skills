#!/bin/bash
# Nightly cron job for skill genome loop
# Add to crontab: 0 4 * * * /path/to/Infrastructure/scripts/cron_genome_loop.sh >> logs/genome-loop.log 2>&1

set -e

# Configuration
REPO_ROOT="/Users/jamiecraik/dev/agent-skills"
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/genome-loop.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $1" >> "$LOG_FILE"
}

# Start
log "=== Starting nightly skill genome loop ==="

# Change to repo root
cd "$REPO_ROOT"

python_cmd=(python3)
if command -v mise >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
    python_cmd=(mise exec -- uv run --python 3.12 python)
elif command -v uv >/dev/null 2>&1; then
    python_cmd=(uv run --python 3.12 python)
fi

# Pull latest changes (optional, uncomment if needed)
# git pull origin main >> "$LOG_FILE" 2>&1

# Run genome loop
log "Running genome loop..."
"${python_cmd[@]}" Infrastructure/scripts/run_skill_genome_loop.py >> "$LOG_FILE" 2>&1
GENOME_EXIT=$?

if [ $GENOME_EXIT -eq 0 ]; then
    log "Genome loop completed successfully"
else
    log "ERROR: Genome loop exited with code $GENOME_EXIT"
fi

# Check for pending candidates
PENDING_COUNT=$("${python_cmd[@]}" Infrastructure/scripts/review_candidates.py --list 2>/dev/null | grep -c "Candidate:" || echo "0")
log "Pending candidates awaiting review: $PENDING_COUNT"

# If candidates pending, send notification (optional - uncomment and configure)
# if [ "$PENDING_COUNT" -gt 0 ]; then
#     # Slack notification
#     curl -X POST -H 'Content-type: application/json' \
#         --data "{\"text\":\"🧬 Skill Genome Loop: $PENDING_COUNT candidate(s) pending review\"}" \
#         "$SLACK_WEBHOOK_URL" >> "$LOG_FILE" 2>&1
# fi

log "=== Nightly run complete ==="
echo "" >> "$LOG_FILE"

exit $GENOME_EXIT
