# -*- coding: utf-8 -*-
"""
Pipeline Stock Footage Narrado — estilo principal do VisualForge.
Gera vídeo narrado com clipes de stock footage relevantes ao tema.
"""

import os
import json
import asyncio
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from pipeline.base import BasePipeline
from models.task import Task
from services.llm import generate_script, generate_keywords
from services.tts import (
    generate_audio,
    generate_subtitles_whisper,
    generate_subtitles_edge,
    get_audio_duration,
)
from services.media import search_videos, search_local_media
from services.ffmpeg_service import assemble_video, normalize_audio

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
LOCAL_MEDIA_DIR = os.getenv("LOCAL_MEDIA_DIR", "./resource/local_media")
SONGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource", "songs")


class StockFootagePipeline(BasePipeline):
    """
    Pipeline para geração de vídeos com stock footage narrado.

    Fluxo:
    1. Gerar roteiro via LLM
    2. Gerar palavras-chave para cada segmento
    3. Buscar vídeos de stock (local + Pexels)
    4. Gerar narração via Kokoro TTS
    5. Gerar legendas (Whisper ou edge-tts)
    6. Montar vídeo final com FFmpeg
    7. Normalizar áudio e exportar
    """

    def run(self, task: Task, db: Session):
        """
        Executa o pipeline completo de geração de vídeo.

        Args:
            task: Objeto Task do banco de dados
            db: Sessão do banco de dados
        """
        try:
            # Parsear configuração
            config = json.loads(task.config) if task.config else {}

            # Extrair script e keywords pré-gerados (do fluxo de preview)
            # Usar pop para remover do config antes de extrair os outros campos
            pre_script = config.pop("script", None)
            pre_keywords = config.pop("keywords", None)

            persona = config.get("persona", "neutro")
            language = config.get("language", "pt-BR")
            duration_seconds = config.get("duration_seconds", 60)
            voice = config.get("voice", "pm_alex")
            music_file = config.get("music_file", None)
            subtitle_position = config.get("subtitle_position", "bottom")
            subtitle_font = config.get("subtitle_font", "default")
            subtitle_mode = config.get("subtitle_mode", "whisper")
            orientation = config.get("orientation", "landscape")

            # Criar diretório de trabalho para esta tarefa
            task_dir = os.path.join(OUTPUT_DIR, task.id)
            os.makedirs(task_dir, exist_ok=True)

            # =====================================================
            # PASSO 1: Gerar roteiro (5%) — pular se já existe
            # =====================================================
            if pre_script:
                script = pre_script
                task.update_progress(5, "Usando roteiro revisado pelo usuário...", db)
            else:
                task.update_progress(5, "Gerando roteiro...", db)

                script = generate_script(
                    subject=task.subject,
                    persona=persona,
                    language=language,
                    duration=duration_seconds,
                )

                if not script:
                    raise RuntimeError("Roteiro vazio — LLM não gerou conteúdo")

            # Salvar roteiro para referência
            script_path = os.path.join(task_dir, "script.txt")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)

            # =====================================================
            # PASSO 2: Gerar palavras-chave (15%) — pular se já existe
            # =====================================================
            if pre_keywords:
                all_keywords = pre_keywords
                task.update_progress(15, "Usando palavras-chave revisadas pelo usuário...", db)
            else:
                task.update_progress(15, "Roteiro gerado. Gerando palavras-chave...", db)

                # Dividir roteiro em segmentos
                segments = [s.strip() for s in script.split("---") if s.strip()]
                if not segments:
                    # Se não houver separadores, tratar tudo como um segmento
                    segments = [script]

                all_keywords = []
                for i, segment in enumerate(segments):
                    keywords = generate_keywords(segment)
                    all_keywords.extend(keywords)

                # Limitar número de palavras-chave
                all_keywords = all_keywords[:len(segments) * 2]

            # Salvar palavras-chave
            keywords_path = os.path.join(task_dir, "keywords.json")
            with open(keywords_path, "w", encoding="utf-8") as f:
                json.dump(all_keywords, f, ensure_ascii=False, indent=2)

            # =====================================================
            # PASSO 3: Buscar vídeos de stock (30%)
            # =====================================================
            task.update_progress(30, "Buscando vídeos de stock...", db)

            # Buscar vídeos para as palavras-chave
            # Usar asyncio para a busca assíncrona
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Se já estamos em um event loop (ex: FastAPI BackgroundTasks)
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        clip_paths = pool.submit(
                            asyncio.run,
                            search_videos(all_keywords, task.id, count=len(segments))
                        ).result()
                else:
                    clip_paths = loop.run_until_complete(
                        search_videos(all_keywords, task.id, count=len(segments))
                    )
            except RuntimeError:
                clip_paths = asyncio.run(
                    search_videos(all_keywords, task.id, count=len(segments))
                )

            if not clip_paths:
                # Se não encontrou vídeos, usar mídia local genérica
                task.append_log("Nenhum vídeo encontrado online. Buscando mídia local genérica...", db)
                generic_clips = []
                local_dir = Path(LOCAL_MEDIA_DIR)
                if local_dir.exists():
                    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
                    for file_path in local_dir.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                            generic_clips.append(str(file_path.resolve()))
                clip_paths = generic_clips

            if not clip_paths:
                raise RuntimeError(
                    "Nenhum vídeo de stock encontrado. Adicione vídeos à pasta "
                    "resource/local_media/ ou configure a API do Pexels."
                )

            # =====================================================
            # PASSO 4: Gerar narração (45%)
            # =====================================================
            task.update_progress(45, "Gerando narração...", db)

            # Texto completo para narração (sem os separadores ---)
            narration_text = script.replace("---", " ").strip()
            narration_text = " ".join(narration_text.split())  # Normalizar espaços

            audio_path = os.path.join(task_dir, "narration.wav")
            generate_audio(narration_text, voice=voice, output_path=audio_path)

            # Obter duração da narração
            audio_duration = get_audio_duration(audio_path)

            # =====================================================
            # PASSO 5: Gerar legendas (60%)
            # =====================================================
            task.update_progress(60, "Gerando legendas...", db)

            # Mapear código de idioma para Whisper
            language_map = {"pt-BR": "pt", "en-US": "en", "es-ES": "es"}
            whisper_lang = language_map.get(language, "pt")

            if subtitle_mode == "whisper":
                subtitle_path = generate_subtitles_whisper(audio_path, language=whisper_lang)
            else:
                subtitle_path = generate_subtitles_edge(
                    narration_text, task_dir, voice=voice
                )

            if not subtitle_path or not os.path.exists(subtitle_path):
                task.append_log("Aviso: Não foi possível gerar legendas. Continuando sem legendas...", db)
                # Criar arquivo SRT vazio para não quebrar o FFmpeg
                subtitle_path = os.path.join(task_dir, "empty.srt")
                with open(subtitle_path, "w", encoding="utf-8") as f:
                    f.write("1\n00:00:00,000 --> 00:00:01,000\n \n\n")

            # =====================================================
            # PASSO 6: Montar vídeo final (75%)
            # =====================================================
            task.update_progress(75, "Montando vídeo final...", db)

            # Buscar música de fundo
            music_path = None
            if music_file and os.path.exists(music_file):
                music_path = music_file
            else:
                # Buscar música padrão na pasta songs
                songs_path = Path(SONGS_DIR)
                if songs_path.exists():
                    audio_extensions = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}
                    for song in songs_path.iterdir():
                        if song.is_file() and song.suffix.lower() in audio_extensions:
                            music_path = str(song)
                            break

            # Caminho de saída temporário (sem normalização)
            raw_output_path = os.path.join(task_dir, "video_raw.mp4")
            # Caminho final
            final_output_path = os.path.join(task_dir, "video_final.mp4")

            assemble_video(
                clips=clip_paths,
                audio_path=audio_path,
                subtitle_path=subtitle_path,
                music_path=music_path,
                orientation=orientation,
                subtitle_position=subtitle_position,
                subtitle_font=subtitle_font,
                output_path=raw_output_path,
            )

            # =====================================================
            # PASSO 7: Renderizar vídeo final (90%)
            # =====================================================
            task.update_progress(90, "Renderizando vídeo...", db)

            # Normalizar áudio do vídeo final
            normalize_audio(raw_output_path, final_output_path)

            # Limpar arquivo temporário
            if os.path.exists(raw_output_path) and raw_output_path != final_output_path:
                os.remove(raw_output_path)

            # =====================================================
            # PASSO 8: Finalizar (100%)
            # =====================================================
            # Mover para diretório de output com nome legível
            safe_subject = "".join(c if c.isalnum() or c in " -_" else "_" for c in task.subject)[:50]
            final_name = f"{task.id[:8]}_{safe_subject}.mp4"
            public_output_path = os.path.join(OUTPUT_DIR, final_name)
            shutil.copy2(final_output_path, public_output_path)

            # Atualizar task
            task.status = "done"
            task.progress = 100
            task.output_path = final_name
            task.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
            task.append_log("Vídeo gerado com sucesso!", db)

        except Exception as e:
            # Qualquer erro deve ser capturado e registrado
            task.status = "failed"
            task.progress = task.progress or 0
            error_msg = f"Erro no pipeline: {str(e)}"
            task.log = (task.log or "") + error_msg + "\n"
            task.updated_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
            db.commit()
