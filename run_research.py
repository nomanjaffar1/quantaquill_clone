from agents.research_agent import ResearchAgent

if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    agent = ResearchAgent()
    results = agent.execute(topic)

    for i, paper in enumerate(results, start=1):
        print(f"\n--- Paper {i} ---")
        print(f"Title   : {paper['title']}")
        print(f"Summary : {paper['summary']}")
        print(f"URL     : {paper['url']}")
