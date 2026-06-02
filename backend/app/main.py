"""FastAPI application entry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="short-drama-writer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .api import generate, projects

app.include_router(generate.router)
app.include_router(projects.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
