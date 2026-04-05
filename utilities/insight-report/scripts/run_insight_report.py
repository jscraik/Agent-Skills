#!/usr/bin/env python3
"""
Codex Insights Report Generator with Ollama LLM Analysis
Full-featured insights matching commercial tools—local LLM-powered facet extraction.

DATA SOURCE NOTES:
- ~/.codex/sessions/ — Session metadata + conversation events (no tool data)
- ~/.codex/history.jsonl — User message text fallback
- ~/.agents/otel-collector/ — Tool spans (requires CODEX_OTEL_ENABLED=1)

Codex runs tools server-side for security, so detailed tool logs aren't stored 
locally like Claude Code's ~/.claude/projects/ format. This report focuses on
session patterns, message analysis, timing, and LLM-generated insights.
"""

from __future__ import annotations

import argparse
import difflib
import gzip
import json
import os
import re
import subprocess
import sys
import webbrowser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

HOME = Path.home()
USAGE_DIR = HOME / "dev" / "config" / "codex" / "usage-data"
REPORT_HTML = USAGE_DIR / "report.html"
FACETS_CACHE = USAGE_DIR / "facets-cache.json"
META_CACHE = USAGE_DIR / "session-meta-cache.json"

# Data sources
SESSIONS_DIR = HOME / ".codex" / "sessions"
HISTORY_FILE = HOME / ".codex" / "history.jsonl"
OTEL_PATHS = [
    HOME / ".agents" / "otel-collector",
    HOME / ".codex" / "otel-collector",
    HOME / "Library" / "Application Support" / "Codex" / "otel-collector",
]

# Ollama configuration
OLLAMA_MODEL = os.getenv("INSIGHTS_MODEL", "qwen3-coder")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MAX_WORKERS = int(os.getenv("INSIGHTS_WORKERS", "3"))

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
    "claude_got_blocked": "Assistant Got Blocked",
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
    parser = argparse.ArgumentParser(description="Generate Codex insights report with LLM analysis")
    parser.add_argument("--days", type=int, default=7, help="Lookback window (default: 7)")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--model", default=OLLAMA_MODEL, help=f"Ollama model (default: {OLLAMA_MODEL})")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM facet extraction (faster)")
    parser.add_argument("--max-sessions", type=int, default=200, help="Max sessions to analyze (default: 200)")
    parser.add_argument("--max-facets", type=int, default=50, help="Max sessions for LLM facet extraction (default: 50)")
    return parser.parse_args()


def find_session_files(days):
    """Find session files from ~/.codex/sessions/ within the lookback period."""
    if not SESSIONS_DIR.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    files = []
    
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
                    if dir_date < cutoff:
                        continue
                except ValueError:
                    continue
                for f in day_dir.glob("rollout-*.jsonl"):
                    files.append(f)
    
    return sorted(files)


def is_meta_session(events):
    """Check if this is a meta-session (insights API call that shouldn't be analyzed)."""
    for event in events[:10]:
        if event.get('type') == 'event_msg':
            payload = event.get('payload', {})
            if payload.get('type') == 'user_message':
                content = payload.get('message', '') or payload.get('content', '')
                if 'RESPOND WITH ONLY A VALID JSON OBJECT' in content or 'record_facets' in content:
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


def parse_session_file(file_path):
    """Parse a Codex session file into structured data."""
    events = []
    session_meta = None
    user_messages = []
    agent_messages = []
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
                        msg_timestamp = payload.get('timestamp')
                        
                        if msg_type == 'user_message':
                            content = payload.get('message', '') or payload.get('content', '')
                            is_human = bool(content and content.strip())
                            
                            if is_human:
                                user_messages.append((msg_timestamp, content))
                                
                                if msg_timestamp:
                                    try:
                                        msg_date = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                        message_hours.append(msg_date.hour)
                                        user_message_timestamps.append(msg_timestamp)
                                    except:
                                        pass
                                
                                if last_assistant_timestamp and msg_timestamp:
                                    try:
                                        assistant_time = datetime.fromisoformat(last_assistant_timestamp.replace('Z', '+00:00'))
                                        user_time = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                        response_time = (user_time - assistant_time).total_seconds()
                                        if 2 < response_time < 3600:
                                            user_response_times.append(response_time)
                                    except:
                                        pass
                            
                            if isinstance(content, str) and '[Request interrupted by user' in content:
                                errors += 1
                        
                        elif msg_type == 'agent_message':
                            content = payload.get('content', '')
                            if content:
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
                        tool_calls_data = payload.get('tool_calls', [])
                        for tc in tool_calls_data:
                            name = tc.get('name', 'unknown')
                            tool_calls[name] += 1
                            
                            if name in ('Edit', 'Write'):
                                tool_input = tc.get('input', {})
                                file_path_mod = tool_input.get('file_path', '')
                                if file_path_mod:
                                    files_modified.add(file_path_mod)
                                    
                                    if name == 'Edit':
                                        old_str = tool_input.get('old_string', '')
                                        new_str = tool_input.get('new_string', '')
                                        if old_str is not None and new_str is not None:
                                            a, r = count_lines_in_diff(old_str, new_str)
                                            lines_added += a
                                            lines_removed += r
                                    
                                    elif name == 'Write':
                                        content = tool_input.get('content', '')
                                        if content:
                                            lines_added += content.count('\n') + 1
                except json.JSONDecodeError:
                    continue
    except Exception:
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
                    except:
                        pass
            if last_msg_time:
                duration_minutes = (last_msg_time - start).total_seconds() / 60
        except:
            pass
    
    return {
        'session_id': session_meta.get('id', 'unknown'),
        'timestamp': start_time,
        'cwd': session_meta.get('cwd', ''),
        'cli_version': session_meta.get('cli_version', ''),
        'model_provider': session_meta.get('model_provider', ''),
        'agent_role': session_meta.get('agent_role', ''),
        'user_messages': len(user_messages),
        'agent_responses': len(agent_messages),
        'tool_calls': dict(tool_calls),
        'errors': errors,
        'tool_error_categories': dict(tool_error_categories),
        'files_modified': len(files_modified),
        'lines_added': lines_added,
        'lines_removed': lines_removed,
        'duration_minutes': duration_minutes,
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
    # Require at least 1 user message (filters out warmup/meta sessions)
    if session['user_messages'] < 1:
        return False
    return True


def is_warmup_only_session(facet):
    """Check if session only has warmup_minimal as goal category."""
    cats = facet.get('goal_categories', {})
    active_cats = [k for k, v in cats.items() if v > 0]
    return len(active_cats) == 1 and active_cats[0] == 'warmup_minimal'


def detect_multi_clauding(sessions):
    """Detect multi-codex usage via timestamp overlap analysis."""
    OVERLAP_WINDOW_MS = 30 * 60000
    
    all_messages = []
    for session in sessions:
        for ts in session.get('user_message_timestamps', []):
            try:
                all_messages.append({
                    'ts': datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp() * 1000,
                    'session_id': session['session_id']
                })
            except:
                pass
    
    all_messages.sort(key=lambda x: x['ts'])
    
    multi_claude_pairs = set()
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
                    multi_claude_pairs.add(pair)
                    messages_during.add(f"{all_messages[prev_index]['ts']}:{msg['session_id']}")
                    messages_during.add(f"{between['ts']}:{between['session_id']}")
                    messages_during.add(f"{msg['ts']}:{msg['session_id']}")
                    break
        
        session_last_index[msg['session_id']] = i
    
    sessions_with_overlaps = set()
    for pair in multi_claude_pairs:
        sessions_with_overlaps.add(pair[0])
        sessions_with_overlaps.add(pair[1])
    
    return {
        'overlap_events': len(multi_claude_pairs),
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


def check_ollama_available(model):
    """Check if Ollama is running and model is available."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"{OLLAMA_HOST}/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return False
        data = json.loads(result.stdout)
        models = [m.get("name", "") for m in data.get("models", [])]
        return any(model in m or m in model for m in models)
    except Exception:
        return False


def ollama_generate(prompt, model, system=""):
    """Generate text using Ollama API."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 2000}
        }
        if system:
            payload["system"] = system
        
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", f"{OLLAMA_HOST}/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return ""
        
        response = json.loads(result.stdout)
        return response.get("response", "")
    except Exception:
        return ""


def load_cached_facets():
    """Load cached facets from disk."""
    try:
        if FACETS_CACHE.exists():
            with open(FACETS_CACHE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}


def save_cached_facets(cache):
    """Save facets cache to disk."""
    try:
        USAGE_DIR.mkdir(parents=True, exist_ok=True)
        with open(FACETS_CACHE, 'w') as f:
            json.dump(cache, f, indent=2)
    except:
        pass


def load_cached_session_meta(session_id):
    """Load cached session metadata from disk."""
    try:
        cache_path = USAGE_DIR / "session-meta" / f"{session_id}.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                return json.load(f)
    except:
        pass
    return None


def save_session_meta(session_id, meta):
    """Save session metadata cache to disk."""
    try:
        meta_dir = USAGE_DIR / "session-meta"
        meta_dir.mkdir(parents=True, exist_ok=True)
        cache_path = meta_dir / f"{session_id}.json"
        with open(cache_path, 'w') as f:
            json.dump(meta, f, indent=2)
    except:
        pass


def extract_facets_with_llm(session_id, transcript, model, cache):
    """Extract session facets using local LLM."""
    if session_id in cache:
        return cache[session_id]
    
    prompt = f"""Analyze this Codex session and extract structured facets.

CRITICAL GUIDELINES:

1. **goal_categories**: Count ONLY what the USER explicitly asked for.
   - DO NOT count the assistant's autonomous codebase exploration
   - DO NOT count work the assistant decided to do on its own
   - ONLY count when user says "can you...", "please...", "I need...", "let's..."

2. **user_satisfaction_counts**: Base ONLY on explicit user signals.
   - "Yay!", "great!", "perfect!" → happy
   - "thanks", "looks good", "that works" → satisfied
   - "ok, now let's..." (continuing without complaint) → likely_satisfied
   - "that's not right", "try again" → dissatisfied
   - "this is broken", "I give up" → frustrated

3. **friction_counts**: Be specific about what went wrong.
   - misunderstood_request: Assistant interpreted incorrectly
   - wrong_approach: Right goal, wrong solution method
   - buggy_code: Code didn't work correctly
   - user_rejected_action: User said no/stop to a tool call
   - excessive_changes: Over-engineered or changed too much

4. If very short or just warmup, use warmup_minimal for goal_category

SESSION:
{transcript[:8000]}

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "underlying_goal": "What the user fundamentally wanted to achieve",
  "goal_categories": {{"category_name": count, ...}},
  "outcome": "fully_achieved|mostly_achieved|partially_achieved|not_achieved|unclear_from_transcript",
  "user_satisfaction_counts": {{"level": count, ...}},
  "assistant_helpfulness": "unhelpful|slightly_helpful|moderately_helpful|very_helpful|essential",
  "session_type": "single_task|multi_task|iterative_refinement|exploration|quick_question",
  "friction_counts": {{"friction_type": count, ...}},
  "friction_detail": "One sentence describing friction or empty",
  "primary_success": "none|fast_accurate_search|correct_code_edits|good_explanations|proactive_help|multi_file_changes|good_debugging",
  "brief_summary": "One sentence: what user wanted and whether they got it",
  "user_instructions_to_assistant": ["instruction 1", "instruction 2"]
}}"""

    response = ollama_generate(prompt, model)
    if not response:
        return None
    
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            facet = json.loads(json_match.group())
            facet['session_id'] = session_id
            cache[session_id] = facet
            return facet
    except:
        pass
    return None


def generate_parallel_insights(data, facets, model):
    """Generate insight sections in parallel using LLM."""
    if not facets:
        return {}
    
    facet_summaries = [f"- {f.get('brief_summary', 'Unknown')} ({f.get('outcome')}, {f.get('assistant_helpfulness')})" for f in facets[:30]]
    friction_details = [f"- {f.get('friction_detail', '')}" for f in facets if f.get('friction_detail')][:20]
    user_instructions = []
    for f in facets:
        user_instructions.extend(f.get('user_instructions_to_assistant', []))
    user_instructions = user_instructions[:15]
    
    data_context = json.dumps({
        "sessions": data['sessions']['total'],
        "analyzed": len(facets),
        "messages": data['metrics']['total_user_messages'],
        "hours": data['sessions'].get('avg_duration_minutes', 0) * data['sessions']['total'] / 60,
        "top_tools": sorted(data['tools']['counts'].items(), key=lambda x: x[1], reverse=True)[:8],
        "lines_added": data['metrics'].get('total_lines_added', 0),
        "lines_removed": data['metrics'].get('total_lines_removed', 0),
        "files_modified": data['metrics'].get('total_files_modified', 0),
        "multi_clauding": data.get('multi_clauding', {}),
    }, indent=2)
    
    full_context = f"""{data_context}

SESSION SUMMARIES:
{chr(10).join(facet_summaries)}

FRICTION DETAILS:
{chr(10).join(friction_details)}

USER INSTRUCTIONS TO ASSISTANT:
{chr(10).join([f"- {i}" for i in user_instructions]) or "None captured"}"""

    sections = {
        "project_areas": f"""Analyze this Codex usage data and identify project areas.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "areas": [
    {{"name": "Area name", "session_count": N, "description": "2-3 sentences about what was worked on."}}
  ]
}}

Include 4-5 areas.

DATA:
{full_context}""",
        "interaction_style": f"""Analyze this Codex usage data and describe the user's interaction style.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "narrative": "2-3 paragraphs analyzing HOW the user interacts with Codex. Use second person 'you'. Describe patterns.",
  "key_pattern": "One sentence summary of most distinctive interaction style"
}}

DATA:
{full_context}""",
        "what_works": f"""Analyze this Codex usage data and identify what's working well.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "intro": "1 sentence of context",
  "impressive_workflows": [
    {{"title": "Short title (3-6 words)", "description": "2-3 sentences describing the impressive workflow. Use 'you'."}}
  ]
}}

Include 3 impressive workflows.

DATA:
{full_context}""",
        "friction_analysis": f"""Analyze this Codex usage data and identify friction points.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "intro": "1 sentence summarizing friction patterns",
  "categories": [
    {{"category": "Concrete category name", "description": "1-2 sentences explaining this category.", "examples": ["Example 1", "Example 2"]}}
  ]
}}

Include 3 friction categories with 2 examples each.

DATA:
{full_context}""",
        "suggestions": f"""Analyze this Codex usage data and suggest improvements.

CODEX FEATURES REFERENCE:
1. **MCP Servers**: Connect Codex to external tools via Model Context Protocol.
   - How: Run `codex mcp add <server-name> -- <command>`
   - Good for: database queries, Slack, GitHub, internal APIs

2. **Custom Skills**: Reusable prompts as markdown files.
   - How: Create `.codex/skills/<name>/SKILL.md`. Then type `/<name>` to run.
   - Good for: repetitive workflows - /commit, /review, /test, /deploy

3. **Hooks**: Shell commands that auto-run at lifecycle events.
   - How: Enable `codex_hooks` feature flag, then configure in ~/.codex/config.toml
   - Good for: auto-formatting, type checks, enforcing conventions

4. **Headless Mode**: Run Codex non-interactively from scripts.
   - How: `codex exec --full-auto "fix lint errors"` (or without --full-auto for approvals)
   - Good for: CI/CD, batch fixes, automated reviews

5. **Task Agents**: Codex spawns focused sub-agents for complex work.
   - How: Ask "use an agent to explore X"
   - Good for: codebase exploration, understanding complex systems

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "agents_md_additions": [
    {{"addition": "A specific instruction to add to AGENTS.md", "why": "Why this helps", "where": "Where to add it"}}
  ],
  "features_to_try": [
    {{"feature": "Feature name", "one_liner": "What it does", "why_for_you": "Why this helps you", "example_code": "Command to copy"}}
  ],
  "usage_patterns": [
    {{"title": "Short title", "suggestion": "Summary", "detail": "Explanation", "copyable_prompt": "Prompt to try"}}
  ]
}}

Include 2-3 items per category.

DATA:
{full_context}""",
        "on_the_horizon": f"""Analyze this Codex usage data and identify future opportunities.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "intro": "1 sentence about evolving AI-assisted development",
  "opportunities": [
    {{"title": "Short title", "whats_possible": "2-3 sentences about autonomous workflows", "how_to_try": "Getting started tip", "copyable_prompt": "Prompt to try"}}
  ]
}}

Include 3 opportunities. Think BIG.

DATA:
{full_context}""",
        "actionable_fixes": f"""Convert friction patterns into v3 actionable fixes.

For each recurring friction pattern in the data, create an execution block with:
1. IMPACT - Why this matters (time lost, sessions wasted)
2. ROOT CAUSE - What's actually happening
3. FIX (shell command) - Exact command to run
4. CLAUDE/CODEX COMMAND - Prompt to auto-fix
5. ENFORCE - Hook/rule/config to prevent recurrence
6. VERIFY - Metric to confirm fix worked

PRIORITIZE by frequency and impact. Include only actionable items.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "executive_summary": {{
    "failures": "High/Medium/Low",
    "time_loss_driver": "Single biggest time sink",
    "top_issue": "Primary fix to apply",
    "priority": "One-line action priority"
  }},
  "harness_gaps": [
    {{"layer": "Preflight|Local Dev|CI Strategy|Git Workflow|Model Mgmt", "missing": "What's missing", "impact": "High/Medium/Low"}}
  ],
  "priority_fixes": [
    {{
      "rank": 1,
      "title": "Fix title",
      "impact": "What this costs you",
      "root_cause": "Why it happens",
      "fix_shell": "Exact shell command to run now",
      "codex_command": "codex exec [options] 'prompt' — headless execution command",
      "enforce": "Hook/config/rule to add (use ~/.codex/config.toml or AGENTS.md)",
      "verify": "Metric to track (before -> target)"
    }}
  ],
  "autofix_queue": [
    "codex exec --full-auto 'First fix to auto-apply'",
    "codex exec 'Second fix to auto-apply'"
  ],
  "stop_doing": [
    "❌ Specific anti-pattern to stop"
  ],
  "execution_order": [
    "1. First step",
    "2. Second step"
  ]
}}

SESSION DATA:
{full_context}""",
        "fun_ending": f"""Find a memorable moment from these session summaries.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "headline": "A memorable QUALITATIVE moment - not a statistic. Something human, funny, or surprising.",
  "detail": "Brief context"
}}

SESSIONS:
{chr(10).join(facet_summaries[:15])}""",
    }
    
    insights = {}
    print(f"Generating {len(sections)} insight sections with {model}...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_name = {
            executor.submit(ollama_generate, spec, model): name
            for name, spec in sections.items()
        }
        
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                response = future.result(timeout=180)
                if response:
                    json_match = re.search(r'\{[\s\S]*\}', response, re.DOTALL)
                    if json_match:
                        insights[name] = json.loads(json_match.group())
                        print(f"  ✓ {name}")
                    else:
                        print(f"  ✗ {name} - no JSON found")
                else:
                    print(f"  ✗ {name} - no response")
            except Exception as e:
                print(f"  ✗ {name} - {e}")
    
    # Generate At a Glance
    if insights:
        project_areas_text = "\n".join([f"- {a.get('name')}: {a.get('description', '')}" for a in insights.get('project_areas', {}).get('areas', [])[:5]])
        big_wins_text = "\n".join([f"- {w.get('title')}: {w.get('description', '')}" for w in insights.get('what_works', {}).get('impressive_workflows', [])[:3]])
        friction_text = "\n".join([f"- {c.get('category')}: {c.get('description', '')}" for c in insights.get('friction_analysis', {}).get('categories', [])[:3]])
        features_text = "\n".join([f"- {f.get('feature')}: {f.get('one_liner', '')}" for f in insights.get('suggestions', {}).get('features_to_try', [])[:3]])
        horizon_text = "\n".join([f"- {o.get('title')}: {o.get('whats_possible', '')}" for o in insights.get('on_the_horizon', {}).get('opportunities', [])[:3]])
        
        at_a_glance_prompt = f"""Write an "At a Glance" summary for a Codex usage report.

Use this 4-part structure:

1. **What's working** - User's unique style and impactful things they've done.
2. **What's hindering you** - Split into (a) assistant issues and (b) user-side friction.
3. **Quick wins to try** - Specific Codex features to try.
4. **Ambitious workflows** - What becomes possible as AI improves.

Keep each section to 2-3 sentences. Use a coaching tone.

RESPOND WITH ONLY A VALID JSON OBJECT:
{{
  "whats_working": "...",
  "whats_hindering": "...",
  "quick_wins": "...",
  "ambitious_workflows": "..."
}}

PROJECT AREAS:
{project_areas_text}

BIG WINS:
{big_wins_text}

FRICTION:
{friction_text}

FEATURES:
{features_text}

HORIZON:
{horizon_text}"""
        
        print("  Generating at_a_glance...")
        response = ollama_generate(at_a_glance_prompt, model)
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response, re.DOTALL)
                if json_match:
                    insights['at_a_glance'] = json.loads(json_match.group())
                    print("  ✓ at_a_glance")
            except:
                pass
    
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
        cats_html = "".join([f'<div class="friction-category"><div class="friction-title">{escape_html(c.get("category", ""))}</div><div class="friction-desc">{escape_html(c.get("description", ""))}</div>{"<ul class=\"friction-examples\">" + "".join([f"<li>{escape_html(e)}</li>" for e in c.get("examples", [])]) + "</ul>" if c.get("examples") else ""}</div>' for c in friction['categories']])
        intro = f'<p class="section-intro">{escape_html(friction.get("intro", ""))}</p>' if friction.get('intro') else ""
        friction_html = f'<h2 id="section-friction">Where Things Go Wrong</h2>{intro}<div class="friction-categories">{cats_html}</div>'
    
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
            summary_html = f'<div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; margin-bottom: 24px;"><div style="font-weight: 600; color: #991b1b; margin-bottom: 8px;">Executive Summary</div>'
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
            fix_card = f'<div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">'
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
            autofix_html = f'<div style="background: #faf5ff; border: 1px solid #e9d5ff; border-radius: 8px; padding: 16px; margin: 24px 0;"><div style="font-weight: 600; color: #5b21b6; margin-bottom: 12px;">⚡ Autofix Queue (run in order)</div>'
            for cmd in actionable['autofix_queue']:
                autofix_html += f'<div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><code style="font-family: monospace; font-size: 12px; flex: 1;">{escape_html(cmd)}</code><button class="copy-btn" onclick="copyText(this)">Copy</button></div>'
            autofix_html += '</div>'
        
        # Stop Doing
        stop_html = ""
        if actionable.get('stop_doing'):
            stop_html = f'<div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; margin: 24px 0;"><div style="font-weight: 600; color: #991b1b; margin-bottom: 12px;">🛑 Stop Doing</div><ul style="margin: 0; padding-left: 20px;">'
            for item in actionable['stop_doing']:
                stop_html += f'<li style="font-size: 13px; color: #7f1d1d; margin-bottom: 4px;">{escape_html(item)}</li>'
            stop_html += '</ul></div>'
        
        # Execution Order
        order_html = ""
        if actionable.get('execution_order'):
            order_html = f'<div style="background: #f0f9ff; border: 1px solid #7dd3fc; border-radius: 8px; padding: 16px; margin: 24px 0;"><div style="font-weight: 600; color: #0369a1; margin-bottom: 12px;">📋 Execution Order</div><ol style="margin: 0; padding-left: 20px;">'
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
    
    multi = data.get('multi_clauding', {})
    if multi.get('overlap_events', 0) == 0:
        multi_html = '<p style="font-size: 14px; color: #64748b; padding: 8px 0;">No parallel session usage detected. You typically work with one Codex session at a time.</p>'
    else:
        total_msgs = data['metrics'].get('total_user_messages', 0)
        pct = round(100 * multi.get('user_messages_during', 0) / total_msgs) if total_msgs else 0
        multi_html = f'<div style="display: flex; gap: 24px; margin: 12px 0;"><div style="text-align: center;"><div style="font-size: 24px; font-weight: 700; color: #7c3aed;">{multi["overlap_events"]}</div><div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Overlap Events</div></div><div style="text-align: center;"><div style="font-size: 24px; font-weight: 700; color: #7c3aed;">{multi["sessions_involved"]}</div><div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Sessions Involved</div></div><div style="text-align: center;"><div style="font-size: 24px; font-weight: 700; color: #7c3aed;">{pct}%</div><div style="font-size: 11px; color: #64748b; text-transform: uppercase;">Of Messages</div></div></div><p style="font-size: 13px; color: #475569; margin-top: 12px;">You run multiple Codex sessions simultaneously. Multi-codex is detected when sessions overlap in time, suggesting parallel workflows.</p>'
    
    tool_errors = data.get('tool_error_categories', {})
    tool_errors_html = generate_bar_chart(tool_errors, '#dc2626') if tool_errors else '<p class="empty">No tool errors</p>'
    
    response_times = data.get('user_response_times', [])
    median_rt = sorted(response_times)[len(response_times)//2] if response_times else 0
    avg_rt = sum(response_times)/len(response_times) if response_times else 0
    
    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: #f8fafc; color: #334155; line-height: 1.65; padding: 48px 24px; }
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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
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
        {generate_bar_chart(data['tools']['counts'], '#0891b2', not_available_text="Not available — Codex runs tools server-side. Enable OPENAI_TELEMETRY_ENABLED=1 for tool data")}
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
        {tool_errors_html if data.get('tool_error_categories') else '<p class="empty">Not available — Codex runs tools server-side. Enable OPENAI_TELEMETRY_ENABLED=1 for tool data</p>'}
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
    print(f"Codex Insights Report")
    print(f"=" * 40)
    
    session_files = find_session_files(args.days)
    if args.verbose:
        print(f"Found {len(session_files)} session files")
    
    if not session_files:
        print("No session data found in ~/.codex/sessions/")
        return _generate_no_data_response(args.days)
    
    use_llm = not args.skip_llm
    ollama_ok = False
    if use_llm:
        ollama_ok = check_ollama_available(args.model)
        if args.verbose:
            print(f"Ollama {args.model}: {'available' if ollama_ok else 'not available'}")
        if not ollama_ok:
            print(f"⚠ Ollama not available. Install: curl -fsSL https://ollama.com/install.sh | sh")
            print(f"  Then: ollama pull {args.model}")
            use_llm = False
    
    sessions = []
    to_parse = []
    
    for file_path in session_files[:args.max_sessions]:
        session_id = file_path.stem.split('-')[-1] if '-' in file_path.stem else file_path.stem
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
        print("No substantive sessions found (need 2+ messages and 1+ minute duration)")
        return _generate_no_data_response(args.days)
    
    cache = load_cached_facets()
    
    facets = []
    if use_llm and ollama_ok:
        print(f"\nExtracting facets with {args.model}...")
        for session in sessions[:args.max_facets]:
            if args.verbose:
                print(f"  Extracting facets for {session['session_id'][:8]}...")
            facet = extract_facets_with_llm(session['session_id'], session['transcript'], args.model, cache)
            if facet and not is_warmup_only_session(facet):
                facets.append(facet)
        save_cached_facets(cache)
        print(f"  Extracted {len(facets)} facets")
    
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
    goal_categories = defaultdict(int)
    outcomes = defaultdict(int)
    satisfaction = defaultdict(int)
    helpfulness = defaultdict(int)
    session_types = defaultdict(int)
    friction = defaultdict(int)
    success = defaultdict(int)
    
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
    
    for facet in facets:
        for cat, count in facet.get('goal_categories', {}).items():
            if count > 0:
                goal_categories[cat] += count
        outcomes[facet.get('outcome', 'unknown')] += 1
        for level, count in facet.get('user_satisfaction_counts', {}).items():
            if count > 0:
                satisfaction[level] += count
        helpfulness[facet.get('assistant_helpfulness', 'unknown')] += 1
        session_types[facet.get('session_type', 'unknown')] += 1
        for ftype, count in facet.get('friction_counts', {}).items():
            if count > 0:
                friction[ftype] += count
        if facet.get('primary_success') and facet['primary_success'] != 'none':
            success[facet['primary_success']] += 1
    
    multi_clauding = detect_multi_clauding(sessions)
    
    data = {
        "period": {
            "start": (datetime.now() - timedelta(days=args.days)).isoformat(),
            "end": datetime.now().isoformat(),
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
        "goal_categories": dict(goal_categories),
        "outcomes": dict(outcomes),
        "satisfaction": dict(satisfaction),
        "session_types": dict(session_types),
        "friction": dict(friction),
        "success": dict(success),
        "multi_clauding": multi_clauding,
        "data_quality": "real",
    }
    
    if use_llm and facets:
        print(f"\nGenerating insights with {args.model}...")
        insights = generate_parallel_insights(data, facets, args.model)
        data["insights"] = insights
    
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
    
    data = collect_session_data(args)
    
    html = generate_html_report(data, data.get("insights", {}))
    REPORT_HTML.write_text(html, encoding="utf-8")
    
    print(f"\n✓ Report ready: file://{REPORT_HTML}")
    
    if data.get("data_quality") == "real":
        sessions = data["sessions"]
        metrics = data.get("metrics", {})
        llm_status = "with LLM analysis" if data.get("insights") else "(basic metrics only)"
        print(f"  Analyzed {sessions['total']} sessions, {metrics.get('total_user_messages', 0)} messages {llm_status}")
    else:
        print("  No session data found.")
    
    if not args.no_open:
        webbrowser.open(f"file://{REPORT_HTML}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
