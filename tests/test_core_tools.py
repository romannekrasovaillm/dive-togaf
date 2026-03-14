"""Tests for core library-based tools (NetworkX + ArchiMate parser).

No network calls required — all data is synthetic.
Tests validate correctness, consistency, and JSON serializability.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pools.live_tools.networkx_tools import (
    graph_get_node_info, graph_find_neighbors, graph_find_paths,
    graph_get_components, graph_find_cycles, graph_get_leaf_nodes,
    graph_get_bridges, graph_get_subgraph,
    graph_compute_centrality, graph_compute_coupling,
    graph_compute_critical_path, graph_compute_impact_score,
    graph_compute_modularity, graph_compute_topology_metrics,
    graph_compute_dependency_depth, graph_compute_similarity,
    graph_compute_topological_sort, graph_compute_clustering,
    graph_compute_gap_analysis, graph_compute_layer_crossing,
    NETWORKX_TOOL_DEFINITIONS,
)
from src.pools.live_tools.archimate_parser_tools import (
    archimate_parse_model_info, archimate_list_elements,
    archimate_list_relationships, archimate_get_element_relationships,
    archimate_list_views, archimate_get_properties,
    archimate_compute_model_metrics, archimate_compute_element_usage,
    archimate_validate_relationships, archimate_extract_to_graph,
    ARCHIMATE_PARSER_TOOL_DEFINITIONS,
)


# =====================================================================
# Test fixtures
# =====================================================================

# Architecture graph: banking domain
BANKING_NODES = [
    {"id": "loan_svc", "type": "ApplicationService", "layer": "application", "name": "Loan Service"},
    {"id": "payment_svc", "type": "ApplicationService", "layer": "application", "name": "Payment Service"},
    {"id": "core_banking", "type": "ApplicationComponent", "layer": "application", "name": "Core Banking"},
    {"id": "loan_db", "type": "DataObject", "layer": "application", "name": "Loan Database"},
    {"id": "api_gateway", "type": "TechnologyService", "layer": "technology", "name": "API Gateway"},
    {"id": "k8s_cluster", "type": "Node", "layer": "technology", "name": "Kubernetes Cluster"},
    {"id": "loan_process", "type": "BusinessProcess", "layer": "business", "name": "Loan Origination"},
    {"id": "customer_onboard", "type": "BusinessProcess", "layer": "business", "name": "Customer Onboarding"},
    {"id": "credit_check", "type": "BusinessFunction", "layer": "business", "name": "Credit Check"},
]

BANKING_EDGES = [
    {"source": "loan_process", "target": "loan_svc", "type": "serving"},
    {"source": "customer_onboard", "target": "core_banking", "type": "serving"},
    {"source": "loan_svc", "target": "core_banking", "type": "flow"},
    {"source": "payment_svc", "target": "core_banking", "type": "flow"},
    {"source": "core_banking", "target": "loan_db", "type": "access"},
    {"source": "core_banking", "target": "api_gateway", "type": "serving"},
    {"source": "api_gateway", "target": "k8s_cluster", "type": "serving"},
    {"source": "loan_process", "target": "credit_check", "type": "triggering"},
    {"source": "credit_check", "target": "loan_svc", "type": "serving"},
]

# DAG for critical path / topological sort
DAG_NODES = [
    {"id": "wave1_sox", "type": "WorkPackage", "name": "SOX Remediation", "layer": "implementation"},
    {"id": "wave2_api", "type": "WorkPackage", "name": "API Gateway Deploy", "layer": "implementation"},
    {"id": "wave2_cloud", "type": "WorkPackage", "name": "Cloud LOS Deploy", "layer": "implementation"},
    {"id": "wave3_decom", "type": "WorkPackage", "name": "Legacy Decommission", "layer": "implementation"},
    {"id": "wave3_cutover", "type": "WorkPackage", "name": "Production Cutover", "layer": "implementation"},
]

DAG_EDGES = [
    {"source": "wave1_sox", "target": "wave2_api", "type": "triggering", "weight": 3},
    {"source": "wave1_sox", "target": "wave2_cloud", "type": "triggering", "weight": 3},
    {"source": "wave2_api", "target": "wave3_decom", "type": "triggering", "weight": 4},
    {"source": "wave2_cloud", "target": "wave3_decom", "type": "triggering", "weight": 6},
    {"source": "wave3_decom", "target": "wave3_cutover", "type": "triggering", "weight": 2},
]

# ArchiMate sample XML
ARCHIMATE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       identifier="model-1" name="Banking Architecture">
  <name>Banking Architecture Model</name>
  <documentation>Sample banking architecture for testing</documentation>
  <elements>
    <element identifier="e1" xsi:type="BusinessProcess">
      <name>Loan Origination</name>
    </element>
    <element identifier="e2" xsi:type="BusinessService">
      <name>Lending Service</name>
    </element>
    <element identifier="e3" xsi:type="ApplicationComponent">
      <name>Core Banking System</name>
    </element>
    <element identifier="e4" xsi:type="ApplicationComponent">
      <name>Loan Module</name>
    </element>
    <element identifier="e5" xsi:type="DataObject">
      <name>Customer Data</name>
    </element>
    <element identifier="e6" xsi:type="TechnologyService">
      <name>API Gateway</name>
    </element>
    <element identifier="e7" xsi:type="Node">
      <name>Cloud Platform</name>
    </element>
    <element identifier="e8" xsi:type="Stakeholder">
      <name>CTO</name>
    </element>
    <element identifier="e9" xsi:type="Goal">
      <name>Reduce Technical Debt</name>
    </element>
  </elements>
  <relationships>
    <relationship identifier="r1" xsi:type="Realization" source="e2" target="e1"/>
    <relationship identifier="r2" xsi:type="Serving" source="e3" target="e2"/>
    <relationship identifier="r3" xsi:type="Composition" source="e3" target="e4"/>
    <relationship identifier="r4" xsi:type="Access" source="e4" target="e5"/>
    <relationship identifier="r5" xsi:type="Serving" source="e6" target="e3"/>
    <relationship identifier="r6" xsi:type="Serving" source="e7" target="e6"/>
    <relationship identifier="r7" xsi:type="Association" source="e8" target="e9"/>
  </relationships>
  <views>
    <view identifier="v1" xsi:type="Diagram">
      <name>Application Landscape</name>
      <node identifier="n1" elementRef="e3"/>
      <node identifier="n2" elementRef="e4"/>
      <node identifier="n3" elementRef="e6"/>
    </view>
  </views>
</model>
"""


# =====================================================================
# NetworkX Retrieval Tests
# =====================================================================

def test_graph_get_node_info():
    r = graph_get_node_info(BANKING_NODES, BANKING_EDGES, "core_banking")
    assert r["node_id"] == "core_banking"
    assert r["in_degree"] >= 2
    assert r["out_degree"] >= 2
    assert len(r["predecessors"]) > 0
    assert len(r["successors"]) > 0
    print(f"  PASS: core_banking — in:{r['in_degree']} out:{r['out_degree']} pred:{len(r['predecessors'])} succ:{len(r['successors'])}")


def test_graph_find_neighbors():
    r = graph_find_neighbors(BANKING_NODES, BANKING_EDGES, "core_banking", depth=2, direction="both")
    assert r["count"] > 3
    print(f"  PASS: core_banking 2-hop neighbors: {r['count']} ({[n['id'] for n in r['neighbors']]})")


def test_graph_find_paths():
    r = graph_find_paths(BANKING_NODES, BANKING_EDGES, "loan_process", "k8s_cluster")
    assert r["shortest_path"] is not None
    assert r["path_count"] >= 1
    print(f"  PASS: loan_process→k8s_cluster: shortest={r['shortest_path']}, total paths={r['path_count']}")


def test_graph_get_components():
    r = graph_get_components(BANKING_NODES, BANKING_EDGES)
    assert r["total_components"] >= 1
    print(f"  PASS: {r['total_components']} components, connected={r['is_connected']}")


def test_graph_find_cycles():
    r = graph_find_cycles(BANKING_NODES, BANKING_EDGES)
    print(f"  PASS: has_cycles={r['has_cycles']}, cycle_count={r['cycle_count']}")


def test_graph_get_leaf_nodes():
    r = graph_get_leaf_nodes(BANKING_NODES, BANKING_EDGES, "sink")
    assert r["count"] > 0
    print(f"  PASS: {r['count']} sinks: {[n['id'] for n in r['leaves']]}")


def test_graph_get_bridges():
    r = graph_get_bridges(BANKING_NODES, BANKING_EDGES)
    print(f"  PASS: has_bridges={r['has_bridges']}, count={r['bridge_count']}")


def test_graph_get_subgraph():
    r = graph_get_subgraph(BANKING_NODES, BANKING_EDGES, "layer", "application")
    assert r["node_count"] >= 3
    print(f"  PASS: application layer subgraph: {r['node_count']} nodes, {r['edge_count']} edges")


# =====================================================================
# NetworkX Processing Tests
# =====================================================================

def test_graph_compute_centrality():
    r = graph_compute_centrality(BANKING_NODES, BANKING_EDGES, "betweenness", top_n=3)
    assert r["count"] > 0
    top = r["top_nodes"][0]
    print(f"  PASS: Top betweenness: {top['id']} (score={top['score']})")


def test_graph_compute_coupling():
    r = graph_compute_coupling(BANKING_NODES, BANKING_EDGES, "layer")
    assert r["group_count"] >= 2
    for g in r["groups"]:
        assert "instability" in g
    print(f"  PASS: {r['group_count']} groups — {[(g['group'], g['instability']) for g in r['groups']]}")


def test_graph_compute_critical_path():
    r = graph_compute_critical_path(DAG_NODES, DAG_EDGES)
    assert "critical_path" in r
    assert r["total_weight"] > 0
    path_ids = [n["id"] for n in r["critical_path"]]
    print(f"  PASS: Critical path: {path_ids}, weight={r['total_weight']}")


def test_graph_compute_impact_score():
    r = graph_compute_impact_score(BANKING_NODES, BANKING_EDGES, ["core_banking"])
    assert r["impacted_count"] > 0
    top = r["impacted_nodes"][0]
    print(f"  PASS: Change core_banking impacts {r['impacted_count']} nodes, top: {top['id']} (score={top['impact_score']})")


def test_graph_compute_modularity():
    r = graph_compute_modularity(BANKING_NODES, BANKING_EDGES, "layer")
    assert "modularity" in r
    print(f"  PASS: Modularity={r['modularity']} ({r['interpretation']})")


def test_graph_compute_topology_metrics():
    r = graph_compute_topology_metrics(BANKING_NODES, BANKING_EDGES)
    assert r["node_count"] == 9
    assert r["edge_count"] == 9
    print(f"  PASS: density={r['density']}, diameter={r['diameter']}, DAG={r['is_dag']}, clustering={r['avg_clustering']}")


def test_graph_compute_dependency_depth():
    r = graph_compute_dependency_depth(DAG_NODES, DAG_EDGES)
    assert r["max_depth"] > 0
    print(f"  PASS: max_depth={r['max_depth']}, sources={r['source_count']}")


def test_graph_compute_similarity():
    # Compare banking graph to itself minus one node
    nodes_b = [n for n in BANKING_NODES if n["id"] != "credit_check"]
    edges_b = [e for e in BANKING_EDGES if e["source"] != "credit_check" and e["target"] != "credit_check"]
    r = graph_compute_similarity(BANKING_NODES, BANKING_EDGES, nodes_b, edges_b)
    assert 0 < r["overall_similarity"] < 1
    assert "credit_check" in r["only_in_a"]
    print(f"  PASS: Similarity={r['overall_similarity']}, only_in_a={r['only_in_a']}")


def test_graph_compute_topological_sort():
    r = graph_compute_topological_sort(DAG_NODES, DAG_EDGES)
    assert r["total_nodes"] == 5
    assert r["generation_count"] >= 2
    print(f"  PASS: {r['generation_count']} generations, max_parallelism={r['max_parallelism']}")


def test_graph_compute_clustering():
    r = graph_compute_clustering(BANKING_NODES, BANKING_EDGES)
    assert r["cluster_count"] >= 1
    print(f"  PASS: {r['cluster_count']} clusters, modularity={r['modularity']}")


def test_graph_compute_gap_analysis():
    target_nodes = BANKING_NODES + [{"id": "fraud_svc", "type": "ApplicationService", "layer": "application", "name": "Fraud Detection"}]
    target_edges = BANKING_EDGES + [{"source": "core_banking", "target": "fraud_svc", "type": "flow"}]
    # Remove loan_db from target
    target_nodes = [n for n in target_nodes if n["id"] != "loan_db"]
    target_edges = [e for e in target_edges if e["source"] != "loan_db" and e["target"] != "loan_db"]

    r = graph_compute_gap_analysis(BANKING_NODES, BANKING_EDGES, target_nodes, target_edges)
    assert r["summary"]["new_count"] >= 1
    assert r["summary"]["eliminated_count"] >= 1
    print(f"  PASS: Gap analysis — new:{r['summary']['new_count']} elim:{r['summary']['eliminated_count']} changed:{r['summary']['changed_count']}")


def test_graph_compute_layer_crossing():
    r = graph_compute_layer_crossing(BANKING_NODES, BANKING_EDGES)
    assert r["total_edges"] == 9
    assert r["cross_layer_edges"] >= 2
    print(f"  PASS: {r['cross_layer_edges']} cross-layer, {r['violation_count']} violations, ratio={r['cross_layer_ratio']}")


# =====================================================================
# ArchiMate Parser Tests
# =====================================================================

def test_archimate_parse_model_info():
    r = archimate_parse_model_info(ARCHIMATE_XML)
    assert r["element_count"] == 9
    assert r["relationship_count"] == 7
    assert r["view_count"] >= 1
    print(f"  PASS: Model '{r['model_name']}': {r['element_count']} elems, {r['relationship_count']} rels, {r['view_count']} views")


def test_archimate_list_elements():
    r = archimate_list_elements(ARCHIMATE_XML)
    assert r["count"] == 9
    r_app = archimate_list_elements(ARCHIMATE_XML, layer="application")
    assert r_app["count"] >= 2
    print(f"  PASS: {r['count']} total elements, {r_app['count']} application layer")


def test_archimate_list_relationships():
    r = archimate_list_relationships(ARCHIMATE_XML)
    assert r["count"] == 7
    r_serving = archimate_list_relationships(ARCHIMATE_XML, relationship_type="Serving")
    assert r_serving["count"] >= 2
    print(f"  PASS: {r['count']} total rels, {r_serving['count']} Serving type")


def test_archimate_get_element_relationships():
    r = archimate_get_element_relationships(ARCHIMATE_XML, "e3")
    assert r["incoming_count"] >= 1
    assert r["outgoing_count"] >= 1
    print(f"  PASS: Element e3: {r['incoming_count']} incoming, {r['outgoing_count']} outgoing")


def test_archimate_list_views():
    r = archimate_list_views(ARCHIMATE_XML)
    assert r["count"] >= 1
    print(f"  PASS: {r['count']} views: {[v.get('name', '?') for v in r['views']]}")


def test_archimate_get_properties():
    r = archimate_get_properties(ARCHIMATE_XML)
    assert isinstance(r, dict)
    print(f"  PASS: {r.get('count', 0)} property definitions")


def test_archimate_compute_model_metrics():
    r = archimate_compute_model_metrics(ARCHIMATE_XML)
    assert r["element_count"] == 9
    assert r["density"] > 0
    assert len(r["layers_used"]) >= 3
    print(f"  PASS: density={r['density']}, layers={r['layers_used']}, diversity={r['type_diversity']}")


def test_archimate_compute_element_usage():
    r = archimate_compute_element_usage(ARCHIMATE_XML)
    assert r["total_elements"] == 9
    assert r["hub_count"] >= 0
    top = r["elements"][0]
    print(f"  PASS: Top used: {top['name']} (total={top['total']}), {r['orphan_count']} orphans")


def test_archimate_validate_relationships():
    r = archimate_validate_relationships(ARCHIMATE_XML)
    assert r["is_valid"] is True
    assert r["dangling_count"] == 0
    print(f"  PASS: Valid model, {r['valid_count']}/{r['total_relationships']} valid rels")


def test_archimate_extract_to_graph():
    r = archimate_extract_to_graph(ARCHIMATE_XML)
    assert r["node_count"] == 9
    assert r["edge_count"] == 7
    layers = {n["layer"] for n in r["nodes"]}
    assert len(layers) >= 3
    print(f"  PASS: Extracted {r['node_count']} nodes, {r['edge_count']} edges, layers={layers}")


# =====================================================================
# Integration: ArchiMate → NetworkX pipeline
# =====================================================================

def test_archimate_to_networkx_pipeline():
    """Test the bridge: parse ArchiMate → extract graph → analyze with NetworkX."""
    graph = archimate_extract_to_graph(ARCHIMATE_XML)
    nodes = graph["nodes"]
    edges = graph["edges"]

    topo = graph_compute_topology_metrics(nodes, edges)
    assert topo["node_count"] == 9

    centrality = graph_compute_centrality(nodes, edges, "betweenness", top_n=3)
    assert centrality["count"] > 0

    coupling = graph_compute_coupling(nodes, edges, "layer")
    assert coupling["group_count"] >= 3

    print(f"  PASS: Pipeline OK — topo:{topo['node_count']}n, top_central:{centrality['top_nodes'][0]['id']}, {coupling['group_count']} layer groups")


# =====================================================================
# Structural validation
# =====================================================================

def test_tool_definitions_count():
    nx_count = len(NETWORKX_TOOL_DEFINITIONS)
    am_count = len(ARCHIMATE_PARSER_TOOL_DEFINITIONS)
    assert nx_count == 20, f"Expected 20 NetworkX tools, got {nx_count}"
    assert am_count == 10, f"Expected 10 ArchiMate tools, got {am_count}"
    print(f"  PASS: {nx_count} NetworkX + {am_count} ArchiMate = {nx_count + am_count} tools")


def test_tool_definitions_structure():
    all_defs = NETWORKX_TOOL_DEFINITIONS + ARCHIMATE_PARSER_TOOL_DEFINITIONS
    for defn in all_defs:
        assert "id" in defn and defn["id"].startswith("live_")
        assert "callable" in defn and callable(defn["callable"])
        assert "tool_type" in defn and defn["tool_type"] in ("retrieval", "processing")
        assert "live" in defn["tags"]
    print(f"  PASS: All {len(all_defs)} tool definitions valid")


def test_tool_ids_unique():
    all_defs = NETWORKX_TOOL_DEFINITIONS + ARCHIMATE_PARSER_TOOL_DEFINITIONS
    ids = [d["id"] for d in all_defs]
    assert len(ids) == len(set(ids))
    print(f"  PASS: All {len(ids)} IDs unique")


def test_all_results_serializable():
    """All tool outputs must be JSON-serializable."""
    results = [
        graph_get_node_info(BANKING_NODES, BANKING_EDGES, "core_banking"),
        graph_compute_centrality(BANKING_NODES, BANKING_EDGES),
        graph_compute_gap_analysis(BANKING_NODES, BANKING_EDGES, DAG_NODES, DAG_EDGES),
        archimate_parse_model_info(ARCHIMATE_XML),
        archimate_extract_to_graph(ARCHIMATE_XML),
        archimate_compute_model_metrics(ARCHIMATE_XML),
    ]
    for r in results:
        json.dumps(r, ensure_ascii=False)
    print(f"  PASS: All {len(results)} sample results JSON-serializable")


def test_networkx_tool_type_distribution():
    retrieval = [d for d in NETWORKX_TOOL_DEFINITIONS if d["tool_type"] == "retrieval"]
    processing = [d for d in NETWORKX_TOOL_DEFINITIONS if d["tool_type"] == "processing"]
    assert len(retrieval) == 8
    assert len(processing) == 12
    print(f"  PASS: NetworkX tools — {len(retrieval)} retrieval + {len(processing)} processing")


def test_archimate_tool_type_distribution():
    retrieval = [d for d in ARCHIMATE_PARSER_TOOL_DEFINITIONS if d["tool_type"] == "retrieval"]
    processing = [d for d in ARCHIMATE_PARSER_TOOL_DEFINITIONS if d["tool_type"] == "processing"]
    assert len(retrieval) == 6
    assert len(processing) == 4
    print(f"  PASS: ArchiMate tools — {len(retrieval)} retrieval + {len(processing)} processing")


def run_all_tests():
    tests = [
        # NetworkX retrieval
        test_graph_get_node_info, test_graph_find_neighbors, test_graph_find_paths,
        test_graph_get_components, test_graph_find_cycles, test_graph_get_leaf_nodes,
        test_graph_get_bridges, test_graph_get_subgraph,
        # NetworkX processing
        test_graph_compute_centrality, test_graph_compute_coupling,
        test_graph_compute_critical_path, test_graph_compute_impact_score,
        test_graph_compute_modularity, test_graph_compute_topology_metrics,
        test_graph_compute_dependency_depth, test_graph_compute_similarity,
        test_graph_compute_topological_sort, test_graph_compute_clustering,
        test_graph_compute_gap_analysis, test_graph_compute_layer_crossing,
        # ArchiMate parser
        test_archimate_parse_model_info, test_archimate_list_elements,
        test_archimate_list_relationships, test_archimate_get_element_relationships,
        test_archimate_list_views, test_archimate_get_properties,
        test_archimate_compute_model_metrics, test_archimate_compute_element_usage,
        test_archimate_validate_relationships, test_archimate_extract_to_graph,
        # Integration
        test_archimate_to_networkx_pipeline,
        # Structural
        test_tool_definitions_count, test_tool_definitions_structure,
        test_tool_ids_unique, test_all_results_serializable,
        test_networkx_tool_type_distribution, test_archimate_tool_type_distribution,
    ]

    print("=" * 60)
    print("DIVE-TOGAF Core Library Tool Tests")
    print("=" * 60)

    passed = 0
    failed = 0
    for test in tests:
        try:
            print(f"\n{test.__name__}:")
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
