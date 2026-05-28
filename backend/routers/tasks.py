import os, json, asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from pipeline import get_pipeline

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("")
async def create_task(body: dict, db: Session = Depends(get_db)):
    style = body.get("style")
    subject = body.get("subject")
    config = body.get("config", {})
    if not style or not subject:
        raise HTTPException(status_code=400, detail="Campos 'style' e 'subject' são obrigatórios.")
    from routers.styles import STYLES
    valid_ids = [s["id"] for s in STYLES]
    if style not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Estilo inválido: {style}")
    task = Task(style=style, subject=subject.strip(), config=json.dumps(config, ensure_ascii=False))
    db.add(task)
    db.commit()
    db.refresh(task)
    pipeline = get_pipeline(style)
    if pipeline:
        from main import run_pipeline_background
        run_pipeline_background(task.id)
    return _task_to_dict(task)

@router.get("")
async def list_tasks(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(limit).all()
    return [_task_to_dict(t) for t in tasks]

@router.get("/{task_id}")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Task não encontrada.")
    return _task_to_dict(task)

@router.get("/{task_id}/stream")
async def stream_task(task_id: str, db: Session = Depends(get_db)):
    async def event_generator():
        count = 0
        while count < 3600:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                yield f"data: {json.dumps({'error': 'Task não encontrada'})}\n\n"
                break
            data = json.dumps({"status": task.status, "progress": task.progress, "log": task.log}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            if task.status in ("done", "failed"): break
            await asyncio.sleep(1)
            count += 1
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Task não encontrada.")
    if task.output_path and os.path.exists(task.output_path):
        try: os.remove(task.output_path)
        except: pass
    task_tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", task_id)
    if os.path.isdir(task_tmp):
        import shutil
        shutil.rmtree(task_tmp, ignore_errors=True)
    db.delete(task)
    db.commit()
    return {"detail": "Task deletada com sucesso."}

@router.get("/{task_id}/video")
async def serve_video(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Task não encontrada.")
    if not task.output_path or not os.path.exists(task.output_path):
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado.")
    return FileResponse(task.output_path, media_type="video/mp4", filename=f"visualforge_{task.style}_{task_id[:8]}.mp4")

def _task_to_dict(task: Task) -> dict:
    return {
        "id": task.id, "style": task.style, "subject": task.subject,
        "config": json.loads(task.config) if task.config else {},
        "status": task.status, "progress": task.progress, "log": task.log,
        "output_path": task.output_path,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }
