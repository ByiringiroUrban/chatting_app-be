import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 Server running at: http://{settings.HOST}:{settings.PORT}")
    print(f"📖 Interactive Swagger Docs: http://localhost:{settings.PORT}/docs")
    print(f"🔌 WebSocket URL: ws://localhost:{settings.PORT}/ws/{{user_id}}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
