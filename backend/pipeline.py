from manager.coordinator import Coordinator

def run_pipeline(topic: str, user_methodology=None, user_experiments=None):
    coordinator = Coordinator()
    coordinator.run_pipeline(topic, user_methodology, user_experiments)
    return "output/full_paper.pdf"
