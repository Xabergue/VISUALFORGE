# -*- coding: utf-8 -*-
"""
Pipeline base — classe abstrata para pipelines de geração de vídeo.
"""

from sqlalchemy.orm import Session


class BasePipeline:
    """Classe base para todos os pipelines de geração de vídeo."""

    def run(self, task, db: Session):
        """
        Executa o pipeline de geração de vídeo.

        Args:
            task: Objeto Task do banco de dados
            db: Sessão do banco de dados

        Raises:
            NotImplementedError: Deve ser implementado por subclasses
        """
        raise NotImplementedError("Pipeline deve implementar o método run()")
