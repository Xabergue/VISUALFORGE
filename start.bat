@echo off
echo Iniciando VisualForge...
start "VisualForge Backend" cmd /k start-backend.bat
timeout /t 2 >nul
start "VisualForge Frontend" cmd /k start-frontend.bat
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs API: http://localhost:8000/docs
