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


def test_validate_spatial_anchors_all_valid(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    anchors = {"sofa_L": "画面左下", "tv_wall": "后景", "center_floor": "中央"}
    valid, invalid = idx.validate_spatial_anchors("客厅", anchors)
    assert valid == ["sofa_L", "tv_wall", "center_floor"]
    assert invalid == []


def test_validate_spatial_anchors_some_invalid(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    anchors = {"sofa_L": "画面左下", "fake_object": "不存在", "tv_wall": "后景"}
    valid, invalid = idx.validate_spatial_anchors("客厅", anchors)
    assert set(valid) == {"sofa_L", "tv_wall"}
    assert invalid == ["fake_object"]


def test_validate_spatial_anchors_no_layout(tmp_project):
    idx = AssetIndex(tmp_project)
    valid, invalid = idx.validate_spatial_anchors("客厅", {"any_key": "desc"})
    assert valid == []
    assert invalid == ["any_key"]


def test_add_scene_master_with_layout(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_master("客厅", tos_url="https://tos.example/x.png",
                         local_path="素材/场景/客厅_master.png",
                         prompt="客厅全景 prompt", layout=sample_scene_layout)

    assert idx.get_scene_master_url("客厅") == "https://tos.example/x.png"
    assert idx.get_scene_layout("客厅") == sample_scene_layout


def test_add_scene_master_without_layout_keeps_none(tmp_project):
    idx = AssetIndex(tmp_project)
    idx.add_scene_master("客厅", tos_url="https://tos.example/x.png")

    assert idx.get_scene_layout("客厅") is None


def test_add_shot_frame_with_fixed_objects(tmp_project):
    idx = AssetIndex(tmp_project)
    idx.add_shot_frame("客厅", "客厅_master", "establishing",
                       tos_url="https://tos.example/f.png",
                       fixed_objects=["sofa_L", "tv_wall"])

    frame = idx.get_shot_frame("客厅", "客厅_master")
    assert frame["fixed_objects"] == ["sofa_L", "tv_wall"]


def test_add_shot_frame_default_empty_fixed_objects(tmp_project):
    idx = AssetIndex(tmp_project)
    idx.add_shot_frame("客厅", "客厅_master", "establishing",
                       tos_url="https://tos.example/f.png")

    frame = idx.get_shot_frame("客厅", "客厅_master")
    assert frame["fixed_objects"] == []
