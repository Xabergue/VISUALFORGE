import os, httpx
from dotenv import load_dotenv
load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
LOCAL_MEDIA_DIR = os.getenv("LOCAL_MEDIA_DIR", "./resource/local_media")
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

def search_media(keywords: list, task_dir: str, orientation: str = "landscape") -> str:
    local = _search_local_media(keywords)
    if local: return local
    return _search_pexels(keywords, task_dir, orientation)

def _search_local_media(keywords: list) -> str:
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", LOCAL_MEDIA_DIR)
    if not os.path.isdir(base_dir): return None
    all_files = [os.path.join(r, f) for r, d, fs in os.walk(base_dir) for f in fs if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS]
    for kw in keywords:
        for fp in all_files:
            if kw.lower() in os.path.basename(fp).lower(): return fp
    return None

def _search_pexels(keywords: list, task_dir: str, orientation: str) -> str:
    if not PEXELS_API_KEY: return None
    for kw in keywords:
        try:
            r = httpx.get("https://api.pexels.com/videos/search", params={"query": kw, "per_page": 5, "orientation": orientation}, headers={"Authorization": PEXELS_API_KEY}, timeout=15.0)
            if r.status_code != 200: continue
            videos = r.json().get("videos", [])
            if not videos: continue
            best = min(videos[0].get("video_files", []), key=lambda x: x.get("width", 9999))
            if not best.get("link"): continue
            out = os.path.join(task_dir, f"pexels_{kw}_{videos[0]['id']}.mp4")
            vr = httpx.get(best["link"], timeout=60.0, follow_redirects=True)
            if vr.status_code == 200:
                with open(out, "wb") as f: f.write(vr.content)
                return out
        except: pass
    return None
