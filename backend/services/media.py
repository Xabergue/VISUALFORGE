# -*- coding: utf-8 -*-
"""
Serviço de busca e download de mídia — vídeos de stock footage.
Prioridade: 1) mídia local  2) Pexels API
"""

import os
import asyncio
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
LOCAL_MEDIA_DIR = os.getenv("LOCAL_MEDIA_DIR", "./resource/local_media")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")


def search_local_media(keyword: str) -> list:
    """
    Busca arquivos na pasta local_media cujo nome contenha a palavra-chave.

    Args:
        keyword: Palavra-chave para busca (substring no nome do arquivo)

    Returns:
        list[str]: Lista de caminhos absolutos dos arquivos encontrados
    """
    local_dir = Path(LOCAL_MEDIA_DIR)
    if not local_dir.exists():
        return []

    keyword_lower = keyword.lower()
    matches = []

    # Extensões de vídeo suportadas
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpg", ".mpeg"}

    for file_path in local_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            if keyword_lower in file_path.name.lower():
                matches.append(str(file_path.resolve()))

    return matches


async def download_pexels_video(keyword: str, task_id: str) -> Optional[str]:
    """
    Busca e baixa um vídeo do Pexels baseado na palavra-chave.

    Args:
        keyword: Palavra-chave para busca
        task_id: ID da tarefa (para organizar downloads)

    Returns:
        str | None: Caminho do arquivo baixado ou None se não encontrado
    """
    if not PEXELS_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Buscar vídeos no Pexels
            response = await client.get(
                "https://api.pexels.com/videos/search",
                params={
                    "query": keyword,
                    "per_page": 5,
                    "orientation": "landscape",
                },
                headers={"Authorization": PEXELS_API_KEY},
            )

            if response.status_code != 200:
                return None

            data = response.json()
            videos = data.get("videos", [])

            if not videos:
                return None

            # Pegar o primeiro vídeo com arquivo HD
            for video in videos:
                video_files = video.get("video_files", [])
                # Preferir arquivos HD (1080p ou 720p)
                for vf in video_files:
                    quality = vf.get("quality", "")
                    if quality in ("hd", "sd"):
                        download_url = vf.get("link")
                        if download_url:
                            # Baixar o vídeo
                            task_dir = os.path.join(OUTPUT_DIR, task_id, "clips")
                            os.makedirs(task_dir, exist_ok=True)

                            # Nome do arquivo baseado no ID do vídeo
                            filename = f"pexels_{video.get('id', 'unknown')}_{keyword.replace(' ', '_')}.mp4"
                            output_path = os.path.join(task_dir, filename)

                            video_response = await client.get(download_url)
                            if video_response.status_code == 200:
                                with open(output_path, "wb") as f:
                                    f.write(video_response.content)
                                return output_path

            return None

    except Exception as e:
        print(f"[MediaService] Erro ao buscar no Pexels: {str(e)}")
        return None


async def search_videos(keywords: list, task_id: str, count: int = 5) -> list:
    """
    Busca vídeos de stock para as palavras-chave fornecidas.
    Prioriza mídia local, depois busca no Pexels.

    Args:
        keywords: Lista de palavras-chave para busca
        task_id: ID da tarefa
        count: Número máximo de vídeos a retornar

    Returns:
        list[str]: Lista de caminhos de arquivos de vídeo
    """
    results = []
    seen = set()

    for keyword in keywords:
        if len(results) >= count:
            break

        # 1. Buscar na mídia local primeiro
        local_matches = search_local_media(keyword)
        for match in local_matches:
            if match not in seen:
                results.append(match)
                seen.add(match)
                if len(results) >= count:
                    break

        # 2. Se não encontrou localmente, buscar no Pexels
        if len(results) < count:
            pexels_video = await download_pexels_video(keyword, task_id)
            if pexels_video and pexels_video not in seen:
                results.append(pexels_video)
                seen.add(pexels_video)

    return results
