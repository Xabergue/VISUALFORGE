import os, subprocess, json, shutil

def assemble_video(clips, audio_path, srt_path, output_path, orientation="landscape", music_path=None, subtitle_position="bottom", subtitle_font_path=None, music_volume=0.15):
    w, h = (1080, 1920) if orientation == "portrait" else (1920, 1080)
    tmp = os.path.join(os.path.dirname(output_path), "tmp_assemble")
    os.makedirs(tmp, exist_ok=True)
    try:
        dur = _get_duration(audio_path)
        clip_dur = dur / len(clips) if clips else dur
        preps = []
        for i, c in enumerate(clips):
            p = os.path.join(tmp, f"clip_{i:03d}.mp4")
            ext = os.path.splitext(c)[1].lower()
            if ext in {".jpg", ".jpeg", ".png"}: _img2vid(c, p, w, h, clip_dur)
            else: _prep_vid(c, p, w, h, clip_dur)
            preps.append(p)
        concat = os.path.join(tmp, "concat.mp4")
        _concat(preps, concat)
        _merge(concat, audio_path, srt_path, output_path, music_path, music_volume, subtitle_position, w, h)
    finally: shutil.rmtree(tmp, ignore_errors=True)

def _get_duration(fp):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", fp], capture_output=True, text=True, timeout=30)
    try: return float(json.loads(r.stdout)["format"]["duration"])
    except: return 0.0

def _img2vid(img, out, w, h, dur):
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", str(dur), "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", "25", "-an", out], capture_output=True, text=True, timeout=120, check=True)

def _prep_vid(clip, out, w, h, dur):
    od = _get_duration(clip) or dur
    if od < dur:
        subprocess.run(["ffmpeg", "-y", "-stream_loop", str(int(dur/od)+1), "-i", clip, "-t", str(dur), "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an", out], capture_output=True, text=True, timeout=120, check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-i", clip, "-t", str(dur), "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", "-an", out], capture_output=True, text=True, timeout=120, check=True)

def _concat(clips, out):
    lst = out.replace(".mp4", "_list.txt")
    with open(lst, "w") as f:
        for c in clips: f.write(f"file '{c.replace(chr(92), '/').replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], capture_output=True, text=True, timeout=120)
    try: os.remove(lst)
    except: pass

def _merge(vid, aud, srt, out, music, mvol, spos, w, h):
    align = {"bottom": 2, "top": 8, "middle": 5}.get(spos, 2)
    mv = 30 if spos != "middle" else h//2 - 40
    esc = srt.replace("\\", "/").replace(":", "\\:")
    sub_f = f"subtitles='{esc}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2,Shadow=1,Alignment={align},MarginV={mv}'"
    cmd = ["ffmpeg", "-y", "-i", vid, "-i", aud]
    if music: cmd.extend(["-i", music])
    cmd.extend(["-vf", sub_f, "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"])
    if music:
        cmd.extend(["-filter_complex", f"[1:a]aresample=44100[n];[2:a]aresample=44100,volume={mvol}[m];[n][m]amix=inputs=2:duration=longest[o]", "-map", "0:v", "-map", "[o]"])
    else:
        cmd.extend(["-map", "0:v", "-map", "1:a"])
    cmd.extend(["-movflags", "+faststart", out])
    subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True)
