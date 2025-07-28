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

    def generate_section(self, section_name, topic, research_data):
        if section_name.lower() == "abstract":
            prompt = f"""
Write a concise **Abstract** (150 words max) for a scientific paper on:
Topic: {topic}

Use the following research summaries:
{research_data}

Ensure the abstract is clear, formal, and suitable for an academic journal.
"""
        elif section_name.lower() == "introduction":
            prompt = f"""
Write an **Introduction** section (250-300 words) for a scientific paper on:
Topic: {topic}

Incorporate the following research insights:
{research_data}

Maintain an academic tone and reference concepts logically.
"""

        template = ChatPromptTemplate.from_template(prompt)
        chain = template | self.llm
        response = chain.invoke({})
        return response.content.strip()

    def execute(self, topic):
        # Load research data
        with open("data/research_output.json", "r", encoding="utf-8") as f:
            research_data = json.load(f)

        research_summary_text = "\n".join([f"- {p['title']}: {p['summary']}" for p in research_data])

        abstract = self.generate_section("abstract", topic, research_summary_text)
        introduction = self.generate_section("introduction", topic, research_summary_text)

        os.makedirs("output", exist_ok=True)
        with open("output/abstract.md", "w", encoding="utf-8") as f:
            f.write("# Abstract\n" + abstract)
        with open("output/introduction.md", "w", encoding="utf-8") as f:
            f.write("# Introduction\n" + introduction)

        # Save to draft JSON
        with open("data/draft_sections.json", "w", encoding="utf-8") as f:
            json.dump({"abstract": abstract, "introduction": introduction}, f, indent=4)

        print("✅ Abstract and Introduction generated and saved.")
        return {"abstract": abstract, "introduction": introduction}
