from pipeline.base import BasePipeline
class RedditStoryPipeline(BasePipeline):
    def run(self, task_id: str):
        self.mark_failed(task_id, "Estilo 'Reddit Story Narrado' não implementado ainda.")
