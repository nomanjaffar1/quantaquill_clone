# validators/paper_validator.py

import json
from symbolic.graph_rules import validate_graph

def generate_validation_report():
    with open("data/knowledge_graph.json", "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    from networkx.readwrite import json_graph
    import networkx as nx
    G = json_graph.node_link_graph(graph_data)

    issues = validate_graph(G)

    with open("output/validation_report.txt", "w", encoding="utf-8") as f:
        if issues:
            f.write("Validation Issues:\n")
            for issue in issues:
                f.write(f"- {issue}\n")
        else:
            f.write("No validation issues found.\n")

    print("✅ Validation report generated at output/validation_report.txt")
