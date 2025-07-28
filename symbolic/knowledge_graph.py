# symbolic/knowledge_graph.py

import networkx as nx
import json
import os

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_concept(self, concept):
        self.graph.add_node(concept, type="concept")

    def add_claim(self, claim, cited=False):
        self.graph.add_node(claim, type="claim", cited=cited)

    def add_relationship(self, src, dst, relation):
        self.graph.add_edge(src, dst, relation=relation)

    def visualize(self, save_path="output/knowledge_graph.png"):
        import matplotlib.pyplot as plt
        pos = nx.spring_layout(self.graph)
        labels = nx.get_edge_attributes(self.graph, 'relation')
        nx.draw(self.graph, pos, with_labels=True, node_size=1500, node_color="lightblue", font_size=8)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)
        plt.savefig(save_path)
        plt.close()

    def export(self, path="data/knowledge_graph.json"):
        data = nx.node_link_data(self.graph, edges="links")
        os.makedirs("data", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
