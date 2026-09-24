@echo off
title EV Battery Health Management System Launcher
echo Starting EV Battery Backend & Frontend Servers...

cd /d "%~dp0"

:: Start Backend Server silently in a new window
start "EV BMS Backend" /min .\.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000

:: Start Frontend Server silently in a new window
start "EV BMS Frontend" /min .\.venv\Scripts\python.exe -m http.server 8080 --directory frontend

echo =======================================================
echo   EV Battery System Servers are now running!
echo   Dashboard: http://127.0.0.1:8080
echo   Backend API: http://127.0.0.1:8000
echo =======================================================
timeout /t 3 >nul
