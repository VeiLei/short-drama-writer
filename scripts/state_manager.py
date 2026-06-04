"""Read/write .drama/state.json projection."""

import json
import os
from datetime import datetime


class StateManager:
    def __init__(self, project_root: str):
        self.root = project_root
        self.state_dir = os.path.join(project_root, ".drama")
        self.state_path = os.path.join(self.state_dir, "state.json")
        os.makedirs(self.state_dir, exist_ok=True)
        if not os.path.exists(self.state_path):
            self._write_default()

    def _write_default(self):
        default = {
            "project_title": "",
            "current_episode": 0,
            "total_episodes": 100,
            "phase": "init",  # init | plan | writing | generate | done
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "episodes_written": 0,
                "episodes_reviewed": 0,
                "shots_generated": 0
            }
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

    def get_state(self) -> dict:
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_state_json(self) -> str:
        return json.dumps(self.get_state(), ensure_ascii=False, indent=2)

    def update(self, key: str, value):
        state = self.get_state()
        # support dot notation: "stats.episodes_written"
        keys = key.split(".")
        target = state
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = self._parse_value(value)
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _parse_value(self, value: str):
        if value.isdigit():
            return int(value)
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        return value

    def advance_phase(self, new_phase: str):
        self.update("phase", new_phase)
