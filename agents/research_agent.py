# agents/research_agent.py

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
        self.max_results = 10  # Fetch up to 10 papers
        self.llm = ChatGroq(temperature=0.3, model_name="llama3-8b-8192", api_key=groq_api_key)

    def search_papers(self, topic):
        """
        Searches ArXiv for papers related to the topic.
        """
        print(f"🔎 Searching ArXiv for papers on: {topic}")
        search = arxiv.Search(
            query=topic,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for result in search.results():
            papers.append({
                "title": result.title.strip(),
                "abstract": result.summary.strip(),
                "authors": [author.name for author in result.authors],
                "published": str(result.published.date()),
                "url": result.entry_id
            })
        return papers

    def summarize(self, abstract):
        """
        Summarizes an abstract into 2 lines using LLM.
        """
        if not abstract or len(abstract.strip()) < 50:
            return "Abstract not available or too short to summarize."

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
        """
        Main function to fetch, summarize, and save research papers.
        """
        papers = self.search_papers(topic)
        summarized_papers = []

        for paper in papers:
            summary = self.summarize(paper["abstract"])
            summarized_papers.append({
                "title": paper["title"],
                "summary": summary,
                "authors": paper["authors"],
                "published": paper["published"],
                "url": paper["url"]
            })

        os.makedirs("data", exist_ok=True)
        with open("data/research_output.json", "w", encoding="utf-8") as f:
            json.dump(summarized_papers, f, indent=4)

        print(f"✅ Saved {len(summarized_papers)} research summaries to data/research_output.json")
