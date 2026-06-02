"""Initialize a new drama project directory."""

import json
import os
from datetime import datetime


DIRS = [
    ".drama",
    "设定集/角色档案",
    "设定集/场景档案",
    "大纲",
    "剧本",
    "分镜",
    "提示词",
    "素材/角色",
    "素材/场景",
    "素材/视频",
    "审查报告",
    "记忆",
    "导出",
]


def sanitize_dirname(title: str) -> str:
    """Remove chars unsafe for directory names."""
    unsafe = '<>:"/\\|?*'
    for ch in unsafe:
        title = title.replace(ch, "")
    return title.strip()[:80]


def init_project(title: str = None):
    cwd = os.getcwd()
    if title:
        project_dir = os.path.join(cwd, sanitize_dirname(title))
        os.makedirs(project_dir, exist_ok=True)
    else:
        project_dir = cwd

    for d in DIRS:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)

    # Write initial state.json
    state = {
        "project_title": title or os.path.basename(project_dir),
        "current_episode": 0,
        "total_episodes": 100,
        "phase": "init",
        "last_updated": datetime.now().isoformat(),
        "stats": {
            "episodes_written": 0,
            "episodes_reviewed": 0,
            "shots_generated": 0
        }
    }
    state_path = os.path.join(project_dir, ".drama", "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # Write empty memory files
    memory_files = {
        "角色状态变迁.json": [],
        "场景状态.json": [],
        "伏笔追踪.json": [],
        "道具-服装追踪.json": {}
    }
    for fname, default in memory_files.items():
        fpath = os.path.join(project_dir, "记忆", fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

    print(f"Project initialized at: {project_dir}")
    return project_dir


if __name__ == "__main__":
    import sys
    title = sys.argv[1] if len(sys.argv) > 1 else None
    init_project(title)
