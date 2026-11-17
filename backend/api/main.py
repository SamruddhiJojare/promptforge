from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.session import engine, Base
from backend.database import models  # noqa: F401 - registers models with Base
from backend.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PromptForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}