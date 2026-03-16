from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, applications, documents, reminders, websocket

app = FastAPI(title="DevTrack")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(documents.router, prefix="/applications", tags=["documents"])
app.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
