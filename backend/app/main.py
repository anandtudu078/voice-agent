from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import websocket

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-time voice-first AI software engineer backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our WebSocket router
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Leo Voice Agent backend is up and running successfully!"
    }