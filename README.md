# CNMOVI — Telegram Cinema Ecosystem & AI Streaming Platform (PRD v7.0 Definitive Architecture)

Ushbu loyiha **PRD v6.0** texnik topshirig'idagi barcha modullarni + **PRD v7.0 Eksklyuziv funksiyalarini** o'z ichiga olgan to'liq ekotizimdir. Maxsus ravishda **4 GB RAM (AMD Ryzen 3)** kompyuterda qotmasdan ishlash uchun **Dual-Engine Lightweight Mode** va server uchun **PostgreSQL 16 + Nginx Blue-Green** arxitekturasida qurilgan.

## 🚀 Ishga tushirish (1-bosishda):
`start_cnmovi.bat` faylini ikki marta bosing yoki terminalda:

1. **Backend (FastAPI + Aiogram 3 Bot + SQLite/PostgreSQL):**
   ```powershell
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. **Frontend (Telegram Mini App + Admin CMS):**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
   So'ngra brauzerda **http://localhost:5173** manzilini oching!
