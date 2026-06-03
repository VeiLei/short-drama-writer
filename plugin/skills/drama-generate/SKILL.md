---
name: drama-generate
description: 生成角色四视图、变装四视图、场景全景图、场景取景框、镜头视频。自动管理 TOS 上传和素材索引。
allowed-tools: Read Bash AskUserQuestion Agent
---

生成视觉素材。四个阶段，按需触发。

## 前置条件

- 后端已启动：`cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001`
- 后端 `.env` 已配置即梦 API Key

---

## 素材生成时序

```
阶段1（drama-init后）：角色基础四视图 + 场景全景图
阶段2（drama-write后）：按需生成取景框 + 变装四视图
阶段3（drama-write后）：生成每镜头的视频提示词 JSON
阶段4（提示词就绪）：逐镜头调 Seedance 生成视频
```

---

## 阶段1：角色基础四视图

**时机**：drama-init 完成、角色档案就绪后。

读取 `设定集/角色档案/`，对每个角色拼装四视图 prompt：

```
CG游戏角色原画风格，半写实渲染，清晰轮廓线，平涂上色，游戏角色设定图质感，非真人照片。
纯白背景。
四视图组合：左侧（版面的三分之一）为角色面部特写（胸部以上），
右侧（版面的三分之二）依次为正面全身、侧面全身、背面全身，
全身照要见到鞋，三视图严格对齐、间距均匀，无重叠。
角色外观：{外貌锚点+着装}。
保持CG游戏角色原画质感，非真人。
```

调用：
```bash
curl -X POST http://localhost:8001/api/generate/character/four-views \
  -H "Content-Type: application/json" \
  -d '{"project_root": "<项目目录>", "characters": [{"name":"林若雪", "prompt":"..."}]}'
```

自动记入 `.drama/assets.json`，outfit="基础"。

---

## 阶段2：场景全景图

读取 `设定集/场景档案/`，对每个场景拼装全景 prompt：

```
{场景类型}，{关键地标}，{空间尺寸}。{氛围基调}，{色调/光照方向}。空镜，无人物。
竖屏9:16构图，展示场景全貌。
```

调用：
```bash
curl -X POST http://localhost:8001/api/generate/scene/master \
  -H "Content-Type: application/json" \
  -d '{"project_root": "<项目目录>", "scenes": [{"name":"咖啡厅", "prompt":"..."}]}'
```

---

## 阶段3：按需生成取景框 + 变装

**时机**：drama-write 完成后。由 drama-write 输出的"缺失素材清单"驱动。

### 3a. 缺失取景框

drama-write 的分镜流图指定了每个镜头使用的取景框。Claude 提取去重后的取景框清单，逐个检查 `assets.json`，缺失的调用：

```bash
curl -X POST http://localhost:8001/api/generate/scene/shot-frame \
  -H "Content-Type: application/json" \
  -d '{
    "project_root": "<项目目录>",
    "frames": [
      {"scene_name":"咖啡厅", "frame_id":"coffee_bar_2shot", "frame_type":"two_shot",
       "prompt": "吧台中景近景：木质吧台占画面下1/3，酒架背景。空镜无人物。参考全景主图的空间布局，仅推进镜头到吧台区域。"}
    ]
  }'
```

后端自动以场景 master 图为 reference_image。

### 3b. 缺失变装四视图

data-agent 输出中 `costume_updates` 标注了新着装。对每个新着装：

```bash
curl -X POST http://localhost:8001/api/generate/character/variant \
  -H "Content-Type: application/json" \
  -d '{
    "project_root": "<项目目录>",
    "characters": [
      {"name":"林若雪", "outfit":"晚宴礼服", "prompt": "CG游戏角色原画风格...新着装：黑色晚礼服长裙...以基础四视图为参考，仅更新着装。"}
    ]
  }'
```

后端自动以基础四视图为 reference_image，保持角色面容和体型一致。

---

## 阶段4：查询素材索引

随时查看已有素材：
```bash
curl "http://localhost:8001/api/generate/assets?project_root=<项目目录>"
```

---

## 关键约束

- 取景框 = 空镜，没有人
- 角色四视图 = 角色+白底，没有场景背景
- 视频生成时取景框(TOS) + 角色(TOS) + 站位指令 → Seedance
- 每个素材生成前检查 assets.json，不重复生成
