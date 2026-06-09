# Scene Spatial Layout & Continuity Check — Design

## Problem

Current state:

1. **ASCII 空间布局是 AI 凭空想象的** — `episode-script.md` 模板要求每场戏画 ASCII 布局，但 AI 没有"看"场景 master 图，是基于场景名脑补。这导致：
   - 布局与场景图实际空间关系脱节
   - 后续镜头的 spatial_anchors 也是基于脑补的布局，引用不存在的物体
2. **没有跨镜头位置连续性校验** — Seedance 拼接多段视频时，每段独立生成，AI 不检查上一镜人物在哪、下一镜是否承接，导致跳位/漂移
3. **ASCII 布局对生成视频提示词没有直接作用** — 视频生成阶段读不到 ASCII，纯人读辅助

## Solution

把责任前移到**场景素材生成提示词**阶段。让即梦生成场景 master/取景框/角色四视图的 prompt 模板里，**结构化要求写清楚固定物体的空间位置**（前/左/右/中/地面/天花，每个固定物含位置+朝向）。生成结果记入 `assets.json` 作为机器可读的"场景物体清单"。后续视频提示词的所有 spatial_anchors **强制从这份清单派生**，新增 CLI 命令 `layout-check` 在生成视频前做跨镜头位置连续性检查。

## Data Structure

### `assets.json` 新增字段

每个 scene 的 `spatial_layout`：

```json
{
  "scenes": {
    "客厅": {
      "master": {
        "tos_url": "...",
        "local_path": "素材/场景/客厅_master.png",
        "prompt": "...",
        "created_at": "..."
      },
      "spatial_layout": {
        "view": "front_elev",
        "description": "客厅正面视角，用于建立场景空间骨架",
        "fixed_objects": [
          {
            "id": "sofa_L",
            "name": "L型灰色布艺沙发",
            "position": "画面左下区域",
            "size": "占画面横向1/3，纵向1/4",
            "orientation": "开口朝右"
          },
          {
            "id": "tv_wall",
            "name": "电视墙",
            "position": "画面后景中央",
            "size": "占画面横向1/4，纵向1/3",
            "orientation": "正面朝镜头"
          },
          {
            "id": "window_R",
            "name": "落地窗",
            "position": "画面右侧通顶",
            "size": "占画面右侧1/3",
            "orientation": "朝内"
          }
        ],
        "walkable_zones": [
          {"id": "center_floor", "position": "画面中央中景", "description": "沙发与电视之间的活动区"}
        ]
      },
      "shot_frames": [
        {
          "frame_id": "客厅_master",
          "view": "front_elev",
          "fixed_objects": ["sofa_L", "tv_wall", "window_R"]
        }
      ]
    }
  }
}
```

### `视频提示词.json` 约束

每个 shot 的 `spatial_anchors`：

```json
{
  "spatial_anchors": {
    "sofa_L": "画面左下，灰色布艺沙发",
    "tv_wall": "画面后景中央",
    "center_floor": "活动区，沙发前方1米处"
  }
}
```

**约束**：键必须存在于 `scene.spatial_layout.fixed_objects` 或 `walkable_zones` 的 `id` 集合内。

## Components

### 1. `backend/app/utils/asset_index.py` — 数据层

新增方法：

- `add_scene_layout(scene_name, layout: dict) -> str` — 写入/替换 `scenes[scene_name].spatial_layout`
- `get_scene_layout(scene_name) -> Optional[dict]` — 查询
- `get_fixed_objects(scene_name) -> list[str]` — 列出所有 fixed_object id
- `add_shot_frame` 接受可选的 `fixed_objects: list[str]` 参数

修改 `add_scene_master`：增加可选 `layout: dict` 参数，一次性写入 master + layout（避免分两次写导致状态不一致）。

### 2. `backend/app/cli.py` — CLI

- `cmd_scene_master` 增加 `--layout` 参数（JSON 字符串路径或内联）
- `cmd_shot_frame` 增加 `--fixed-objects` 参数（逗号分隔 id 列表）
- `cmd_video_generate` 增加 `--check-layout` 开关，启用校验流程
- 新增 `cmd_layout_check` 子命令（独立运行，不绑定生成）

### 3. `plugin/templates/scene-card.md` — 设定集模板

新增"固定物空间布局"字段（drama-init 阶段填写）：

```markdown
## 固定物空间布局

| 固定物 ID | 名称 | 画面位置 | 朝向 | 备注 |
|----------|------|---------|------|------|
| sofa_L | L型沙发 | 左下区域 | 开口朝右 | 主沙发 |
| tv_wall | 电视墙 | 后景中央 | 朝镜头 | 电视挂墙 |
| window_R | 落地窗 | 右侧通顶 | 朝内 | 主光源方向 |
```

### 4. `plugin/skills/drama-init/SKILL.md` — 设定集生成

- 阶段1（场景档案生成）后增加：让 AI 基于场景描述填写 scene-card.md 的"固定物空间布局"表
- AI 填写依据：场景名 + 类型 + 用途，**不需要读图**

### 5. `plugin/skills/drama-generate/SKILL.md` — 素材生成

- 阶段1（场景 master）提示词模板改为结构化：

```
{场景类型}，{关键地标}，{空间尺寸}。
固定物空间布局：
- 前（后景）：{描述}
- 左：{描述}
- 右：{描述}
- 中央：{描述}
- 地面/天花：{描述}
{氛围基调}，{色调/光照方向}。空镜，无人物。
竖屏9:16构图，展示场景全貌。
```

- `CLI scene-master` 调用时加 `--layout` 参数（从 scene-card 读取）
- 阶段2（取景框）类似结构化

### 6. `plugin/references/video-prompt-rules.md` — 规则

- §3 加约束：spatial_anchors 键必须从 `scene.spatial_layout.fixed_objects[].id` + `walkable_zones[].id` 选
- 禁止添加 layout 中不存在的键
- 每个键的位置描述必须与 layout 一致或合理派生

### 7. `plugin/templates/episode-script.md` — 移除 ASCII 布局

- 删除 "ASCII 空间布局" 章节
- 改为引用 scene.spatial_layout（在分镜流图顶部加一句"参考 `设定集/场景档案/{场景名}.md` 的固定物空间布局"）

### 8. `cmd_layout_check` — 校验逻辑

输入：剧集号 + 集号
读取 `提示词/第N集-视频提示词.json` + `assets.json`
按场景分组 → 提取每个镜头的 spatial_anchors → 检查：

**同场景连续镜头**：
- 上一镜出现的固定物在下一镜位置是否一致
- 人物位置（通过 prompt 描述解析）是否在合理延续范围
- 道具状态是否衔接

**跨场景连续场景集**：
- A 场景最后一镜的固定物清单 = B 场景第一镜的固定物清单
- 角色离开 A 场景的描述 = 进入 B 场景的描述

输出：人读 Markdown 报告 + 每处问题的修改建议（AI 提议）。

**错误分级**：
- `blocking`：位置/物体/道具凭空跳位 → 必须修改
- `warning`：描述粒度差异 → 仅提示

**修改流程**：
- AI 提议修改方案（diff 形式）
- 人类确认后写回 `视频提示词.json`
- 不阻塞视频生成

## Out of Scope

- ❌ 不让 AI 读图（用户明确要求）
- ❌ 不保留 ASCII 布局（用户判断无作用）
- ❌ 不做端到端自动生成视频（用户要人工审核）
- ❌ 不做图像模型识别（成本高、稳定性差）
- ❌ 不改 Seedance adapter（提示词层已足够约束）
- ❌ 不改前端 dashboard

## Files Changed

| 文件 | 类型 |
|------|------|
| `backend/app/utils/asset_index.py` | 新增方法 |
| `backend/app/cli.py` | 新增命令 + 参数 |
| `plugin/templates/scene-card.md` | 新增字段 |
| `plugin/templates/episode-script.md` | 移除 ASCII 章节 |
| `plugin/skills/drama-init/SKILL.md` | 新增布局填写步骤 |
| `plugin/skills/drama-generate/SKILL.md` | 改 prompt 模板 |
| `plugin/references/video-prompt-rules.md` | 加 spatial_anchors 来源约束 |

## Success Criteria

1. drama-init 完成时，每个场景在 scene-card.md 有结构化的"固定物空间布局"表
2. drama-generate 阶段 1/2 完成时，`assets.json` 的 scene 含 `spatial_layout` 字段
3. drama-write 写视频提示词时，每个 shot 的 `spatial_anchors` 键都在该场景的 `spatial_layout` 键集合内
4. `python -m app.cli layout-check --project <项目> --episode N` 能输出校验报告
5. 校验发现的问题有 AI 修改建议 + diff，人类可一键采纳
