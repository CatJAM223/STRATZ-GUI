import subprocess
import sys
import os
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "app" / "backend"
FRONTEND_DIR = BASE_DIR / "app" / "frontend"

os.chdir(BACKEND_DIR)

print("=" * 50)
print("   DOTA 2 PLAYER STATS OVERLAY")
print("=" * 50)
print()

print("[1/2] Запуск бэкенда...")
backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001", "--reload"],
    cwd=str(BACKEND_DIR)
)

time.sleep(3)

print("[2/2] Запуск фронтенда...")
frontend = subprocess.Popen(
    [sys.executable, "main.py"],
    cwd=str(FRONTEND_DIR)
)

print()
print("=" * 50)
print("   ✅ ЗАПУЩЕНО!")
print("   Бэкенд: http://127.0.0.1:8001")
print("   Закрой окно для выхода")
print("=" * 50)

frontend.wait()
backend.terminate()