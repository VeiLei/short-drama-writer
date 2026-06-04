"""Project management API routes."""

import json
import os
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from app.config import config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["projects"])


def _scan_projects(base_dir: str) -> list[dict]:
    """Scan base_dir subdirectories for drama projects (those containing .drama/state.json)."""
    base = Path(base_dir).resolve()
    if not base.is_dir():
        raise HTTPException(400, f"Directory not found: {base_dir}")

    projects = []
    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        state_path = entry / ".drama" / "state.json"
        if not state_path.is_file():
            continue

        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        assets = {}
        assets_path = entry / ".drama" / "assets.json"
        if assets_path.is_file():
            try:
                assets = json.loads(assets_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        projects.append({
            "title": state.get("project_title", entry.name),
            "path": str(entry),
            "phase": state.get("phase", "init"),
            "current_episode": state.get("current_episode", 0),
            "total_episodes": state.get("total_episodes", 100),
            "stats": state.get("stats", {
                "episodes_written": 0,
                "episodes_reviewed": 0,
                "shots_generated": 0,
            }),
            "characters": list(assets.get("characters", {}).keys()),
            "scenes": list(assets.get("scenes", {}).keys()),
            "assets": assets,
            "last_updated": state.get("last_updated", ""),
        })

    return projects


@router.get("/overview")
async def project_overview(
    projects_root: str = Query(default="", description="Base directory to scan for drama projects")
):
    """Scan for drama projects and return aggregated overview."""
    root = projects_root or config.STORAGE_DIR or str(Path.cwd())
    projects = _scan_projects(root)
    return {"projects": projects, "count": len(projects)}


@router.get("/")
async def list_projects():
    return {"projects": []}


@router.get("/{project_id}")
async def get_project(project_id: int):
    return {"id": project_id, "title": "stub"}
