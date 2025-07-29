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

    def inject_citations(self, text, research_data):
        """
        Adds heuristic-based citations to text.
        Rules:
            - Add citation if sentence contains a number OR contains 'AI' OR 'model'
        """
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
        """
        Initial citation injection (heuristic-based).
        """
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

    def auto_fix_missing_citations(self, validation_issues):
        """
        Automatically fixes missing citations using LLM-based reference matching.
        Steps:
            1. For each sentence flagged in validation issues, ask LLM to select best references.
            2. Update draft sections and Markdown files.
        """
        # Load research data
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        # Load draft sections
        with open("data/draft_sections.json", "r", encoding="utf-8") as f:
            draft = json.load(f)

        fixed_sections = {}

        for issue in validation_issues:
            # Extract problematic sentence
            sentence = issue.split("'")[1] if "'" in issue else None
            if not sentence:
                continue

            # Prepare research titles for LLM
            research_titles = "\n".join([f"[{i+1}] {p['title']}" for i, p in enumerate(research_data)])

            # Prompt for best reference selection
            prompt = f"""
You are a citation assistant. Given this sentence from a scientific paper:
"{sentence}"

Here are available research papers:
{research_titles}

Which one or two papers best support the claim? Reply with index numbers only (e.g., "2" or "1,3").
"""
            template = ChatPromptTemplate.from_template(prompt)
            chain = template | self.llm
            response = chain.invoke({})
            chosen_refs = response.content.strip()

            # Format citation like [2] or [1][3]
            citation_text = "".join([f"[{r.strip()}]" for r in chosen_refs.split(",") if r.strip().isdigit()])

            # Update the section containing this sentence
            for section_name, text in draft.items():
                if sentence in text:
                    updated_text = text.replace(sentence, sentence + " " + citation_text)
                    draft[section_name] = updated_text
                    fixed_sections[section_name] = updated_text

        # Save updated draft
        with open("data/draft_sections.json", "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=4)

        # Update Markdown files
        os.makedirs("output", exist_ok=True)
        for section_name, text in fixed_sections.items():
            file_path = f"output/{section_name}.md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {section_name.capitalize()}\n" + text)

        print("✅ Missing citations added using LLM-based matching.")
