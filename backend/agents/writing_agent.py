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
        # Remove common filler patterns
        text = re.sub(r'(?i)(here is|a potential|note that|this section).*', '', text)
        # Remove redundant section names
        text = re.sub(r'(?i)(abstract|introduction|methodology|experiments|results|conclusion)[: ]+', '', text)
        return text.strip()

    def generate_section(self, section_name, topic, research_data, user_input=None):
        """
        Generate content for each section with academic tone.
        """
        if section_name.lower() == "abstract":
            prompt = f"""
Write a formal Abstract (150 words max) for a scientific paper:
Topic: {topic}
Context: {research_data}

Instructions:
- Do NOT include headings or meta-comments.
- Maintain academic tone and clarity.
- Highlight objectives, approach, and contributions.
"""
        elif section_name.lower() == "introduction":
            prompt = f"""
Write an Introduction (300-400 words) for a scientific paper:
Topic: {topic}
Context: {research_data}

Include:
- Background and motivation
- Problem statement and objectives
- Brief summary of contributions
- Academic tone only, no placeholders
"""
        elif section_name.lower() == "methodology":
            if user_input and len(user_input.strip()) > 20:
                prompt = f"""
Refine and format this Methodology section:
{user_input}

Ensure:
- Academic tone
- Use structured format (e.g., Architecture, Components, Tools)
- No redundant comments or headings
"""
            else:
                prompt = f"""
Write a Methodology section for:
Topic: {topic}
Context: {research_data}

Include:
- Multi-agent framework details
- Knowledge Graph integration
- Tools and datasets used
"""
        elif section_name.lower() == "experiments":
            if user_input and len(user_input.strip()) > 20:
                prompt = f"""
Refine and format this Experiments section:
{user_input}

Ensure:
- Academic tone
- Include setup, datasets, and evaluation metrics
"""
            else:
                prompt = f"""
Write an Experiments section for:
Topic: {topic}

Include:
- Experimental setup
- Evaluation metrics and performance benchmarks
"""
        elif section_name.lower() == "results":
            prompt = f"""
Write a Results section that explains how the proposed system generated this paper:
Topic: {topic}

Include:
- Brief description of pipeline steps (Research, Writing, Citation, Knowledge Graph)
- Mention validation and citation correction
- Use academic tone
"""
        elif section_name.lower() == "conclusion":
            prompt = f"""
Write a strong Conclusion for:
Topic: {topic}

Include:
- Summary of contributions
- Impact on research automation
- Future work suggestions
"""

        template = ChatPromptTemplate.from_template(prompt)
        chain = template | self.llm
        response = chain.invoke({})
        return self.clean_text(response.content)

    def execute(self, topic, user_methodology=None, user_experiments=None):
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        research_summary_text = "\n".join([f"- {p['title']}: {p['summary']}" for p in research_data])

        # Generate all sections
        abstract = self.generate_section("abstract", topic, research_summary_text)
        introduction = self.generate_section("introduction", topic, research_summary_text)
        methodology = self.generate_section("methodology", topic, research_summary_text, user_methodology)
        experiments = self.generate_section("experiments", topic, research_summary_text, user_experiments)
        results = self.generate_section("results", topic, research_summary_text)
        conclusion = self.generate_section("conclusion", topic, research_summary_text)


        # Save sections
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

        # Save JSON for final assembly
        with open("data/draft_sections.json", "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4)

        print("✅ All sections generated and cleaned.")
        return sections
