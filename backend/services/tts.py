# -*- coding: utf-8 -*-
"""
Serviço de TTS (Text-to-Speech) — geração de áudio e legendas.
Suporta Kokoro-82M para narração e Whisper/edge-tts para legendas.
"""

import os
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TTS_ENGINE = os.getenv("TTS_ENGINE", "kokoro")
TTS_DEFAULT_VOICE = os.getenv("TTS_DEFAULT_VOICE", "pm_alex")
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")


def generate_audio(text: str, voice: str = "pm_alex", output_path: str = "output.wav") -> str:
    """
    Gera áudio a partir de texto usando Kokoro-82M.

    Args:
        text: Texto para narração
        voice: Nome da voz (pm_alex, pm_santa, pf_dora)
        output_path: Caminho do arquivo WAV de saída

    Returns:
        str: Caminho do arquivo de áudio gerado
    """
    voice = voice or TTS_DEFAULT_VOICE

    try:
        from kokoro import KPipeline
        import soundfile as sf

        # Determinar código do idioma baseado na voz
        # 'p' = português, 'a' = americano, 'e' = espanhol
        lang_code = "p"  # Padrão português
        if voice.startswith("pm_alex") or voice.startswith("pm_santa"):
            lang_code = "p"
        elif voice.startswith("pf_dora"):
            lang_code = "p"

        pipeline = KPipeline(lang_code=lang_code)
        generator = pipeline(text, voice=voice, speed=1.0)

        # Coletar todos os segmentos de áudio
        audio_segments = []
        for i, (gs, ps, audio) in enumerate(generator):
            if audio is not None:
                audio_segments.append(audio)

        if audio_segments:
            import numpy as np
            full_audio = np.concatenate(audio_segments)
            sf.write(output_path, full_audio, 24000)
        else:
            raise RuntimeError("Nenhum segmento de áudio foi gerado pelo Kokoro")

        return output_path

    except ImportError:
        raise RuntimeError(
            "Kokoro não está instalado. Instale com: pip install kokoro soundfile"
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar áudio com Kokoro: {str(e)}")


def generate_subtitles_whisper(audio_path: str, language: str = "pt") -> str:
    """
    Gera legendas no formato SRT usando Whisper.

    Args:
        audio_path: Caminho do arquivo de áudio
        language: Código do idioma (pt, en, es)

    Returns:
        str: Caminho do arquivo SRT gerado
    """
    try:
        import whisper

        model = whisper.load_model(WHISPER_MODEL_NAME)
        result = model.transcribe(audio_path, language=language)

        # Converter segmentos para formato SRT
        srt_path = os.path.splitext(audio_path)[0] + ".srt"

        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start_time = _format_srt_time(segment["start"])
                end_time = _format_srt_time(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

        return srt_path

    except ImportError:
        raise RuntimeError(
            "Whisper não está instalado. Instale com: pip install openai-whisper"
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar legendas com Whisper: {str(e)}")


def generate_subtitles_edge(text: str, output_dir: str, voice: str = "pm_alex") -> str:
    """
    Gera legendas usando edge-tts (Microsoft Edge TTS).
    Usa o SubMaker para gerar timestamps das palavras.

    Args:
        text: Texto narrado
        output_dir: Diretório de saída
        voice: Nome da voz para edge-tts

    Returns:
        str: Caminho do arquivo SRT gerado
    """
    try:
        import asyncio
        import edge_tts
        from edge_tts import SubMaker
        from edge_tts.submaker import SubMaker as SubMakerClass

        # Mapear vozes Kokoro para vozes edge-tts
        voice_map = {
            "pm_alex": "pt-BR-AntonioNeural",
            "pm_santa": "pt-BR-EnioNeural",
            "pf_dora": "pt-BR-FranciscaNeural",
        }
        edge_voice = voice_map.get(voice, "pt-BR-AntonioNeural")

        async def _generate():
            communicate = edge_tts.Communicate(text, edge_voice)
            submaker = SubMakerClass()

            # Gerar áudio e coletar timestamps
            audio_path = os.path.join(output_dir, "edge_tts_temp.mp3")
            with open(audio_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        submaker.create_sub(
                            (chunk["offset"], chunk["duration"]), chunk["text"]
                        )

            # Gerar VTT e converter para SRT
            vtt_content = submaker.generate_subs()
            srt_path = os.path.join(output_dir, "subtitles.srt")
            srt_content = _vtt_to_srt(vtt_content)

            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

            # Limpar arquivo temporário
            if os.path.exists(audio_path):
                os.remove(audio_path)

            return srt_path

        # Executar função assíncrona
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Se já estamos em um event loop, criar uma nova thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(asyncio.run, _generate()).result()
                return result
            else:
                return loop.run_until_complete(_generate())
        except RuntimeError:
            return asyncio.run(_generate())

    except ImportError:
        raise RuntimeError(
            "edge-tts não está instalado. Instale com: pip install edge-tts"
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar legendas com edge-tts: {str(e)}")


def _format_srt_time(seconds: float) -> str:
    """Formata tempo em segundos para formato SRT (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _vtt_to_srt(vtt_content: str) -> str:
    """Converte conteúdo VTT para formato SRT."""
    lines = vtt_content.strip().split("\n")
    srt_lines = []
    index = 1
    skip_header = True

    for line in lines:
        # Pular cabeçalho WEBVTT
        if skip_header:
            if line.strip().startswith("WEBVTT"):
                continue
            if "-->" in line:
                skip_header = False
            else:
                continue

        # Converter timestamp VTT (00:00:00.000) para SRT (00:00:00,000)
        if "-->" in line:
            parts = line.split("-->")
            start = parts[0].strip().replace(".", ",")
            end = parts[1].strip().replace(".", ",")
            srt_lines.append(f"{index}")
            srt_lines.append(f"{start} --> {end}")
            index += 1
        elif line.strip():
            srt_lines.append(line.strip())
        else:
            srt_lines.append("")

    return "\n".join(srt_lines)


def get_audio_duration(audio_path: str) -> float:
    """
    Retorna a duração do arquivo de áudio em segundos usando FFprobe.

    Args:
        audio_path: Caminho do arquivo de áudio

    Returns:
        float: Duração em segundos
    """
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Erro ao obter duração do áudio: {str(e)}")
