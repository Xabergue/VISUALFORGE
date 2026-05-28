# -*- coding: utf-8 -*-
import json
from database import SessionLocal
from models.task import Task

class BasePipeline:
    def run(self, task_id: str):
        raise NotImplementedError("Subclasses devem implementar run()")

    def _update_task(self, task_id: str, **kwargs):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key): setattr(task, key, value)
                db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    def update_progress(self, task_id: str, progress: int, message: str):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.progress = min(max(progress, 0), 100)
                task.log = (task.log + "\n" + message).strip()
                task.status = "running"
                db.commit()
        except: db.rollback()
        finally: db.close()

    def mark_failed(self, task_id: str, error_message: str):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "failed"
                task.log = (task.log + "\n" + f"ERRO: {error_message}").strip()
                db.commit()
        except: db.rollback()
        finally: db.close()

    def mark_done(self, task_id: str, output_path: str):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "done"
                task.progress = 100
                task.output_path = output_path
                task.log = (task.log + "\nV�deo gerado com sucesso!").strip()
                db.commit()
        except: db.rollback()
        finally: db.close()
