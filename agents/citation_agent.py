# agents/citation_agent.py

from agents.base_agent import BaseAgent
import json
import os
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class CitationAgent(BaseAgent):
    def __init__(self):
        super().__init__("CitationAgent")
        self.llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))

    def format_ieee_reference(self, index, paper):
        authors_list = paper.get('authors', ['Unknown Author'])
        authors = ", ".join(authors_list[:3])
        if len(authors_list) > 3:
            authors += " et al."
        title = paper.get('title', 'No Title')
        year = paper.get('published', 'n.d.')[:4] if paper.get('published') else "n.d."
        url = paper.get('url', '')
        return f"[{index}] {authors}, \"{title},\" arXiv, {year}. [Online]. Available: {url}"

    def inject_citations(self, text, research_data):
        """
        Adds citations to sentences based on heuristic rules.
        """
        sentences = text.split(". ")
        cited_text = []
        used_refs = []
        total_refs = len(research_data)

        for sentence in sentences:
            citation_needed = bool(re.search(r"\d+", sentence)) or "AI" in sentence or "model" in sentence
            if citation_needed and total_refs > 0:
                ref_index = (len(used_refs) % total_refs) + 1
                cited_text.append(sentence + f" [{ref_index}]")
                if ref_index not in used_refs:
                    used_refs.append(ref_index)
            else:
                cited_text.append(sentence)

        ref_list = [self.format_ieee_reference(i, research_data[i - 1]) for i in used_refs]
        return ". ".join(cited_text), ref_list

    def execute(self):
        """
        Injects citations and creates References.md in IEEE format.
        """
        with open("data/draft_sections.json", "r", encoding="utf-8") as f:
            draft = json.load(f)
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        cited_abstract, refs_abstract = self.inject_citations(draft["abstract"], research_data)
        cited_intro, refs_intro = self.inject_citations(draft["introduction"], research_data)

        combined_refs = refs_abstract + [r for r in refs_intro if r not in refs_abstract]

        os.makedirs("output", exist_ok=True)
        with open("output/abstract.md", "w", encoding="utf-8") as f:
            f.write("# Abstract\n" + cited_abstract)
        with open("output/introduction.md", "w", encoding="utf-8") as f:
            f.write("# Introduction\n" + cited_intro)
        with open("output/references.md", "w", encoding="utf-8") as f:
            f.write("# References\n" + "\n".join(combined_refs))

        print("✅ Citations injected and IEEE references saved.")

    def auto_fix_missing_citations(self, validation_issues):
        """
        Fixes missing citations using LLM-based selection.
        """
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)
        with open("data/draft_sections.json", "r", encoding="utf-8") as f:
            draft = json.load(f)

        fixed_sections = {}
        research_titles = "\n".join([f"[{i+1}] {p['title']}" for i, p in enumerate(research_data)])

        for issue in validation_issues:
            sentence = issue.split("'")[1] if "'" in issue else None
            if not sentence:
                continue

            prompt = f"""
Select the best references for this sentence:
"{sentence}"

Available papers:
{research_titles}

Return only index numbers separated by commas (e.g., 1,3).
"""
            template = ChatPromptTemplate.from_template(prompt)
            chain = template | self.llm
            response = chain.invoke({})
            chosen_refs = response.content.strip()

            citation_text = "".join([f"[{r.strip()}]" for r in chosen_refs.split(",") if r.strip().isdigit()])

            for section_name, text in draft.items():
                if sentence in text:
                    updated_text = text.replace(sentence, sentence + " " + citation_text)
                    draft[section_name] = updated_text
                    fixed_sections[section_name] = updated_text

        with open("data/draft_sections.json", "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=4)

        for section_name, text in fixed_sections.items():
            with open(f"output/{section_name}.md", "w", encoding="utf-8") as f:
                f.write(f"# {section_name.capitalize()}\n" + text)

        print("✅ Missing citations fixed and updated in text.")
