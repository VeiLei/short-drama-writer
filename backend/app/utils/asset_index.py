"""本地 Asset 索引 — 轻量 JSON 文件追踪已生成素材及 TOS URL。

不依赖 MySQL，直接读写项目目录下的 .drama/assets.json。
"""

import json
import os
from datetime import datetime
from pathlib import Path


class AssetIndex:
    """管理项目素材索引。每个短剧项目一个索引文件。"""

    def __init__(self, project_root: str):
        self.index_dir = os.path.join(project_root, ".drama")
        self.index_path = os.path.join(self.index_dir, "assets.json")
        os.makedirs(self.index_dir, exist_ok=True)
        if not os.path.exists(self.index_path):
            self._write({})

    def _read(self) -> dict:
        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict):
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, asset_type: str, related_id: str, tos_url: str = "",
            local_path: str = "", prompt: str = "", metadata: dict = None) -> str:
        """添加一条素材记录，返回 asset_id。

        Args:
            asset_type: character_image | scene_image | video
            related_id: 角色名/场景名/镜头ID
            tos_url: TOS 公网 URL
            local_path: 本地文件路径
            prompt: 生成所用的提示词
            metadata: 额外元数据
        """
        data = self._read()
        assets = data.setdefault("assets", [])
        asset_id = f"{asset_type}/{related_id}"
        assets.append({
            "asset_id": asset_id,
            "asset_type": asset_type,
            "related_id": related_id,
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        })
        data["updated_at"] = datetime.now().isoformat()
        self._write(data)
        return asset_id

    def get_by_related(self, related_id: str) -> list[dict]:
        """按 related_id 查询素材。"""
        data = self._read()
        return [a for a in data.get("assets", []) if a["related_id"] == related_id]

    def get_tos_urls(self, related_ids: list[str]) -> list[str]:
        """批量获取 TOS URL。用于构建 reference_images。"""
        data = self._read()
        urls = []
        for a in data.get("assets", []):
            if a["related_id"] in related_ids and a.get("tos_url"):
                urls.append(a["tos_url"])
        return urls

    def get_all_characters(self) -> dict[str, str]:
        """返回 {角色名: tos_url} 映射。"""
        data = self._read()
        return {
            a["related_id"]: a["tos_url"]
            for a in data.get("assets", [])
            if a["asset_type"] == "character_image" and a.get("tos_url")
        }

    def get_all_scenes(self) -> dict[str, str]:
        """返回 {场景名: tos_url} 映射。"""
        data = self._read()
        return {
            a["related_id"]: a["tos_url"]
            for a in data.get("assets", [])
            if a["asset_type"] == "scene_image" and a.get("tos_url")
        }

    def to_dict(self) -> dict:
        return self._read()
