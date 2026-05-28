# -*- coding: utf-8 -*-
import os, asyncio, subprocess
from dotenv import load_dotenv
load_dotenv()

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

def generate_audio(text: str, voice: str, output_path: str, subtitle_mode: str = "whisper"):
    if subtitle_mode == "edge": _generate_audio_edge(text, voice, output_path)
    else: _generate_audio_kokoro(text, voice, output_path)

def _generate_audio_kokoro(text: str, voice: str, output_path: str):
    from kokoro import KPipeline
    import soundfile as sf
    import numpy as np
    pipeline = KPipeline(lang_code='p')
    all_audio = [audio for i, (gs, ps, audio) in enumerate(pipeline(text, voice=voice, speed=1.0)) if audio is not None]
    if not all_audio: raise Exception("Kokoro TTS n�o gerou nenhum �udio.")
    sf.write(output_path, np.concatenate(all_audio), 24000)

def _generate_audio_edge(text: str, voice: str, output_path: str):
    import edge_tts
    edge_voice_map = {"pm_alex": "pt-BR-AntonioNeural", "pm_santa": "pt-BR-PlatformNeural", "pf_dora": "pt-BR-FranciscaNeural"}
    edge_voice = edge_voice_map.get(voice, "pt-BR-AntonioNeural")
    tmp_mp3 = output_path.replace(".wav", "_edge.mp3")
    async def _run():
        communicate = edge_tts.Communicate(text, edge_voice)
        submaker = edge_tts.SubMaker()
        with open(tmp_mp3, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary": submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
        with open(output_path.replace(".wav", "_edge.vtt"), "w", encoding="utf-8") as f: f.write(submaker.generate_subs())
    try: asyncio.run(_run())
    except RuntimeError: pass
    subprocess.run(["ffmpeg", "-y", "-i", tmp_mp3, "-acodec", "pcm_s16le", "-ar", "24000", output_path], check=True, capture_output=True)
    try: os.remove(tmp_mp3)
    except: pass

def generate_subtitles(audio_path: str, srt_path: str, mode: str = "whisper", language: str = "pt-BR", edge_vtt_path: str = None, script_text: str = None, voice: str = None):
    if mode == "edge": _generate_subtitles_edge(audio_path, srt_path, edge_vtt_path)
    else: _generate_subtitles_whisper(audio_path, srt_path, language)

def _generate_subtitles_whisper(audio_path: str, srt_path: str, language: str = "pt-BR"):
    import whisper
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path, language=language.split("-")[0])
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result.get("segments", []), 1):
            f.write(f"{i}\n{_seconds_to_srt_time(seg['start'])} --> {_seconds_to_srt_time(seg['end'])}\n{seg['text'].strip()}\n\n")

def _generate_subtitles_edge(audio_path: str, srt_path: str, vtt_path: str = None):
    vtt = vtt_path or audio_path.replace(".wav", "_edge.vtt")
    if os.path.exists(vtt): _vtt_to_srt(vtt, srt_path)
    else: raise Exception("VTT n�o encontrado.")

def _vtt_to_srt(vtt_path: str, srt_path: str):
    with open(vtt_path, "r", encoding="utf-8") as f: lines = f.read().strip().split("\n")
    entries, i = [], 0
    while i < len(lines) and "-->" not in lines[i]: i += 1
    idx = 1
    while i < len(lines):
        if "-->" in lines[i]:
            parts = lines[i].split("-->")
            start, end = parts[0].strip().replace(".",","), parts[1].strip().replace(".",",")
            i += 1; text = []
            while i < len(lines) and lines[i].strip() and "-->" not in lines[i]: text.append(lines[i].strip()); i += 1
            if text: entries.append(f"{idx}\n{start} --> {end}\n{' '.join(text)}\n"); idx += 1
        else: i += 1
    with open(srt_path, "w", encoding="utf-8") as f: f.write("\n".join(entries))

def _seconds_to_srt_time(s: float) -> str:
    return f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d},{int((s%1)*1000):03d}"
