# -*- coding: utf-8 -*-
import os, json, shutil, re
from pipeline.base import BasePipeline
from services.llm import generate_script, generate_keywords
from services.tts import generate_audio, generate_subtitles
from services.media import search_media
from services.ffmpeg_service import assemble_video
from database import SessionLocal
from models.task import Task

class StockFootagePipeline(BasePipeline):
    def run(self, task_id: str):
        try:
            db = SessionLocal()
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task: return
            task.status = "running"
            task.log = "Iniciando pipeline Stock Footage Narrado..."
            db.commit()
            db.close()

            config = json.loads(task.config) if task.config else {}
            subject = task.subject
            persona = config.get("persona", "neutro")
            language = config.get("language", "pt-BR")
            duration_seconds = config.get("duration_seconds", 60)
            voice = config.get("voice", "pm_alex")
            music_file = config.get("music_file")
            subtitle_position = config.get("subtitle_position", "bottom")
            subtitle_font = config.get("subtitle_font", "default")
            subtitle_mode = config.get("subtitle_mode", "whisper")
            orientation = config.get("orientation", "landscape")

            output_dir = os.getenv("OUTPUT_DIR", "./output")
            task_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", output_dir, task_id)
            os.makedirs(task_dir, exist_ok=True)

            self.update_progress(task_id, 2, "Gerando roteiro com IA...")
            script = generate_script(subject, persona, language, duration_seconds)
            self.update_progress(task_id, 15, f"Roteiro gerado ({len(script)} caracteres)")

            self.update_progress(task_id, 16, "Dividindo roteiro em segmentos...")
            segments = self._split_script(script)
            self.update_progress(task_id, 18, f"Roteiro dividido em {len(segments)} segmentos")

            keywords_list = []
            for i, seg in enumerate(segments):
                progress = 18 + int((i / max(len(segments), 1)) * 7)
                self.update_progress(task_id, progress, f"Gerando palavras-chave para segmento {i+1}/{len(segments)}...")
                kws = generate_keywords(seg)
                keywords_list.append(kws)
            self.update_progress(task_id, 25, f"Palavras-chave geradas para {len(segments)} segmentos")

            media_paths = []
            for i, keywords in enumerate(keywords_list):
                progress = 25 + int((i / max(len(keywords_list), 1)) * 25)
                self.update_progress(task_id, progress, f"Buscando v�deo para segmento {i+1}/{len(keywords_list)}: {', '.join(keywords[:3])}...")
                try:
                    path = search_media(keywords, task_dir, orientation)
                    if path: media_paths.append(path)
                except Exception as e:
                    self.update_progress(task_id, progress, f"Erro ao buscar m�dia: {str(e)}")

            if not media_paths:
                raise Exception("Nenhum v�deo encontrado. Verifique Pexels ou m�dia local.")
            self.update_progress(task_id, 50, f"M�dia encontrada: {len(media_paths)} clipes")

            self.update_progress(task_id, 52, "Gerando narra��o com TTS...")
            audio_path = os.path.join(task_dir, "narration.wav")
            generate_audio(script, voice, audio_path, subtitle_mode)
            self.update_progress(task_id, 65, "Narra��o gerada com sucesso")

            self.update_progress(task_id, 67, "Gerando legendas...")
            srt_path = os.path.join(task_dir, "subtitles.srt")
            edge_vtt = os.path.join(task_dir, "edge_subtitles.vtt") if subtitle_mode == "edge" else None
            generate_subtitles(audio_path, srt_path, subtitle_mode, language, edge_vtt, script, voice)
            self.update_progress(task_id, 80, "Legendas geradas com sucesso")

            self.update_progress(task_id, 82, "Montando v�deo final com FFmpeg...")
            music_path = None
            if music_file:
                songs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resource", "songs")
                candidate = os.path.join(songs_dir, music_file)
                if os.path.exists(candidate): music_path = candidate

            fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resource", "fonts")
            subtitle_font_path = os.path.join(fonts_dir, "default.ttf") if os.path.exists(os.path.join(fonts_dir, "default.ttf")) else None

            output_filename = f"visualforge_{task_id[:8]}.mp4"
            final_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", output_dir, output_filename)

            assemble_video(clips=media_paths, audio_path=audio_path, srt_path=srt_path, output_path=final_output, orientation=orientation, music_path=music_path, subtitle_position=subtitle_position, subtitle_font_path=subtitle_font_path, music_volume=0.15)
            self.update_progress(task_id, 95, "V�deo montado � finalizando...")
            try: shutil.rmtree(task_dir, ignore_errors=True)
            except: pass
            self.mark_done(task_id, final_output)

        except Exception as e:
            self.mark_failed(task_id, str(e))

    def _split_script(self, script: str) -> list:
        segments = [s.strip() for s in script.split('\n\n') if s.strip()]
        if len(segments) <= 1:
            sentences = re.split(r'(?<=[.!?]) +', script)
            if len(sentences) > 2:
                segments = []
                for i in range(0, len(sentences), 2):
                    segment = ' '.join(sentences[i:i+2]).strip()
                    if segment: segments.append(segment)
            else:
                segments = [script]
        return segments
