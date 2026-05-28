@echo off
echo === VisualForge — Instalacao ===
echo.
echo [1/4] Instalando uv (gerenciador Python)...
powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
echo.
echo [2/4] Instalando dependencias Python...
cd backend
uv venv
uv pip install -r requirements.txt
cd ..
echo.
echo [3/4] Instalando dependencias frontend...
cd frontend
npm install
cd ..
echo.
echo [4/4] Verificando FFmpeg...
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo FFmpeg nao encontrado. Baixando via winget...
    winget install --id Gyan.FFmpeg -e --source winget
) else (
    echo FFmpeg ja instalado.
)
echo.
echo === Instalacao concluida! ===
echo Copie backend\.env.example para backend\.env e configure suas chaves.
pause
