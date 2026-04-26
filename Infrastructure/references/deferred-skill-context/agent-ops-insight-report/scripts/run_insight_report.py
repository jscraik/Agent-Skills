#!/usr/bin/env python3
"""
Codex Insights Report Generator
Full-featured insights matching commercial tools, with Codex as the only
narrative insight writer.

DATA SOURCE NOTES:
- ~/.codex/sessions/ — Session metadata + conversation events (no tool data)
- ~/.codex/history.jsonl — User message text fallback
- ~/.agents/otel-collector/ — Tool spans (requires CODEX_OTEL_ENABLED=1)

Codex runs tools server-side for security, so detailed tool logs aren't stored 
locally like Codex's ~/.codex/projects/ format. This report focuses on
session patterns, message analysis, timing, and Codex-generated insights.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
USAGE_DIR = Path(os.getenv("INSIGHT_REPORT_USAGE_DIR", HOME / ".codex" / "usage-data")).expanduser()
REPORT_HTML = USAGE_DIR / "report.html"
EVIDENCE_JSON = USAGE_DIR / "insight-evidence.json"
PROMPT_MD = USAGE_DIR / "INSIGHT_PROMPT.md"
INSIGHTS_JSON = USAGE_DIR / "insights.generated.json"

# Data sources
SESSIONS_DIR = Path(os.getenv("CODEX_SESSIONS_DIR", HOME / ".codex" / "sessions")).expanduser()
HISTORY_FILE = Path(os.getenv("CODEX_HISTORY_FILE", HOME / ".codex" / "history.jsonl")).expanduser()
OTEL_PATHS = [
    HOME / ".agents" / "otel-collector",
    HOME / ".codex" / "otel-collector",
    HOME / "Library" / "Application Support" / "Codex" / "otel-collector",
]

# Codex writer configuration
CODEX_TIMEOUT = int(os.getenv("INSIGHTS_CODEX_TIMEOUT", "900"))
PARSER_VERSION = 3

# Missing tool data message
MISSING_TOOL_DATA_MSG = "Not available — Codex runs tools server-side. Enable CODEX_OTEL_ENABLED=1 for tool data"

# Tool name normalization
TOOL_ALIASES = {
    "bash": "Shell",
    "shell": "Shell",
    "read_file": "ReadFile",
    "str_replace_file": "StrReplaceFile",
    "write_file": "WriteFile",
    "agent": "Agent",
    "web_search": "WebSearch",
    "web_fetch": "WebFetch",
}

# Label map for cleaning up category names
LABEL_MAP = {
    "debug_investigate": "Debug/Investigate",
    "implement_feature": "Implement Feature",
    "fix_bug": "Fix Bug",
    "write_script_tool": "Write Script/Tool",
    "refactor_code": "Refactor Code",
    "configure_system": "Configure System",
    "create_pr_commit": "Create PR/Commit",
    "analyze_data": "Analyze Data",
    "understand_codebase": "Understand Codebase",
    "write_tests": "Write Tests",
    "write_docs": "Write Docs",
    "deploy_infra": "Deploy/Infra",
    "warmup_minimal": "Cache Warmup",
    "fast_accurate_search": "Fast/Accurate Search",
    "correct_code_edits": "Correct Code Edits",
    "good_explanations": "Good Explanations",
    "proactive_help": "Proactive Help",
    "multi_file_changes": "Multi-file Changes",
    "handled_complexity": "Multi-file Changes",
    "good_debugging": "Good Debugging",
    "misunderstood_request": "Misunderstood Request",
    "wrong_approach": "Wrong Approach",
    "buggy_code": "Buggy Code",
    "user_rejected_action": "User Rejected Action",
    "codex_got_blocked": "Assistant Got Blocked",
    "user_stopped_early": "User Stopped Early",
    "wrong_file_or_location": "Wrong File/Location",
    "excessive_changes": "Excessive Changes",
    "slow_or_verbose": "Slow/Verbose",
    "tool_failed": "Tool Failed",
    "user_unclear": "User Unclear",
    "external_issue": "External Issue",
    "frustrated": "Frustrated",
    "dissatisfied": "Dissatisfied",
    "likely_satisfied": "Likely Satisfied",
    "satisfied": "Satisfied",
    "happy": "Happy",
    "unsure": "Unsure",
    "neutral": "Neutral",
    "delighted": "Delighted",
    "single_task": "Single Task",
    "multi_task": "Multi Task",
    "iterative_refinement": "Iterative Refinement",
    "exploration": "Exploration",
    "quick_question": "Quick Question",
    "fully_achieved": "Fully Achieved",
    "mostly_achieved": "Mostly Achieved",
    "partially_achieved": "Partially Achieved",
    "not_achieved": "Not Achieved",
    "unclear_from_transcript": "Unclear",
    "unhelpful": "Unhelpful",
    "slightly_helpful": "Slightly Helpful",
    "moderately_helpful": "Moderately Helpful",
    "very_helpful": "Very Helpful",
    "essential": "Essential",
}

SATISFACTION_ORDER = [
    "frustrated", "dissatisfied", "likely_satisfied", "satisfied", "happy", "unsure"
]
OUTCOME_ORDER = [
    "not_achieved", "partially_achieved", "mostly_achieved", "fully_achieved", "unclear_from_transcript"
]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Codex insights report with Codex-authored analysis")
    parser.add_argument("--days", type=int, default=7, help="Lookback window (default: 7)")
    parser.add_argument("--no-open", action="store_true", help="Compatibility flag; the runner never opens the OS browser")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--prepare-only", action="store_true", help="Write evidence and Codex prompt, then exit before invoking Codex")
    parser.add_argument("--render-only", action="store_true", help="Render HTML from existing evidence and insights JSON")
    parser.add_argument("--max-sessions", type=int, default=200, help="Max sessions to analyze (default: 200)")
    parser.add_argument("--max-evidence-sessions", type=int, default=30, help="Max transcript excerpts to include for Codex (default: 30)")
    parser.add_argument("--evidence-out", default=str(EVIDENCE_JSON), help=f"Evidence JSON path (default: {EVIDENCE_JSON})")
    parser.add_argument("--prompt-out", default=str(PROMPT_MD), help=f"Codex prompt path (default: {PROMPT_MD})")
    parser.add_argument("--insights-out", default=str(INSIGHTS_JSON), help=f"Generated insights JSON path (default: {INSIGHTS_JSON})")
    parser.add_argument("--insights-in", default=str(INSIGHTS_JSON), help=f"Insights JSON path for --render-only (default: {INSIGHTS_JSON})")
    args = parser.parse_args()
    if args.prepare_only and args.render_only:
        parser.error("--prepare-only and --render-only are mutually exclusive")
    return args


def find_session_files(days):
    """Find session files from ~/.codex/sessions/ within the lookback period."""
    if not SESSIONS_DIR.exists():
        return []
    
    cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
    cutoff_timestamp = cutoff.timestamp()
    files_with_mtime = []
    
    for year_dir in SESSIONS_DIR.iterdir():
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        year = int(year_dir.name)
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir() or not month_dir.name.isdigit():
                continue
            month = int(month_dir.name)
            for day_dir in month_dir.iterdir():
                if not day_dir.is_dir() or not day_dir.name.isdigit():
                    continue
                day = int(day_dir.name)
                try:
                    dir_date = datetime(year, month, day)
                    if dir_date < cutoff - timedelta(days=1):
                        continue
                except ValueError:
                    continue
                for f in day_dir.glob("rollout-*.jsonl"):
                    try:
                        file_timestamp = f.stat().st_mtime
                        if file_timestamp >= cutoff_timestamp:
                            files_with_mtime.append((f, file_timestamp))
                    except OSError:
                        continue
    
    # Sort by modification time (newest first) so max_sessions limit keeps recent sessions
    files_with_mtime.sort(key=lambda item: item[1], reverse=True)
    return [path for path, mtime in files_with_mtime]


def is_meta_session(events):
    """Check if this is a meta-session (insights API call that shouldn't be analyzed)."""
    for event in events[:10]:
        if event.get('type') == 'event_msg':
            payload = event.get('payload', {})
            if payload.get('type') == 'user_message':
                content = payload.get('message', '') or payload.get('content', '')
                if 'RESPOND WITH ONLY A VALID JSON OBJECT' in content:
                    return True
    return False


def count_lines_in_diff(old, new):
    """Count lines added/removed using unified diff."""
    old_lines = old.split('\n')
    new_lines = new.split('\n')
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
    
    added = 0
    removed = 0
    for line in diff[2:]:
        if line.startswith('+') and not line.startswith('+++'):
            added += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed += 1
    return added, removed


def extract_message_text(content):
    """Extract visible text from Codex message content blocks."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""

    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(parts)


def parse_session_file(file_path):
    """Parse a Codex session file into structured data."""
    events = []
    session_meta = None
    user_messages = []
    agent_messages = []
    seen_user_messages = set()
    seen_agent_messages = set()
    tool_calls = defaultdict(int)
    errors = 0
    tool_error_categories = defaultdict(int)
    files_modified = set()
    lines_added = 0
    lines_removed = 0
    message_hours = []
    user_message_timestamps = []
    last_assistant_timestamp = None
    user_response_times = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                    
                    if event.get('type') == 'session_meta':
                        session_meta = event.get('payload', {})
                    
                    elif event.get('type') == 'event_msg':
                        payload = event.get('payload', {})
                        msg_type = payload.get('type')
                        msg_timestamp = payload.get('timestamp') or event.get('timestamp')
                        
                        if msg_type == 'user_message':
                            content = payload.get('message', '') or payload.get('content', '')
                            # Handle block arrays - convert to string for analysis
                            if isinstance(content, list):
                                content = json.dumps(content)
                            is_human = bool(content and isinstance(content, str) and content.strip())
                            
                            if is_human:
                                message_key = (msg_timestamp, content.strip())
                                if message_key in seen_user_messages:
                                    continue
                                seen_user_messages.add(message_key)
                                user_messages.append((msg_timestamp, content))
                                
                                if msg_timestamp:
                                    try:
                                        msg_date = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                        message_hours.append(msg_date.hour)
                                        user_message_timestamps.append(msg_timestamp)
                                    except (TypeError, ValueError):
                                        continue
                                
                                if last_assistant_timestamp and msg_timestamp:
                                    try:
                                        assistant_time = datetime.fromisoformat(last_assistant_timestamp.replace('Z', '+00:00'))
                                        user_time = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                        response_time = (user_time - assistant_time).total_seconds()
                                        if 2 < response_time < 3600:
                                            user_response_times.append(response_time)
                                    except (TypeError, ValueError):
                                        continue
                            
                            if isinstance(content, str) and '[Request interrupted by user' in content:
                                errors += 1
                        
                        elif msg_type == 'agent_message':
                            content = payload.get('content', '')
                            if content:
                                message_key = (msg_timestamp, str(content).strip())
                                if message_key not in seen_agent_messages:
                                    seen_agent_messages.add(message_key)
                                    agent_messages.append((msg_timestamp, content))
                            if msg_timestamp:
                                last_assistant_timestamp = msg_timestamp
                        
                        elif msg_type == 'task_complete':
                            if payload.get('outcome') == 'error':
                                errors += 1
                        
                        if msg_type == 'user_message' and isinstance(payload.get('content'), list):
                            for block in payload['content']:
                                if block.get('type') == 'tool_result':
                                    if block.get('is_error'):
                                        errors += 1
                                        result_content = block.get('content', '')
                                        category = categorize_tool_error(result_content)
                                        tool_error_categories[category] += 1
                    
                    elif event.get('type') == 'response_item':
                        payload = event.get('payload', {})
                        payload_type = payload.get('type')

                        if payload_type == 'message':
                            role = payload.get('role')
                            content = extract_message_text(payload.get('content'))
                            msg_timestamp = event.get('timestamp')
                            if role == 'user' and content.strip():
                                message_key = (msg_timestamp, content.strip())
                                if message_key in seen_user_messages:
                                    continue
                                seen_user_messages.add(message_key)
                                user_messages.append((msg_timestamp, content))
                                if msg_timestamp:
                                    try:
                                        msg_date = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                        message_hours.append(msg_date.hour)
                                        user_message_timestamps.append(msg_timestamp)
                                    except (TypeError, ValueError):
                                        pass
                                if last_assistant_timestamp and msg_timestamp:
                                    try:
                                        assistant_time = datetime.fromisoformat(last_assistant_timestamp.replace('Z', '+00:00'))
                                        user_time = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                        response_time = (user_time - assistant_time).total_seconds()
                                        if 2 < response_time < 3600:
                                            user_response_times.append(response_time)
                                    except (TypeError, ValueError):
                                        pass
                            elif role == 'assistant' and content.strip():
                                message_key = (msg_timestamp, content.strip())
                                if message_key in seen_agent_messages:
                                    continue
                                seen_agent_messages.add(message_key)
                                agent_messages.append((msg_timestamp, content))
                                if msg_timestamp:
                                    last_assistant_timestamp = msg_timestamp

                        elif payload_type == 'function_call':
                            name = payload.get('name') or 'unknown'
                            normalized_name = TOOL_ALIASES.get(name, name)
                            tool_calls[normalized_name] += 1
                            arguments = payload.get('arguments') or {}
                            if isinstance(arguments, dict):
                                tool_input = arguments
                            else:
                                try:
                                    tool_input = json.loads(arguments) if isinstance(arguments, str) else {}
                                except json.JSONDecodeError:
                                    tool_input = {}

                            # Use normalized name for edit-metric classification so aliases
                            # like str_replace_file / write_file still count.
                            if normalized_name in ('Edit', 'Write', 'apply_patch', 'StrReplaceFile', 'WriteFile'):
                                file_path_mod = tool_input.get('file_path') or tool_input.get('path') or ''
                                if file_path_mod:
                                    files_modified.add(file_path_mod)

                                if normalized_name in ('Edit', 'StrReplaceFile'):
                                    old_str = tool_input.get('old_string', '')
                                    new_str = tool_input.get('new_string', '')
                                    if old_str is not None and new_str is not None:
                                        a, r = count_lines_in_diff(old_str, new_str)
                                        lines_added += a
                                        lines_removed += r
                                elif normalized_name in ('Write', 'WriteFile'):
                                    write_content = tool_input.get('content', '')
                                    if write_content:
                                        lines_added += write_content.count('\n') + 1

                        elif payload_type == 'function_call_output':
                            output = payload.get('output', '')
                            if isinstance(output, str):
                                match = re.search(r'Process exited with code ([1-9]\d*)', output)
                                if match:
                                    errors += 1
                                    category = categorize_tool_error(output)
                                    tool_error_categories[category] += 1
                except json.JSONDecodeError:
                    continue
    except (OSError, UnicodeError):
        return None
    
    if not session_meta:
        return None
    
    if is_meta_session(events):
        return None
    
    transcript_lines = []
    for i, (ts, msg) in enumerate(user_messages[:20]):
        transcript_lines.append(f"User: {msg[:300]}")
        if i < len(agent_messages):
            transcript_lines.append(f"Assistant: {agent_messages[i][1][:300]}")
    
    start_time = session_meta.get('timestamp', '')
    duration_minutes = 0
    if user_messages and start_time:
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            last_msg_time = None
            for ts, _ in user_messages[-1:]:
                if ts:
                    try:
                        last_msg_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        break
                    except (TypeError, ValueError):
                        continue
            if last_msg_time:
                duration_minutes = (last_msg_time - start).total_seconds() / 60
        except (TypeError, ValueError):
            duration_minutes = 0
    
    return {
        'parser_version': PARSER_VERSION,
        'session_id': session_meta.get('id', 'unknown'),
        'project_path': session_meta.get('cwd', ''),
        'start_time': start_time,
        'timestamp': start_time,
        'cwd': session_meta.get('cwd', ''),
        'cli_version': session_meta.get('cli_version', ''),
        'model_provider': session_meta.get('model_provider', ''),
        'agent_role': session_meta.get('agent_role', ''),
        'user_messages': len(user_messages),
        'agent_messages': len(agent_messages),
        'agent_responses': len(agent_messages),
        'tool_calls': dict(tool_calls),
        'errors': errors,
        'tool_error_categories': dict(tool_error_categories),
        'files_modified': len(files_modified),
        'lines_added': lines_added,
        'lines_removed': lines_removed,
        'duration_minutes': duration_minutes,
        'first_prompt': user_messages[0][1] if user_messages else '',
        'message_hours': message_hours,
        'user_message_timestamps': user_message_timestamps,
        'user_response_times': user_response_times,
        'transcript': '\n'.join(transcript_lines),
    }


def categorize_tool_error(content):
    """Categorize tool errors based on error message content."""
    if not isinstance(content, str):
        return "Other"
    
    lower = content.lower()
    if 'exit code' in lower:
        return "Command Failed"
    elif 'rejected' in lower or "doesn't want" in lower:
        return "User Rejected"
    elif 'string to replace not found' in lower or 'no changes' in lower:
        return "Edit Failed"
    elif 'modified since read' in lower:
        return "File Changed"
    elif 'exceeds maximum' in lower or 'too large' in lower:
        return "File Too Large"
    elif 'file not found' in lower or 'does not exist' in lower:
        return "File Not Found"
    return "Other"


def is_substantive_session(session):
    """Check if session is substantive enough to analyze."""
    # Require at least 2 user messages and 1+ minute duration
    # to filter out warmup, meta, and accidental micro-sessions.
    if session['user_messages'] < 2:
        return False
    duration_minutes = session.get('duration_minutes', 0) or 0
    if duration_minutes < 1:
        return False
    return True


def detect_parallel_codex_sessions(sessions):
    """Detect parallel Codex usage via timestamp overlap analysis."""
    OVERLAP_WINDOW_MS = 30 * 60000
    
    all_messages = []
    for session in sessions:
        for ts in session.get('user_message_timestamps', []):
            try:
                all_messages.append({
                    'ts': datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp() * 1000,
                    'session_id': session['session_id']
                })
            except (TypeError, ValueError):
                continue
    
    all_messages.sort(key=lambda x: x['ts'])
    
    parallel_codex_pairs = []
    messages_during = set()
    
    window_start = 0
    session_last_index = {}
    
    for i, msg in enumerate(all_messages):
        while window_start < i and msg['ts'] - all_messages[window_start]['ts'] > OVERLAP_WINDOW_MS:
            expiring = all_messages[window_start]
            if session_last_index.get(expiring['session_id']) == window_start:
                del session_last_index[expiring['session_id']]
            window_start += 1
        
        prev_index = session_last_index.get(msg['session_id'])
        if prev_index is not None:
            for j in range(prev_index + 1, i):
                between = all_messages[j]
                if between['session_id'] != msg['session_id']:
                    pair = tuple(sorted([msg['session_id'], between['session_id']]))
                    parallel_codex_pairs.append(pair)
                    messages_during.add(f"{all_messages[prev_index]['ts']}:{msg['session_id']}")
                    messages_during.add(f"{between['ts']}:{between['session_id']}")
                    messages_during.add(f"{msg['ts']}:{msg['session_id']}")
                    break
        
        session_last_index[msg['session_id']] = i
    
    sessions_with_overlaps = set()
    for pair in parallel_codex_pairs:
        sessions_with_overlaps.add(pair[0])
        sessions_with_overlaps.add(pair[1])
    
    return {
        'overlap_events': len(parallel_codex_pairs),
        'sessions_involved': len(sessions_with_overlaps),
        'user_messages_during': len(messages_during)
    }


def deduplicate_sessions(sessions):
    """Deduplicate session branches - keep the one with most user messages per session_id."""
    best_by_session = {}
    
    for session in sessions:
        session_id = session['session_id']
        existing = best_by_session.get(session_id)
        if not existing:
            best_by_session[session_id] = session
        elif session['user_messages'] > existing['user_messages']:
            best_by_session[session_id] = session
        elif session['user_messages'] == existing['user_messages'] and session['duration_minutes'] > existing['duration_minutes']:
            best_by_session[session_id] = session
    
    return list(best_by_session.values())


def extract_json_object(text):
    """Extract the first JSON object from a Codex response."""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def write_json(path, value):
    """Write JSON with private-by-default permissions."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
    except Exception:
        raise


def read_json(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object in {path}")
    return value


def load_cached_session_meta(session_id):
    """Load cached session metadata from disk."""
    try:
        cache_path = USAGE_DIR / "session-meta" / f"{session_id}.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            if cached.get("parser_version") == PARSER_VERSION:
                return cached
    except (OSError, json.JSONDecodeError):
        return None
    return None


def save_session_meta(session_id, meta):
    """Save session metadata cache to disk with private-by-default permissions."""
    try:
        meta_dir = USAGE_DIR / "session-meta"
        meta_dir.mkdir(parents=True, exist_ok=True)
        cache_path = meta_dir / f"{session_id}.json"
        with open(cache_path, 'w', encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        try:
            cache_path.chmod(0o600)
        except OSError:
            pass
    except OSError:
        return


def build_evidence_bundle(data, sessions, args):
    """Build the evidence bundle Codex uses to write the report."""
    samples = []
    for session in sessions[:args.max_evidence_sessions]:
        samples.append({
            "session_id": session.get("session_id", "")[:12],
            "project_path": session.get("project_path", ""),
            "start_time": session.get("start_time", ""),
            "duration_minutes": session.get("duration_minutes", 0),
            "user_messages": session.get("user_messages", 0),
            "assistant_messages": session.get("agent_messages", 0),
            "tool_calls": session.get("tool_calls", {}),
            "errors": session.get("errors", 0),
            "first_prompt": session.get("first_prompt", ""),
            "transcript_excerpt": session.get("transcript", "")[:3500],
        })

    metrics = {
        "period": data.get("period", {}),
        "sessions": data.get("sessions", {}),
        "tools": data.get("tools", {}),
        "metrics": data.get("metrics", {}),
        "tool_error_categories": data.get("tool_error_categories", {}),
        "parallel_codex": data.get("parallel_codex", {}),
        "data_quality": data.get("data_quality", "unknown"),
    }

    return {
        "schema_version": "codex-insight-evidence.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "writer": "codex",
        "notes": [
            "This file is evidence only; narrative insight must be written by Codex.",
            "Use only the evidence here. Do not invent unavailable tool logs, outcomes, or user intent.",
        ],
        "data": data,
        "metrics": metrics,
        "session_samples": samples,
    }


def build_codex_prompt(evidence):
    """Create the prompt passed to Codex for JSON insight writing."""
    evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    return f"""# Codex Insight Report Writer

You are Codex writing Jamie's Codex usage insight report from local evidence.

Return ONLY a valid JSON object. Do not wrap it in Markdown. Do not include commentary outside JSON.

## Grounding Rules

- Use only the evidence in this prompt.
- Do not invent exact outcomes, files, tools, errors, or user feelings when the evidence is weak.
- Write in second person ("you") and use plain English.
- Be candid and useful, not fluffy.
- Separate Codex-side friction from Jamie-side ambiguity when possible.
- Include prompt help for moments where Jamie may not know the technical vocabulary.
- Prefer copyable prompts that let Jamie describe intent without knowing the exact term.
- If evidence is thin, say so in `metadata.limitations`.

## Required JSON Shape

{{
  "metadata": {{
    "schema_version": "codex-insights.v1",
    "writer_provider": "codex",
    "generated_at": "ISO-8601 timestamp",
    "confidence": "high|medium|low",
    "limitations": ["missing or weak evidence"]
  }},
  "at_a_glance": {{
    "whats_working": "2-3 sentences",
    "whats_hindering": "2-3 sentences",
    "quick_wins": "2-3 sentences",
    "ambitious_workflows": "2-3 sentences"
  }},
  "project_areas": {{
    "areas": [
      {{"name": "Area name", "session_count": 1, "description": "2-3 sentences", "evidence": ["session id, metric, or transcript summary"]}}
    ]
  }},
  "interaction_style": {{
    "narrative": "2-3 paragraphs describing how Jamie uses Codex",
    "key_pattern": "One concise sentence"
  }},
  "what_works": {{
    "intro": "One sentence",
    "impressive_workflows": [
      {{"title": "Short title", "description": "2-3 sentences", "evidence": ["session id, metric, or transcript summary"]}}
    ]
  }},
  "friction_analysis": {{
    "intro": "One sentence",
    "categories": [
      {{"category": "Concrete category", "description": "1-2 sentences", "examples": ["specific example", "specific example"], "evidence": ["session id, metric, or transcript summary"]}}
    ]
  }},
  "prompting_help": {{
    "plain_english_patterns": [
      {{"situation": "When to use this", "copyable_prompt": "Prompt Jamie can paste", "evidence": ["session id, metric, or transcript summary"]}}
    ],
    "terms_to_learn": [
      {{"term": "technical term", "plain_english": "plain explanation", "when_to_use": "when it helps", "evidence": ["session id, metric, or transcript summary"]}}
    ]
  }},
  "suggestions": {{
    "agents_md_additions": [
      {{"addition": "Instruction to add", "why": "Why it helps", "where": "Suggested location", "evidence": ["session id, metric, or transcript summary"]}}
    ],
    "features_to_try": [
      {{"feature": "Codex feature", "one_liner": "What it does", "why_for_you": "Why it helps Jamie", "example_code": "Copyable command or prompt", "evidence": ["session id, metric, or transcript summary"]}}
    ],
    "usage_patterns": [
      {{"title": "Short title", "suggestion": "1-2 sentences", "detail": "3-4 sentences", "copyable_prompt": "Prompt to try", "evidence": ["session id, metric, or transcript summary"]}}
    ]
  }},
  "on_the_horizon": {{
    "intro": "One sentence",
    "opportunities": [
      {{"title": "Short title", "whats_possible": "2-3 sentences", "how_to_try": "1-2 sentences", "copyable_prompt": "Prompt to try", "evidence": ["session id, metric, or transcript summary"]}}
    ]
  }},
  "actionable_fixes": {{
    "executive_summary": {{
      "failures": "High|Medium|Low",
      "time_loss_driver": "Single biggest time sink",
      "top_issue": "Primary fix to apply",
      "priority": "One-line action priority"
    }},
    "priority_fixes": [
      {{
        "rank": 1,
        "title": "Fix title",
        "impact": "What this costs",
        "root_cause": "Why it happens",
        "fix_shell": "Exact shell command if safe, or empty string",
        "codex_command": "Copyable Codex prompt or command",
        "enforce": "AGENTS.md/hook/skill/config enforcement",
        "verify": "How Jamie knows it improved",
        "evidence": ["session id, metric, or transcript summary"]
      }}
    ],
    "stop_doing": ["Specific anti-pattern to stop"],
    "execution_order": ["1. First step", "2. Second step"]
  }},
  "fun_ending": {{
    "headline": "A memorable qualitative moment",
    "detail": "Brief context"
  }}
}}

## Evidence

{evidence_json}
"""


def validate_insights(insights):
    """Return writer-contract validation errors for generated insight JSON."""
    errors = []

    # Validate schema_version first
    metadata = insights.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("schema_version") != "codex-insights.v1":
        errors.append("metadata.schema_version must be 'codex-insights.v1'")

    required_sections = {
        "metadata": ("schema_version", "writer_provider", "generated_at", "confidence", "limitations"),
        "at_a_glance": ("whats_working", "whats_hindering", "quick_wins", "ambitious_workflows"),
        "project_areas": ("areas",),
        "interaction_style": ("narrative", "key_pattern"),
        "what_works": ("intro", "impressive_workflows"),
        "friction_analysis": ("intro", "categories"),
        "prompting_help": ("plain_english_patterns", "terms_to_learn"),
        "suggestions": ("agents_md_additions", "features_to_try", "usage_patterns"),
        "on_the_horizon": ("intro", "opportunities"),
        "actionable_fixes": ("executive_summary", "priority_fixes", "stop_doing", "execution_order"),
        "fun_ending": ("headline", "detail"),
    }
    required_list_fields = {
        "metadata.limitations",
        "project_areas.areas",
        "what_works.impressive_workflows",
        "friction_analysis.categories",
        "prompting_help.plain_english_patterns",
        "prompting_help.terms_to_learn",
        "suggestions.agents_md_additions",
        "suggestions.features_to_try",
        "suggestions.usage_patterns",
        "on_the_horizon.opportunities",
        "actionable_fixes.priority_fixes",
        "actionable_fixes.stop_doing",
        "actionable_fixes.execution_order",
    }
    second_person_paths = {
        "at_a_glance.whats_working",
        "at_a_glance.whats_hindering",
        "at_a_glance.quick_wins",
        "at_a_glance.ambitious_workflows",
        "interaction_style.narrative",
        "interaction_style.key_pattern",
        "suggestions.features_to_try[].why_for_you",
    }
    evidence_item_paths = {
        "project_areas.areas",
        "what_works.impressive_workflows",
        "friction_analysis.categories",
        "prompting_help.plain_english_patterns",
        "prompting_help.terms_to_learn",
        "suggestions.agents_md_additions",
        "suggestions.features_to_try",
        "suggestions.usage_patterns",
        "on_the_horizon.opportunities",
        "actionable_fixes.priority_fixes",
    }

    def has_second_person(value: str) -> bool:
        return bool(re.search(r"\b(you|your|yours|yourself)\b", value, flags=re.IGNORECASE))

    def section_payload(name: str) -> dict:
        payload = insights.get(name)
        return payload if isinstance(payload, dict) else {}

    for section, fields in required_sections.items():
        payload = insights.get(section)
        if not isinstance(payload, dict):
            errors.append(f"{section} must be an object")
            continue
        for field in fields:
            path = f"{section}.{field}"
            value = payload.get(field)
            if path in required_list_fields:
                if not isinstance(value, list):
                    errors.append(f"{path} must be a list")
                continue
            if value in (None, "", [], {}):
                errors.append(f"{path} is required")

    for path in evidence_item_paths:
        section, field = path.split(".", 1)
        values = section_payload(section).get(field, [])
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                errors.append(f"{path}[{index}] must be an object")
                continue
            evidence = item.get("evidence")
            if not isinstance(evidence, list) or not any(isinstance(entry, str) and entry.strip() for entry in evidence):
                errors.append(f"{path}[{index}].evidence must include at least one evidence entry")

    features = section_payload("suggestions").get("features_to_try", [])
    if isinstance(features, list):
        for index, item in enumerate(features):
            if not isinstance(item, dict):
                errors.append(f"suggestions.features_to_try[{index}] must be an object")
                continue
            for field in ("feature", "one_liner", "why_for_you", "example_code"):
                if not item.get(field):
                    errors.append(f"suggestions.features_to_try[{index}].{field} is required")

    for path in second_person_paths:
        if "[]" in path:
            section, rest = path.split(".", 1)
            list_name, field = rest.split("[].")
            values = section_payload(section).get(list_name, [])
            if isinstance(values, list) and not any(
                isinstance(item, dict) and isinstance(item.get(field), str) and has_second_person(item[field])
                for item in values
            ):
                errors.append(f"{path} must use second-person phrasing")
            continue
        section, field = path.split(".", 1)
        value = section_payload(section).get(field)
        if isinstance(value, str) and not has_second_person(value):
            errors.append(f"{path} must use second-person phrasing")

    return errors


def codex_command() -> list[str]:
    configured = os.getenv("INSIGHTS_CODEX_COMMAND", "").strip()
    if configured:
        return shlex.split(configured)
    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise RuntimeError("Codex CLI unavailable; set INSIGHTS_CODEX_COMMAND or rerun with --prepare-only.")
    return [codex_bin]


def run_codex_writer(prompt):
    """Ask Codex CLI to write the insight JSON and return the parsed object."""
    # Safety: fixed executable and fixed arguments; session evidence is passed on stdin only.
    result = subprocess.run(
        [*codex_command(), "exec", "--sandbox", "read-only"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=CODEX_TIMEOUT,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Codex writer failed with exit code {result.returncode}: {detail}")

    insights = extract_json_object(result.stdout)
    if not isinstance(insights, dict):
        raise RuntimeError("Codex writer did not return a valid JSON object")
    missing = validate_insights(insights)
    if missing:
        raise RuntimeError(f"Codex writer JSON missing required sections: {', '.join(missing)}")
    return insights


def generate_html_report(data, insights):
    """Generate full-featured HTML report."""
    
    def escape_html(text):
        text = str(text) if text else ""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    def escape_html_with_bold(text):
        escaped = escape_html(text)
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
    
    def generate_bar_chart(data_dict, color, max_items=6, fixed_order=None, not_available_text="No data"):
        if fixed_order:
            entries = [(k, data_dict.get(k, 0)) for k in fixed_order if k in data_dict and data_dict.get(k, 0) > 0]
        else:
            entries = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:max_items]
        
        if not entries:
            return f'<p class="empty">{not_available_text}</p>'
        
        max_val = max(e[1] for e in entries)
        if max_val == 0:
            return '<p class="empty">No data</p>'
        
        html = ""
        for label, count in entries:
            pct = (count / max_val) * 100
            clean_label = LABEL_MAP.get(label, label.replace('_', ' ').title())
            html += f'<div class="bar-row"><div class="bar-label">{escape_html(clean_label)}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div><div class="bar-value">{count}</div></div>'
        return html
    
    def generate_response_time_histogram(times):
        if not times:
            return '<p class="empty">No response time data</p>'
        
        buckets = {'2-10s': 0, '10-30s': 0, '30s-1m': 0, '1-2m': 0, '2-5m': 0, '5-15m': 0, '>15m': 0}
        for t in times:
            if t < 10:
                buckets['2-10s'] += 1
            elif t < 30:
                buckets['10-30s'] += 1
            elif t < 60:
                buckets['30s-1m'] += 1
            elif t < 120:
                buckets['1-2m'] += 1
            elif t < 300:
                buckets['2-5m'] += 1
            elif t < 900:
                buckets['5-15m'] += 1
            else:
                buckets['>15m'] += 1
        
        max_val = max(buckets.values())
        if max_val == 0:
            return '<p class="empty">No response time data</p>'
        
        html = ""
        for label, count in buckets.items():
            pct = (count / max_val) * 100
            html += f'<div class="bar-row"><div class="bar-label">{label}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:#6366f1"></div></div><div class="bar-value">{count}</div></div>'
        return html
    
    def generate_time_of_day_chart(hours):
        if not hours:
            return '<p class="empty">No time data</p>'
        
        hour_counts = {}
        for h in hours:
            hour_counts[h] = hour_counts.get(h, 0) + 1
        
        periods = [
            ('Morning (6-12)', [6, 7, 8, 9, 10, 11]),
            ('Afternoon (12-18)', [12, 13, 14, 15, 16, 17]),
            ('Evening (18-24)', [18, 19, 20, 21, 22, 23]),
            ('Night (0-6)', [0, 1, 2, 3, 4, 5]),
        ]
        
        period_counts = []
        for label, range_hours in periods:
            count = sum(hour_counts.get(h, 0) for h in range_hours)
            period_counts.append((label, count))
        
        max_val = max(c for _, c in period_counts) if period_counts else 1
        
        html = '<div id="hour-histogram">'
        for label, count in period_counts:
            pct = (count / max_val) * 100 if max_val > 0 else 0
            html += f'<div class="bar-row"><div class="bar-label">{label}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:#8b5cf6"></div></div><div class="bar-value">{count}</div></div>'
        html += '</div>'
        return html
    
    # Build sections
    at_a_glance = insights.get('at_a_glance', {})
    at_a_glance_html = ""
    if at_a_glance:
        sections = []
        if at_a_glance.get('whats_working'):
            sections.append(f'<div class="glance-section"><strong>What\'s working:</strong> {escape_html_with_bold(at_a_glance["whats_working"])} <a href="#section-wins" class="see-more">Impressive Things You Did →</a></div>')
        if at_a_glance.get('whats_hindering'):
            sections.append(f'<div class="glance-section"><strong>What\'s hindering you:</strong> {escape_html_with_bold(at_a_glance["whats_hindering"])} <a href="#section-friction" class="see-more">Where Things Go Wrong →</a></div>')
        if at_a_glance.get('quick_wins'):
            sections.append(f'<div class="glance-section"><strong>Quick wins to try:</strong> {escape_html_with_bold(at_a_glance["quick_wins"])} <a href="#section-features" class="see-more">Features to Try →</a></div>')
        if at_a_glance.get('ambitious_workflows'):
            sections.append(f'<div class="glance-section"><strong>Ambitious workflows:</strong> {escape_html_with_bold(at_a_glance["ambitious_workflows"])} <a href="#section-horizon" class="see-more">On the Horizon →</a></div>')
        
        at_a_glance_html = f'<div class="at-a-glance"><div class="glance-title">At a Glance</div><div class="glance-sections">{ "".join(sections) }</div></div>'
    
    # Project areas
    project_areas = insights.get('project_areas', {}).get('areas', [])
    project_areas_html = ""
    if project_areas:
        areas_html = "".join([f'<div class="project-area"><div class="area-header"><span class="area-name">{escape_html(a.get("name", ""))}</span><span class="area-count">~{a.get("session_count", 0)} sessions</span></div><div class="area-desc">{escape_html(a.get("description", ""))}</div></div>' for a in project_areas])
        project_areas_html = f'<h2 id="section-work">What You Work On</h2><div class="project-areas">{areas_html}</div>'
    
    # Other sections
    interaction = insights.get('interaction_style', {})
    interaction_html = ""
    if interaction:
        narrative = ""
        for para in (interaction.get('narrative', '') or '').split('\n\n'):
            if para.strip():
                narrative += f'<p>{escape_html_with_bold(para)}</p>'
        key_pattern = f'<div class="key-insight"><strong>Key pattern:</strong> {escape_html(interaction.get("key_pattern", ""))}</div>' if interaction.get('key_pattern') else ""
        interaction_html = f'<h2 id="section-usage">How You Use Codex</h2><div class="narrative">{narrative}{key_pattern}</div>'
    
    what_works = insights.get('what_works', {})
    what_works_html = ""
    if what_works and what_works.get('impressive_workflows'):
        workflows_html = "".join([f'<div class="big-win"><div class="big-win-title">{escape_html(w.get("title", ""))}</div><div class="big-win-desc">{escape_html(w.get("description", ""))}</div></div>' for w in what_works['impressive_workflows']])
        intro = f'<p class="section-intro">{escape_html(what_works.get("intro", ""))}</p>' if what_works.get('intro') else ""
        what_works_html = f'<h2 id="section-wins">Impressive Things You Did</h2>{intro}<div class="big-wins">{workflows_html}</div>'
    
    friction = insights.get('friction_analysis', {})
    friction_html = ""
    if friction and friction.get('categories'):
        cat_parts = []
        for category in friction['categories']:
            examples = category.get("examples", [])
            examples_html = ""
            if examples:
                items_html = "".join(f"<li>{escape_html(example)}</li>" for example in examples)
                examples_html = f'<ul class="friction-examples">{items_html}</ul>'
            cat_parts.append(
                f'<div class="friction-category"><div class="friction-title">{escape_html(category.get("category", ""))}</div>'
                f'<div class="friction-desc">{escape_html(category.get("description", ""))}</div>{examples_html}</div>'
            )
        cats_html = "".join(cat_parts)
        intro = f'<p class="section-intro">{escape_html(friction.get("intro", ""))}</p>' if friction.get('intro') else ""
        friction_html = f'<h2 id="section-friction">Where Things Go Wrong</h2>{intro}<div class="friction-categories">{cats_html}</div>'

    prompting_help = insights.get('prompting_help', {})
    prompting_help_html = ""
    if prompting_help:
        pattern_parts = []
        for item in prompting_help.get('plain_english_patterns', [])[:4]:
            pattern_parts.append(
                f'<div class="pattern-card"><div class="pattern-title">{escape_html(item.get("situation", ""))}</div>'
                f'<div class="copyable-prompt-section"><div class="prompt-label">Paste into Codex:</div>'
                f'<div class="copyable-prompt-row"><code class="copyable-prompt">{escape_html(item.get("copyable_prompt", ""))}</code>'
                f'<button class="copy-btn" onclick="copyText(this)">Copy</button></div></div></div>'
            )
        term_parts = []
        for item in prompting_help.get('terms_to_learn', [])[:6]:
            term_parts.append(
                f'<div class="feature-card"><div class="feature-title">{escape_html(item.get("term", ""))}</div>'
                f'<div class="feature-oneliner">{escape_html(item.get("plain_english", ""))}</div>'
                f'<div class="feature-why"><strong>When to use:</strong> {escape_html(item.get("when_to_use", ""))}</div></div>'
            )
        if pattern_parts or term_parts:
            prompting_help_html = (
                '<h2 id="section-prompting">Plain-English Prompting Help</h2>'
                '<p class="section-intro">Use these when you know what you want but not the technical vocabulary.</p>'
                f'<div class="patterns-section">{"".join(pattern_parts)}</div>'
                f'<div class="features-section">{"".join(term_parts)}</div>'
            )
    
    suggestions = insights.get('suggestions', {})
    suggestions_html = ""
    if suggestions:
        additions = suggestions.get('agents_md_additions', [])
        if additions:
            adds_html = "".join([f'<div class="agents-md-item"><input type="checkbox" id="cmd-{i}" class="cmd-checkbox" checked data-text="{escape_html(a.get("where", "Add to AGENTS.md") + chr(10) + chr(10) + a.get("addition", ""))}"><label for="cmd-{i}"><code class="cmd-code">{escape_html(a.get("addition", ""))}</code><button class="copy-btn" onclick="copyCmdItem({i})">Copy</button></label><div class="cmd-why">{escape_html(a.get("why", ""))}</div></div>' for i, a in enumerate(additions[:3])])
            suggestions_html += f'<h2 id="section-features">Suggested AGENTS.md Additions</h2><div class="agents-md-section">{adds_html}</div>'
        
        features = suggestions.get('features_to_try', [])
        if features:
            feats_parts = []
            for f in features[:3]:
                feat_html = f'<div class="feature-card"><div class="feature-title">{escape_html(f.get("feature", ""))}</div><div class="feature-oneliner">{escape_html(f.get("one_liner", ""))}</div><div class="feature-why"><strong>Why for you:</strong> {escape_html(f.get("why_for_you", ""))}</div>'
                if f.get("example_code"):
                    feat_html += f'<div class="feature-examples"><div class="example-code-row"><code class="example-code">{escape_html(f.get("example_code", ""))}</code><button class="copy-btn" onclick="copyText(this)">Copy</button></div></div>'
                feat_html += '</div>'
                feats_parts.append(feat_html)
            feats_html = "".join(feats_parts)
            suggestions_html += f'<h2 id="section-features-list">Features to Try</h2><div class="features-section">{feats_html}</div>'
        
        patterns = suggestions.get('usage_patterns', [])
        if patterns:
            pat_parts = []
            for p in patterns[:3]:
                pat_html = f'<div class="pattern-card"><div class="pattern-title">{escape_html(p.get("title", ""))}</div><div class="pattern-summary">{escape_html(p.get("suggestion", ""))}</div>'
                if p.get("detail"):
                    pat_html += f'<div class="pattern-detail">{escape_html(p.get("detail", ""))}</div>'
                if p.get("copyable_prompt"):
                    pat_html += f'<div class="copyable-prompt-section"><div class="prompt-label">Paste into Codex:</div><div class="copyable-prompt-row"><code class="copyable-prompt">{escape_html(p.get("copyable_prompt", ""))}</code><button class="copy-btn" onclick="copyText(this)">Copy</button></div></div>'
                pat_html += '</div>'
                pat_parts.append(pat_html)
            pat_html = "".join(pat_parts)
            suggestions_html += f'<h2 id="section-patterns">New Ways to Use Codex</h2><div class="patterns-section">{pat_html}</div>'
    
    horizon = insights.get('on_the_horizon', {})
    horizon_html = ""
    if horizon and horizon.get('opportunities'):
        opp_parts = []
        for o in horizon['opportunities'][:3]:
            opp_html = f'<div class="horizon-card"><div class="horizon-title">{escape_html(o.get("title", ""))}</div><div class="horizon-possible">{escape_html(o.get("whats_possible", ""))}</div>'
            if o.get("how_to_try"):
                opp_html += f'<div class="horizon-tip"><strong>Getting started:</strong> {escape_html(o.get("how_to_try", ""))}</div>'
            if o.get("copyable_prompt"):
                opp_html += f'<div class="pattern-prompt"><div class="prompt-label">Paste into Codex:</div><code>{escape_html(o.get("copyable_prompt", ""))}</code><button class="copy-btn" onclick="copyText(this)">Copy</button></div>'
            opp_html += '</div>'
            opp_parts.append(opp_html)
        opp_html = "".join(opp_parts)
        intro = f'<p class="section-intro">{escape_html(horizon.get("intro", ""))}</p>' if horizon.get('intro') else ""
        horizon_html = f'<h2 id="section-horizon">On the Horizon</h2>{intro}<div class="horizon-section">{opp_html}</div>'
    
    # V3 Actionable Fixes Section
    actionable = insights.get('actionable_fixes', {})
    actionable_html = ""
    if actionable:
        exec_summary = actionable.get('executive_summary', {})
        summary_html = ""
        if exec_summary:
            summary_html = '<div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; margin-bottom: 24px;"><div style="font-weight: 600; color: #991b1b; margin-bottom: 8px;">Executive Summary</div>'
            if exec_summary.get('failures'):
                summary_html += f'<div style="font-size: 13px; color: #7f1d1d; margin-bottom: 4px;"><strong>Failures:</strong> {escape_html(exec_summary["failures"])}</div>'
            if exec_summary.get('time_loss_driver'):
                summary_html += f'<div style="font-size: 13px; color: #7f1d1d; margin-bottom: 4px;"><strong>Time Loss Driver:</strong> {escape_html(exec_summary["time_loss_driver"])}</div>'
            if exec_summary.get('top_issue'):
                summary_html += f'<div style="font-size: 13px; color: #7f1d1d; margin-bottom: 4px;"><strong>Top Issue:</strong> {escape_html(exec_summary["top_issue"])}</div>'
            if exec_summary.get('priority'):
                summary_html += f'<div style="font-size: 13px; color: #7f1d1d;"><strong>Priority:</strong> {escape_html(exec_summary["priority"])}</div>'
            summary_html += '</div>'
        
        # Priority Fixes
        fixes_html = ""
        for fix in actionable.get('priority_fixes', []):
            fix_card = '<div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">'
            fix_card += f'<div style="font-weight: 600; font-size: 16px; color: #0f172a; margin-bottom: 8px;">#{fix.get("rank", "")} {escape_html(fix.get("title", ""))}</div>'
            if fix.get('impact'):
                fix_card += f'<div style="font-size: 13px; color: #64748b; margin-bottom: 8px;"><strong>Impact:</strong> {escape_html(fix["impact"])}</div>'
            if fix.get('root_cause'):
                fix_card += f'<div style="font-size: 13px; color: #64748b; margin-bottom: 12px;"><strong>Root Cause:</strong> {escape_html(fix["root_cause"])}</div>'
            if fix.get('fix_shell'):
                fix_card += f'<div style="background: #f1f5f9; padding: 10px; border-radius: 4px; margin-bottom: 8px;"><div style="font-size: 11px; color: #64748b; margin-bottom: 4px;">🔧 FIX (run this)</div><code style="font-family: monospace; font-size: 12px;">{escape_html(fix["fix_shell"])}</code></div>'
            if fix.get('codex_command'):
                fix_card += f'<div style="background: #eff6ff; padding: 10px; border-radius: 4px; margin-bottom: 8px;"><div style="font-size: 11px; color: #64748b; margin-bottom: 4px;">🧠 Codex Command</div><code style="font-family: monospace; font-size: 12px;">{escape_html(fix["codex_command"])}</code><button class="copy-btn" onclick="copyText(this)" style="margin-left: 8px;">Copy</button></div>'
            if fix.get('enforce'):
                fix_card += f'<div style="background: #f0fdf4; padding: 10px; border-radius: 4px; margin-bottom: 8px;"><div style="font-size: 11px; color: #64748b; margin-bottom: 4px;">🛡 Enforce</div><div style="font-size: 13px;">{escape_html(fix["enforce"])}</div></div>'
            if fix.get('verify'):
                fix_card += f'<div style="font-size: 12px; color: #166534; background: #f0fdf4; padding: 8px; border-radius: 4px;"><strong>✅ Verify:</strong> {escape_html(fix["verify"])}</div>'
            fix_card += '</div>'
            fixes_html += fix_card
        
        # Autofix Queue
        autofix_html = ""
        if actionable.get('autofix_queue'):
            autofix_html = '<div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 8px; padding: 16px; margin: 24px 0;"><div style="font-weight: 600; color: #5b21b6; margin-bottom: 12px;">Autofix Queue (run in order)</div>'
            for cmd in actionable['autofix_queue']:
                autofix_html += f'<div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><code style="font-family: monospace; font-size: 12px; flex: 1;">{escape_html(cmd)}</code><button class="copy-btn" onclick="copyText(this)">Copy</button></div>'
            autofix_html += '</div>'
        
        # Stop Doing
        stop_html = ""
        if actionable.get('stop_doing'):
            stop_html = '<div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; margin: 24px 0;"><div style="font-weight: 600; color: #991b1b; margin-bottom: 12px;">Stop Doing</div><ul style="margin: 0; padding-left: 20px;">'
            for item in actionable['stop_doing']:
                stop_html += f'<li style="font-size: 13px; color: #7f1d1d; margin-bottom: 4px;">{escape_html(item)}</li>'
            stop_html += '</ul></div>'
        
        # Execution Order
        order_html = ""
        if actionable.get('execution_order'):
            order_html = '<div style="background: #f0f9ff; border: 1px solid #7dd3fc; border-radius: 8px; padding: 16px; margin: 24px 0;"><div style="font-weight: 600; color: #0369a1; margin-bottom: 12px;">Execution Order</div><ol style="margin: 0; padding-left: 20px;">'
            for step in actionable['execution_order']:
                order_html += f'<li style="font-size: 13px; color: #0c4a6e; margin-bottom: 4px;">{escape_html(step)}</li>'
            order_html += '</ol></div>'
        
        actionable_html = f'<h2 id="section-actionable" style="color: #dc2626;">🚨 Priority Fixes</h2>{summary_html}{fixes_html}{autofix_html}{stop_html}{order_html}'
    
    fun_ending = insights.get('fun_ending', {})
    fun_html = ""
    if fun_ending and fun_ending.get('headline'):
        fun_html = f'<div class="fun-ending"><div class="fun-headline">"{escape_html(fun_ending["headline"])}"</div>'
        if fun_ending.get("detail"):
            fun_html += f'<div class="fun-detail">{escape_html(fun_ending.get("detail", ""))}</div>'
        fun_html += '</div>'
    
    multi = data.get('parallel_codex', {})
    if multi.get('overlap_events', 0) == 0:
        multi_html = '<p style="font-size: 14px; color: #64748b; padding: 8px 0;">No parallel session usage detected. You typically work with one Codex session at a time.</p>'
    else:
        total_msgs = data['metrics'].get('total_user_messages', 0)
        pct = round(100 * multi.get('user_messages_during', 0) / total_msgs) if total_msgs else 0
        multi_html = f'<div style="display: flex; gap: 24px; margin: 12px 0;"><div style="text-align: center;"><div style="font-size: 24px; font-weight: 700; color: #7c3aed;">{multi["overlap_events"]}</div><div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Overlap Events</div></div><div style="text-align: center;"><div style="font-size: 24px; font-weight: 700; color: #7c3aed;">{multi["sessions_involved"]}</div><div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Sessions Involved</div></div><div style="text-align: center;"><div style="font-size: 24px; font-weight: 700; color: #7c3aed;">{pct}%</div><div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Of Messages</div></div></div><p style="font-size: 13px; color: #475569; margin-top: 12px;">You run multiple Codex sessions simultaneously. Parallel Codex usage is detected when sessions overlap in time.</p>'
    
    tool_errors = data.get('tool_error_categories', {})
    tool_errors_html = generate_bar_chart(tool_errors, '#dc2626') if tool_errors else '<p class="empty">No tool errors</p>'
    
    response_times = data.get('user_response_times', [])
    median_rt = sorted(response_times)[len(response_times)//2] if response_times else 0
    avg_rt = sum(response_times)/len(response_times) if response_times else 0
    
    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #334155; line-height: 1.65; padding: 48px 24px; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { font-size: 32px; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
    h2 { font-size: 20px; font-weight: 600; color: #0f172a; margin-top: 48px; margin-bottom: 16px; }
    .subtitle { color: #64748b; font-size: 15px; margin-bottom: 32px; }
    .nav-toc { display: flex; flex-wrap: wrap; gap: 8px; margin: 24px 0 32px 0; padding: 16px; background: white; border-radius: 8px; border: 1px solid #e2e8f0; }
    .nav-toc a { font-size: 12px; color: #64748b; text-decoration: none; padding: 6px 12px; border-radius: 6px; background: #f1f5f9; transition: all 0.15s; }
    .nav-toc a:hover { background: #e2e8f0; color: #334155; }
    .stats-row { display: flex; gap: 24px; margin-bottom: 40px; padding: 20px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }
    .stat { text-align: center; }
    .stat-value { font-size: 24px; font-weight: 700; color: #0f172a; }
    .stat-label { font-size: 11px; color: #64748b; text-transform: uppercase; }
    .at-a-glance { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #f59e0b; border-radius: 12px; padding: 20px 24px; margin-bottom: 32px; }
    .glance-title { font-size: 16px; font-weight: 700; color: #92400e; margin-bottom: 16px; }
    .glance-sections { display: flex; flex-direction: column; gap: 12px; }
    .glance-section { font-size: 14px; color: #78350f; line-height: 1.6; }
    .glance-section strong { color: #92400e; }
    .see-more { color: #b45309; text-decoration: none; font-size: 13px; white-space: nowrap; }
    .see-more:hover { text-decoration: underline; }
    .project-areas { display: flex; flex-direction: column; gap: 12px; margin-bottom: 32px; }
    .project-area { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }
    .area-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .area-name { font-weight: 600; font-size: 15px; color: #0f172a; }
    .area-count { font-size: 12px; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 4px; }
    .area-desc { font-size: 14px; color: #475569; line-height: 1.5; }
    .narrative { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 24px; }
    .narrative p { margin-bottom: 12px; font-size: 14px; color: #475569; line-height: 1.7; }
    .key-insight { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px 16px; margin-top: 12px; font-size: 14px; color: #166534; }
    .section-intro { font-size: 14px; color: #64748b; margin-bottom: 16px; }
    .big-wins { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
    .big-win { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; }
    .big-win-title { font-weight: 600; font-size: 15px; color: #166534; margin-bottom: 8px; }
    .big-win-desc { font-size: 14px; color: #15803d; line-height: 1.5; }
    .friction-categories { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }
    .friction-category { background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; }
    .friction-title { font-weight: 600; font-size: 15px; color: #991b1b; margin-bottom: 6px; }
    .friction-desc { font-size: 13px; color: #7f1d1d; margin-bottom: 10px; }
    .friction-examples { margin: 0 0 0 20px; font-size: 13px; color: #334155; }
    .friction-examples li { margin-bottom: 4px; }
    .agents-md-section { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
    .agents-md-item { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 8px; padding: 10px 0; border-bottom: 1px solid #dbeafe; }
    .agents-md-item:last-child { border-bottom: none; }
    .cmd-checkbox { margin-top: 2px; }
    .cmd-code { background: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; color: #1e40af; border: 1px solid #bfdbfe; font-family: monospace; display: block; white-space: pre-wrap; word-break: break-word; flex: 1; }
    .cmd-why { font-size: 12px; color: #64748b; width: 100%; padding-left: 24px; margin-top: 4px; }
    .features-section, .patterns-section { display: flex; flex-direction: column; gap: 12px; margin: 16px 0; }
    .feature-card { background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 16px; }
    .pattern-card { background: #f0f9ff; border: 1px solid #7dd3fc; border-radius: 8px; padding: 16px; }
    .feature-title, .pattern-title { font-weight: 600; font-size: 15px; color: #0f172a; margin-bottom: 6px; }
    .feature-oneliner, .pattern-summary { font-size: 14px; color: #475569; margin-bottom: 8px; }
    .feature-why, .pattern-detail { font-size: 13px; color: #334155; line-height: 1.5; }
    .feature-examples { margin-top: 12px; }
    .example-code-row { display: flex; align-items: flex-start; gap: 8px; }
    .example-code { flex: 1; background: #f1f5f9; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #334155; overflow-x: auto; white-space: pre-wrap; }
    .copyable-prompt-section { margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0; }
    .copyable-prompt-row { display: flex; align-items: flex-start; gap: 8px; }
    .copyable-prompt { flex: 1; background: #f8fafc; padding: 10px 12px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #334155; border: 1px solid #e2e8f0; white-space: pre-wrap; line-height: 1.5; }
    .pattern-prompt { background: #f8fafc; padding: 12px; border-radius: 6px; margin-top: 12px; border: 1px solid #e2e8f0; }
    .pattern-prompt code { font-family: monospace; font-size: 12px; color: #334155; display: block; white-space: pre-wrap; margin-bottom: 8px; }
    .prompt-label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 6px; }
    .copy-btn { background: #e2e8f0; border: none; border-radius: 4px; padding: 4px 8px; font-size: 11px; cursor: pointer; color: #475569; flex-shrink: 0; }
    .copy-btn:hover { background: #cbd5e1; }
    .charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 24px 0; }
    .chart-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }
    .chart-title { font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
    .bar-row { display: flex; align-items: center; margin-bottom: 6px; }
    .bar-label { width: 120px; font-size: 11px; color: #475569; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .bar-track { flex: 1; height: 6px; background: #f1f5f9; border-radius: 3px; margin: 0 8px; }
    .bar-fill { height: 100%; border-radius: 3px; }
    .bar-value { width: 28px; font-size: 11px; font-weight: 500; color: #64748b; text-align: right; }
    .empty { color: #94a3b8; font-size: 13px; }
    .horizon-section { display: flex; flex-direction: column; gap: 16px; }
    .horizon-card { background: linear-gradient(135deg, #faf5ff 0%, #f5f3ff 100%); border: 1px solid #c4b5fd; border-radius: 8px; padding: 16px; }
    .horizon-title { font-weight: 600; font-size: 15px; color: #5b21b6; margin-bottom: 8px; }
    .horizon-possible { font-size: 14px; color: #334155; margin-bottom: 10px; line-height: 1.5; }
    .horizon-tip { font-size: 13px; color: #6b21a8; background: rgba(255,255,255,0.6); padding: 8px 12px; border-radius: 4px; }
    .fun-ending { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #fbbf24; border-radius: 12px; padding: 24px; margin-top: 40px; text-align: center; }
    .fun-headline { font-size: 18px; font-weight: 600; color: #78350f; margin-bottom: 8px; }
    .fun-detail { font-size: 14px; color: #92400e; }
    @media (max-width: 640px) { .charts-row { grid-template-columns: 1fr; } .stats-row { justify-content: center; } }
    """
    
    js = """
    function copyText(btn) {
      const code = btn.previousElementSibling;
      navigator.clipboard.writeText(code.textContent).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
      });
    }
    function copyCmdItem(idx) {
      const checkbox = document.getElementById('cmd-' + idx);
      if (checkbox && checkbox.dataset.text) {
        navigator.clipboard.writeText(checkbox.dataset.text).then(() => {
          const btn = checkbox.nextElementSibling.querySelector('.copy-btn');
          if (btn) { btn.textContent = 'Copied!'; setTimeout(() => { btn.textContent = 'Copy'; }, 2000); }
        });
      }
    }
    """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Codex Insights</title>
  <style>{css}</style>
</head>
<body>
  <div class="container">
    <h1>Codex Insights</h1>
    <p class="subtitle">{data['metrics']['total_user_messages']:,} messages across {data['sessions']['total']} sessions | {data['period']['start'][:10]} to {data['period']['end'][:10]}</p>

    {at_a_glance_html}

    <nav class="nav-toc">
      <a href="#section-work">What You Work On</a>
      <a href="#section-usage">How You Use Codex</a>
      <a href="#section-wins">Impressive Things</a>
      <a href="#section-friction">Where Things Go Wrong</a>
      <a href="#section-prompting">Plain-English Prompting</a>
      <a href="#section-features">Features to Try</a>
      <a href="#section-patterns">New Usage Patterns</a>
      <a href="#section-horizon">On the Horizon</a>
      <a href="#section-actionable" style="background: #fef2f2; color: #991b1b; font-weight: 600;">🚨 Priority Fixes</a>
    </nav>

    <div class="stats-row">
      <div class="stat"><div class="stat-value">{data['sessions']['total']}</div><div class="stat-label">Sessions</div></div>
      <div class="stat"><div class="stat-value">{data['metrics']['total_user_messages']:,}</div><div class="stat-label">Messages</div></div>
      <div class="stat"><div class="stat-value">{'+{:,}/-{:,}'.format(data['metrics'].get('total_lines_added', 0), data['metrics'].get('total_lines_removed', 0)) if data['metrics'].get('total_lines_added', 0) > 0 or data['metrics'].get('total_lines_removed', 0) > 0 else 'N/A'}</div><div class="stat-label">Lines</div></div>
      <div class="stat"><div class="stat-value">{data['metrics'].get('total_files_modified', 0) if data['metrics'].get('total_files_modified', 0) > 0 else 'N/A'}</div><div class="stat-label">Files</div></div>
      <div class="stat"><div class="stat-value">{data['metrics'].get('total_tool_errors', 0) if data['metrics'].get('total_tool_errors', 0) > 0 else 'N/A'}</div><div class="stat-label">Tool Errors</div></div>
    </div>

    {project_areas_html}

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">What You Wanted</div>
        {generate_bar_chart(data.get('goal_categories', {}), '#2563eb')}
      </div>
      <div class="chart-card">
        <div class="chart-title">Top Tools Used</div>
        {generate_bar_chart(data['tools']['counts'], '#0891b2', not_available_text=MISSING_TOOL_DATA_MSG)}
      </div>
    </div>

    {interaction_html}

    <div class="chart-card" style="margin: 24px 0;">
      <div class="chart-title">User Response Time Distribution</div>
      {generate_response_time_histogram(response_times)}
      <div style="font-size: 12px; color: #64748b; margin-top: 8px;">
        Median: {median_rt:.1f}s &bull; Average: {avg_rt:.1f}s
      </div>
    </div>

    <div class="chart-card" style="margin: 24px 0;">
      <div class="chart-title">Multi-Codex (Parallel Sessions)</div>
      {multi_html}
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">User Messages by Time of Day</div>
        {generate_time_of_day_chart(data.get('message_hours', []))}
      </div>
      <div class="chart-card">
        <div class="chart-title">Tool Errors Encountered</div>
        {tool_errors_html if data.get('tool_error_categories') else f'<p class="empty">{MISSING_TOOL_DATA_MSG}</p>'}
      </div>
    </div>

    {what_works_html}

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">What Helped Most</div>
        {generate_bar_chart(data.get('success', {}), '#16a34a')}
      </div>
      <div class="chart-card">
        <div class="chart-title">Outcomes</div>
        {generate_bar_chart(data.get('outcomes', {}), '#8b5cf6', 6, OUTCOME_ORDER)}
      </div>
    </div>

    {friction_html}

    {prompting_help_html}

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">Primary Friction Types</div>
        {generate_bar_chart(data.get('friction', {}), '#dc2626')}
      </div>
      <div class="chart-card">
        <div class="chart-title">Inferred Satisfaction</div>
        {generate_bar_chart(data.get('satisfaction', {}), '#eab308', 6, SATISFACTION_ORDER)}
      </div>
    </div>

    {suggestions_html}

    {horizon_html}

    {actionable_html}

    {fun_html}
  </div>
  <script>{js}</script>
</body>
</html>"""
    
    return html


def collect_session_data(args):
    """Collect and analyze Codex session data."""
    print("Codex Insights Report")
    print("=" * 40)
    
    session_files = find_session_files(args.days)
    if args.verbose:
        print(f"Found {len(session_files)} session files")
    
    if not session_files:
        print("No session data found in ~/.codex/sessions/")
        return _generate_no_data_response(args.days)

    sessions = []
    to_parse = []
    
    for file_path in session_files[:args.max_sessions]:
        # Use full stem as session_id to avoid collisions from truncated tokens
        session_id = file_path.stem
        cached = load_cached_session_meta(session_id)
        if cached:
            sessions.append(cached)
        else:
            to_parse.append((file_path, session_id))
    
    for file_path, session_id in to_parse:
        if args.verbose:
            print(f"  Parsing {session_id[:8]}...")
        session = parse_session_file(file_path)
        if session:
            save_session_meta(session_id, session)
            sessions.append(session)
    
    if args.verbose:
        print(f"Loaded {len(sessions)} sessions")
    
    sessions = deduplicate_sessions(sessions)
    if args.verbose:
        print(f"After deduplication: {len(sessions)} sessions")
    
    sessions = [s for s in sessions if is_substantive_session(s)]
    if args.verbose:
        print(f"After substantive filter: {len(sessions)} sessions")
    
    if not sessions:
        print("No substantive sessions found (need 2+ user messages and 1+ minute duration)")
        return _generate_no_data_response(args.days)
    
    all_tool_counts = defaultdict(int)
    total_errors = 0
    total_user_msgs = 0
    total_lines_added = 0
    total_lines_removed = 0
    total_files_modified = 0
    total_tool_errors = 0
    all_tool_error_categories = defaultdict(int)
    all_message_hours = []
    all_response_times = []

    for session in sessions:
        for tool, count in session['tool_calls'].items():
            all_tool_counts[tool] += count
        total_errors += session['errors']
        total_user_msgs += session['user_messages']
        total_lines_added += session['lines_added']
        total_lines_removed += session['lines_removed']
        total_files_modified += session['files_modified']
        total_tool_errors += sum(session.get('tool_error_categories', {}).values())
        for cat, count in session.get('tool_error_categories', {}).items():
            all_tool_error_categories[cat] += count
        all_message_hours.extend(session['message_hours'])
        all_response_times.extend(session['user_response_times'])
    parallel_codex = detect_parallel_codex_sessions(sessions)
    
    data = {
        "period": {
            "start": (datetime.now(tz=timezone.utc) - timedelta(days=args.days)).isoformat(),
            "end": datetime.now(tz=timezone.utc).isoformat(),
            "days": args.days,
        },
        "sessions": {
            "total": len(sessions),
        },
        "tools": {
            "counts": dict(all_tool_counts),
        },
        "metrics": {
            "total_errors": total_errors,
            "total_user_messages": total_user_msgs,
            "total_lines_added": total_lines_added,
            "total_lines_removed": total_lines_removed,
            "total_files_modified": total_files_modified,
            "total_tool_errors": total_tool_errors,
        },
        "tool_error_categories": dict(all_tool_error_categories),
        "message_hours": all_message_hours,
        "user_response_times": all_response_times,
        "goal_categories": {},
        "outcomes": {},
        "satisfaction": {},
        "session_types": {},
        "friction": {},
        "success": {},
        "parallel_codex": parallel_codex,
        "data_quality": "real",
    }
    data["_sessions_for_evidence"] = sessions

    return data


def _generate_no_data_response(days):
    return {
        "period": {"start": (datetime.now() - timedelta(days=days)).isoformat(), "end": datetime.now().isoformat(), "days": days},
        "sessions": {"total": 0},
        "tools": {"counts": {}},
        "metrics": {"total_errors": 0, "total_user_messages": 0, "total_lines_added": 0, "total_lines_removed": 0, "total_files_modified": 0, "total_tool_errors": 0},
        "insights": {},
        "data_quality": "no_data",
    }


def main():
    args = parse_args()
    USAGE_DIR.mkdir(parents=True, exist_ok=True)

    if args.render_only:
        evidence = read_json(args.evidence_out)
        data = evidence.get("data", {})
        insights = read_json(args.insights_in)
        data["insights"] = insights
    else:
        data = collect_session_data(args)
        sessions_for_evidence = data.pop("_sessions_for_evidence", [])
        evidence = build_evidence_bundle(data, sessions_for_evidence, args)
        prompt = build_codex_prompt(evidence)
        write_json(args.evidence_out, evidence)

        # Write prompt with secure permissions
        prompt_path = Path(args.prompt_out)
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(prompt_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(prompt)
        except Exception:
            raise

        print(f"\nCodex evidence ready: {args.evidence_out}")
        print(f"Codex prompt ready: {args.prompt_out}")

        insights = {}
        if data.get("data_quality") == "real" and not args.prepare_only:
            print("\nAsking Codex to write insights...")
            insights = run_codex_writer(prompt)
            write_json(args.insights_out, insights)
            print(f"Codex insights ready: {args.insights_out}")
        elif args.prepare_only:
            print("Prepare-only mode: Codex prompt written; report rendering skipped.")
            return 0

        data["insights"] = insights

    html = generate_html_report(data, data.get("insights", {}))
    REPORT_HTML.write_text(html, encoding="utf-8")
    report_url = f"file://{REPORT_HTML}"
    
    print(f"\n✓ Report ready: {report_url}")
    print(f"REPORT_URL={report_url}")
    
    if data.get("data_quality") == "real":
        sessions = data["sessions"]
        metrics = data.get("metrics", {})
        codex_status = "with Codex-written insights" if data.get("insights") else "(metrics only)"
        print(f"  Analyzed {sessions['total']} sessions, {metrics.get('total_user_messages', 0)} messages {codex_status}")
    else:
        print("  No session data found.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
