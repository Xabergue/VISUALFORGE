# -*- coding: utf-8 -*-
"""
Serviço FFmpeg — montagem e renderização de vídeos.
Usa subprocess para chamar FFmpeg diretamente.
"""

import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")


def get_video_duration(video_path: str) -> float:
    """
    Retorna a duração de um vídeo em segundos usando ffprobe.

    Args:
        video_path: Caminho do arquivo de vídeo

    Returns:
        float: Duração em segundos
    """
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Erro ao obter duração do vídeo {video_path}: {str(e)}")


def get_video_resolution(video_path: str) -> tuple:
    """
    Retorna a resolução do vídeo (width, height).

    Args:
        video_path: Caminho do arquivo de vídeo

    Returns:
        tuple: (width, height)
    """
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "stream=width,height",
                "-of", "json",
                "-select_streams", "v:0",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]
        return (stream.get("width", 1920), stream.get("height", 1080))
    except Exception:
        return (1920, 1080)


def _get_subtitle_filter(
    subtitle_path: str,
    subtitle_position: str = "bottom",
    subtitle_font: str = "default",
    orientation: str = "landscape",
) -> str:
    """
    Gera o filtro de legendas para o FFmpeg.

    Args:
        subtitle_path: Caminho do arquivo SRT
        subtitle_position: Posição (bottom, top, center)
        subtitle_font: Fonte (default, bold, italic)
        orientation: Orientação (landscape, portrait)

    Returns:
        str: Filtro de legenda para FFmpeg
    """
    # Escapar caminho para o filtro do FFmpeg
    escaped_path = subtitle_path.replace("\\", "/").replace(":", "\\:")

    # Configurações de fonte
    font_settings = {
        "default": "Fontsize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2",
        "bold": "Fontsize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Bold=1",
        "italic": "Fontsize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Italic=1",
    }
    font_param = font_settings.get(subtitle_font, font_settings["default"])

    # Configurações de posição (MarginV = margem vertical)
    position_settings = {
        "bottom": "MarginV=30,Alignment=2",
        "top": "MarginV=30,Alignment=8",
        "center": "MarginV=0,Alignment=6",
    }
    position_param = position_settings.get(subtitle_position, position_settings["bottom"])

    # Construir filtro de legenda
    subtitle_filter = (
        f"subtitles='{escaped_path}'"
        f":force_style='{font_param},{position_param}'"
    )

    return subtitle_filter


def _normalize_clip(input_path: str, output_path: str, target_width: int, target_height: int) -> str:
    """
    Normaliza um clipe para a resolução e formato alvo.

    Args:
        input_path: Caminho do vídeo de entrada
        output_path: Caminho do vídeo normalizado
        target_width: Largura alvo
        target_height: Altura alvo

    Returns:
        str: Caminho do arquivo normalizado
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-an",
        output_path,
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def _concat_clips(clip_paths: list, output_path: str, target_duration: float = None) -> str:
    """
    Concatena múltiplos clipes de vídeo.
    Se target_duration for fornecida, ajusta a velocidade dos clipes proporcionalmente.

    Args:
        clip_paths: Lista de caminhos dos clipes
        output_path: Caminho do vídeo concatenado
        target_duration: Duração alvo em segundos (None = manter original)

    Returns:
        str: Caminho do vídeo concatenado
    """
    if not clip_paths:
        raise RuntimeError("Nenhum clipe fornecido para concatenação")

    # Se houver apenas um clipe
    if len(clip_paths) == 1:
        if target_duration:
            clip_duration = get_video_duration(clip_paths[0])
            speed = clip_duration / target_duration
            # Ajustar velocidade do clipe
            cmd = [
                "ffmpeg", "-y",
                "-i", clip_paths[0],
                "-filter_complex", f"[0:v]setpts={speed}*PTS[v]",
                "-map", "[v]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-an",
                output_path,
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        else:
            # Apenas copiar
            import shutil
            shutil.copy2(clip_paths[0], output_path)
        return output_path

    # Obter durações dos clipes
    clip_durations = []
    for clip in clip_paths:
        try:
            dur = get_video_duration(clip)
            clip_durations.append(dur)
        except Exception:
            clip_durations.append(5.0)  # Fallback: 5 segundos

    total_duration = sum(clip_durations)

    # Calcular fator de velocidade para cada clipe se target_duration fornecido
    if target_duration and total_duration > 0:
        speed_factor = total_duration / target_duration
    else:
        speed_factor = 1.0

    # Criar arquivo de concatenação
    concat_dir = os.path.dirname(output_path)
    concat_file = os.path.join(concat_dir, "concat_list.txt")

    # Ajustar cada clipe individualmente se necessário
    adjusted_clips = []
    for i, clip_path in enumerate(clip_paths):
        if speed_factor != 1.0:
            adjusted_path = os.path.join(concat_dir, f"adjusted_{i}.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", clip_path,
                "-filter_complex", f"[0:v]setpts={speed_factor}*PTS[v]",
                "-map", "[v]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-an",
                adjusted_path,
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                adjusted_clips.append(adjusted_path)
            except subprocess.CalledProcessError:
                adjusted_clips.append(clip_path)
        else:
            adjusted_clips.append(clip_path)

    # Escrever arquivo de concatenação
    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in adjusted_clips:
            # Escapar caracteres especiais no caminho
            escaped = clip.replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

    # Concatenar clipes
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-an",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Limpar arquivos temporários
    if os.path.exists(concat_file):
        os.remove(concat_file)
    for clip in adjusted_clips:
        if clip != clip_paths[adjusted_clips.index(clip)] and os.path.exists(clip):
            os.remove(clip)

    return output_path


def assemble_video(
    clips: list,
    audio_path: str,
    subtitle_path: str,
    music_path: str = None,
    orientation: str = "landscape",
    subtitle_position: str = "bottom",
    subtitle_font: str = "default",
    output_path: str = "output.mp4",
) -> str:
    """
    Monta o vídeo final combinando clipes, narração, música de fundo e legendas.

    Args:
        clips: Lista de caminhos dos clipes de vídeo
        audio_path: Caminho do arquivo de narração
        subtitle_path: Caminho do arquivo SRT de legendas
        music_path: Caminho do arquivo de música de fundo (opcional)
        orientation: Orientação do vídeo (landscape ou portrait)
        subtitle_position: Posição das legendas (bottom, top, center)
        subtitle_font: Fonte das legendas (default, bold, italic)
        output_path: Caminho do arquivo de saída

    Returns:
        str: Caminho do vídeo final gerado
    """
    # Configurar resolução baseada na orientação
    if orientation == "portrait":
        target_width, target_height = 1080, 1920
    else:
        target_width, target_height = 1920, 1080

    # Criar diretório de saída
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    work_dir = os.path.dirname(output_path) or "."

    # ===== PASSO 1: Normalizar clipes =====
    normalized_clips = []
    for i, clip in enumerate(clips):
        norm_path = os.path.join(work_dir, f"normalized_{i}.mp4")
        _normalize_clip(clip, norm_path, target_width, target_height)
        normalized_clips.append(norm_path)

    # ===== PASSO 2: Obter duração da narração =====
    from services.tts import get_audio_duration
    audio_duration = get_audio_duration(audio_path)

    # ===== PASSO 3: Concatenar clipes ajustando duração =====
    concat_path = os.path.join(work_dir, "concat_raw.mp4")
    _concat_clips(normalized_clips, concat_path, target_duration=audio_duration)

    # Limpar clipes normalizados
    for clip in normalized_clips:
        if os.path.exists(clip):
            os.remove(clip)

    # ===== PASSO 4: Combinar vídeo + narração + legendas =====
    # Construir filtro de vídeo (legendas)
    video_filter = _get_subtitle_filter(subtitle_path, subtitle_position, subtitle_font, orientation)

    # Construir filtros de áudio
    audio_inputs = ["-i", audio_path]
    audio_filter_parts = ["[1:a]"]

    if music_path and os.path.exists(music_path):
        # Narração + música de fundo a 15% volume
        audio_inputs.extend(["-i", music_path])
        audio_filter_parts = [
            "[1:a]aresample=44100[narr];",
            f"[2:a]volume=0.15,aresample=44100[music];",
            "[narr][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        ]
        audio_map = ["-map", "[aout]"]
    else:
        # Apenas narração
        audio_filter_parts = ["[1:a]aresample=44100[aout]"]
        audio_map = ["-map", "[aout]"]

    audio_filter = "".join(audio_filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-i", concat_path,
        *audio_inputs,
        "-vf", video_filter,
        "-filter_complex", audio_filter,
        *audio_map,
        "-map", "0:v",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao montar vídeo final: {result.stderr}")

    # Limpar arquivo temporário de concatenação
    if os.path.exists(concat_path):
        os.remove(concat_path)

    return output_path


def normalize_audio(input_path: str, output_path: str = None) -> str:
    """
    Normaliza o volume do áudio de um vídeo usando loudnorm.

    Args:
        input_path: Caminho do vídeo de entrada
        output_path: Caminho do vídeo normalizado (None = sobrescrever)

    Returns:
        str: Caminho do arquivo normalizado
    """
    if output_path is None:
        output_path = input_path

    temp_path = input_path + ".norm.tmp.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        temp_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Erro ao normalizar áudio: {result.stderr}")

    # Substituir arquivo original
    os.replace(temp_path, output_path)
    return output_path
