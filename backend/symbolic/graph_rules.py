# symbolic/graph_rules.py

def validate_graph(graph):
    issues = []

    for node, attrs in graph.nodes(data=True):
        if attrs.get("type") == "claim":
            if any(char.isdigit() for char in node) and not attrs.get("cited"):
                issues.append(f"Claim '{node}' contains numbers but lacks citation.")
    return issues
