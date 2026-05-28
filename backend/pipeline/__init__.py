# -*- coding: utf-8 -*-
"""
Registro de pipelines — mapeia estilos para implementações de pipeline.
"""

from pipeline.base import BasePipeline
from pipeline.stock_footage import StockFootagePipeline
from pipeline.image_carousel import ImageCarouselPipeline
from pipeline.reddit_story import RedditStoryPipeline
from pipeline.talking_head import TalkingHeadPipeline

# Registro de pipelines disponíveis
_PIPELINE_REGISTRY = {
    "stock_footage": StockFootagePipeline,
    "image_carousel": ImageCarouselPipeline,
    "reddit_story": RedditStoryPipeline,
    "talking_head": TalkingHeadPipeline,
}


def get_pipeline(style: str) -> BasePipeline:
    """
    Retorna a instância do pipeline correspondente ao estilo.

    Args:
        style: Identificador do estilo (stock_footage, image_carousel, etc.)

    Returns:
        BasePipeline: Instância do pipeline

    Raises:
        ValueError: Se o estilo não for reconhecido
    """
    pipeline_class = _PIPELINE_REGISTRY.get(style)
    if pipeline_class is None:
        raise ValueError(f"Estilo desconhecido: {style}. Estilos disponíveis: {list(_PIPELINE_REGISTRY.keys())}")
    return pipeline_class()
