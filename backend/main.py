import os, threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from database import init_db
from routers import tasks, styles

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    base = os.path.dirname(os.path.abspath(__file__))
    for d in [os.getenv("OUTPUT_DIR", "./output"), os.getenv("LOCAL_MEDIA_DIR", "./resource/local_media"), "resource/fonts", "resource/songs"]:
        os.makedirs(os.path.join(base, d), exist_ok=True)
    print("? VisualForge Backend iniciado!")
    yield

app = FastAPI(title="VisualForge", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(tasks.router)
app.include_router(styles.router)

def run_pipeline_background(task_id: str):
    def _run():
        from pipeline import get_pipeline
        from database import SessionLocal
        from models.task import Task
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        if not task: return
        pipeline = get_pipeline(task.style)
        if pipeline: pipeline.run(task_id)
        else:
            from pipeline.base import BasePipeline
            BasePipeline().mark_failed(task_id, f"Pipeline não encontrado: {task.style}")
    threading.Thread(target=_run, daemon=True).start()

@app.get("/api/health")
async def health(): return {"status": "ok"}
