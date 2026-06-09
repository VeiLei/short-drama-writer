"""跨镜头位置连续性校验。

检查两类问题：
1. invalid_key: spatial_anchors 键不在 scene.spatial_layout 内
2. object_appeared / object_disappeared: 同场景连续镜头中固定物出现/消失
"""

from typing import Optional


def _layout_id_set(layout: dict) -> set[str]:
    """从 layout 提取所有有效 id（含 fixed_objects 和 walkable_zones）。"""
    ids = {obj["id"] for obj in layout.get("fixed_objects", []) if "id" in obj}
    ids.update({z["id"] for z in layout.get("walkable_zones", []) if "id" in z})
    return ids


def check_anchor_validity(anchors: dict, layout: dict) -> list[dict]:
    """检查单个镜头的 spatial_anchors 是否全部来自 layout。"""
    valid_ids = _layout_id_set(layout)
    issues = []
    for key in anchors:
        if key not in valid_ids:
            issues.append({
                "type": "invalid_key",
                "key": key,
                "severity": "blocking",
                "message": f"空间锚点 '{key}' 不在 scene.spatial_layout 的 fixed_objects/walkable_zones 中"
            })
    return issues


def check_cross_shot_continuity(shots: list[dict], layout: dict) -> list[dict]:
    """检查同场景连续镜头的固定物连续性。

    shots: 同一场景的镜头列表（按 shot_id 顺序）
    """
    issues = []
    if len(shots) < 2:
        return issues

    for i in range(1, len(shots)):
        prev = shots[i - 1]
        curr = shots[i]
        prev_anchors = set(prev.get("spatial_anchors", {}).keys())
        curr_anchors = set(curr.get("spatial_anchors", {}).keys())

        disappeared = prev_anchors - curr_anchors
        appeared = curr_anchors - prev_anchors

        for key in disappeared:
            issues.append({
                "shot_id": curr.get("shot_id"),
                "type": "object_disappeared",
                "key": key,
                "severity": "warning",
                "message": f"固定物 '{key}' 在 {prev.get('shot_id')} 出现，{curr.get('shot_id')} 消失。请确认是否合理（摄影机切角度时可不出现）"
            })

        for key in appeared:
            issues.append({
                "shot_id": curr.get("shot_id"),
                "type": "object_appeared",
                "key": key,
                "severity": "blocking",
                "message": f"固定物 '{key}' 在 {prev.get('shot_id')} 未出现，{curr.get('shot_id')} 凭空出现。必须从 layout 派生，不允许凭空"
            })

    return issues


def check_episode(shots_by_scene: dict, layouts: dict) -> list[dict]:
    """校验整集。

    shots_by_scene: {scene_name: [shot_dict, ...]}
    layouts: {scene_name: layout_dict}
    """
    all_issues = []
    for scene_name, shots in shots_by_scene.items():
        layout = layouts.get(scene_name)
        if not layout:
            all_issues.append({
                "scene": scene_name,
                "type": "missing_layout",
                "severity": "blocking",
                "message": f"场景 '{scene_name}' 没有 spatial_layout，无法校验"
            })
            continue

        for shot in shots:
            anchors = shot.get("spatial_anchors", {})
            all_issues.extend(check_anchor_validity(anchors, layout))

        all_issues.extend(check_cross_shot_continuity(shots, layout))

    return all_issues


def format_report_markdown(issues: list[dict]) -> str:
    if not issues:
        return "# 站位校验报告\n\n✓ 全部通过，无问题\n"

    blocking = [i for i in issues if i.get("severity") == "blocking"]
    warnings = [i for i in issues if i.get("severity") == "warning"]

    lines = ["# 站位校验报告", ""]
    lines.append(f"共 {len(issues)} 处问题（{len(blocking)} blocking / {len(warnings)} warning）")
    lines.append("")

    if blocking:
        lines.append(f"## Blocking ({len(blocking)})")
        lines.append("")
        for i in blocking:
            shot = i.get("shot_id", i.get("scene", "?"))
            lines.append(f"- **{shot}** [{i['type']}] {i['message']}")
        lines.append("")

    if warnings:
        lines.append(f"## Warning ({len(warnings)})")
        lines.append("")
        for i in warnings:
            shot = i.get("shot_id", i.get("scene", "?"))
            lines.append(f"- **{shot}** [{i['type']}] {i['message']}")
        lines.append("")

    return "\n".join(lines)
