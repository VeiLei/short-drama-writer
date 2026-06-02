"""Project management API routes (stub — full CRUD to be fleshed out)."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/")
async def list_projects():
    return {"projects": []}


@router.get("/{project_id}")
async def get_project(project_id: int):
    return {"id": project_id, "title": "stub"}
