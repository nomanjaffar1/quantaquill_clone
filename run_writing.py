# run_writing.py

from agents.writing_agent import WritingAgent
from agents.citation_agent import CitationAgent

if __name__ == "__main__":
    topic = input("Enter the research topic (same as Week 1): ")
    
    print("🖋 Generating Abstract and Introduction...")
    writing_agent = WritingAgent()
    sections = writing_agent.execute(topic)

    print("\n📚 Adding citations and references...")
    citation_agent = CitationAgent()
    citation_agent.execute()

    print("\n✅ Draft ready in 'output/' folder!")
