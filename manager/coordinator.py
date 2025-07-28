import subprocess
from agents.research_agent import ResearchAgent
from agents.writing_agent import WritingAgent
from agents.citation_agent import CitationAgent
from symbolic.knowledge_graph import KnowledgeGraph
from symbolic.graph_rules import validate_graph
import os  # Add this at the top of coordinator.py

class Coordinator:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.citation_agent = CitationAgent()
        self.kg = KnowledgeGraph()

    def run_pipeline(self, topic):
        print("\n🔍 [Step 1] Researching...")
        self.research_agent.execute(topic)

        print("\n🖋 [Step 2] Writing structured sections...")
        sections = self.writing_agent.execute(topic)

        print("\n📚 [Step 3] Adding citations...")
        self.citation_agent.execute()

        print("\n🔗 [Step 4] Building Knowledge Graph...")
        self.build_knowledge_graph(sections)

        print("\n📄 [Step 5] Assembling full paper...")
        self.assemble_final_paper()

        print("\n📝 [Step 6] Exporting PDF...")
        self.export_pdf()

        print("\n✅ [Step 7] Generating validation report...")
        from validators.paper_validator import generate_validation_report
        generate_validation_report()

        print("\n✅ All steps completed! Check 'output/' folder.")

    

    def assemble_final_paper(self):
        section_files = [
            "output/abstract.md",
            "output/introduction.md",
            "output/methodology.md",
            "output/experiments.md",
            "output/conclusion.md",
            "output/references.md"
        ]

        combined_content = "# Full Paper\n\n"
        for file in section_files:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    combined_content += f.read() + "\n\n"

        with open("output/full_paper.md", "w", encoding="utf-8") as f:
            f.write(combined_content)

        print("✅ Full paper assembled at output/full_paper.md")


    def export_pdf(self):
        input_file = "output/full_paper.md"
        output_file = "output/full_paper.pdf"
        try:
            command = f"markdown-pdf {input_file} -o {output_file}"
            subprocess.run(command, shell=True, check=True)
            print(f"✅ PDF exported successfully: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ PDF export failed: {e}")

    def build_knowledge_graph(self, sections):
        abstract = sections.get("abstract", "")
        intro = sections.get("introduction", "")

        for sentence in abstract.split(". "):
            if "AI" in sentence:
                self.kg.add_concept("AI")
            self.kg.add_claim(sentence)

        for sentence in intro.split(". "):
            if "model" in sentence:
                self.kg.add_concept("model")
            self.kg.add_claim(sentence)

        self.kg.add_relationship("AI", "model", "supports")
        self.kg.export()
        self.kg.visualize()

        issues = validate_graph(self.kg.graph)
        if issues:
            print("\n⚠ Validation Issues:")
            for issue in issues:
                print(f" - {issue}")
        else:
            print("\n✅ No validation issues found.")
