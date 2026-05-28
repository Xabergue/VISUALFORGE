# -*- coding: utf-8 -*-
from pipeline.stock_footage import StockFootagePipeline
from pipeline.image_carousel import ImageCarouselPipeline
from pipeline.reddit_story import RedditStoryPipeline
from pipeline.talking_head import TalkingHeadPipeline

PIPELINES = {
    "stock_footage": StockFootagePipeline,
    "image_carousel": ImageCarouselPipeline,
    "reddit_story": RedditStoryPipeline,
    "talking_head": TalkingHeadPipeline,
}

def get_pipeline(style: str):
    cls = PIPELINES.get(style)
    return cls() if cls else None
