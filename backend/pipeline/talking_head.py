# -*- coding: utf-8 -*-
"""
Pipeline Talking Head — estilo Talking Head com SadTalker.
Ainda não implementado — será usado SadTalker.
"""

from sqlalchemy.orm import Session

from pipeline.base import BasePipeline
from models.task import Task


class TalkingHeadPipeline(BasePipeline):
    """Pipeline para estilo Talking Head com SadTalker (não implementado)."""

    def run(self, task: Task, db: Session):
        task.status = "failed"
        task.log = (task.log or "") + "Estilo Talking Head ainda não implementado — será usado SadTalker.\n"
        task.progress = 0
        db.commit()
