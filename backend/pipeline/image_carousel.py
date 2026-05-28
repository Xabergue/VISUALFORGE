# -*- coding: utf-8 -*-
from pipeline.base import BasePipeline
class ImageCarouselPipeline(BasePipeline):
    def run(self, task_id: str):
        self.mark_failed(task_id, "Estilo 'Carrossel de Imagens' n�o implementado ainda.")
