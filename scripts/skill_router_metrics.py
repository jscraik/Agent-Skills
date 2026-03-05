#!/usr/bin/env python3
"""Aggregate router telemetry into first-hit and guardrail metrics."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


def load_events(path: Path) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("event_type") == "skill_router.route_decision":
            events.append(obj)
    return events


def safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def compute_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_actor: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    prompt_outcomes: Dict[str, List[bool]] = defaultdict(list)

    correction_samples = []
    override_regret_count = 0
    with_selected_rank = 0

    for event in events:
        actor = str(event.get("actor_type", "unknown"))
        top1_chosen = event.get("top1_chosen")
        selected_rank = event.get("selected_rank")
        prompt_hash = str(event.get("prompt_hash", ""))

        by_actor[actor]["total"] += 1
        if top1_chosen is True:
            by_actor[actor]["first_hit"] += 1
            prompt_outcomes[prompt_hash].append(True)
        elif selected_rank is not None:
            prompt_outcomes[prompt_hash].append(False)

        if selected_rank is not None:
            with_selected_rank += 1
            if bool(event.get("override_regret_flag")):
                override_regret_count += 1

        latency = event.get("correction_latency_ms")
        if isinstance(latency, int) and latency >= 0:
            correction_samples.append(latency)

    repeat_misroute_prompts = 0
    for _prompt_hash, outcomes in prompt_outcomes.items():
        if outcomes.count(False) >= 2:
            repeat_misroute_prompts += 1

    actors_summary: Dict[str, Dict[str, float]] = {}
    for actor, counts in sorted(by_actor.items()):
        actors_summary[actor] = {
            "total": counts["total"],
            "first_hit_rate": safe_rate(counts["first_hit"], counts["total"]),
        }

    avg_correction_latency = (
        round(sum(correction_samples) / len(correction_samples), 2) if correction_samples else 0.0
    )

    return {
        "events_total": len(events),
        "first_hit_by_actor": actors_summary,
        "override_regret_rate": safe_rate(override_regret_count, with_selected_rank),
        "avg_correction_latency_ms": avg_correction_latency,
        "repeat_misroute_prompt_count": repeat_misroute_prompts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute skill-router metrics from event logs")
    parser.add_argument("--events", type=Path, required=True, help="Path to route events JSONL file")
    parser.add_argument("--json", action="store_true", help="Output metrics as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    events = load_events(args.events)
    metrics = compute_metrics(events)
    if args.json:
        print(json.dumps(metrics, indent=2, sort_keys=True))
    else:
        print(f"events_total={metrics['events_total']}")
        print(f"first_hit_by_actor={json.dumps(metrics['first_hit_by_actor'], sort_keys=True)}")
        print(f"override_regret_rate={metrics['override_regret_rate']}")
        print(f"avg_correction_latency_ms={metrics['avg_correction_latency_ms']}")
        print(f"repeat_misroute_prompt_count={metrics['repeat_misroute_prompt_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
