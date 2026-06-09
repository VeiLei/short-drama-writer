import pytest
from app.utils.layout_checker import (
    check_anchor_validity,
    check_cross_shot_continuity,
    format_report_markdown,
)


SAMPLE_LAYOUT = {
    "view": "front_elev",
    "fixed_objects": [
        {"id": "sofa_L", "name": "L型沙发", "position": "画面左下区域"},
        {"id": "tv_wall", "name": "电视墙", "position": "画面后景中央"},
        {"id": "window_R", "name": "落地窗", "position": "画面右侧通顶"},
    ],
    "walkable_zones": [
        {"id": "center_floor", "position": "画面中央中景"}
    ]
}


def test_check_anchor_validity_all_in_layout():
    anchors = {"sofa_L": "画面左下", "center_floor": "中央"}
    issues = check_anchor_validity(anchors, SAMPLE_LAYOUT)
    assert issues == []


def test_check_anchor_validity_finds_invalid_key():
    anchors = {"sofa_L": "画面左下", "fake_door": "右侧"}
    issues = check_anchor_validity(anchors, SAMPLE_LAYOUT)
    assert len(issues) == 1
    assert issues[0]["key"] == "fake_door"
    assert issues[0]["severity"] == "blocking"


def test_check_cross_shot_continuity_same_position():
    """同场景连续镜头，固定物位置应一致。"""
    shots = [
        {"shot_id": "S1_F01", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
        {"shot_id": "S1_F02", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
    ]
    issues = check_cross_shot_continuity(shots, SAMPLE_LAYOUT)
    assert issues == []


def test_check_cross_shot_continuity_object_disappears():
    """同场景下一镜某固定物消失 → blocking。"""
    shots = [
        {"shot_id": "S1_F01", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
        {"shot_id": "S1_F02", "spatial_anchors": {"sofa_L": "画面左下"}},
    ]
    issues = check_cross_shot_continuity(shots, SAMPLE_LAYOUT)
    assert any(i["type"] == "object_disappeared" for i in issues)
    assert any(i["severity"] == "warning" for i in issues)


def test_check_cross_shot_continuity_object_appears():
    """同场景下一镜出现新固定物 → blocking（应从 layout 派生，不是凭空出现）。"""
    shots = [
        {"shot_id": "S1_F01", "spatial_anchors": {"sofa_L": "画面左下"}},
        {"shot_id": "S1_F02", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
    ]
    issues = check_cross_shot_continuity(shots, SAMPLE_LAYOUT)
    assert any(i["type"] == "object_appeared" for i in issues)


def test_format_report_markdown_empty():
    out = format_report_markdown([])
    assert "无问题" in out or "通过" in out


def test_format_report_markdown_with_issues():
    issues = [
        {"shot_id": "S1_F02", "type": "invalid_key", "key": "fake",
         "severity": "blocking", "message": "fake 不在 layout 中"}
    ]
    out = format_report_markdown(issues)
    assert "S1_F02" in out
    assert "blocking" in out
    assert "fake" in out
