# agents/writing_agent.py

from agents.base_agent import BaseAgent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv
import re

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class WritingAgent(BaseAgent):
    def __init__(self):
        super().__init__("WritingAgent")
        self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=groq_api_key)

    def clean_text(self, text):
        """
        Remove filler phrases, duplicate titles, and meta-comments.
        """
        # Remove lines starting with 'Here is' or 'a potential'
        text = re.sub(r'(?i)(here is|a potential|note that).*', '', text)
        # Remove redundant section names inside text
        text = re.sub(r'(?i)(abstract|introduction|methodology|experiments|results|conclusion)[: ]+', '', text)
        return text.strip()

    def generate_section(self, section_name, topic, research_data, user_input=None):
        """
        Generate clean academic content for a specific section using LLM.
        """
        if section_name.lower() == "abstract":
            prompt = f"""
Write a **formal Abstract** (150 words max) for a scientific paper:
Topic: {topic}

Context:
{research_data}

Instructions:
- Do NOT include headings or phrases like 'Here is...' or 'a potential abstract'.
- Use academic tone only.
- Provide the final text only.
"""
        elif section_name.lower() == "introduction":
            prompt = f"""
Write an **Introduction** (300-400 words) for a scientific paper:
Topic: {topic}

Context:
{research_data}

Instructions:
- Avoid meta-comments or placeholders.
- Include background, problem statement, and contributions.
- Maintain logical flow and academic tone.
"""
        elif section_name.lower() == "methodology":
            if user_input and len(user_input.strip()) > 20:
                prompt = f"""
Refine this **Methodology** section for academic tone:
{user_input}

Ensure:
- No redundant headings or comments.
- Use subheadings like 'Architecture', 'Components', 'Tools' if needed.
"""
            else:
                prompt = f"""
Write a **Methodology** section for a scientific paper on:
Topic: {topic}

Context:
{research_data}

Instructions:
- Explain multi-agent framework (Research, Writing, Citation, Knowledge Graph).
- Describe tools and architecture clearly.
"""
        elif section_name.lower() == "experiments":
            if user_input and len(user_input.strip()) > 20:
                prompt = f"""
Refine this **Experiments** section for clarity and academic tone:
{user_input}
"""
            else:
                prompt = f"""
Write an **Experiments** section for:
Topic: {topic}

Include:
- Experimental setup
- Datasets and metrics
- Expected performance benchmarks
"""
        elif section_name.lower() == "results":
            prompt = f"""
Write a **Results** section that explains how this AI system wrote the paper itself:
Topic: {topic}

Include:
- Brief summary of pipeline steps (Research, Writing, Citation, KG validation)
- Mention auto-citation correction and PDF export
- Keep academic tone (avoid meta or self-referential jokes)
"""
        elif section_name.lower() == "conclusion":
            prompt = f"""
Write a strong **Conclusion** for a scientific paper on:
Topic: {topic}

Instructions:
- Summarize key contributions and findings
- Highlight impact on research automation
- Suggest future work
"""

        template = ChatPromptTemplate.from_template(prompt)
        chain = template | self.llm
        response = chain.invoke({})
        return self.clean_text(response.content)

    def execute(self, topic):
        # Load research data
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        research_summary_text = "\n".join([f"- {p['title']}: {p['summary']}" for p in research_data])

        print("\n(Optional) Enter details for Methodology section (press Enter to skip):")
        user_methodology = input().strip()
        print("\n(Optional) Enter details for Experiments section (press Enter to skip):")
        user_experiments = input().strip()

        # Generate sections
        abstract = self.generate_section("abstract", topic, research_summary_text)
        introduction = self.generate_section("introduction", topic, research_summary_text)
        methodology = self.generate_section("methodology", topic, research_summary_text, user_methodology)
        experiments = self.generate_section("experiments", topic, research_summary_text, user_experiments)
        results = self.generate_section("results", topic, research_summary_text)
        conclusion = self.generate_section("conclusion", topic, research_summary_text)

        # Save Markdown files
        os.makedirs("output", exist_ok=True)
        sections = {
            "abstract": abstract,
            "introduction": introduction,
            "methodology": methodology,
            "experiments": experiments,
            "results": results,
            "conclusion": conclusion
        }

        for sec, content in sections.items():
            with open(f"output/{sec}.md", "w", encoding="utf-8") as f:
                f.write(f"# {sec.capitalize()}\n{content}")

        # Save draft for pipeline
        with open("data/draft_sections.json", "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4)

        print("✅ All sections generated and cleaned.")
        return sections
