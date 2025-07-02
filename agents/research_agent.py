from agents.base_agent import BaseAgent
import arxiv
import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("ResearchAgent")
        self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=groq_api_key)

    def search_papers(self, topic, max_results=3):
        print(f"🔎 Searching ArXiv for papers on: {topic}")
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = []
        for result in search.results():
            papers.append({
                "title": result.title.strip(),
                "abstract": result.summary.strip(),
                "authors": [author.name for author in result.authors],
                "url": result.entry_id
            })
        return papers

    def summarize(self, abstract):
        if not abstract or len(abstract.strip()) < 50:
            return "❌ Abstract not available or too short to summarize."

        prompt_template = ChatPromptTemplate.from_template(
            "Summarize the following scientific abstract in 2 lines:\n\n{abstract}"
        )

        try:
            chain = prompt_template | self.llm
            result = chain.invoke({"abstract": abstract})
            return result.content.strip()
        except Exception as e:
            return f"⚠️ Error in summarization: {e}"

    def execute(self, topic):
        papers = self.search_papers(topic)
        for paper in papers:
            paper["summary"] = self.summarize(paper["abstract"])

        os.makedirs("data", exist_ok=True)
        with open("data/research_output.json", "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=4, ensure_ascii=False)
        print(f"✅ Saved research output to data/research_output.json")
        return papers
