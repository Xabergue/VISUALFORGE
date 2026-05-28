# -*- coding: utf-8 -*-
"""
Pipeline Reddit Story — estilo Reddit Story Narrado.
Ainda não implementado.
"""

from sqlalchemy.orm import Session

from pipeline.base import BasePipeline
from models.task import Task


class RedditStoryPipeline(BasePipeline):
    """Pipeline para estilo Reddit Story Narrado (não implementado)."""

    def run(self, task: Task, db: Session):
        task.status = "failed"
        task.log = (task.log or "") + "Estilo Reddit Story ainda não implementado.\n"
        task.progress = 0
        db.commit()
