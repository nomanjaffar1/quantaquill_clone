# agents/citation_agent.py

from agents.base_agent import BaseAgent
import json
import os
import re

class CitationAgent(BaseAgent):
    def __init__(self):
        super().__init__("CitationAgent")

    def inject_citations(self, text, research_data):
        # Add citation after sentences containing numbers or keywords
        sentences = text.split(". ")
        cited_text = []
        ref_map = {}
        ref_list = []
        total_refs = len(research_data)

        for sentence in sentences:
            citation_needed = bool(re.search(r"\d+", sentence)) or "AI" in sentence or "model" in sentence
            if citation_needed and total_refs > 0:
                ref_index = (len(ref_map) % total_refs) + 1  # cycle through references
                cited_text.append(sentence + f" [{ref_index}]")

                if sentence not in ref_map:
                    reference = f"{research_data[ref_index - 1]['title']} - {research_data[ref_index - 1]['url']}"
                    ref_map[sentence] = reference
                    ref_list.append(f"[{ref_index}] {reference}")
            else:
                cited_text.append(sentence)

        return ". ".join(cited_text), ref_list

    def execute(self):
        with open("data/draft_sections.json", "r", encoding="utf-8") as f:
            draft = json.load(f)
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        cited_abstract, refs_abstract = self.inject_citations(draft["abstract"], research_data)
        cited_intro, refs_intro = self.inject_citations(draft["introduction"], research_data)

        os.makedirs("output", exist_ok=True)
        with open("output/abstract.md", "w", encoding="utf-8") as f:
            f.write("# Abstract\n" + cited_abstract)
        with open("output/introduction.md", "w", encoding="utf-8") as f:
            f.write("# Introduction\n" + cited_intro)
        with open("output/references.md", "w", encoding="utf-8") as f:
            f.write("# References\n" + "\n".join(set(refs_abstract + refs_intro)))

        print("✅ Citations injected and references saved.")
