"""CLI argument recovery and helpful error helpers for ask."""

from __future__ import annotations

import argparse
import contextlib
import difflib
import io
from typing import List, Optional, Tuple

from ask.command_metadata import (
    ACTION_TO_TOPICS,
    COMMAND_EXAMPLES,
    FUZZY_MATCHES,
    TOPIC_EXAMPLES,
    VALID_ACTIONS,
    VALID_TOPICS,
)
from ask.envelope import CallResult, ErrorCode, ErrorObject


TOPIC_RECOVERY_COMMANDS = {
    "repo": "./bin/ask repo status --json --robot",
    "skills": "./bin/ask skills list --json --robot",
    "reviewers": "./bin/ask reviewers resolve skill-inspector --json --robot",
    "runtime": "./bin/ask runtime surface --json --robot",
    "plugins": "./bin/ask plugins list --json --robot",
    "evals": "./bin/ask evals dashboard --json --robot",
    "workouts": "./bin/ask workouts list --json --robot",
    "graph": "./bin/ask graph list --json --robot",
    "mcp": "./bin/ask mcp sync --dry-run --json --robot",
    "memory": "./bin/ask memory list --json --robot",
    "wiki": "./bin/ask wiki lint --json --robot",
}
FALLBACK_RECOVERY_TOPICS = ["skills", "repo", "graph"]


def _valid_actions_fix_suggestion(topic: str | None) -> str:
    if topic in VALID_ACTIONS:
        return f"Valid actions: {', '.join(VALID_ACTIONS[topic])}"
    return "Use 'ask --help' for global usage or '<topic> <action> --help' for command details."


def _attach_recovery_data(
    result: CallResult,
    topic: str | None,
    examples: List[str],
    *,
    validation_commands: List[str] | None = None,
) -> None:
    if validation_commands is None:
        validation_commands = _recovery_commands_for_topic(topic)
    if validation_commands:
        result.data["validation_commands"] = validation_commands
    if examples:
        result.data["candidate_commands"] = examples[:3]


def _ambiguous_action_commands(action: str, topics: List[str]) -> List[str]:
    return [f"ask {topic} {action}" for topic in topics[:3]]


def _quote_commands(commands: List[str]) -> str:
    return ", ".join(f"'{command}'" for command in commands)


def _ambiguous_action_fix_suggestion(action: str, topics: List[str]) -> str:
    commands = _quote_commands(_ambiguous_action_commands(action, topics))
    return f"Use an explicit topic: {commands}."


def _fallback_recovery_commands() -> List[str]:
    return _recovery_commands_for_topics(FALLBACK_RECOVERY_TOPICS)


def _recovery_commands_for_topics(topics: List[str]) -> List[str]:
    return [
        command
        for topic in topics[:3]
        for command in _recovery_commands_for_topic(topic)
    ]


def _fallback_topic_fix_suggestion() -> str:
    commands = _quote_commands(_fallback_recovery_commands())
    return f"Run a valid topic recovery command: {commands}."


def _closest_action_fix_suggestion(topic: str, action: str) -> str:
    return f"Closest action guess: 'ask {topic} {action}'."


def _closest_topic_fix_suggestion(topic: str) -> str:
    return f"Closest topic guess: 'ask {topic}'."


def build_unknown_action_result(
    topic: str,
    action: str | None,
    fix_suggestion: str | None = None,
) -> CallResult:
    """Build a standard error result for an unknown or missing topic action."""
    result = CallResult()
    result.status = "error"
    examples = _example_commands(topic, action, limit=3)
    valid_actions = VALID_ACTIONS.get(topic, [])
    closest_action = get_closest_match(action, valid_actions) if action else None
    if closest_action:
        examples = _example_commands(topic, closest_action, limit=3)
    _attach_recovery_data(result, topic, examples)
    if fix_suggestion is None:
        if closest_action:
            fix_suggestion = _closest_action_fix_suggestion(topic, closest_action)
        else:
            fix_suggestion = _valid_actions_fix_suggestion(topic)
    action_msg = f"unknown action '{action}'" if action else "missing action"
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message=f"{action_msg} for topic '{topic}'",
            fix_suggestion=fix_suggestion,
        )
    )
    return result


def get_closest_match(query: str, options: List[str], cutoff: float = 0.6) -> Optional[str]:
    """Find closest match using difflib."""
    matches = difflib.get_close_matches(query, options, n=1, cutoff=cutoff)
    return matches[0] if matches else None


def format_correction(original: str, corrected: str, robot_mode: bool = False) -> str:
    """Format a command correction message."""
    if robot_mode:
        return f"🤖 Robot mode: Interpreting '{original}' as '{corrected}'\n   💡 Tip: Use '{corrected}' for exact matching next time."
    return f"💡 Did you mean: '{corrected}'? (Use --robot to auto-correct)"


def _normalize_token(token: str) -> str:
    """Normalize a command token for robust fuzzy matching."""
    return token.strip().lower().replace("_", "-")


def _extract_argparse_error(stderr_text: Optional[str]) -> Optional[str]:
    """Extract the actionable argparse error line."""
    if not stderr_text:
        return None
    lines = [line.strip() for line in stderr_text.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("ask: error:"):
            return line.replace("ask: error:", "", 1).strip()
    return lines[-1] if lines else None


def _example_commands(topic: Optional[str], action: Optional[str], *, limit: int = 3) -> List[str]:
    """Return contextual command examples, preferring command-specific examples."""
    if limit <= 0:
        return []
    if topic and action and (topic, action) in COMMAND_EXAMPLES:
        return COMMAND_EXAMPLES[(topic, action)][:limit]
    if topic and topic in TOPIC_EXAMPLES:
        return TOPIC_EXAMPLES[topic][:limit]
    fallback = []
    for fallback_topic in FALLBACK_RECOVERY_TOPICS:
        fallback.extend(TOPIC_EXAMPLES.get(fallback_topic, []))
    return fallback[:limit]


def _recovery_commands_for_topic(topic: Optional[str]) -> List[str]:
    if topic in TOPIC_RECOVERY_COMMANDS:
        return [TOPIC_RECOVERY_COMMANDS[topic]]
    return []


def _merge_corrections(existing: Optional[str], new_note: Optional[str]) -> Optional[str]:
    """Merge correction notes without duplicating text blocks."""
    if not existing:
        return new_note
    if not new_note:
        return existing
    if new_note in existing.splitlines():
        return existing
    return f"{existing}\n{new_note}"


def consume_global_prefix_flags(raw_args: List[str]) -> Tuple[List[str], List[str]]:
    """Split leading global flags from positional command tokens."""
    global_flags = {"--json", "--trace-id", "--robot", "--agent-mode", "-r", "--help", "-h"}
    prefix_flags: List[str] = []
    idx = 0
    while idx < len(raw_args) and raw_args[idx].startswith("-"):
        flag = raw_args[idx]
        if flag.startswith("--trace-id="):
            prefix_flags.append(flag)
            idx += 1
            continue
        if flag not in global_flags:
            break
        prefix_flags.append(flag)
        idx += 1
        if flag in {"--trace-id"} and idx < len(raw_args) and not raw_args[idx].startswith("-"):
            prefix_flags.append(raw_args[idx])
            idx += 1
    return prefix_flags, raw_args[idx:]


def build_helpful_error(
    topic: Optional[str],
    action: Optional[str],
    raw_args: List[str],
    *,
    parser_error: Optional[str] = None,
) -> CallResult:
    """Build a detailed error message when command intent is unclear."""
    result = CallResult()
    result.status = "error"
    entered = "ask " + " ".join(raw_args) if raw_args else "ask"
    _, working_args = consume_global_prefix_flags(raw_args)
    parsed_error = _extract_argparse_error(parser_error)
    error_msg = "I couldn't reliably determine command intent."
    suggestions: List[str] = []
    examples = _example_commands(topic, action, limit=3)
    recovery_topic = topic
    ambiguous_topics: List[str] = []
    use_fallback_recovery = False
    fix_suggestion_override: str | None = None
    if not topic:
        error_msg = "Missing or unknown command topic."
        suggestions.append(f"Start with a topic: {', '.join(VALID_TOPICS)}")
        if working_args:
            first = _normalize_token(working_args[0])
            action_topics = ACTION_TO_TOPICS.get(first, [])
            if len(action_topics) == 1:
                guessed_topic = action_topics[0]
                recovery_topic = guessed_topic
                suggestions.append(f"'{first}' is an action under '{guessed_topic}'. Try 'ask {guessed_topic} {first}'.")
                examples = _example_commands(guessed_topic, first, limit=3)
            elif len(action_topics) > 1:
                topics_text = ", ".join(action_topics)
                suggestions.append(f"'{first}' is ambiguous and exists under topics: {topics_text}.")
                ambiguous_topics = action_topics
                examples = _ambiguous_action_commands(first, action_topics)
                fix_suggestion_override = _ambiguous_action_fix_suggestion(first, action_topics)
            else:
                guess = get_closest_match(first, VALID_TOPICS)
                if guess:
                    recovery_topic = guess
                    closest_topic_suggestion = _closest_topic_fix_suggestion(guess)
                    suggestions.append(closest_topic_suggestion)
                    examples = _example_commands(guess, None, limit=3)
                    fix_suggestion_override = closest_topic_suggestion
                else:
                    use_fallback_recovery = True
                    fix_suggestion_override = _fallback_topic_fix_suggestion()
    elif topic not in VALID_TOPICS:
        normalized_topic = _normalize_token(topic)
        action_topics = ACTION_TO_TOPICS.get(normalized_topic, [])
        if len(action_topics) == 1:
            inferred_topic = action_topics[0]
            recovery_topic = inferred_topic
            error_msg = f"Unknown topic: '{topic}'"
            suggestions.append(
                f"'{normalized_topic}' is an action under '{inferred_topic}'. Try 'ask {inferred_topic} {normalized_topic}'."
            )
            examples = _example_commands(inferred_topic, normalized_topic, limit=3)
        elif len(action_topics) > 1:
            error_msg = f"Unknown topic: '{topic}'"
            options = ", ".join(action_topics)
            suggestions.append(
                f"'{normalized_topic}' is ambiguous and can belong to: {options}. Use an explicit topic."
            )
            ambiguous_topics = action_topics
            examples = _ambiguous_action_commands(normalized_topic, action_topics)
            examples.extend(_example_commands(None, None, limit=max(0, 3 - len(examples))))
            fix_suggestion_override = _ambiguous_action_fix_suggestion(normalized_topic, action_topics)
        else:
            guess = get_closest_match(normalized_topic, VALID_TOPICS)
            if guess:
                recovery_topic = guess
                error_msg = f"Unknown topic: '{topic}'"
                closest_topic_suggestion = _closest_topic_fix_suggestion(guess)
                suggestions.append(closest_topic_suggestion)
                examples = _example_commands(guess, None, limit=3)
                fix_suggestion_override = closest_topic_suggestion
            else:
                error_msg = f"Unknown topic: '{topic}'"
                suggestions.append(f"Valid topics: {', '.join(VALID_TOPICS)}")
                use_fallback_recovery = True
                fix_suggestion_override = _fallback_topic_fix_suggestion()
    elif not action:
        error_msg = f"Missing action for 'ask {topic}'"
        valid_actions = VALID_ACTIONS.get(topic, [])
        suggestions.append(f"Valid actions for '{topic}': {', '.join(valid_actions)}")
        examples = _example_commands(topic, None, limit=3)
    elif action not in VALID_ACTIONS.get(topic, []):
        valid = VALID_ACTIONS.get(topic, [])
        guess = get_closest_match(action, valid)
        if guess:
            error_msg = f"Unknown action: '{action}' for topic '{topic}'"
            suggestions.append(_closest_action_fix_suggestion(topic, guess))
            examples = _example_commands(topic, guess, limit=3)
            fix_suggestion_override = _closest_action_fix_suggestion(topic, guess)
        else:
            error_msg = f"Unknown action: '{action}' for topic '{topic}'"
            suggestions.append(f"Valid actions for '{topic}': {', '.join(valid)}")
            examples = _example_commands(topic, None, limit=3)
    full_message = f"❌ {error_msg}\n\n   Entered: `{entered}`"
    if parsed_error:
        full_message += f"\n   Parser detail: {parsed_error}"
    if suggestions:
        full_message += "\n\n🧭 Guidance:\n"
        full_message += "\n".join(f"   • {s}" for s in suggestions)
    if examples:
        full_message += "\n\n📚 Try one of these:\n"
        full_message += "\n".join(f"   • {e}" for e in examples[:3])
    fix_suggestion = fix_suggestion_override or _valid_actions_fix_suggestion(recovery_topic)
    if ambiguous_topics:
        _attach_recovery_data(
            result,
            None,
            examples,
            validation_commands=_recovery_commands_for_topics(ambiguous_topics),
        )
    elif use_fallback_recovery:
        _attach_recovery_data(
            result,
            None,
            examples,
            validation_commands=_fallback_recovery_commands(),
        )
    else:
        _attach_recovery_data(result, recovery_topic, examples)
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message=full_message,
            fix_suggestion=fix_suggestion,
        )
    )
    return result


def build_argument_error(
    topic: str,
    action: str,
    raw_args: List[str],
    *,
    parser_error: Optional[str] = None,
) -> CallResult:
    """Build a detailed error when command intent is clear but args are invalid."""
    result = CallResult()
    result.status = "error"
    entered = "ask " + " ".join(raw_args) if raw_args else f"ask {topic} {action}"
    parsed_error = _extract_argparse_error(parser_error) or "Argument syntax was invalid for this command."
    examples = _example_commands(topic, action, limit=3)
    _attach_recovery_data(result, topic, examples)
    message_lines = [
        "❌ Command intent was understood, but argument syntax is invalid.",
        "",
        f"   Entered: `{entered}`",
        f"   Parsed intent: `ask {topic} {action}`",
        f"   Parser detail: {parsed_error}",
        "",
        "🧭 Guidance:",
        f"   • Run `ask {topic} {action} --help` to see required/optional arguments.",
    ]
    if examples:
        message_lines.append("   • Use one of the valid example forms below.")
        message_lines.append("")
        message_lines.append("📚 Valid examples:")
        for example in examples:
            message_lines.append(f"   • {example}")
    result.errors.append(
        ErrorObject(
            code=ErrorCode.ERR_VALIDATION,
            message="\n".join(message_lines),
            fix_suggestion=f"Run 'ask {topic} {action} --help' and retry with the shown argument shape.",
        )
    )
    return result


def parse_args_with_capture(parser: argparse.ArgumentParser, argv: List[str]) -> Tuple[Optional[argparse.Namespace], Optional[int], str]:
    """Parse CLI args while capturing argparse stderr for richer error reporting."""
    stderr_buffer = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr_buffer):
            parsed = parser.parse_args(argv)
        return parsed, None, stderr_buffer.getvalue()
    except SystemExit as exc:
        return None, int(exc.code), stderr_buffer.getvalue()


def try_fuzzy_parse(raw_args: List[str], robot_mode: bool = False) -> Tuple[Optional[str], Optional[str], List[str], Optional[str]]:
    """
    Try to parse args with fuzzy matching.
    Returns: (topic, action, remaining_args, correction_note)
    """
    if not raw_args:
        return None, None, [], None
    prefix_flags, working_args = consume_global_prefix_flags(raw_args)
    if not working_args:
        return None, None, raw_args, None
    correction_note: Optional[str] = None
    first_token = _normalize_token(working_args[0])
    second_token = _normalize_token(working_args[1]) if len(working_args) > 1 else None
    if first_token == "goal":
        topic = "skills"
        action = "goal"
        return topic, action, prefix_flags + working_args[1:], format_correction("goal", "skills goal", robot_mode)
    if len(working_args) >= 2 and first_token == "doctor" and second_token == "catalog":
        topic = "repo"
        action = "doctor-catalog"
        return topic, action, prefix_flags + working_args[2:], format_correction("doctor catalog", "repo doctor-catalog", robot_mode)
    if len(working_args) >= 2:
        swapped_topic_candidate = second_token
        swapped_action_candidate = first_token
        if swapped_topic_candidate in VALID_TOPICS:
            swapped_valid_actions = VALID_ACTIONS.get(swapped_topic_candidate, [])
            resolved_swapped_action = None
            if swapped_action_candidate in swapped_valid_actions:
                resolved_swapped_action = swapped_action_candidate
            else:
                mapped_action = FUZZY_MATCHES.get(swapped_action_candidate)
                if mapped_action in swapped_valid_actions:
                    resolved_swapped_action = mapped_action
                else:
                    guess_action = get_closest_match(swapped_action_candidate, swapped_valid_actions)
                    if guess_action:
                        resolved_swapped_action = guess_action
            if resolved_swapped_action:
                correction_note = format_correction(
                    f"{working_args[0]} {working_args[1]}",
                    f"{swapped_topic_candidate} {resolved_swapped_action}",
                    robot_mode,
                )
                return (
                    swapped_topic_candidate,
                    resolved_swapped_action,
                    prefix_flags + working_args[2:],
                    correction_note,
                )
    topic = first_token
    remaining = working_args[1:]
    if topic not in VALID_TOPICS:
        if topic in FUZZY_MATCHES and FUZZY_MATCHES[topic] in VALID_TOPICS:
            corrected = FUZZY_MATCHES[topic]
            correction_note = format_correction(working_args[0], corrected, robot_mode)
            topic = corrected
        else:
            guess = get_closest_match(topic, VALID_TOPICS)
            if guess:
                correction_note = format_correction(working_args[0], guess, robot_mode)
                topic = guess
            else:
                unique_topics = ACTION_TO_TOPICS.get(topic, [])
                if len(unique_topics) == 1:
                    inferred_topic = unique_topics[0]
                    correction_note = format_correction(working_args[0], f"{inferred_topic} {topic}", robot_mode)
                    return inferred_topic, topic, prefix_flags + working_args[1:], correction_note
    action = None
    action_index = None
    for idx, token in enumerate(remaining):
        if token.startswith("-"):
            continue
        action = _normalize_token(token)
        action_index = idx
        break
    if action is not None:
        valid_actions = VALID_ACTIONS.get(topic, [])
        original_action = action
        if action not in valid_actions:
            mapped_action = FUZZY_MATCHES.get(action)
            if mapped_action in valid_actions:
                action = mapped_action
            else:
                guess = get_closest_match(action, valid_actions)
                if guess:
                    action = guess
        if action != original_action:
            correction_note = _merge_corrections(
                correction_note,
                format_correction(original_action, action, robot_mode),
            )
        remaining = remaining[:action_index] + remaining[action_index + 1:]
    full_remaining = prefix_flags + remaining
    return topic, action, full_remaining, correction_note
