# -*- coding: utf-8 -*-
"""
VisualForge Backend — FastAPI entrypoint.
Serviço local de geração automática de vídeos.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

from database import engine, Base
from routers import tasks, styles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle da aplicação — cria tabelas do banco ao iniciar.
    """
    # Criar todas as tabelas no banco de dados
    Base.metadata.create_all(bind=engine)
    print("[VisualForge] Banco de dados inicializado.")

    # Garantir que o diretório de output existe
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)

    # Garantir que o diretório de mídia local existe
    local_media_dir = os.getenv("LOCAL_MEDIA_DIR", "./resource/local_media")
    os.makedirs(local_media_dir, exist_ok=True)

    print("[VisualForge] Diretórios verificados.")
    print("[VisualForge] Backend pronto para receber requisições.")

    yield

    print("[VisualForge] Encerrando backend...")


# Criar aplicação FastAPI
app = FastAPI(
    title="VisualForge",
    description="Serviço local de geração automática de vídeos",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS — permitir todas as origens para desenvolvimento local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(tasks.router)
app.include_router(tasks.preview_router)
app.include_router(styles.router)

# Montar diretório de output como arquivos estáticos para servir vídeos
output_dir = os.getenv("OUTPUT_DIR", "./output")
os.makedirs(output_dir, exist_ok=True)
app.mount("/api/videos", StaticFiles(directory=output_dir), name="videos")


# Endpoint de health check
@app.get("/api/health")
def health_check():
    """Verifica se o backend está rodando."""
    return {"status": "ok", "service": "VisualForge Backend"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
    )
