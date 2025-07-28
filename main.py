# main.py
from manager.coordinator import Coordinator

if __name__ == "__main__":
    topic = input("Enter research topic: ")
    coordinator = Coordinator()
    coordinator.run_pipeline(topic)
