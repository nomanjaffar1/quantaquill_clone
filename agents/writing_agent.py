# agents/writing_agent.py

from agents.base_agent import BaseAgent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class WritingAgent(BaseAgent):
    def __init__(self):
        super().__init__("WritingAgent")
        self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=groq_api_key)

    def generate_section(self, section_name, topic, research_data, user_input=None):
        if section_name.lower() == "abstract":
            prompt = f"""
Write a **clear and concise Abstract** (max 150 words) for a research paper:
Topic: {topic}

Context from research:
{research_data}

Structure:
- 2-3 sentences for background
- 1 sentence about the approach
- 1 sentence about the key contributions and significance
"""
        elif section_name.lower() == "introduction":
            prompt = f"""
Write a **detailed Introduction** (300-400 words) for a research paper:
Topic: {topic}

Research insights:
{research_data}

Structure:
- Background and importance
- Problem statement
- Objectives of this work
- 2-3 in-text references using [1], [2], etc.
Maintain academic tone and logical flow.
"""
        elif section_name.lower() == "methodology":
            if user_input and len(user_input.strip()) > 20:
                prompt = f"""
Refine and format the following user-provided **Methodology** for a research paper:
Topic: {topic}
User input:
{user_input}

Ensure:
- Proper academic language
- Subheadings if necessary
- Mention tools, frameworks, or datasets explicitly
"""
            else:
                prompt = f"""
Write a **Methodology section** for a research paper:
Topic: {topic}
Use the research context below:
{research_data}

Structure:
- Approach overview
- Key steps or algorithms
- Mention knowledge graph, multi-agent system if relevant
"""
        elif section_name.lower() == "experiments":
            if user_input and len(user_input.strip()) > 20:
                prompt = f"""
Refine and structure the following user-provided **Experiments** section:
Topic: {topic}
User input:
{user_input}

Ensure:
- Include experimental setup, metrics, and expected results
- Academic tone with clarity
"""
            else:
                prompt = f"""
Write an **Experiments section** for a research paper:
Topic: {topic}
Structure:
- Describe hypothetical experimental setup
- Mention datasets, evaluation metrics, and performance goals
"""
        elif section_name.lower() == "conclusion":
            prompt = f"""
Write a strong **Conclusion** for a research paper:
Topic: {topic}

Context:
{research_data}

Structure:
- Summarize key contributions
- Highlight impact and future work directions
"""

        # LLM call
        template = ChatPromptTemplate.from_template(prompt)
        chain = template | self.llm
        response = chain.invoke({})
        return response.content.strip()

    def execute(self, topic):
        # Load research data
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        research_summary_text = "\n".join([f"- {p['title']}: {p['summary']}" for p in research_data])

        # Ask for optional user inputs
        print("\n(Optional) Enter details for Methodology section (press Enter to skip):")
        user_methodology = input().strip()
        print("\n(Optional) Enter details for Experiments section (press Enter to skip):")
        user_experiments = input().strip()

        # Generate all sections
        abstract = self.generate_section("abstract", topic, research_summary_text)
        introduction = self.generate_section("introduction", topic, research_summary_text)
        methodology = self.generate_section("methodology", topic, research_summary_text, user_methodology)
        experiments = self.generate_section("experiments", topic, research_summary_text, user_experiments)
        conclusion = self.generate_section("conclusion", topic, research_summary_text)

        # Save each section as Markdown
        os.makedirs("output", exist_ok=True)
        with open("output/abstract.md", "w", encoding="utf-8") as f: f.write("# Abstract\n" + abstract)
        with open("output/introduction.md", "w", encoding="utf-8") as f: f.write("# Introduction\n" + introduction)
        with open("output/methodology.md", "w", encoding="utf-8") as f: f.write("# Methodology\n" + methodology)
        with open("output/experiments.md", "w", encoding="utf-8") as f: f.write("# Experiments\n" + experiments)
        with open("output/conclusion.md", "w", encoding="utf-8") as f: f.write("# Conclusion\n" + conclusion)

        # Save to JSON for final assembly
        sections = {
            "abstract": abstract,
            "introduction": introduction,
            "methodology": methodology,
            "experiments": experiments,
            "conclusion": conclusion
        }
        with open("data/draft_sections.json", "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4)

        print("✅ All sections generated and saved.")
        return sections
