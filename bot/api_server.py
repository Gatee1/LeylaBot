# api_server.py
import uvicorn
from bot.api import app  # ← импортируем FastAPI приложение из api.py

if __name__ == "__main__":
    print("🚀 Starting Leyla API server on http://0.0.0.0:7328")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7328,
        log_level="info",
        reload=False  # важно выключить на проде
    )