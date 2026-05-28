# -*- coding: utf-8 -*-
"""
Pipeline Image Carousel — estilo Carrossel de Imagens.
Ainda não implementado.
"""

from sqlalchemy.orm import Session

from pipeline.base import BasePipeline
from models.task import Task


class ImageCarouselPipeline(BasePipeline):
    """Pipeline para estilo Carrossel de Imagens (não implementado)."""

    def run(self, task: Task, db: Session):
        task.status = "failed"
        task.log = (task.log or "") + "Estilo Carrossel de Imagens ainda não implementado.\n"
        task.progress = 0
        db.commit()
