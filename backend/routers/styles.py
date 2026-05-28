from fastapi import APIRouter

router = APIRouter(prefix="/api/styles", tags=["styles"])

STYLES = [
    {
        "id": "stock_footage", "name": "Stock Footage Narrado",
        "description": "Vídeos de arquivo com narração gerada por IA, legendas e música opcional.",
        "icon": "film", "implemented": True,
        "config_schema": {
            "persona": {"type": "select", "label": "Persona", "options": ["neutro", "educativo", "entretenimento", "corporativo"], "default": "neutro", "description": "Estilo de narração do roteiro"},
            "language": {"type": "select", "label": "Idioma", "options": ["pt-BR", "en-US", "es-ES"], "default": "pt-BR"},
            "duration_seconds": {"type": "number", "label": "Duração (segundos)", "default": 60, "min": 15, "max": 300, "description": "Duração aproximada do vídeo"},
            "voice": {"type": "select", "label": "Voz", "options": ["pm_alex", "pm_santa", "pf_dora"], "default": "pm_alex", "description": "Voz da narração (Kokoro TTS)"},
            "music_file": {"type": "text", "label": "Música de fundo", "default": None, "description": "Nome do arquivo em resource/songs/ (opcional)"},
            "subtitle_position": {"type": "select", "label": "Posição da legenda", "options": ["bottom", "top", "middle"], "default": "bottom"},
            "subtitle_font": {"type": "select", "label": "Fonte da legenda", "options": ["default", "bold", "italic"], "default": "default"},
            "subtitle_mode": {"type": "select", "label": "Modo de legenda", "options": ["whisper", "edge"], "default": "whisper", "description": "Whisper (preciso) ou Edge (rápido)"},
            "orientation": {"type": "select", "label": "Orientação", "options": ["landscape", "portrait"], "default": "landscape"}
        }
    },
    {
        "id": "image_carousel", "name": "Carrossel de Imagens", "description": "Apresentação de imagens com transições, narração e legendas.", "icon": "image", "implemented": False,
        "config_schema": {
            "slides_count": {"type": "number", "label": "Número de slides", "default": 8, "min": 3, "max": 30},
            "duration_per_slide": {"type": "number", "label": "Duração por slide (s)", "default": 5, "min": 2, "max": 15},
            "transition_style": {"type": "select", "label": "Transição", "options": ["fade", "slide", "zoom"], "default": "fade"},
            "voice": {"type": "select", "label": "Voz", "options": ["pm_alex", "pm_santa", "pf_dora"], "default": "pm_alex"},
            "music_file": {"type": "text", "label": "Música de fundo", "default": None}
        }
    },
    {
        "id": "reddit_story", "name": "Reddit Story Narrado", "description": "Histórias do Reddit narradas com fundo temático e legendas.", "icon": "message", "implemented": False,
        "config_schema": {
            "custom_text": {"type": "textarea", "label": "Texto personalizado", "default": None, "description": "Texto manual ou gerado pela LLM"},
            "background_style": {"type": "select", "label": "Estilo de fundo", "options": ["dark", "gameplay", "minecraft"], "default": "dark"},
            "voice": {"type": "select", "label": "Voz", "options": ["pm_alex", "pm_santa", "pf_dora"], "default": "pm_alex"}
        }
    },
    {
        "id": "talking_head", "name": "Talking Head", "description": "Avatar animado que fala o roteiro gerado por IA.", "icon": "user", "implemented": False,
        "config_schema": {
            "avatar_image": {"type": "text", "label": "Imagem do avatar", "default": None, "description": "Caminho da imagem de referência"},
            "voice": {"type": "select", "label": "Voz", "options": ["pm_alex", "pm_santa", "pf_dora"], "default": "pm_alex"}
        }
    }
]

@router.get("")
async def list_styles():
    return STYLES
