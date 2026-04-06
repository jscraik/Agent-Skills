"""Skill graph navigation and discovery for agent-native workflows."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
from ask.envelope import CallResult, ErrorObject

def _get_graph_path(repo_root: Path) -> Path:
    """Returns the path to skill-edges.json."""
    return repo_root / "ops" / "metrics" / "graph" / "skill-edges.json"

def _load_graph(repo_root: Path) -> tuple[Optional[dict], Optional[ErrorObject]]:
    """Loads the skill graph from skill-edges.json.

    Returns:
        Tuple of (graph_data, error). If error is not None, graph_data is None.
    """
    edges_path = _get_graph_path(repo_root)
    if not edges_path.exists():
        return None, ErrorObject(
            code="ERR_DEPENDENCY",
            message="Skill graph data not found.",
            fix_suggestion="Run: python3 scripts/build-adjacency-yaml.py ."
        )
    try:
        data = json.loads(edges_path.read_text())
    except json.JSONDecodeError as e:
        return None, ErrorObject(
            code="ERR_DEPENDENCY",
            message=f"Skill graph is not valid JSON: {e}",
            fix_suggestion="Regenerate the graph with: python3 scripts/build-adjacency-yaml.py ."
        )

    # Validate required keys
    if "nodes" not in data or "edges" not in data:
        return None, ErrorObject(
            code="ERR_DEPENDENCY",
            message="Skill graph is missing required 'nodes' or 'edges' keys.",
            fix_suggestion="Regenerate the graph with: python3 scripts/build-adjacency-yaml.py ."
        )

    # Validate node structure
    for i, node in enumerate(data.get("nodes", [])):
        if "id" not in node:
            return None, ErrorObject(
                code="ERR_DEPENDENCY",
                message=f"Skill graph node at index {i} is missing required 'id' field.",
                fix_suggestion="Regenerate the graph with: python3 scripts/build-adjacency-yaml.py ."
            )

    # Validate edge structure
    for i, edge in enumerate(data.get("edges", [])):
        if "from" not in edge or "to" not in edge:
            return None, ErrorObject(
                code="ERR_DEPENDENCY",
                message=f"Skill graph edge at index {i} is missing required 'from' or 'to' fields.",
                fix_suggestion="Regenerate the graph with: python3 scripts/build-adjacency-yaml.py ."
            )

    return data, None

def _build_index(data: dict):
    """Builds node map and forward/reverse edge indices."""
    node_map = {n["id"]: n for n in data["nodes"]}
    fwd: dict[str, list] = defaultdict(list)
    rev: dict[str, list] = defaultdict(list)
    for e in data["edges"]:
        fwd[e["from"]].append(e)
        rev[e["to"]].append(e)
    return node_map, fwd, rev

def _find_node(data: dict, query: str) -> tuple[str | None, list[str] | None]:
    """Finds a skill node by query (exact match, prefix, or substring).

    Returns:
        Tuple of (matched_node_id, ambiguous_matches).
        - If exact match: returns (node_id, None)
        - If single partial match: returns (node_id, None)
        - If multiple matches: returns (None, list_of_matches)
        - If no match: returns (None, None)
    """
    nodes = {n["id"] for n in data["nodes"]}
    if query in nodes:
        return query, None
    matches = sorted(n for n in nodes if query.lower() in n.lower())
    if len(matches) == 1:
        return matches[0], None
    if len(matches) > 1:
        prefixed = [m for m in matches if m.startswith(query.lower())]
        if len(prefixed) == 1:
            return prefixed[0], None
        # Return ambiguous matches for caller to handle
        return None, (prefixed if prefixed else matches)
    return None, None

def _bfs_path(fwd: dict, start: str, end: str, max_depth: int = 6) -> list[str] | None:
    """Finds shortest path between two skills via BFS."""
    if start == end:
        return [start]
    visited: dict[str, str | None] = {start: None}
    queue = deque([(start, 0)])
    while queue:
        current, d = queue.popleft()
        if d >= max_depth:
            continue
        for edge in fwd.get(current, []):
            peer = edge["to"]
            if peer in visited:
                continue
            visited[peer] = current
            if peer == end:
                path = [end]
                while path[-1] != start:
                    path.append(visited[path[-1]])
                return list(reversed(path))
            queue.append((peer, d + 1))
    return None

def graph_related(repo_root: Path, skill: str, depth: int = 1, reverse: bool = False,
                  topic: str = None, tier: str = None) -> CallResult:
    """Finds related skills in the skill graph."""
    result = CallResult()
    data, error = _load_graph(repo_root)

    if error:
        result.status = "error"
        result.errors.append(error)
        return result
    
    node_map, fwd, rev = _build_index(data)
    start, ambiguous = _find_node(data, skill)

    if ambiguous:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Ambiguous skill name '{skill}'. Matches: {', '.join(ambiguous[:5])}",
            fix_suggestion="Use a more specific skill name."
        ))
        return result

    if not start:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Skill not found: '{skill}'"
        ))
        return result

    # Build related skills list
    adj = rev if reverse else fwd
    in_deg = {n["id"]: n.get("in_degree", 0) for n in node_map.values()}
    visited: dict[str, int] = {start: 0}
    queue = deque([(start, 0)])
    related = []
    
    while queue:
        current, d = queue.popleft()
        if d >= depth:
            continue
        edges = sorted(adj.get(current, []),
                      key=lambda e: (-e.get("weight", 1.0), 
                                    -in_deg.get(e["to"] if not reverse else e["from"], 0)))
        for edge in edges:
            peer = edge["from"] if reverse else edge["to"]
            if peer == start or peer in visited:
                continue
            visited[peer] = d + 1
            queue.append((peer, d + 1))
            pn = node_map.get(peer, {})
            if topic and pn.get("topic") != topic:
                continue
            if tier and pn.get("tier") != tier:
                continue
            related.append({
                "skill": peer,
                "topic": pn.get("topic", "unknown"),
                "tier": pn.get("tier", "experimental"),
                "depth": d + 1,
                "weight": round(edge.get("weight", 1.0), 3),
                "description": edge.get("desc", ""),
                "in_links": in_deg.get(peer, 0),
            })
    
    related.sort(key=lambda r: (-r["weight"], -r["in_links"]))
    
    result.status = "success"
    result.data["skill"] = start
    result.data["node"] = node_map.get(start, {})
    result.data["related"] = related
    result.data["count"] = len(related)
    result.data["direction"] = "in-links" if reverse else "out-links"
    result.data["depth"] = depth
    result.metadata["next_steps"] = [f"ask graph info {start}"]
    return result

def graph_find(repo_root: Path, query: str, topic: str = None, tier: str = None) -> CallResult:
    """Full-text search across skill names and topics."""
    result = CallResult()
    data, error = _load_graph(repo_root)

    if error:
        result.status = "error"
        result.errors.append(error)
        return result
    
    ql = query.lower()
    scored: list[tuple[float, dict]] = []
    
    for n in data["nodes"]:
        nid = n["id"]
        score = 0
        if ql == nid:
            score = 100
        elif nid.startswith(ql):
            score = 80
        elif ql in nid:
            score = 60
        elif ql in n.get("topic", ""):
            score = 30
        if score == 0:
            continue
        if topic and n.get("topic") != topic:
            continue
        if tier and n.get("tier") != tier:
            continue
        score += n.get("in_degree", 0) * 0.5
        scored.append((score, n))
    
    scored.sort(key=lambda x: -x[0])
    
    result.status = "success"
    result.data["query"] = query
    result.data["matches"] = [n for _, n in scored]
    result.data["count"] = len(scored)
    result.metadata["next_steps"] = [f"ask graph info <skill>"]
    return result

def graph_info(repo_root: Path, skill: str) -> CallResult:
    """Returns full node details including topic, tier, degree, and links."""
    result = CallResult()
    data, error = _load_graph(repo_root)

    if error:
        result.status = "error"
        result.errors.append(error)
        return result
    
    node_map, fwd, rev = _build_index(data)
    start, ambiguous = _find_node(data, skill)

    if ambiguous:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Ambiguous skill name '{skill}'. Matches: {', '.join(ambiguous[:5])}",
            fix_suggestion="Use a more specific skill name."
        ))
        return result

    if not start:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Skill not found: '{skill}'"
        ))
        return result

    n = node_map.get(start, {"id": start})
    out_edges = sorted(fwd.get(start, []), key=lambda e: -e.get("weight", 1.0))
    in_edges = sorted(rev.get(start, []), key=lambda e: -e.get("weight", 1.0))
    
    result.status = "success"
    result.data["skill"] = start
    result.data["node"] = n
    result.data["out_edges"] = out_edges
    result.data["in_edges"] = in_edges
    result.data["metrics"] = {
        "in_degree": n.get("in_degree", len(in_edges)),
        "out_degree": n.get("out_degree", len(out_edges)),
        "topic": n.get("topic", "unknown"),
        "tier": n.get("tier", "experimental"),
        "stability": n.get("stability", "unknown"),
    }
    result.metadata["next_steps"] = [
        f"ask graph related {start}",
        f"ask skills audit {start} --level strict"
    ]
    return result

def graph_chain(repo_root: Path, from_skill: str, to_skill: str) -> CallResult:
    """Finds the shortest path between two skills."""
    result = CallResult()
    data, error = _load_graph(repo_root)

    if error:
        result.status = "error"
        result.errors.append(error)
        return result
    
    node_map, fwd, rev = _build_index(data)
    start, start_ambiguous = _find_node(data, from_skill)
    end, end_ambiguous = _find_node(data, to_skill)

    if start_ambiguous:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Ambiguous skill name '{from_skill}'. Matches: {', '.join(start_ambiguous[:5])}",
            fix_suggestion="Use a more specific skill name."
        ))
        return result

    if end_ambiguous:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Ambiguous skill name '{to_skill}'. Matches: {', '.join(end_ambiguous[:5])}",
            fix_suggestion="Use a more specific skill name."
        ))
        return result

    if not start or not end:
        missing = []
        if not start:
            missing.append(f"'{from_skill}'")
        if not end:
            missing.append(f"'{to_skill}'")
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Skill(s) not found: {', '.join(missing)}"
        ))
        return result

    path = _bfs_path(fwd, start, end)

    if path is None:
        # Skills exist but no path found between them
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"No path found between '{start}' and '{end}' within max depth.",
            fix_suggestion="Try increasing the search depth or check if skills are in different disconnected clusters."
        ))
        result.data["from"] = start
        result.data["to"] = end
        result.data["path"] = None
        result.data["hops"] = None
        result.data["reachable"] = False
        return result

    result.status = "success"
    result.data["from"] = start
    result.data["to"] = end
    result.data["path"] = path
    result.data["hops"] = len(path) - 1
    result.data["reachable"] = True
    result.metadata["next_steps"] = [f"ask graph info {s}" for s in path]
    return result

def graph_list(repo_root: Path, topic: str = None, tier: str = None) -> CallResult:
    """Lists all skills with optional filtering."""
    result = CallResult()
    data, error = _load_graph(repo_root)

    if error:
        result.status = "error"
        result.errors.append(error)
        return result
    
    nodes = data["nodes"]
    if topic:
        nodes = [n for n in nodes if n.get("topic") == topic]
    if tier:
        nodes = [n for n in nodes if n.get("tier") == tier]
    
    nodes = sorted(nodes, key=lambda n: (-n.get("in_degree", 0), n["id"]))
    
    result.status = "success"
    result.data["skills"] = nodes
    result.data["count"] = len(nodes)
    result.data["filters"] = {"topic": topic, "tier": tier}
    result.metadata["next_steps"] = [f"ask graph info {n['id']}" for n in nodes[:3]]
    return result

def graph_topics(repo_root: Path) -> CallResult:
    """Lists all topic clusters in the skill graph."""
    result = CallResult()
    data, error = _load_graph(repo_root)

    if error:
        result.status = "error"
        result.errors.append(error)
        return result
    
    topics: dict[str, int] = defaultdict(int)
    for n in data["nodes"]:
        topic = n.get("topic", "unknown")
        topics[topic] += 1
    
    result.status = "success"
    result.data["topics"] = dict(sorted(topics.items(), key=lambda x: -x[1]))
    result.data["count"] = len(topics)
    result.metadata["next_steps"] = ["ask graph list --topic <topic>"]
    return result
