@echo off
title CNMOVI v7.0 - Telegram Cinema Ecosystem & AI Streaming Platform
echo ======================================================================
echo   CNMOVI v7.0 - Ultra-Lightweight Mode (Faqat ~65 MB RAM sarflaydi!)
echo ======================================================================
echo Tizim ishga tushirilmoqda: http://127.0.0.1:8000
start "" "http://127.0.0.1:8000"
cd /d %~dp0backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
