"""本地 Asset 索引 — 轻量 JSON 文件追踪已生成素材。

角色资产：基础四视图 + 变装四视图（outfit 区分）
场景资产：全景参考图 (master) + 取景框 (shot_frame, parent=master)
"""

import json
import os
from datetime import datetime
from typing import Optional


class AssetIndex:
    def __init__(self, project_root: str):
        self.index_dir = os.path.join(project_root, ".drama")
        self.index_path = os.path.join(self.index_dir, "assets.json")
        os.makedirs(self.index_dir, exist_ok=True)
        if not os.path.exists(self.index_path):
            self._write({"characters": {}, "scenes": {}, "updated_at": ""})

    def _read(self) -> dict:
        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict):
        data["updated_at"] = datetime.now().isoformat()
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── 角色 ─────────────────────────────────────────────────

    def add_character(self, name: str, tos_url: str, local_path: str = "",
                      outfit: str = "基础", is_base: bool = True, prompt: str = "") -> str:
        """添加角色四视图。outfit 区分基础版和变装版。"""
        data = self._read()
        chars = data.setdefault("characters", {})
        char_entry = chars.setdefault(name, {"variants": []})

        # 同 outfit 替换旧条目
        char_entry["variants"] = [
            v for v in char_entry["variants"] if v.get("outfit") != outfit
        ]
        variant = {
            "outfit": outfit,
            "is_base": is_base,
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
        }
        char_entry["variants"].append(variant)
        self._write(data)
        return f"{name}/{outfit}"

    def get_character_variant(self, name: str, outfit: str = "基础") -> Optional[dict]:
        """查询角色指定着装版本的四视图。"""
        data = self._read()
        char = data.get("characters", {}).get(name, {})
        for v in char.get("variants", []):
            if v.get("outfit") == outfit:
                return v
        return None

    def get_character_base(self, name: str) -> Optional[dict]:
        """查询角色基础四视图。"""
        return self.get_character_variant(name, "基础")

    def list_character_outfits(self, name: str) -> list[str]:
        """列出角色的所有着装版本。"""
        data = self._read()
        char = data.get("characters", {}).get(name, {})
        return [v.get("outfit", "") for v in char.get("variants", [])]

    def character_has_outfit(self, name: str, outfit: str) -> bool:
        return self.get_character_variant(name, outfit) is not None

    def get_character_tos_url(self, name: str, outfit: str = "基础") -> str:
        v = self.get_character_variant(name, outfit)
        return v["tos_url"] if v else ""

    # ── 场景 ─────────────────────────────────────────────────

    def add_scene_master(self, name: str, tos_url: str, local_path: str = "",
                         prompt: str = "", layout: Optional[dict] = None) -> str:
        """添加场景全景参考图。已存在则替换。
        若提供 layout，则一次性写入 master + spatial_layout。
        """
        data = self._read()
        scenes = data.setdefault("scenes", {})
        scene_entry = scenes.setdefault(name, {"master": None, "shot_frames": []})
        scene_entry["master"] = {
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
        }
        if layout is not None:
            scene_entry["spatial_layout"] = layout
        self._write(data)
        return f"{name}/master"

    def get_scene_master(self, name: str) -> Optional[dict]:
        data = self._read()
        scene = data.get("scenes", {}).get(name, {})
        return scene.get("master")

    def get_scene_master_url(self, name: str) -> str:
        m = self.get_scene_master(name)
        return m["tos_url"] if m else ""

    def add_scene_layout(self, name: str, layout: dict) -> str:
        """添加/替换场景的固定物空间布局。"""
        data = self._read()
        scenes = data.setdefault("scenes", {})
        scene_entry = scenes.setdefault(name, {"master": None, "shot_frames": []})
        scene_entry["spatial_layout"] = layout
        self._write(data)
        return f"{name}/layout"

    def get_scene_layout(self, name: str) -> Optional[dict]:
        data = self._read()
        scene = data.get("scenes", {}).get(name, {})
        return scene.get("spatial_layout")

    def get_fixed_object_ids(self, name: str) -> list[str]:
        """列出场景 spatial_layout 中所有 fixed_objects 和 walkable_zones 的 id。"""
        layout = self.get_scene_layout(name)
        if not layout:
            return []
        ids = [obj["id"] for obj in layout.get("fixed_objects", []) if "id" in obj]
        ids += [zone["id"] for zone in layout.get("walkable_zones", []) if "id" in zone]
        return ids

    def validate_spatial_anchors(self, scene_name: str, anchors: dict) -> tuple[list[str], list[str]]:
        """校验 spatial_anchors 键是否都在该场景的 layout 内。

        Returns:
            (valid_keys, invalid_keys) — 拆分两个列表便于报告
        """
        valid_ids = set(self.get_fixed_object_ids(scene_name))
        valid, invalid = [], []
        for key in anchors:
            (valid if key in valid_ids else invalid).append(key)
        return valid, invalid

    def add_shot_frame(self, scene_name: str, frame_id: str, frame_type: str,
                       tos_url: str, local_path: str = "", prompt: str = "") -> str:
        """添加场景取景框。frame_id 如 'coffee_bar_2shot'，parent 固定为 scene master。"""
        data = self._read()
        scenes = data.setdefault("scenes", {})
        scene_entry = scenes.setdefault(scene_name, {"master": None, "shot_frames": []})

        # 同 frame_id 替换
        scene_entry["shot_frames"] = [
            f for f in scene_entry["shot_frames"] if f.get("frame_id") != frame_id
        ]
        scene_entry["shot_frames"].append({
            "frame_id": frame_id,
            "frame_type": frame_type,
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
        })
        self._write(data)
        return f"{scene_name}/{frame_id}"

    def get_shot_frame(self, scene_name: str, frame_id: str) -> Optional[dict]:
        data = self._read()
        scene = data.get("scenes", {}).get(scene_name, {})
        for f in scene.get("shot_frames", []):
            if f.get("frame_id") == frame_id:
                return f
        return None

    def get_shot_frame_url(self, scene_name: str, frame_id: str) -> str:
        f = self.get_shot_frame(scene_name, frame_id)
        return f["tos_url"] if f else ""

    def list_scene_frames(self, scene_name: str) -> list[str]:
        data = self._read()
        scene = data.get("scenes", {}).get(scene_name, {})
        return [f.get("frame_id", "") for f in scene.get("shot_frames", [])]

    def has_shot_frame(self, scene_name: str, frame_id: str) -> bool:
        return self.get_shot_frame(scene_name, frame_id) is not None

    # ── 道具 ─────────────────────────────────────────────────

    def add_prop(self, name: str, tos_url: str, local_path: str = "",
                 scene_name: str = "", prompt: str = "") -> str:
        """添加道具参考图。同道具名替换旧条目。"""
        data = self._read()
        props = data.setdefault("props", {})
        props[name] = {
            "name": name,
            "tos_url": tos_url,
            "local_path": local_path,
            "scene_name": scene_name,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
        }
        self._write(data)
        return name

    def get_prop(self, name: str) -> Optional[dict]:
        data = self._read()
        return data.get("props", {}).get(name)

    def get_prop_tos_url(self, name: str) -> str:
        p = self.get_prop(name)
        return p["tos_url"] if p else ""

    def prop_exists(self, name: str) -> bool:
        return self.get_prop(name) is not None

    def list_props(self) -> list[str]:
        data = self._read()
        return list(data.get("props", {}).keys())

    # ── 批量查询 ──────────────────────────────────────────────

    def get_reference_urls(self, character_entries: list[dict],
                           scene_name: str, frame_id: str) -> dict:
        """一次查询拿到视频生成所需的全部 TOS URL。

        Args:
            character_entries: [{name, outfit}] 本镜头出场角色及着装
            scene_name: 场景名
            frame_id: 取景框ID

        Returns:
            {character_urls: [...], scene_url: str, missing: [...]}
        """
        result = {"character_urls": [], "scene_url": "", "missing": []}

        for entry in character_entries:
            url = self.get_character_tos_url(entry["name"], entry.get("outfit", "基础"))
            if url:
                result["character_urls"].append(url)
            else:
                result["missing"].append(f"角色:{entry['name']}/{entry.get('outfit', '基础')}")

        scene_url = self.get_shot_frame_url(scene_name, frame_id)
        if scene_url:
            result["scene_url"] = scene_url
        else:
            result["missing"].append(f"取景框:{scene_name}/{frame_id}")

        return result

    # ── 封面 ─────────────────────────────────────────────────

    def add_cover(self, name: str, tos_url: str, local_path: str, prompt: str):
        """记录一个视频封面。"""
        data = self._read()
        if "covers" not in data:
            data["covers"] = {}
        data["covers"][name] = {
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
        }
        self._write(data)

    def to_dict(self) -> dict:
        return self._read()
