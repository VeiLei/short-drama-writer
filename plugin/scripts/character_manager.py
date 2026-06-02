"""Read/write character card files in 设定集/角色档案/."""

import os
import re


class CharacterManager:
    def __init__(self, project_root: str):
        self.char_dir = os.path.join(project_root, "设定集", "角色档案")
        os.makedirs(self.char_dir, exist_ok=True)

    def list_characters(self) -> list[str]:
        """List all character names (from filenames)."""
        chars = []
        for fname in os.listdir(self.char_dir):
            if fname.endswith(".md"):
                # Strip prefix like "主角-" or "反派-"
                name = re.sub(r"^(主角|反派|配角|女主|男主)-", "", fname)
                name = name.replace(".md", "")
                chars.append(name)
        return sorted(chars)

    def get_character(self, name: str) -> str | None:
        """Read a character card by name. Returns markdown content."""
        for fname in os.listdir(self.char_dir):
            if name in fname and fname.endswith(".md"):
                fpath = os.path.join(self.char_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    return f.read()
        return None

    def save_character(self, name: str, content: str, role: str = "角色"):
        """Save or update a character card."""
        safe_name = name.replace("/", "_")
        fname = f"{role}-{safe_name}.md"
        fpath = os.path.join(self.char_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        return fpath

    def get_character_summary(self, name: str) -> dict | None:
        """Extract key fields from character card as dict."""
        content = self.get_character(name)
        if not content:
            return None

        summary = {"name": name}
        current_section = None
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                current_section = line[3:]
            elif current_section == "外貌锚点" and "|" in line and "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0] != "属性":
                    summary[parts[0]] = parts[1]
            elif current_section == "禁忌行为" and line.startswith("- "):
                summary.setdefault("forbidden_behaviors", []).append(line[2:])
        return summary
