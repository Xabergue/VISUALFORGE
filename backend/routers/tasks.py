# -*- coding: utf-8 -*-
"""
Router de Tasks — CRUD + SSE para tarefas de geração de vídeo.
"""

import os
import json
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.task import Task
from pipeline import get_pipeline

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# ==============================================================
# Schemas Pydantic
# ==============================================================

class TaskCreate(BaseModel):
    style: str  # stock_footage | image_carousel | reddit_story | talking_head
    subject: str
    config: Optional[dict] = None


class TaskResponse(BaseModel):
    id: str
    style: str
    subject: str
    config: Optional[str] = None
    status: str
    progress: int
    log: Optional[str] = None
    output_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==============================================================
# Funções auxiliares
# ==============================================================

def run_pipeline(task_id: str):
    """
    Executa o pipeline de geração de vídeo em background.
    Cria uma nova sessão do banco para a task em background.
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        # Marcar como running
        task.status = "running"
        task.append_log("Iniciando pipeline de geração...", db)

        # Obter pipeline correto e executar
        pipeline = get_pipeline(task.style)
        pipeline.run(task, db)

    except Exception as e:
        # Garantir que a task seja marcada como failed
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task and task.status not in ("done", "failed"):
                task.status = "failed"
                task.log = (task.log or "") + f"Erro fatal no pipeline: {str(e)}\n"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


# ==============================================================
# Endpoints
# ==============================================================

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Cria uma nova tarefa de geração de vídeo e inicia o pipeline em background.
    """
    # Validar estilo
    valid_styles = ["stock_footage", "image_carousel", "reddit_story", "talking_head"]
    if task_data.style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Estilo inválido: {task_data.style}. Estilos válidos: {valid_styles}",
        )

    # Criar task no banco
    task = Task(
        style=task_data.style,
        subject=task_data.subject,
        config=json.dumps(task_data.config) if task_data.config else None,
        status="pending",
        progress=0,
        log="",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Iniciar pipeline em background
    background_tasks.add_task(run_pipeline, task.id)

    return _task_to_response(task)


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    """
    Lista todas as tarefas ordenadas por data de criação (mais recentes primeiro).
    """
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    return [_task_to_response(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Obtém detalhes de uma tarefa específica.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return _task_to_response(task)


@router.get("/{task_id}/stream")
async def stream_task(task_id: str):
    """
    SSE (Server-Sent Events) para acompanhamento em tempo real do progresso.
    Emite eventos a cada segundo enquanto a tarefa estiver pending/running,
    e um evento final quando estiver done/failed.
    """
    from database import SessionLocal

    async def event_generator():
        while True:
            db = SessionLocal()
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    data = json.dumps({"status": "not_found", "progress": 0, "log": "Tarefa não encontrada"})
                    yield f"data: {data}\n\n"
                    break

                data = json.dumps({
                    "status": task.status,
                    "progress": task.progress,
                    "log": task.log,
                })
                yield f"data: {data}\n\n"

                if task.status in ("done", "failed"):
                    break
            finally:
                db.close()

            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    Remove uma tarefa e seu arquivo de vídeo associado.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    # Remover arquivo de vídeo se existir
    if task.output_path:
        video_path = os.path.join(OUTPUT_DIR, task.output_path)
        if os.path.exists(video_path):
            os.remove(video_path)

    # Remover diretório da tarefa se existir
    task_dir = os.path.join(OUTPUT_DIR, task_id)
    if os.path.exists(task_dir):
        import shutil
        shutil.rmtree(task_dir)

    # Remover do banco
    db.delete(task)
    db.commit()

    return {"message": "Tarefa removida com sucesso", "id": task_id}


@router.get("/{task_id}/video")
def serve_video(task_id: str, db: Session = Depends(get_db)):
    """
    Serve o arquivo de vídeo gerado para streaming.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    if task.status != "done" or not task.output_path:
        raise HTTPException(status_code=404, detail="Vídeo não disponível")

    video_path = os.path.join(OUTPUT_DIR, task.output_path)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=task.output_path,
    )


# ==============================================================
# Funções auxiliares
# ==============================================================

def _task_to_response(task: Task) -> TaskResponse:
    """Converte um objeto Task para TaskResponse."""
    return TaskResponse(
        id=task.id,
        style=task.style,
        subject=task.subject,
        config=task.config,
        status=task.status,
        progress=task.progress,
        log=task.log,
        output_path=task.output_path,
        created_at=task.created_at.isoformat() if task.created_at else None,
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
    )
