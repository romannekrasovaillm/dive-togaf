"""ArchiMate Open Exchange Format parser tools built on lxml.

Wraps lxml into TOGAF-domain tools for parsing, querying, and analyzing
ArchiMate models in the standard Open Exchange Format (.xml).
Analogous to how DIVE wraps NCBI Entrez into retrieval tools.

The ArchiMate Model Exchange File Format is the standard interchange
format defined by The Open Group (Technical Standard C13).

One library → many tools, each a focused query on the parsed model.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from lxml import etree


# ArchiMate 3.x namespace
ARCHIMATE_NS = {
    "am": "http://www.opengroup.org/xsd/archimate/3.0/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# Fallback for models without explicit namespace
ARCHIMATE_NS_ALT = {
    "am": "http://www.opengroup.org/xsd/archimate",
}


def _parse_model(xml_content: str) -> tuple[etree._Element, dict]:
    """Parse ArchiMate XML and detect namespace."""
    root = etree.fromstring(xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content)

    # Detect namespace from root tag
    ns = ARCHIMATE_NS.copy()
    root_ns = etree.QName(root).namespace
    if root_ns and "3.0" not in root_ns:
        ns["am"] = root_ns

    return root, ns


def _elem_to_dict(elem: etree._Element, ns: dict) -> dict:
    """Convert an ArchiMate XML element to a dict."""
    result = dict(elem.attrib)

    # Get name from child element or attribute
    name_elem = elem.find("am:name", ns)
    if name_elem is not None and name_elem.text:
        result["name"] = name_elem.text
    elif "name" not in result:
        name_elem_no_ns = elem.find("name")
        if name_elem_no_ns is not None and name_elem_no_ns.text:
            result["name"] = name_elem_no_ns.text

    # Get documentation
    doc_elem = elem.find("am:documentation", ns)
    if doc_elem is not None and doc_elem.text:
        result["documentation"] = doc_elem.text[:500]

    # Get xsi:type
    xsi_type = elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
    if xsi_type:
        result["type"] = xsi_type

    return result


# =====================================================================
# RETRIEVAL TOOLS
# =====================================================================

# Tool R1: archimate_parse_model_info
def archimate_parse_model_info(xml_content: str) -> dict:
    """Parse an ArchiMate exchange file and return model metadata:
    name, documentation, element count, relationship count.

    Args:
        xml_content: ArchiMate Open Exchange Format XML string.

    Returns:
        Model metadata summary.
    """
    root, ns = _parse_model(xml_content)

    name_elem = root.find("am:name", ns)
    model_name = name_elem.text if name_elem is not None else root.get("name", "")

    doc_elem = root.find("am:documentation", ns)
    documentation = doc_elem.text[:500] if doc_elem is not None and doc_elem.text else ""

    # Count elements
    elements = root.findall(".//am:element", ns)
    if not elements:
        elements = root.findall(".//{%s}element" % ns.get("am", ""))

    # Count relationships
    relationships = root.findall(".//am:relationship", ns)
    if not relationships:
        relationships = root.findall(".//{%s}relationship" % ns.get("am", ""))

    # Count views
    views = root.findall(".//am:view", ns) or root.findall(".//am:diagram", ns)

    # Element type breakdown
    type_counts: dict[str, int] = {}
    for elem in elements:
        etype = elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", elem.get("type", "unknown"))
        type_counts[etype] = type_counts.get(etype, 0) + 1

    return {
        "model_name": model_name,
        "documentation": documentation,
        "element_count": len(elements),
        "relationship_count": len(relationships),
        "view_count": len(views),
        "element_types": type_counts,
        "identifier": root.get("identifier", ""),
    }


# Tool R2: archimate_list_elements
def archimate_list_elements(
    xml_content: str,
    element_type: str | None = None,
    layer: str | None = None,
) -> dict:
    """List all elements in the model, optionally filtered by type or layer.

    Args:
        xml_content: ArchiMate XML string.
        element_type: Filter by ArchiMate type (e.g. "BusinessProcess", "ApplicationComponent").
        layer: Filter by layer (business, application, technology, motivation, strategy).

    Returns:
        List of elements with id, name, type.
    """
    root, ns = _parse_model(xml_content)

    # Layer to type prefix mapping
    layer_prefixes = {
        "business": ["Business"],
        "application": ["Application", "Data"],
        "technology": ["Technology", "Node", "Device", "SystemSoftware", "Artifact", "Path", "CommunicationNetwork"],
        "motivation": ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle", "Requirement", "Constraint", "Meaning", "Value"],
        "strategy": ["Resource", "Capability", "ValueStream", "CourseOfAction"],
        "implementation": ["WorkPackage", "Deliverable", "ImplementationEvent", "Plateau", "Gap"],
        "physical": ["Equipment", "Facility", "DistributionNetwork", "Material"],
    }

    elements = root.findall(".//am:element", ns)
    if not elements:
        elements = [e for e in root.iter() if "element" in e.tag.lower() and e.get("identifier")]

    result = []
    for elem in elements:
        info = _elem_to_dict(elem, ns)
        etype = info.get("type", "")

        # Apply type filter
        if element_type and element_type.lower() not in etype.lower():
            continue

        # Apply layer filter
        if layer and layer.lower() in layer_prefixes:
            prefixes = layer_prefixes[layer.lower()]
            if not any(etype.startswith(p) or p.lower() in etype.lower() for p in prefixes):
                continue

        result.append(info)

    return {
        "elements": result,
        "count": len(result),
        "filter": {"element_type": element_type, "layer": layer},
    }


# Tool R3: archimate_list_relationships
def archimate_list_relationships(
    xml_content: str,
    relationship_type: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
) -> dict:
    """List all relationships, optionally filtered by type, source, or target.

    Args:
        xml_content: ArchiMate XML string.
        relationship_type: Filter by type (e.g. "Serving", "Composition", "Flow").
        source_id: Filter by source element identifier.
        target_id: Filter by target element identifier.

    Returns:
        List of relationships with source, target, type.
    """
    root, ns = _parse_model(xml_content)

    relationships = root.findall(".//am:relationship", ns)
    if not relationships:
        relationships = [e for e in root.iter() if "relationship" in e.tag.lower() and e.get("identifier")]

    result = []
    for rel in relationships:
        info = _elem_to_dict(rel, ns)

        rtype = info.get("type", "")
        src = info.get("source", "")
        tgt = info.get("target", "")

        if relationship_type and relationship_type.lower() not in rtype.lower():
            continue
        if source_id and src != source_id:
            continue
        if target_id and tgt != target_id:
            continue

        result.append(info)

    return {
        "relationships": result,
        "count": len(result),
        "filter": {"relationship_type": relationship_type, "source_id": source_id, "target_id": target_id},
    }


# Tool R4: archimate_get_element_relationships
def archimate_get_element_relationships(
    xml_content: str,
    element_id: str,
) -> dict:
    """Get all relationships involving a specific element (as source or target).

    Args:
        xml_content: ArchiMate XML string.
        element_id: Element identifier to search for.

    Returns:
        Incoming and outgoing relationships for the element.
    """
    root, ns = _parse_model(xml_content)

    # Find the element
    all_elements = root.findall(".//am:element", ns)
    element_info = None
    for elem in all_elements:
        eid = elem.get("identifier", "")
        if eid == element_id:
            element_info = _elem_to_dict(elem, ns)
            break

    relationships = root.findall(".//am:relationship", ns)
    if not relationships:
        relationships = [e for e in root.iter() if "relationship" in e.tag.lower()]

    incoming = []
    outgoing = []
    for rel in relationships:
        info = _elem_to_dict(rel, ns)
        if info.get("source") == element_id:
            outgoing.append(info)
        elif info.get("target") == element_id:
            incoming.append(info)

    return {
        "element_id": element_id,
        "element": element_info,
        "incoming": incoming,
        "outgoing": outgoing,
        "incoming_count": len(incoming),
        "outgoing_count": len(outgoing),
    }


# Tool R5: archimate_list_views
def archimate_list_views(xml_content: str) -> dict:
    """List all views (diagrams) defined in the model.

    Args:
        xml_content: ArchiMate XML string.

    Returns:
        List of views with name, type, viewpoint, and element count.
    """
    root, ns = _parse_model(xml_content)

    views = root.findall(".//am:view", ns)
    if not views:
        views = root.findall(".//am:diagram", ns)
    if not views:
        views = [e for e in root.iter() if "view" in e.tag.lower() or "diagram" in e.tag.lower()]

    result = []
    for view in views:
        info = _elem_to_dict(view, ns)
        # Count nodes in view
        view_nodes = view.findall(".//am:node", ns)
        if not view_nodes:
            view_nodes = [e for e in view.iter() if "node" in e.tag.lower()]

        info["node_count"] = len(view_nodes)
        result.append(info)

    return {
        "views": result,
        "count": len(result),
    }


# Tool R6: archimate_get_properties
def archimate_get_properties(
    xml_content: str,
    element_id: str | None = None,
) -> dict:
    """Get custom properties defined on model elements.

    Args:
        xml_content: ArchiMate XML string.
        element_id: If specified, get properties for this element only.

    Returns:
        Properties with key-value pairs.
    """
    root, ns = _parse_model(xml_content)

    if element_id:
        # Find specific element
        all_elements = root.findall(".//am:element", ns)
        for elem in all_elements:
            if elem.get("identifier") == element_id:
                props = elem.findall("am:property", ns)
                if not props:
                    props = elem.findall("am:properties/am:property", ns)

                result = []
                for p in props:
                    key = p.get("propertyDefinitionRef", p.get("key", ""))
                    val_elem = p.find("am:value", ns)
                    val = val_elem.text if val_elem is not None else p.get("value", "")
                    result.append({"key": key, "value": val})

                return {"element_id": element_id, "properties": result, "count": len(result)}

        return {"element_id": element_id, "properties": [], "count": 0, "error": "Element not found"}

    # Get property definitions
    prop_defs = root.findall(".//am:propertyDefinition", ns) or root.findall(".//am:propertydef", ns)
    definitions = []
    for pd in prop_defs:
        name_elem = pd.find("am:name", ns)
        definitions.append({
            "identifier": pd.get("identifier", ""),
            "name": name_elem.text if name_elem is not None else pd.get("name", ""),
            "type": pd.get("type", "string"),
        })

    return {
        "property_definitions": definitions,
        "count": len(definitions),
    }


# =====================================================================
# PROCESSING TOOLS
# =====================================================================

# Tool P1: archimate_compute_model_metrics
def archimate_compute_model_metrics(xml_content: str) -> dict:
    """Compute metrics for an ArchiMate model:
    complexity, element type distribution, relationship density, layer coverage.

    Args:
        xml_content: ArchiMate XML string.

    Returns:
        Comprehensive model metrics.
    """
    root, ns = _parse_model(xml_content)

    elements = root.findall(".//am:element", ns)
    relationships = root.findall(".//am:relationship", ns)

    n_elem = len(elements)
    n_rel = len(relationships)

    # Type distribution
    type_dist: dict[str, int] = {}
    for elem in elements:
        etype = elem.get("{http://www.w3.org/2001/XMLSchema-instance}type", elem.get("type", "unknown"))
        type_dist[etype] = type_dist.get(etype, 0) + 1

    # Relationship type distribution
    rel_dist: dict[str, int] = {}
    for rel in relationships:
        rtype = rel.get("{http://www.w3.org/2001/XMLSchema-instance}type", rel.get("type", "unknown"))
        rel_dist[rtype] = rel_dist.get(rtype, 0) + 1

    # Layer coverage
    layer_map = {
        "Business": "business", "Application": "application", "Data": "application",
        "Technology": "technology", "Node": "technology", "Device": "technology",
        "Motivation": "motivation", "Strategy": "strategy",
        "Implementation": "implementation", "Physical": "physical",
    }
    layers_used: set[str] = set()
    for etype in type_dist:
        for prefix, layer in layer_map.items():
            if prefix.lower() in etype.lower():
                layers_used.add(layer)
                break

    density = n_rel / (n_elem * (n_elem - 1)) if n_elem > 1 else 0
    type_diversity = len(type_dist)

    return {
        "element_count": n_elem,
        "relationship_count": n_rel,
        "density": round(density, 6),
        "type_diversity": type_diversity,
        "element_type_distribution": type_dist,
        "relationship_type_distribution": rel_dist,
        "layers_used": sorted(layers_used),
        "layer_coverage": len(layers_used),
        "avg_relationships_per_element": round(n_rel / n_elem, 2) if n_elem > 0 else 0,
    }


# Tool P2: archimate_compute_element_usage
def archimate_compute_element_usage(xml_content: str) -> dict:
    """Compute element usage statistics — how many relationships
    each element participates in. Identifies over-connected hubs
    and unused orphan elements.

    Returns:
        Ranked list of elements by usage (relationship count).
    """
    root, ns = _parse_model(xml_content)

    elements = root.findall(".//am:element", ns)
    relationships = root.findall(".//am:relationship", ns)

    # Build usage map
    usage: dict[str, dict] = {}
    for elem in elements:
        eid = elem.get("identifier", "")
        info = _elem_to_dict(elem, ns)
        usage[eid] = {"id": eid, "name": info.get("name", ""), "type": info.get("type", ""),
                      "as_source": 0, "as_target": 0, "total": 0}

    for rel in relationships:
        src = rel.get("source", "")
        tgt = rel.get("target", "")
        if src in usage:
            usage[src]["as_source"] += 1
            usage[src]["total"] += 1
        if tgt in usage:
            usage[tgt]["as_target"] += 1
            usage[tgt]["total"] += 1

    ranked = sorted(usage.values(), key=lambda x: x["total"], reverse=True)

    orphans = [e for e in ranked if e["total"] == 0]
    hubs = [e for e in ranked if e["total"] >= 5]

    return {
        "elements": ranked[:20],
        "total_elements": len(ranked),
        "orphan_count": len(orphans),
        "orphans": orphans[:10],
        "hub_count": len(hubs),
        "hubs": hubs[:10],
    }


# Tool P3: archimate_validate_relationships
def archimate_validate_relationships(xml_content: str) -> dict:
    """Validate that relationships reference existing elements.
    Finds dangling references (source or target not found).

    Returns:
        Validation results with dangling references.
    """
    root, ns = _parse_model(xml_content)

    elements = root.findall(".//am:element", ns)
    relationships = root.findall(".//am:relationship", ns)

    element_ids = {elem.get("identifier", "") for elem in elements}

    dangling = []
    valid_count = 0

    for rel in relationships:
        src = rel.get("source", "")
        tgt = rel.get("target", "")
        info = _elem_to_dict(rel, ns)

        issues = []
        if src and src not in element_ids:
            issues.append(f"source '{src}' not found")
        if tgt and tgt not in element_ids:
            issues.append(f"target '{tgt}' not found")

        if issues:
            dangling.append({**info, "issues": issues})
        else:
            valid_count += 1

    return {
        "total_relationships": len(relationships),
        "valid_count": valid_count,
        "dangling_count": len(dangling),
        "dangling_references": dangling[:20],
        "is_valid": len(dangling) == 0,
    }


# Tool P4: archimate_extract_to_graph
def archimate_extract_to_graph(xml_content: str) -> dict:
    """Extract an ArchiMate model into a graph format (nodes + edges)
    compatible with the NetworkX graph analysis tools.

    This is the bridge between ArchiMate parser and graph analysis.

    Returns:
        Nodes and edges lists ready for NetworkX tools.
    """
    root, ns = _parse_model(xml_content)

    elements = root.findall(".//am:element", ns)
    relationships = root.findall(".//am:relationship", ns)

    # Detect layer from type
    def _detect_layer(etype: str) -> str:
        etype_lower = etype.lower()
        if "business" in etype_lower:
            return "business"
        if "application" in etype_lower or "data" in etype_lower:
            return "application"
        if any(x in etype_lower for x in ["technology", "node", "device", "system", "artifact", "path", "communication"]):
            return "technology"
        if any(x in etype_lower for x in ["motivation", "stakeholder", "driver", "goal", "principle", "requirement"]):
            return "motivation"
        if any(x in etype_lower for x in ["strategy", "capability", "resource", "valuestream", "courseofaction"]):
            return "strategy"
        if any(x in etype_lower for x in ["work", "deliverable", "plateau", "gap", "implementation"]):
            return "implementation_migration"
        if any(x in etype_lower for x in ["equipment", "facility", "distribution", "material"]):
            return "physical"
        return "unknown"

    nodes = []
    for elem in elements:
        info = _elem_to_dict(elem, ns)
        eid = info.get("identifier", elem.get("identifier", ""))
        etype = info.get("type", "")
        nodes.append({
            "id": eid,
            "name": info.get("name", ""),
            "type": etype,
            "layer": _detect_layer(etype),
        })

    edges = []
    for rel in relationships:
        info = _elem_to_dict(rel, ns)
        edges.append({
            "source": info.get("source", rel.get("source", "")),
            "target": info.get("target", rel.get("target", "")),
            "type": info.get("type", ""),
            "id": info.get("identifier", rel.get("identifier", "")),
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


# =====================================================================
# Tool definitions registry
# =====================================================================

ARCHIMATE_PARSER_TOOL_DEFINITIONS = [
    # Retrieval tools
    {
        "id": "live_archimate_parse_model_info", "name": "archimate_parse_model_info",
        "description": "Parse ArchiMate exchange file and return model metadata (name, counts, types).",
        "tool_type": "retrieval", "domain": "archimate", "callable": archimate_parse_model_info,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"model_name": {"type": "string"}, "element_count": {"type": "integer"}, "relationship_count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "metadata"],
    },
    {
        "id": "live_archimate_list_elements", "name": "archimate_list_elements",
        "description": "List all elements in an ArchiMate model, with optional type/layer filtering.",
        "tool_type": "retrieval", "domain": "archimate", "callable": archimate_list_elements,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
            {"name": "element_type", "type": "string", "description": "Filter by element type", "required": False},
            {"name": "layer", "type": "string", "description": "Filter by layer", "required": False},
        ],
        "return_schema": {"type": "object", "properties": {"elements": {"type": "array"}, "count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "elements"],
    },
    {
        "id": "live_archimate_list_relationships", "name": "archimate_list_relationships",
        "description": "List all relationships in an ArchiMate model, with optional type/source/target filtering.",
        "tool_type": "retrieval", "domain": "archimate", "callable": archimate_list_relationships,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
            {"name": "relationship_type", "type": "string", "description": "Filter by type", "required": False},
            {"name": "source_id", "type": "string", "description": "Filter by source element", "required": False},
            {"name": "target_id", "type": "string", "description": "Filter by target element", "required": False},
        ],
        "return_schema": {"type": "object", "properties": {"relationships": {"type": "array"}, "count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "relationships"],
    },
    {
        "id": "live_archimate_get_element_relationships", "name": "archimate_get_element_relationships",
        "description": "Get all incoming and outgoing relationships for a specific ArchiMate element.",
        "tool_type": "retrieval", "domain": "archimate", "callable": archimate_get_element_relationships,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
            {"name": "element_id", "type": "string", "description": "Element identifier", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"incoming": {"type": "array"}, "outgoing": {"type": "array"}}},
        "tags": ["live", "archimate", "parser", "element_relations"],
    },
    {
        "id": "live_archimate_list_views", "name": "archimate_list_views",
        "description": "List all views (diagrams) defined in an ArchiMate model.",
        "tool_type": "retrieval", "domain": "archimate", "callable": archimate_list_views,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"views": {"type": "array"}, "count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "views"],
    },
    {
        "id": "live_archimate_get_properties", "name": "archimate_get_properties",
        "description": "Get custom properties defined on model elements or property definitions.",
        "tool_type": "retrieval", "domain": "archimate", "callable": archimate_get_properties,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
            {"name": "element_id", "type": "string", "description": "Element identifier (optional)", "required": False},
        ],
        "return_schema": {"type": "object", "properties": {"properties": {"type": "array"}, "count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "properties"],
    },
    # Processing tools
    {
        "id": "live_archimate_compute_model_metrics", "name": "archimate_compute_model_metrics",
        "description": "Compute ArchiMate model metrics: complexity, density, type distribution, layer coverage.",
        "tool_type": "processing", "domain": "archimate", "callable": archimate_compute_model_metrics,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"element_count": {"type": "integer"}, "density": {"type": "number"}, "layers_used": {"type": "array"}}},
        "tags": ["live", "archimate", "parser", "metrics"],
    },
    {
        "id": "live_archimate_compute_element_usage", "name": "archimate_compute_element_usage",
        "description": "Rank ArchiMate elements by usage — find over-connected hubs and unused orphans.",
        "tool_type": "processing", "domain": "archimate", "callable": archimate_compute_element_usage,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"orphan_count": {"type": "integer"}, "hub_count": {"type": "integer"}, "hubs": {"type": "array"}}},
        "tags": ["live", "archimate", "parser", "usage", "hubs"],
    },
    {
        "id": "live_archimate_validate_relationships", "name": "archimate_validate_relationships",
        "description": "Validate ArchiMate relationships — find dangling references (missing source/target).",
        "tool_type": "processing", "domain": "archimate", "callable": archimate_validate_relationships,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"is_valid": {"type": "boolean"}, "dangling_count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "validation"],
    },
    {
        "id": "live_archimate_extract_to_graph", "name": "archimate_extract_to_graph",
        "description": "Extract ArchiMate model to graph format (nodes+edges) for NetworkX analysis — the bridge tool.",
        "tool_type": "processing", "domain": "archimate", "callable": archimate_extract_to_graph,
        "parameters": [
            {"name": "xml_content", "type": "string", "description": "ArchiMate XML content", "required": True},
        ],
        "return_schema": {"type": "object", "properties": {"nodes": {"type": "array"}, "edges": {"type": "array"}, "node_count": {"type": "integer"}}},
        "tags": ["live", "archimate", "parser", "graph", "bridge"],
    },
]
