#!/usr/bin/env bash
# Monitor CI health and alert when fallback may be needed
# Run this as a cron job every 5 minutes

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '.')"
ALERT_WEBHOOK="${FALLBACK_ALERT_WEBHOOK:-}"
LOG_FILE="${FALLBACK_MONITOR_LOG:-/tmp/fallback-monitor.log}"
STATE_FILE="${FALLBACK_STATE_FILE:-/tmp/fallback-monitor-state}"

# Thresholds (minutes)
QUEUE_THRESHOLD="${FALLBACK_QUEUE_THRESHOLD:-30}"
RATE_LIMIT_THRESHOLD="${FALLBACK_RATE_THRESHOLD:-10}"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*" | tee -a "$LOG_FILE"
}

check_workflow_queue() {
    local workflow="${1:-release.yml}"
    local queued_minutes=0
    
    # Get most recent workflow run status
    local run_info
    if ! run_info=$(gh run list --workflow="$workflow" --limit 1 --json status,startedAt,conclusion 2>/dev/null); then
        log "ERROR: Failed to query workflow status"
        return 1
    fi
    
    local status
    status=$(echo "$run_info" | jq -r '.[0].status')
    
    if [[ "$status" == "queued" || "$status" == "waiting" ]]; then
        local started_at
        started_at=$(echo "$run_info" | jq -r '.[0].startedAt')
        local started_epoch
        started_epoch=$(date -d "$started_at" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$started_at" +%s)
        local now_epoch
        now_epoch=$(date +%s)
        queued_minutes=$(( (now_epoch - started_epoch) / 60 ))
    fi
    
    echo "$queued_minutes"
}

check_rate_limits() {
    local remaining
    local limit
    
    if ! remaining=$(gh api rate_limit --jq '.resources.core.remaining' 2>/dev/null); then
        log "WARNING: Could not check rate limits"
        echo "100"  # Assume OK if we can't check
        return
    fi
    
    limit=$(gh api rate_limit --jq '.resources.core.limit')
    local percent=$(( remaining * 100 / limit ))
    
    echo "$percent"
}

check_github_status() {
    local indicator
    
    if ! indicator=$(curl -s --max-time 10 \
        https://www.githubstatus.com/api/v2/status.json | \
        jq -r '.status.indicator' 2>/dev/null); then
        log "WARNING: Could not check GitHub status"
        echo "unknown"
        return
    fi
    
    echo "$indicator"
}

send_alert() {
    local severity="$1"
    local message="$2"
    
    log "ALERT [$severity]: $message"
    
    # Console notification
    if [[ -n "${FALLBACK_NOTIFY_TERMINAL:-}" ]]; then
        echo -e "\a"  # Bell character
    fi
    
    # Webhook notification (Slack/Discord/etc)
    if [[ -n "$ALERT_WEBHOOK" ]]; then
        local payload
        payload=$(jq -n \
            --arg severity "$severity" \
            --arg message "$message" \
            --arg repo "$(basename "$REPO_ROOT")" \
            '{
                text: "Fallback Release Alert",
                attachments: [{
                    color: (if $severity == "critical" then "danger" elif $severity == "warning" then "warning" else "good" end),
                    fields: [
                        {title: "Repository", value: $repo, short: true},
                        {title: "Severity", value: $severity, short: true},
                        {title: "Message", value: $message, short: false}
                    ]
                }]
            }')
        
        curl -s -X POST -H "Content-Type: application/json" \
            -d "$payload" "$ALERT_WEBHOOK" > /dev/null || true
    fi
}

main() {
    log "Starting CI health check..."
    
    local issues=0
    local warnings=0
    
    # Check 1: Workflow queue time
    local queue_minutes
    queue_minutes=$(check_workflow_queue)
    log "Workflow queue time: ${queue_minutes} minutes"
    
    if [[ $queue_minutes -ge $QUEUE_THRESHOLD ]]; then
        send_alert "critical" "Workflow queued for ${queue_minutes} minutes (threshold: ${QUEUE_THRESHOLD})"
        ((issues++)) || true
    elif [[ $queue_minutes -ge $((QUEUE_THRESHOLD / 2)) ]]; then
        send_alert "warning" "Workflow queued for ${queue_minutes} minutes"
        ((warnings++)) || true
    fi
    
    # Check 2: API rate limits
    local rate_percent
    rate_percent=$(check_rate_limits)
    log "API rate limit: ${rate_percent}% remaining"
    
    if [[ $rate_percent -le $RATE_LIMIT_THRESHOLD ]]; then
        send_alert "critical" "API rate limit at ${rate_percent}% (threshold: ${RATE_LIMIT_THRESHOLD}%)"
        ((issues++)) || true
    elif [[ $rate_percent -le 25 ]]; then
        send_alert "warning" "API rate limit at ${rate_percent}%"
        ((warnings++)) || true
    fi
    
    # Check 3: GitHub status page
    local status_indicator
    status_indicator=$(check_github_status)
    log "GitHub status: $status_indicator"
    
    if [[ "$status_indicator" == "major" || "$status_indicator" == "critical" ]]; then
        send_alert "critical" "GitHub reports $status_indicator incident"
        ((issues++)) || true
    elif [[ "$status_indicator" == "minor" ]]; then
        send_alert "warning" "GitHub reports minor incident"
        ((warnings++)) || true
    fi
    
    # Update state file
    cat > "$STATE_FILE" << STATE
{
    "last_check": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "queue_minutes": $queue_minutes,
    "rate_percent": $rate_percent,
    "github_status": "$status_indicator",
    "issues": $issues,
    "warnings": $warnings
}
STATE
    
    # Summary
    if [[ $issues -gt 0 ]]; then
        log "CHECK FAILED: $issues issue(s), $warnings warning(s)"
        log "Consider activating fallback release path"
        exit 1
    elif [[ $warnings -gt 0 ]]; then
        log "CHECK PASSED with $warnings warning(s)"
        exit 0
    else
        log "CHECK PASSED: All systems healthy"
        exit 0
    fi
}

# Run main check
main "$@"
