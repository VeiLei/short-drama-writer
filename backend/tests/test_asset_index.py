import json
from app.utils.asset_index import AssetIndex


def test_add_scene_layout_creates_new_scene(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    stored = idx.get_scene_layout("客厅")
    assert stored == sample_scene_layout


def test_add_scene_layout_replaces_existing(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    updated = dict(sample_scene_layout)
    updated["description"] = "updated description"
    idx.add_scene_layout("客厅", updated)

    assert idx.get_scene_layout("客厅")["description"] == "updated description"


def test_get_scene_layout_returns_none_for_missing(tmp_project):
    idx = AssetIndex(tmp_project)
    assert idx.get_scene_layout("不存在的场景") is None


def test_get_fixed_object_ids_returns_all_ids(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    ids = idx.get_fixed_object_ids("客厅")
    assert set(ids) == {"sofa_L", "tv_wall", "window_R", "center_floor"}


def test_get_fixed_object_ids_empty_when_no_layout(tmp_project):
    idx = AssetIndex(tmp_project)
    assert idx.get_fixed_object_ids("客厅") == []


def test_get_fixed_object_ids_missing_scene(tmp_project):
    idx = AssetIndex(tmp_project)
    assert idx.get_fixed_object_ids("不存在的场景") == []
