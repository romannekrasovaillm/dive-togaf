"""Architecture graph analysis tools built on NetworkX.

Wraps NetworkX into TOGAF-domain tools for analyzing architecture
dependency graphs, component coupling, critical paths, impact analysis,
and topology metrics. Analogous to how DIVE wraps BioPython into 61 tools.

One library → many tools, each a focused operation on architecture graphs.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import networkx as nx
import numpy as np


# =====================================================================
# Internal: graph construction from architecture data
# =====================================================================

def _build_graph(nodes: list[dict], edges: list[dict], directed: bool = True) -> nx.DiGraph | nx.Graph:
    """Build a NetworkX graph from node/edge dicts.

    Nodes: [{"id": "sys1", "type": "application", "layer": "application", ...}]
    Edges: [{"source": "sys1", "target": "sys2", "type": "serving", "weight": 1.0}]
    """
    G = nx.DiGraph() if directed else nx.Graph()
    for node in nodes:
        nid = node["id"]
        G.add_node(nid, **{k: v for k, v in node.items() if k != "id"})
    for edge in edges:
        G.add_edge(
            edge["source"], edge["target"],
            **{k: v for k, v in edge.items() if k not in ("source", "target")},
        )
    return G


# =====================================================================
# RETRIEVAL TOOLS — query/extract info from architecture graphs
# =====================================================================

# Tool R1: graph_get_node_info
def graph_get_node_info(
    nodes: list[dict], edges: list[dict], node_id: str,
) -> dict:
    """Get all information about a specific node: attributes, neighbors,
    in-degree, out-degree.

    Args:
        nodes: List of node dicts with 'id' and attributes.
        edges: List of edge dicts with 'source', 'target', and attributes.
        node_id: ID of the node to query.

    Returns:
        Node attributes, predecessors, successors, degree info.
    """
    G = _build_graph(nodes, edges)
    if node_id not in G:
        return {"error": f"Node '{node_id}' not found", "available_nodes": list(G.nodes)[:20]}

    attrs = dict(G.nodes[node_id])
    preds = [{"id": p, **dict(G.edges[p, node_id])} for p in G.predecessors(node_id)]
    succs = [{"id": s, **dict(G.edges[node_id, s])} for s in G.successors(node_id)]

    return {
        "node_id": node_id,
        "attributes": attrs,
        "in_degree": G.in_degree(node_id),
        "out_degree": G.out_degree(node_id),
        "predecessors": preds,
        "successors": succs,
    }


# Tool R2: graph_find_neighbors
def graph_find_neighbors(
    nodes: list[dict], edges: list[dict], node_id: str,
    depth: int = 1, direction: str = "both",
) -> dict:
    """Find all neighbors of a node up to a given depth (hop count).
    Useful for blast-radius / impact analysis.

    Args:
        nodes/edges: Graph data.
        node_id: Starting node.
        depth: Max hops (1-5).
        direction: "outgoing", "incoming", or "both".
    """
    G = _build_graph(nodes, edges)
    if node_id not in G:
        return {"error": f"Node '{node_id}' not found"}

    depth = min(depth, 5)

    if direction == "outgoing":
        tree = nx.bfs_tree(G, node_id, depth_limit=depth)
        reachable = set(tree.nodes) - {node_id}
    elif direction == "incoming":
        tree = nx.bfs_tree(G.reverse(), node_id, depth_limit=depth)
        reachable = set(tree.nodes) - {node_id}
    else:
        out_tree = nx.bfs_tree(G, node_id, depth_limit=depth)
        in_tree = nx.bfs_tree(G.reverse(), node_id, depth_limit=depth)
        reachable = (set(out_tree.nodes) | set(in_tree.nodes)) - {node_id}

    neighbor_details = []
    for nid in reachable:
        neighbor_details.append({"id": nid, **dict(G.nodes[nid])})

    return {
        "node_id": node_id,
        "direction": direction,
        "depth": depth,
        "neighbors": neighbor_details,
        "count": len(neighbor_details),
    }


# Tool R3: graph_find_paths
def graph_find_paths(
    nodes: list[dict], edges: list[dict],
    source: str, target: str, max_paths: int = 5,
) -> dict:
    """Find all simple paths between two nodes. Useful for understanding
    dependency chains and integration pathways.

    Args:
        nodes/edges: Graph data.
        source: Start node.
        target: End node.
        max_paths: Max paths to return.
    """
    G = _build_graph(nodes, edges)
    if source not in G or target not in G:
        return {"error": "Source or target not found"}

    try:
        paths = list(nx.all_simple_paths(G, source, target, cutoff=10))
        paths = paths[:max_paths]
    except nx.NetworkXError:
        paths = []

    shortest = None
    try:
        shortest = nx.shortest_path(G, source, target)
    except nx.NetworkXNoPath:
        pass

    return {
        "source": source,
        "target": target,
        "shortest_path": shortest,
        "shortest_length": len(shortest) - 1 if shortest else None,
        "all_paths": paths,
        "path_count": len(paths),
    }


# Tool R4: graph_get_components
def graph_get_components(
    nodes: list[dict], edges: list[dict],
) -> dict:
    """Find connected components (subsystems / architecture domains).
    Weakly connected for directed graphs.

    Returns list of components with their nodes and sizes.
    """
    G = _build_graph(nodes, edges)
    components = []
    for i, comp in enumerate(sorted(nx.weakly_connected_components(G), key=len, reverse=True)):
        comp_nodes = [{"id": n, **dict(G.nodes[n])} for n in comp]
        components.append({
            "component_id": i,
            "size": len(comp),
            "nodes": comp_nodes,
        })

    return {
        "total_components": len(components),
        "components": components,
        "is_connected": len(components) == 1,
    }


# Tool R5: graph_find_cycles
def graph_find_cycles(
    nodes: list[dict], edges: list[dict],
) -> dict:
    """Detect circular dependencies in the architecture graph.
    Critical for identifying architectural anti-patterns.

    Returns all simple cycles found.
    """
    G = _build_graph(nodes, edges)
    try:
        cycles = list(nx.simple_cycles(G))
    except Exception:
        cycles = []

    cycle_details = []
    for cycle in cycles[:50]:  # cap at 50
        edge_types = []
        for i in range(len(cycle)):
            src = cycle[i]
            tgt = cycle[(i + 1) % len(cycle)]
            if G.has_edge(src, tgt):
                edge_types.append(G.edges[src, tgt].get("type", "unknown"))
        cycle_details.append({
            "nodes": cycle,
            "length": len(cycle),
            "edge_types": edge_types,
        })

    return {
        "has_cycles": len(cycles) > 0,
        "cycle_count": len(cycles),
        "cycles": cycle_details,
    }


# Tool R6: graph_get_leaf_nodes
def graph_get_leaf_nodes(
    nodes: list[dict], edges: list[dict],
    leaf_type: str = "sink",
) -> dict:
    """Find leaf nodes — sinks (no outgoing) or sources (no incoming).
    Sinks = end-consumers, sources = providers/data-origins.

    Args:
        leaf_type: "sink" (out-degree=0), "source" (in-degree=0), or "isolated" (degree=0).
    """
    G = _build_graph(nodes, edges)
    leaves = []

    for n in G.nodes:
        if leaf_type == "sink" and G.out_degree(n) == 0:
            leaves.append({"id": n, **dict(G.nodes[n])})
        elif leaf_type == "source" and G.in_degree(n) == 0:
            leaves.append({"id": n, **dict(G.nodes[n])})
        elif leaf_type == "isolated" and G.degree(n) == 0:
            leaves.append({"id": n, **dict(G.nodes[n])})

    return {
        "leaf_type": leaf_type,
        "leaves": leaves,
        "count": len(leaves),
    }


# Tool R7: graph_get_bridges
def graph_get_bridges(
    nodes: list[dict], edges: list[dict],
) -> dict:
    """Find bridge edges — edges whose removal disconnects the graph.
    These represent single points of failure in the architecture.
    """
    G = _build_graph(nodes, edges, directed=False)
    bridges = list(nx.bridges(G))

    bridge_details = []
    for u, v in bridges:
        edge_data = dict(G.edges[u, v]) if G.has_edge(u, v) else {}
        bridge_details.append({
            "source": u,
            "target": v,
            **edge_data,
        })

    return {
        "has_bridges": len(bridges) > 0,
        "bridge_count": len(bridges),
        "bridges": bridge_details,
    }


# Tool R8: graph_get_subgraph
def graph_get_subgraph(
    nodes: list[dict], edges: list[dict],
    filter_key: str, filter_value: str,
) -> dict:
    """Extract a subgraph by filtering nodes on an attribute.
    E.g. filter_key="layer", filter_value="application" → application-layer subgraph.

    Args:
        filter_key: Node attribute to filter on.
        filter_value: Required value.
    """
    G = _build_graph(nodes, edges)
    matching = [n for n, d in G.nodes(data=True) if d.get(filter_key) == filter_value]
    sub = G.subgraph(matching)

    sub_nodes = [{"id": n, **dict(sub.nodes[n])} for n in sub.nodes]
    sub_edges = [{"source": u, "target": v, **dict(sub.edges[u, v])} for u, v in sub.edges]

    return {
        "filter": {filter_key: filter_value},
        "nodes": sub_nodes,
        "edges": sub_edges,
        "node_count": len(sub_nodes),
        "edge_count": len(sub_edges),
    }


# =====================================================================
# PROCESSING TOOLS — compute metrics / transformations
# =====================================================================

# Tool P1: graph_compute_centrality
def graph_compute_centrality(
    nodes: list[dict], edges: list[dict],
    metric: str = "betweenness", top_n: int = 10,
) -> dict:
    """Compute centrality metrics to find the most critical components.

    Args:
        metric: "betweenness", "closeness", "degree", "eigenvector", "pagerank".
        top_n: Number of top nodes to return.

    Returns:
        Ranked list of nodes by centrality score.
    """
    G = _build_graph(nodes, edges)

    if metric == "betweenness":
        scores = nx.betweenness_centrality(G)
    elif metric == "closeness":
        scores = nx.closeness_centrality(G)
    elif metric == "degree":
        scores = nx.degree_centrality(G)
    elif metric == "eigenvector":
        try:
            scores = nx.eigenvector_centrality(G, max_iter=500)
        except nx.PowerIterationFailedConvergence:
            scores = nx.eigenvector_centrality_numpy(G)
    elif metric == "pagerank":
        scores = nx.pagerank(G)
    else:
        return {"error": f"Unknown metric: {metric}"}

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    result = []
    for nid, score in ranked:
        result.append({"id": nid, "score": round(score, 6), **dict(G.nodes[nid])})

    return {
        "metric": metric,
        "top_nodes": result,
        "count": len(result),
        "total_nodes": G.number_of_nodes(),
    }


# Tool P2: graph_compute_coupling
def graph_compute_coupling(
    nodes: list[dict], edges: list[dict],
    group_key: str = "layer",
) -> dict:
    """Compute coupling and cohesion metrics between node groups.
    Groups are defined by a node attribute (e.g. "layer", "domain").

    Afferent coupling (Ca): incoming dependencies from other groups.
    Efferent coupling (Ce): outgoing dependencies to other groups.
    Instability = Ce / (Ca + Ce).

    Returns per-group coupling metrics.
    """
    G = _build_graph(nodes, edges)

    groups: dict[str, set] = {}
    for n, d in G.nodes(data=True):
        g = d.get(group_key, "unknown")
        groups.setdefault(g, set()).add(n)

    metrics = []
    for group_name, group_nodes in groups.items():
        ca = 0  # afferent
        ce = 0  # efferent
        internal = 0

        for u, v in G.edges:
            u_group = G.nodes[u].get(group_key, "unknown")
            v_group = G.nodes[v].get(group_key, "unknown")

            if u_group == group_name and v_group == group_name:
                internal += 1
            elif u_group == group_name and v_group != group_name:
                ce += 1
            elif u_group != group_name and v_group == group_name:
                ca += 1

        instability = round(ce / (ca + ce), 4) if (ca + ce) > 0 else 0.0
        cohesion = round(internal / len(group_nodes), 4) if len(group_nodes) > 0 else 0.0

        metrics.append({
            "group": group_name,
            "node_count": len(group_nodes),
            "internal_edges": internal,
            "afferent_coupling": ca,
            "efferent_coupling": ce,
            "instability": instability,
            "cohesion": cohesion,
        })

    return {
        "group_key": group_key,
        "groups": metrics,
        "group_count": len(metrics),
    }


# Tool P3: graph_compute_critical_path
def graph_compute_critical_path(
    nodes: list[dict], edges: list[dict],
    weight_key: str = "weight",
) -> dict:
    """Compute the critical path (longest path) in a DAG.
    Used for migration roadmap sequencing and bottleneck identification.

    Args:
        weight_key: Edge attribute for duration/cost weighting.

    Returns:
        Critical path nodes, total weight, and slack for each node.
    """
    G = _build_graph(nodes, edges)

    if not nx.is_directed_acyclic_graph(G):
        return {"error": "Graph has cycles — critical path requires a DAG", "has_cycles": True}

    # Compute longest path using topological order
    topo_order = list(nx.topological_sort(G))

    dist: dict[str, float] = {n: 0.0 for n in G.nodes}
    predecessor: dict[str, str | None] = {n: None for n in G.nodes}

    for u in topo_order:
        for v in G.successors(u):
            w = G.edges[u, v].get(weight_key, 1.0)
            if isinstance(w, str):
                try:
                    w = float(w)
                except ValueError:
                    w = 1.0
            if dist[u] + w > dist[v]:
                dist[v] = dist[u] + w
                predecessor[v] = u

    # Find endpoint of critical path
    end_node = max(dist, key=dist.get)
    total_weight = dist[end_node]

    # Reconstruct path
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = predecessor[current]
    path.reverse()

    # Compute slack
    slack = {}
    for n in G.nodes:
        latest = total_weight - dist[n]
        slack[n] = round(latest - dist[n], 4) if n not in path else 0.0

    path_details = []
    for n in path:
        path_details.append({"id": n, "earliest_start": round(dist[n], 4), **dict(G.nodes[n])})

    return {
        "critical_path": path_details,
        "total_weight": round(total_weight, 4),
        "path_length": len(path),
        "slack": {n: s for n, s in slack.items() if s > 0},
    }


# Tool P4: graph_compute_impact_score
def graph_compute_impact_score(
    nodes: list[dict], edges: list[dict],
    changed_nodes: list[str],
    propagation_decay: float = 0.5,
) -> dict:
    """Compute change impact propagation scores.
    Simulates how a change to one or more nodes propagates through
    the dependency graph with decay.

    Args:
        changed_nodes: List of node IDs being changed.
        propagation_decay: Decay factor per hop (0-1). Lower = faster decay.

    Returns:
        Impact score for every affected node, sorted by impact.
    """
    G = _build_graph(nodes, edges)

    impact: dict[str, float] = {}
    for start in changed_nodes:
        if start not in G:
            continue
        # BFS with decay
        visited = {start: 1.0}
        queue = [(start, 1.0)]
        while queue:
            current, score = queue.pop(0)
            for neighbor in G.successors(current):
                new_score = score * propagation_decay
                if neighbor not in visited or visited[neighbor] < new_score:
                    visited[neighbor] = new_score
                    queue.append((neighbor, new_score))

        for n, s in visited.items():
            if n not in changed_nodes:
                impact[n] = impact.get(n, 0) + s

    ranked = sorted(impact.items(), key=lambda x: x[1], reverse=True)
    impacted = []
    for nid, score in ranked:
        impacted.append({"id": nid, "impact_score": round(score, 6), **dict(G.nodes.get(nid, {}))})

    return {
        "changed_nodes": changed_nodes,
        "propagation_decay": propagation_decay,
        "impacted_nodes": impacted,
        "impacted_count": len(impacted),
        "max_impact_score": round(ranked[0][1], 6) if ranked else 0,
    }


# Tool P5: graph_compute_modularity
def graph_compute_modularity(
    nodes: list[dict], edges: list[dict],
    group_key: str = "layer",
) -> dict:
    """Compute modularity score for the current node grouping.
    Higher modularity means the architecture is well-decomposed.

    Uses Newman's modularity Q metric.
    """
    G = _build_graph(nodes, edges, directed=False)

    communities = []
    groups: dict[str, set] = {}
    for n, d in G.nodes(data=True):
        g = d.get(group_key, "unknown")
        groups.setdefault(g, set()).add(n)
    communities = list(groups.values())

    try:
        q = nx.community.modularity(G, communities)
    except Exception:
        q = 0.0

    return {
        "group_key": group_key,
        "modularity": round(q, 6),
        "group_count": len(communities),
        "interpretation": (
            "excellent" if q > 0.6 else
            "good" if q > 0.4 else
            "moderate" if q > 0.2 else
            "poor"
        ),
        "groups": {name: len(nodes_set) for name, nodes_set in groups.items()},
    }


# Tool P6: graph_compute_topology_metrics
def graph_compute_topology_metrics(
    nodes: list[dict], edges: list[dict],
) -> dict:
    """Compute overall graph topology metrics:
    density, average degree, diameter, clustering coefficient.

    Gives a high-level health check of the architecture graph.
    """
    G = _build_graph(nodes, edges)
    n = G.number_of_nodes()
    e = G.number_of_edges()

    density = nx.density(G)
    avg_in = sum(d for _, d in G.in_degree()) / n if n > 0 else 0
    avg_out = sum(d for _, d in G.out_degree()) / n if n > 0 else 0

    # Diameter on largest weakly connected component
    largest_cc = max(nx.weakly_connected_components(G), key=len) if n > 0 else set()
    try:
        undirected_sub = G.subgraph(largest_cc).to_undirected()
        diameter = nx.diameter(undirected_sub)
    except Exception:
        diameter = None

    # Clustering on undirected view
    try:
        avg_clustering = nx.average_clustering(G.to_undirected())
    except Exception:
        avg_clustering = 0.0

    is_dag = nx.is_directed_acyclic_graph(G)

    return {
        "node_count": n,
        "edge_count": e,
        "density": round(density, 6),
        "avg_in_degree": round(avg_in, 4),
        "avg_out_degree": round(avg_out, 4),
        "diameter": diameter,
        "avg_clustering": round(avg_clustering, 6),
        "is_dag": is_dag,
        "weakly_connected_components": nx.number_weakly_connected_components(G),
    }


# Tool P7: graph_compute_dependency_depth
def graph_compute_dependency_depth(
    nodes: list[dict], edges: list[dict],
) -> dict:
    """Compute the dependency depth for each node — how many hops
    to reach a source (root) node. Deep dependency chains are a smell.

    Returns nodes with their depth and the max depth.
    """
    G = _build_graph(nodes, edges)

    if not nx.is_directed_acyclic_graph(G):
        return {"error": "Graph has cycles — depth requires a DAG"}

    # Sources = in-degree 0
    sources = [n for n in G.nodes if G.in_degree(n) == 0]

    depths: dict[str, int] = {}
    for source in sources:
        for n, d in nx.single_source_shortest_path_length(G, source).items():
            if n not in depths or d > depths[n]:
                depths[n] = d

    depth_distribution: dict[int, int] = {}
    for d in depths.values():
        depth_distribution[d] = depth_distribution.get(d, 0) + 1

    node_depths = sorted(
        [{"id": n, "depth": d, **dict(G.nodes[n])} for n, d in depths.items()],
        key=lambda x: x["depth"], reverse=True,
    )

    return {
        "max_depth": max(depths.values()) if depths else 0,
        "depth_distribution": depth_distribution,
        "deepest_nodes": node_depths[:10],
        "source_count": len(sources),
    }


# Tool P8: graph_compute_similarity
def graph_compute_similarity(
    nodes_a: list[dict], edges_a: list[dict],
    nodes_b: list[dict], edges_b: list[dict],
) -> dict:
    """Compute structural similarity between two architecture graphs.
    Uses Jaccard similarity on node sets and edge sets.

    Useful for comparing baseline vs target, or two architecture alternatives.
    """
    G_a = _build_graph(nodes_a, edges_a)
    G_b = _build_graph(nodes_b, edges_b)

    nodes_set_a = set(G_a.nodes)
    nodes_set_b = set(G_b.nodes)
    edges_set_a = set(G_a.edges)
    edges_set_b = set(G_b.edges)

    node_intersection = nodes_set_a & nodes_set_b
    node_union = nodes_set_a | nodes_set_b
    edge_intersection = edges_set_a & edges_set_b
    edge_union = edges_set_a | edges_set_b

    node_jaccard = len(node_intersection) / len(node_union) if node_union else 1.0
    edge_jaccard = len(edge_intersection) / len(edge_union) if edge_union else 1.0

    only_in_a_nodes = nodes_set_a - nodes_set_b
    only_in_b_nodes = nodes_set_b - nodes_set_a

    return {
        "node_similarity": round(node_jaccard, 4),
        "edge_similarity": round(edge_jaccard, 4),
        "overall_similarity": round((node_jaccard + edge_jaccard) / 2, 4),
        "shared_nodes": len(node_intersection),
        "only_in_a": list(only_in_a_nodes),
        "only_in_b": list(only_in_b_nodes),
        "shared_edges": len(edge_intersection),
        "graph_a": {"nodes": G_a.number_of_nodes(), "edges": G_a.number_of_edges()},
        "graph_b": {"nodes": G_b.number_of_nodes(), "edges": G_b.number_of_edges()},
    }


# Tool P9: graph_compute_topological_sort
def graph_compute_topological_sort(
    nodes: list[dict], edges: list[dict],
) -> dict:
    """Compute topological ordering of nodes in a DAG.
    Determines the correct execution/migration sequence.

    Returns ordered list of nodes and their generation (parallel level).
    """
    G = _build_graph(nodes, edges)

    if not nx.is_directed_acyclic_graph(G):
        cycles = list(nx.simple_cycles(G))[:5]
        return {"error": "Graph has cycles — topological sort requires a DAG", "cycles": cycles}

    order = list(nx.topological_sort(G))

    # Compute generations (levels for parallel execution)
    generations = list(nx.topological_generations(G))
    node_to_gen = {}
    for gen_idx, gen_nodes in enumerate(generations):
        for n in gen_nodes:
            node_to_gen[n] = gen_idx

    ordered = []
    for n in order:
        ordered.append({"id": n, "generation": node_to_gen.get(n, 0), **dict(G.nodes[n])})

    gen_summary = [{"generation": i, "nodes": list(gen), "count": len(gen)} for i, gen in enumerate(generations)]

    return {
        "order": ordered,
        "total_nodes": len(order),
        "generations": gen_summary,
        "generation_count": len(generations),
        "max_parallelism": max(len(g) for g in generations) if generations else 0,
    }


# Tool P10: graph_compute_clustering
def graph_compute_clustering(
    nodes: list[dict], edges: list[dict],
    algorithm: str = "greedy_modularity",
) -> dict:
    """Detect communities/clusters in the architecture graph.
    Useful for discovering natural domain boundaries.

    Args:
        algorithm: "greedy_modularity", "label_propagation", or "girvan_newman".
    """
    G = _build_graph(nodes, edges, directed=False)

    if algorithm == "greedy_modularity":
        communities = list(nx.community.greedy_modularity_communities(G))
    elif algorithm == "label_propagation":
        communities = list(nx.community.label_propagation_communities(G))
    elif algorithm == "girvan_newman":
        comp = nx.community.girvan_newman(G)
        communities = next(comp)  # first level split
        communities = [set(c) for c in communities]
    else:
        return {"error": f"Unknown algorithm: {algorithm}"}

    try:
        modularity = nx.community.modularity(G, communities)
    except Exception:
        modularity = 0.0

    clusters = []
    for i, comm in enumerate(communities):
        clusters.append({
            "cluster_id": i,
            "nodes": list(comm),
            "size": len(comm),
        })

    return {
        "algorithm": algorithm,
        "cluster_count": len(clusters),
        "modularity": round(modularity, 6),
        "clusters": sorted(clusters, key=lambda x: x["size"], reverse=True),
    }


# Tool P11: graph_compute_gap_analysis
def graph_compute_gap_analysis(
    baseline_nodes: list[dict], baseline_edges: list[dict],
    target_nodes: list[dict], target_edges: list[dict],
) -> dict:
    """Compute architecture gap analysis between baseline and target graphs.
    Identifies new, eliminated, and changed elements and relationships.

    This is the TOGAF gap analysis matrix, implemented as graph diff.
    """
    G_base = _build_graph(baseline_nodes, baseline_edges)
    G_target = _build_graph(target_nodes, target_edges)

    base_nodes_set = set(G_base.nodes)
    target_nodes_set = set(G_target.nodes)
    base_edges_set = set(G_base.edges)
    target_edges_set = set(G_target.edges)

    new_nodes = target_nodes_set - base_nodes_set
    eliminated_nodes = base_nodes_set - target_nodes_set
    retained_nodes = base_nodes_set & target_nodes_set

    new_edges = target_edges_set - base_edges_set
    eliminated_edges = base_edges_set - target_edges_set

    # Detect changed nodes (same ID, different attributes)
    changed_nodes = []
    for n in retained_nodes:
        base_attrs = dict(G_base.nodes[n])
        target_attrs = dict(G_target.nodes[n])
        if base_attrs != target_attrs:
            changed_nodes.append({
                "id": n,
                "baseline": base_attrs,
                "target": target_attrs,
            })

    return {
        "new_elements": [{"id": n, **dict(G_target.nodes[n])} for n in new_nodes],
        "eliminated_elements": [{"id": n, **dict(G_base.nodes[n])} for n in eliminated_nodes],
        "changed_elements": changed_nodes,
        "retained_elements": len(retained_nodes) - len(changed_nodes),
        "new_relationships": [{"source": u, "target": v} for u, v in new_edges],
        "eliminated_relationships": [{"source": u, "target": v} for u, v in eliminated_edges],
        "summary": {
            "new_count": len(new_nodes),
            "eliminated_count": len(eliminated_nodes),
            "changed_count": len(changed_nodes),
            "retained_count": len(retained_nodes) - len(changed_nodes),
            "new_edge_count": len(new_edges),
            "eliminated_edge_count": len(eliminated_edges),
        },
    }


# Tool P12: graph_compute_layer_crossing
def graph_compute_layer_crossing(
    nodes: list[dict], edges: list[dict],
    layer_key: str = "layer",
) -> dict:
    """Analyze cross-layer dependencies. In well-layered architecture,
    dependencies should flow in one direction (top → bottom).
    Back-dependencies (bottom → top) indicate architectural violations.

    Returns cross-layer edge analysis with violation detection.
    """
    G = _build_graph(nodes, edges)

    # Define standard TOGAF/ArchiMate layer order
    layer_order = {
        "strategy": 0, "motivation": 0,
        "business": 1,
        "application": 2, "data": 2,
        "technology": 3, "infrastructure": 3,
        "physical": 4,
        "implementation_migration": 5,
    }

    cross_layer = []
    violations = []
    same_layer = 0
    total_edges = G.number_of_edges()

    for u, v, data in G.edges(data=True):
        u_layer = G.nodes[u].get(layer_key, "unknown")
        v_layer = G.nodes[v].get(layer_key, "unknown")

        if u_layer == v_layer:
            same_layer += 1
            continue

        u_order = layer_order.get(u_layer, -1)
        v_order = layer_order.get(v_layer, -1)

        entry = {
            "source": u, "source_layer": u_layer,
            "target": v, "target_layer": v_layer,
            "edge_type": data.get("type", ""),
        }
        cross_layer.append(entry)

        # Violation if going from lower layer to upper layer
        if u_order > v_order and u_order >= 0 and v_order >= 0:
            violations.append(entry)

    return {
        "total_edges": total_edges,
        "same_layer_edges": same_layer,
        "cross_layer_edges": len(cross_layer),
        "violations": violations,
        "violation_count": len(violations),
        "cross_layer_ratio": round(len(cross_layer) / total_edges, 4) if total_edges > 0 else 0,
    }


# =====================================================================
# Tool definitions registry
# =====================================================================

NETWORKX_TOOL_DEFINITIONS = [
    # Retrieval tools
    {
        "id": "live_graph_get_node_info", "name": "graph_get_node_info",
        "description": "Get info about a specific node: attributes, neighbors, degrees.",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_get_node_info,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "node_id", "type": "string", "description": "Node ID", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"node_id": {"type": "string"}, "in_degree": {"type": "integer"}, "out_degree": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "node"],
    },
    {
        "id": "live_graph_find_neighbors", "name": "graph_find_neighbors",
        "description": "Find neighbors up to N hops for blast-radius / impact analysis.",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_find_neighbors,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "node_id", "type": "string", "description": "Starting node", "required": True},
            {"name": "depth", "type": "integer", "description": "Max hops (1-5)", "required": False, "default": 1},
            {"name": "direction", "type": "string", "description": "outgoing/incoming/both", "required": False, "default": "both"},
        ],
        "return_schema": {"type": "object", "properties": {"neighbors": {"type": "array"}, "count": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "neighbors", "impact"],
    },
    {
        "id": "live_graph_find_paths", "name": "graph_find_paths",
        "description": "Find all simple paths between two nodes — dependency chains and integration pathways.",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_find_paths,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "source", "type": "string", "description": "Start node", "required": True},
            {"name": "target", "type": "string", "description": "End node", "required": True},
            {"name": "max_paths", "type": "integer", "description": "Max paths to return", "required": False, "default": 5},
        ],
        "return_schema": {"type": "object", "properties": {"shortest_path": {"type": "array"}, "all_paths": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "paths", "dependency"],
    },
    {
        "id": "live_graph_get_components", "name": "graph_get_components",
        "description": "Find connected components — subsystems / architecture domains.",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_get_components,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"total_components": {"type": "integer"}, "components": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "components"],
    },
    {
        "id": "live_graph_find_cycles", "name": "graph_find_cycles",
        "description": "Detect circular dependencies — architectural anti-patterns.",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_find_cycles,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"has_cycles": {"type": "boolean"}, "cycle_count": {"type": "integer"}, "cycles": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "cycles", "antipattern"],
    },
    {
        "id": "live_graph_get_leaf_nodes", "name": "graph_get_leaf_nodes",
        "description": "Find leaf nodes — sinks (consumers) or sources (providers).",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_get_leaf_nodes,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "leaf_type", "type": "string", "description": "sink/source/isolated", "required": False, "default": "sink"},
        ],
        "return_schema": {"type": "object", "properties": {"leaves": {"type": "array"}, "count": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "leaf"],
    },
    {
        "id": "live_graph_get_bridges", "name": "graph_get_bridges",
        "description": "Find bridge edges — single points of failure in the architecture.",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_get_bridges,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"has_bridges": {"type": "boolean"}, "bridge_count": {"type": "integer"}, "bridges": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "bridge", "spof"],
    },
    {
        "id": "live_graph_get_subgraph", "name": "graph_get_subgraph",
        "description": "Extract a subgraph by filtering nodes on an attribute (layer, domain, type).",
        "tool_type": "retrieval", "domain": "archimate", "callable": graph_get_subgraph,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "filter_key", "type": "string", "description": "Attribute to filter on", "required": True},
            {"name": "filter_value", "type": "string", "description": "Required value", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"nodes": {"type": "array"}, "edges": {"type": "array"}, "node_count": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "subgraph", "filter"],
    },
    # Processing tools
    {
        "id": "live_graph_compute_centrality", "name": "graph_compute_centrality",
        "description": "Compute centrality metrics (betweenness, closeness, degree, pagerank) to find critical components.",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_centrality,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "metric", "type": "string", "description": "betweenness/closeness/degree/eigenvector/pagerank", "required": False, "default": "betweenness"},
            {"name": "top_n", "type": "integer", "description": "Top N nodes", "required": False, "default": 10},
        ],
        "return_schema": {"type": "object", "properties": {"metric": {"type": "string"}, "top_nodes": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "centrality", "critical"],
    },
    {
        "id": "live_graph_compute_coupling", "name": "graph_compute_coupling",
        "description": "Compute coupling/cohesion metrics between architecture groups (layers, domains).",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_coupling,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "group_key", "type": "string", "description": "Grouping attribute", "required": False, "default": "layer"},
        ],
        "return_schema": {"type": "object", "properties": {"groups": {"type": "array"}, "group_count": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "coupling", "cohesion"],
    },
    {
        "id": "live_graph_compute_critical_path", "name": "graph_compute_critical_path",
        "description": "Compute critical path (longest path) in a DAG — migration sequencing and bottleneck identification.",
        "tool_type": "processing", "domain": "adm", "callable": graph_compute_critical_path,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "weight_key", "type": "string", "description": "Edge weight attribute", "required": False, "default": "weight"},
        ],
        "return_schema": {"type": "object", "properties": {"critical_path": {"type": "array"}, "total_weight": {"type": "number"}}},
        "tags": ["live", "networkx", "graph", "critical_path", "roadmap"],
    },
    {
        "id": "live_graph_compute_impact_score", "name": "graph_compute_impact_score",
        "description": "Compute change impact propagation — how changes ripple through the architecture.",
        "tool_type": "processing", "domain": "adm", "callable": graph_compute_impact_score,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "changed_nodes", "type": "array", "description": "Changed node IDs", "required": True},
            {"name": "propagation_decay", "type": "number", "description": "Decay factor per hop (0-1)", "required": False, "default": 0.5},
        ],
        "return_schema": {"type": "object", "properties": {"impacted_nodes": {"type": "array"}, "impacted_count": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "impact", "change"],
    },
    {
        "id": "live_graph_compute_modularity", "name": "graph_compute_modularity",
        "description": "Compute modularity score — how well the architecture is decomposed into groups.",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_modularity,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "group_key", "type": "string", "description": "Grouping attribute", "required": False, "default": "layer"},
        ],
        "return_schema": {"type": "object", "properties": {"modularity": {"type": "number"}, "interpretation": {"type": "string"}}},
        "tags": ["live", "networkx", "graph", "modularity"],
    },
    {
        "id": "live_graph_compute_topology_metrics", "name": "graph_compute_topology_metrics",
        "description": "Compute graph topology metrics: density, diameter, clustering, DAG check.",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_topology_metrics,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"density": {"type": "number"}, "diameter": {"type": "integer"}, "is_dag": {"type": "boolean"}}},
        "tags": ["live", "networkx", "graph", "topology"],
    },
    {
        "id": "live_graph_compute_dependency_depth", "name": "graph_compute_dependency_depth",
        "description": "Compute dependency depth per node — deep chains indicate architectural smell.",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_dependency_depth,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"max_depth": {"type": "integer"}, "deepest_nodes": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "depth", "smell"],
    },
    {
        "id": "live_graph_compute_similarity", "name": "graph_compute_similarity",
        "description": "Compute structural similarity between two architecture graphs (Jaccard on nodes/edges).",
        "tool_type": "processing", "domain": "adm", "callable": graph_compute_similarity,
        "parameters": [
            {"name": "nodes_a", "type": "array", "description": "Graph A nodes", "required": True},
            {"name": "edges_a", "type": "array", "description": "Graph A edges", "required": True},
            {"name": "nodes_b", "type": "array", "description": "Graph B nodes", "required": True},
            {"name": "edges_b", "type": "array", "description": "Graph B edges", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"overall_similarity": {"type": "number"}, "only_in_a": {"type": "array"}, "only_in_b": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "similarity", "comparison"],
    },
    {
        "id": "live_graph_compute_topological_sort", "name": "graph_compute_topological_sort",
        "description": "Topological ordering of DAG — correct migration/execution sequence with parallel generations.",
        "tool_type": "processing", "domain": "adm", "callable": graph_compute_topological_sort,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"order": {"type": "array"}, "generations": {"type": "array"}, "max_parallelism": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "topological", "sequence"],
    },
    {
        "id": "live_graph_compute_clustering", "name": "graph_compute_clustering",
        "description": "Detect communities/clusters in the architecture — discover natural domain boundaries.",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_clustering,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "algorithm", "type": "string", "description": "greedy_modularity/label_propagation/girvan_newman", "required": False, "default": "greedy_modularity"},
        ],
        "return_schema": {"type": "object", "properties": {"cluster_count": {"type": "integer"}, "modularity": {"type": "number"}, "clusters": {"type": "array"}}},
        "tags": ["live", "networkx", "graph", "clustering", "community"],
    },
    {
        "id": "live_graph_compute_gap_analysis", "name": "graph_compute_gap_analysis",
        "description": "TOGAF gap analysis as graph diff — new, eliminated, changed elements between baseline and target.",
        "tool_type": "processing", "domain": "adm", "callable": graph_compute_gap_analysis,
        "parameters": [
            {"name": "baseline_nodes", "type": "array", "description": "Baseline graph nodes", "required": True},
            {"name": "baseline_edges", "type": "array", "description": "Baseline graph edges", "required": True},
            {"name": "target_nodes", "type": "array", "description": "Target graph nodes", "required": True},
            {"name": "target_edges", "type": "array", "description": "Target graph edges", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"new_elements": {"type": "array"}, "eliminated_elements": {"type": "array"}, "changed_elements": {"type": "array"}, "summary": {"type": "object"}}},
        "tags": ["live", "networkx", "graph", "gap_analysis", "togaf"],
    },
    {
        "id": "live_graph_compute_layer_crossing", "name": "graph_compute_layer_crossing",
        "description": "Analyze cross-layer dependencies — detect layering violations (bottom→top back-dependencies).",
        "tool_type": "processing", "domain": "archimate", "callable": graph_compute_layer_crossing,
        "parameters": [
            {"name": "nodes", "type": "array", "description": "Node list", "required": True},
            {"name": "edges", "type": "array", "description": "Edge list", "required": True},
            {"name": "layer_key", "type": "string", "description": "Node attribute for layer", "required": False, "default": "layer"},
        ],
        "return_schema": {"type": "object", "properties": {"cross_layer_edges": {"type": "integer"}, "violations": {"type": "array"}, "violation_count": {"type": "integer"}}},
        "tags": ["live", "networkx", "graph", "layering", "violation"],
    },
]
