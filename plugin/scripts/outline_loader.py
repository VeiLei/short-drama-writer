"""Load episode outline data."""

import json
import os
import re


class OutlineLoader:
    def __init__(self, project_root: str):
        self.outline_dir = os.path.join(project_root, "大纲")
        self.outline_path = os.path.join(self.outline_dir, "分集大纲.md")

    def get_all_outlines_json(self) -> str:
        """Return the full outline file content."""
        if not os.path.exists(self.outline_path):
            return "{}"
        with open(self.outline_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Parse markdown into structured dict
        episodes = {}
        current_ep = None
        current_section = None
        for line in content.split("\n"):
            ep_match = re.match(r"^## 第(\d{4})集", line)
            if ep_match:
                current_ep = ep_match.group(1)
                episodes[current_ep] = {}
                current_section = None
            elif current_ep and line.startswith("### "):
                current_section = line[4:]
                episodes[current_ep][current_section] = ""
            elif current_ep and current_section:
                episodes[current_ep][current_section] += line + "\n"
        return json.dumps(episodes, ensure_ascii=False, indent=2)

    def get_episode_outline(self, ep_num: str) -> str:
        """Get outline for a specific episode as markdown."""
        if not os.path.exists(self.outline_path):
            return ""
        with open(self.outline_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract the section for this episode
        pattern = rf"(## 第{ep_num}集.*?)(?=\n## 第|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else ""
