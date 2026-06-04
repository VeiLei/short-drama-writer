"""Read/write memory files for cross-episode consistency."""

import json
import os


class MemoryManager:
    def __init__(self, project_root: str):
        self.mem_dir = os.path.join(project_root, "记忆")
        os.makedirs(self.mem_dir, exist_ok=True)

    def _read_json(self, filename: str) -> dict | list:
        fpath = os.path.join(self.mem_dir, filename)
        if not os.path.exists(fpath):
            return {}
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, filename: str, data):
        fpath = os.path.join(self.mem_dir, filename)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_character_states(self) -> list:
        return self._read_json("角色状态变迁.json")

    def get_character_states_json(self) -> str:
        return json.dumps(self.get_character_states(), ensure_ascii=False, indent=2)

    def update_character_state(self, episode_id: str, character_name: str,
                                state: dict, changes: list[str]):
        """Append a new state snapshot for a character after an episode."""
        states = self.get_character_states()
        entry = {
            "episode": episode_id,
            "character": character_name,
            "state": state,
            "changes": changes
        }
        states.append(entry)
        self._write_json("角色状态变迁.json", states)

    def get_foreshadowing(self) -> list:
        return self._read_json("伏笔追踪.json")

    def get_foreshadowing_json(self) -> str:
        return json.dumps(self.get_foreshadowing(), ensure_ascii=False, indent=2)

    def update_foreshadowing(self, foreshadowing_list: list):
        """Replace foreshadowing list entirely after data-agent extraction."""
        self._write_json("伏笔追踪.json", foreshadowing_list)

    def get_scene_states(self) -> list:
        return self._read_json("场景状态.json")

    def update_scene_state(self, scene_name: str, episode_id: str, changes: dict):
        states = self.get_scene_states()
        states.append({
            "scene": scene_name,
            "episode": episode_id,
            "changes": changes
        })
        self._write_json("场景状态.json", states)

    def get_costume_tracking(self) -> dict:
        return self._read_json("道具-服装追踪.json")

    def update_costume(self, character: str, outfit: str, episode_id: str):
        tracking = self.get_costume_tracking()
        tracking[character] = {
            "current_outfit": outfit,
            "last_updated_episode": episode_id
        }
        self._write_json("道具-服装追踪.json", tracking)

    def get_summary(self) -> str:
        """Return a compact summary of all memory for context-agent."""
        parts = []

        char_states = self.get_character_states()
        if char_states:
            # Get latest state per character
            latest = {}
            for entry in char_states:
                latest[entry["character"]] = entry
            parts.append("## 角色当前状态")
            for char, entry in latest.items():
                parts.append(f"- {char} (第{entry['episode']}集后): {json.dumps(entry['state'], ensure_ascii=False)}")

        foreshadowing = self.get_foreshadowing()
        if foreshadowing:
            active = [f for f in foreshadowing if f.get("status") != "resolved"]
            if active:
                parts.append("## 未闭合伏笔")
                for fb in active:
                    parts.append(f"- [{fb.get('id')}] {fb.get('content')} (埋设于第{fb.get('planted_in')}集)")

        costumes = self.get_costume_tracking()
        if costumes:
            parts.append("## 当前服装状态")
            for char, info in costumes.items():
                parts.append(f"- {char}: {info['current_outfit']} (第{info['last_updated_episode']}集)")

        return "\n\n".join(parts) if parts else "(无记忆数据)"
