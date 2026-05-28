# -*- coding: utf-8 -*-
"""
Router de Styles — retorna os estilos de vídeo disponíveis com seus schemas de configuração.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/styles", tags=["styles"])

# Definição dos estilos disponíveis
STYLES = [
    {
        "id": "stock_footage",
        "name": "Stock Footage Narrado",
        "description": "Vídeo narrado com clipes de stock footage relevantes ao tema",
        "implemented": True,
        "config_schema": {
            "persona": {
                "type": "select",
                "options": ["neutro", "educativo", "entretenimento", "corporativo"],
                "default": "neutro",
            },
            "language": {
                "type": "select",
                "options": ["pt-BR", "en-US", "es-ES"],
                "default": "pt-BR",
            },
            "duration_seconds": {
                "type": "number",
                "min": 15,
                "max": 300,
                "default": 60,
            },
            "voice": {
                "type": "select",
                "options": ["pm_alex", "pm_santa", "pf_dora"],
                "default": "pm_alex",
            },
            "music_file": {
                "type": "text",
                "default": None,
                "label": "Arquivo de música (opcional)",
            },
            "subtitle_position": {
                "type": "select",
                "options": ["bottom", "top", "center"],
                "default": "bottom",
            },
            "subtitle_font": {
                "type": "select",
                "options": ["default", "bold", "italic"],
                "default": "default",
            },
            "subtitle_mode": {
                "type": "select",
                "options": ["whisper", "edge"],
                "default": "whisper",
            },
            "orientation": {
                "type": "select",
                "options": ["landscape", "portrait"],
                "default": "landscape",
            },
        },
    },
    {
        "id": "image_carousel",
        "name": "Carrossel de Imagens",
        "description": "Apresentação de slides com imagens e narração",
        "implemented": False,
        "config_schema": {
            "slides_count": {
                "type": "number",
                "min": 3,
                "max": 20,
                "default": 6,
            },
            "duration_per_slide": {
                "type": "number",
                "min": 2,
                "max": 15,
                "default": 5,
            },
            "transition_style": {
                "type": "select",
                "options": ["fade", "slide", "zoom"],
                "default": "fade",
            },
            "voice": {
                "type": "select",
                "options": ["pm_alex", "pm_santa", "pf_dora"],
                "default": "pm_alex",
            },
            "music_file": {
                "type": "text",
                "default": None,
            },
        },
    },
    {
        "id": "reddit_story",
        "name": "Reddit Story Narrado",
        "description": "História estilo Reddit com fundo estilizado e narração",
        "implemented": False,
        "config_schema": {
            "custom_text": {
                "type": "textarea",
                "default": None,
                "label": "Texto personalizado (vazio = gerado pela IA)",
            },
            "background_style": {
                "type": "select",
                "options": ["minecraft", "gta", "subway"],
                "default": "minecraft",
            },
            "voice": {
                "type": "select",
                "options": ["pm_alex", "pm_santa", "pf_dora"],
                "default": "pm_alex",
            },
        },
    },
    {
        "id": "talking_head",
        "name": "Talking Head",
        "description": "Avatar que fala com sincronia labial (SadTalker)",
        "implemented": False,
        "config_schema": {},
    },
]


@router.get("")
def get_styles():
    """
    Retorna a lista de estilos de vídeo disponíveis com seus schemas de configuração.
    """
    return STYLES
