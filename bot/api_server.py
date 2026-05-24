# api_server.py
import sys
import os

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
from bot.api import app

if __name__ == "__main__":
    print("🚀 Starting Leyla API server on http://0.0.0.0:7328")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7328,
        log_level="info"
    )