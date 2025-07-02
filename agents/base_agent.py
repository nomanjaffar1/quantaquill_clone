class BaseAgent:
    def __init__(self, name):
        self.name = name

    def receive_task(self, task_data):
        raise NotImplementedError("Must override receive_task")

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Must override execute")
