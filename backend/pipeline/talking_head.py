from pipeline.base import BasePipeline
class TalkingHeadPipeline(BasePipeline):
    def run(self, task_id: str):
        self.mark_failed(task_id, "Estilo 'Talking Head' não implementado ainda — usará SadTalker no futuro.")
