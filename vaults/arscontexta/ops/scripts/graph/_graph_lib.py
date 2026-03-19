#!/usr/bin/env python3
"""Shared helpers for Ars Contexta graph operations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


class GraphIndexError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise GraphIndexError(f"unable to read {path}: {exc}") from exc


def write_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent), suffix=".tmp") as tmp:
        json.dump(data, tmp, indent=2, sort_keys=True, ensure_ascii=False)
        tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, path)


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent), suffix=".tmp") as tmp:
        tmp.write(text)
        if not text.endswith("\n"):
            tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, path)


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return f"sha256:{hasher.hexdigest()}"


def append_ndjson_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    existing = []
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            existing = handle.readlines()
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent), suffix=".tmp") as tmp:
        if existing:
            tmp.writelines(existing)
            if existing and not existing[-1].endswith("\n"):
                tmp.write("\n")
        tmp.write(encoded)
        tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, path)


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def read_ndjson_lines(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            value = line.strip()
            if not value:
                continue
            try:
                rows.append(json.loads(value))
            except json.JSONDecodeError as exc:
                raise GraphIndexError(f"invalid ndjson line {line_no} in {path}: {exc}") from exc
    return rows


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, []

    frontmatter: Dict[str, Any] = {}
    warnings: List[Dict[str, str]] = []
    consumed = False

    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            consumed = True
            break
        if not line.strip():
            continue
        if ":" not in line:
            warnings.append(
                {
                    "code": "frontmatter_syntax",
                    "message": f"frontmatter line is not key-value: {line.strip()}",
                    "line": str(idx + 1),
                }
            )
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')

    if not consumed:
        warnings.append(
            {
                "code": "frontmatter_unterminated",
                "message": "frontmatter did not close with '---'",
            }
        )
        return {}, warnings

    return frontmatter, warnings


def normalize_link(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    # Strip alias (|alias), heading anchor (#section), and block ref (^id)
    raw = raw.split("|", 1)[0].strip()
    raw = raw.split("#", 1)[0].strip()
    raw = raw.split("^", 1)[0].strip()
    return raw


def extract_links(text: str) -> List[str]:
    links: List[str] = []
    for raw in LINK_PATTERN.findall(text):
        target = normalize_link(raw)
        if target:
            links.append(target)
    return links


def discover_note_files(notes_dir: Path) -> List[Path]:
    if not notes_dir.exists():
        return []
    files = []
    for path in notes_dir.rglob("*.md"):
        if path.is_file():
            files.append(path)
    return sorted(files)


def canonical_node_id(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    return str(rel.with_suffix(""))


def build_graph_index(notes_dir: Path) -> Dict[str, Any]:
    notes = discover_note_files(notes_dir)
    nodes: Dict[str, Dict[str, Any]] = {}
    by_basename: Dict[str, List[str]] = defaultdict(list)
    raw_links: Dict[str, List[str]] = {}
    warnings: List[Dict[str, str]] = []

    for note_path in sorted(notes):
        try:
            text = read_text(note_path)
        except GraphIndexError as exc:
            warnings.append({"code": "note_read_error", "message": str(exc), "path": str(note_path)})
            continue

        frontmatter, frontmatter_warnings = parse_frontmatter(text)
        for warning in frontmatter_warnings:
            warning = dict(warning)
            warning.setdefault("path", str(note_path))
            warnings.append(warning)

        try:
            node_id = canonical_node_id(note_path, notes_dir)
        except ValueError:
            node_id = str(note_path)

        title = frontmatter.get("title") or note_path.stem
        node = {
            "id": node_id,
            "path": str(note_path),
            "basename": note_path.stem,
            "title": title,
            "in_degree": 0,
            "out_degree": 0,
            "note_type": frontmatter.get("type") or "note",
        }
        nodes[node_id] = node
        by_basename[note_path.stem].append(node_id)

        links = []
        seen_links = set()
        for link in extract_links(text):
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            links.append(link)
        raw_links[node_id] = links

    edges: Set[Tuple[str, str]] = set()
    adjacency_out = defaultdict(set)
    adjacency_in = defaultdict(set)
    dangling_counts: Counter[str] = Counter()
    ambiguous_warned = set()

    for source_id, link_targets in sorted(raw_links.items(), key=lambda item: item[0]):
        if source_id not in nodes:
            continue
        for target_name in link_targets:
            chosen_target = None
            # Try exact node ID match first (for folder-qualified links)
            if target_name in nodes:
                chosen_target = target_name
            # Fall back to basename matching
            elif target_name in by_basename:
                candidates = sorted(by_basename[target_name])
                chosen_target = candidates[0]
                if len(candidates) > 1 and target_name not in ambiguous_warned:
                    warnings.append(
                        {
                            "code": "duplicate_basename",
                            "message": (
                                f"duplicate basename '{target_name}' for targets {candidates}; "
                                f"resolved to '{chosen_target}'"
                            ),
                            "target": target_name,
                            "candidates": ",".join(candidates),
                        }
                    )
                    ambiguous_warned.add(target_name)

            if chosen_target is not None:
                if chosen_target != source_id:
                    edges.add((source_id, chosen_target))
                    adjacency_out[source_id].add(chosen_target)
                    adjacency_in[chosen_target].add(source_id)
            else:
                dangling_counts[f"{source_id}=>{target_name}"] += 1
                warnings.append(
                    {
                        "code": "dangling_link",
                        "source": source_id,
                        "target": target_name,
                    }
                )

    node_summary = []
    for node_id in sorted(nodes):
        node = dict(nodes[node_id])
        node["in_degree"] = len(adjacency_in[node_id])
        node["out_degree"] = len(adjacency_out[node_id])
        node_summary.append(node)

    edge_rows = [
        {"from": source, "to": target}
        for source, target in sorted(edges, key=lambda item: (item[0], item[1]))
    ]

    built_at = _build_built_at(notes)
    index = {
        "schema": "arscontexta_graph_index.v1",
        "built_at": built_at,
        "notes_dir": str(notes_dir),
        "nodes": node_summary,
        "edges": edge_rows,
        "warnings": warnings,
        "stats": {
            "node_count": len(node_summary),
            "edge_count": len(edge_rows),
            "orphan_count": sum(1 for node in node_summary if node["in_degree"] + node["out_degree"] == 0),
            "dangling_count": len(dangling_counts),
            "duplicate_basename_count": sum(1 for candidates in by_basename.values() if len(candidates) > 1),
            "max_nodes_requested": None,
            "max_edges_requested": None,
        },
        "parse_summary": {
            "notes_seen": len(nodes),
            "note_files_found": len(notes),
            "notes_index_basenames": sum(len(v) for v in by_basename.values()),
        },
    }
    return index


def _build_built_at(notes: List[Path]) -> str:
    if not notes:
        return datetime.fromtimestamp(0, tz=timezone.utc).isoformat()
    latest = max(path.stat().st_mtime for path in notes)
    return datetime.fromtimestamp(latest, tz=timezone.utc).isoformat()


def build_truncated_view(index: Dict[str, Any], max_nodes: int, max_edges: int) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    warnings: List[Dict[str, str]] = []
    nodes = sorted(index["nodes"], key=lambda item: (-(item["in_degree"] + item["out_degree"]), item["id"]))

    total_nodes = len(nodes)
    keep_nodes = nodes
    truncated_nodes = False
    if max_nodes and max_nodes > 0 and len(nodes) > max_nodes:
        keep_nodes = nodes[:max_nodes]
        truncated_nodes = True
        warnings.append(
            {
                "code": "graph_truncation",
                "message": f"max_nodes reached: requested {max_nodes}, kept {len(keep_nodes)} of {total_nodes}",
            }
        )

    keep_ids = {node["id"] for node in keep_nodes}
    filtered_edges = [edge for edge in sorted(index["edges"], key=lambda edge: (edge["from"], edge["to"])) if edge["from"] in keep_ids and edge["to"] in keep_ids]

    total_edges = len(filtered_edges)
    truncated_edges = False
    if max_edges and max_edges > 0 and total_edges > max_edges:
        filtered_edges = filtered_edges[:max_edges]
        truncated_edges = True
        warnings.append(
            {
                "code": "graph_truncation",
                "message": f"max_edges reached: requested {max_edges}, kept {len(filtered_edges)} of {total_edges}",
            }
        )

    # Recompute degrees based on filtered edges
    in_degree: Counter[str] = Counter()
    out_degree: Counter[str] = Counter()
    for edge in filtered_edges:
        out_degree[edge["from"]] += 1
        in_degree[edge["to"]] += 1

    # Update node degrees to match filtered edges
    updated_nodes = []
    for node in keep_nodes:
        updated_node = dict(node)
        updated_node["in_degree"] = in_degree.get(node["id"], 0)
        updated_node["out_degree"] = out_degree.get(node["id"], 0)
        updated_nodes.append(updated_node)

    truncated_view = {
        "schema": "arscontexta_graph_index.v1",
        "built_at": index["built_at"],
        "notes_dir": index["notes_dir"],
        "nodes": sorted(updated_nodes, key=lambda item: item["id"]),
        "edges": filtered_edges,
        "warnings": index["warnings"] + warnings,
        "stats": {
            "node_count": len(updated_nodes),
            "edge_count": len(filtered_edges),
            "truncated_nodes": truncated_nodes,
            "truncated_edges": truncated_edges,
            "source_node_count": total_nodes,
            "source_edge_count": len(index["edges"]),
        },
    }
    return truncated_view, warnings


def compute_components(index: Dict[str, Any]) -> Tuple[List[List[str]], Counter[str], Counter[str]]:
    adjacency: Dict[str, set] = defaultdict(set)
    for node in index["nodes"]:
        adjacency[node["id"]] = set()
    for edge in index["edges"]:
        source = edge["from"]
        target = edge["to"]
        adjacency[source].add(target)
        adjacency[target].add(source)

    seen = set()
    communities: List[List[str]] = []
    for node in sorted(adjacency):
        if node in seen:
            continue
        queue = deque([node])
        seen.add(node)
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for nxt in sorted(adjacency[current]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        communities.append(sorted(component))

    communities.sort(key=lambda c: (-len(c), c[0] if c else ""))

    node_in_degrees = Counter()
    node_out_degrees = Counter()
    for edge in index["edges"]:
        node_out_degrees[edge["from"]] += 1
        node_in_degrees[edge["to"]] += 1

    return communities, node_in_degrees, node_out_degrees


def compute_metric_payload(index: Dict[str, Any], communities: List[List[str]], node_in: Counter, node_out: Counter) -> Dict[str, Any]:
    node_count = len(index["nodes"])
    edge_count = len(index["edges"])
    possible = max(node_count * (node_count - 1), 1)
    degree_total = sum(node_in.values()) + sum(node_out.values())

    degree_map: Dict[str, int] = {}
    for node in index["nodes"]:
        degree_map[node["id"]] = node["in_degree"] + node["out_degree"]

    hubs = sorted(degree_map.items(), key=lambda item: (-item[1], item[0]))[:5]
    largest = max((len(component) for component in communities), default=0)

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "density": round((edge_count * 1.0) / possible, 6),
        "orphan_count": sum(1 for item in index["nodes"] if (item["in_degree"] + item["out_degree"]) == 0),
        "dangling_count": len([warning for warning in index.get("warnings", []) if warning.get("code") == "dangling_link"]),
        "avg_degree": round((degree_total / node_count), 6) if node_count else 0.0,
        "giant_component_size": largest,
        "community_count": len(communities),
        "top_hubs": [
            {"id": node_id, "degree": degree}
            for node_id, degree in hubs
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notes-dir")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-nodes", type=int, default=200)
    parser.add_argument("--max-edges", type=int, default=1000)
    parser.add_argument("--vault-root", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index = build_graph_index(Path(args.notes_dir))
    index["stats"]["max_nodes_requested"] = args.max_nodes
    index["stats"]["max_edges_requested"] = args.max_edges
    if args.vault_root:
        index["vault_root"] = args.vault_root

    output = Path(args.output)
    if args.max_nodes > 0 or args.max_edges > 0:
        truncated, _ = build_truncated_view(index, args.max_nodes, args.max_edges)
        write_json_atomic(output, truncated)
    else:
        write_json_atomic(output, index)


if __name__ == "__main__":
    main()
