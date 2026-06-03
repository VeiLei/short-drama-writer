---
name: drama-generate
description: 生成角色参考图、场景参考图、镜头视频。通过后端 API 调用即梦/Seedance，自动管理 TOS 上传和素材索引。
allowed-tools: Read Bash AskUserQuestion
---

生成视觉素材。调用后端 API，自动处理 TOS 上传和参考图关联。

## 前置条件

- 角色档案已存在（`设定集/角色档案/`）
- 剧本已生成，分镜 JSON 已存在（`分镜/`）
- 后端已启动：`cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001`
- 后端 `.env` 已配置 API Key

## 生成顺序（有依赖关系）

```
角色参考图 → 场景参考图 → 镜头视频
    ↓            ↓            ↓
 角色档案     场景档案      分镜.json
 外貌锚点     +角色TOS URL  +角色TOS URL
              (自动查询)    +场景TOS URL
                           (自动查询)
```

---

## Workflow

### Step 1: 确定生成范围

用 AskUserQuestion 问用户：

1. **角色参考图** — 基于角色档案生成角色定妆照（全剧通用，只生成一次）
2. **场景参考图** — 基于场景档案生成空镜（可引用已生成的角色图保证一致性）
3. **镜头视频** — 基于分镜 JSON 生成视频（需要角色图+场景图已存在）
4. **完整管线** — 角色→场景→视频 一键生成

### Step 2: 生成角色参考图

遍历 `设定集/角色档案/` 下的所有角色，对每个角色：
- 从角色卡中提取外貌锚点，按 `references/video-prompt-rules.md` 框架构建 prompt
- 调用后端 API：

```bash
curl -X POST http://localhost:8001/api/generate/character \
  -H "Content-Type: application/json" \
  -d '{
    "project_root": "<项目目录>",
    "characters": [
      {"name": "林若雪", "prompt": "CG游戏角色原画风格，半写实渲染...（外貌锚点+着装+9:16竖屏+纯白背景）"}
    ]
  }'
```

后端自动：生成图片 → 上传 TOS → 保存本地 → 记入 `.drama/assets.json` 索引。

### Step 3: 生成场景参考图

遍历 `设定集/场景档案/` 下的场景，对每个场景：
- 从场景卡提取空间锚点，构建 prompt
- 查看分镜 JSON 确定本场景出场角色
- 调用后端时自动关联角色 TOS URL 作为 reference_images：

```bash
curl -X POST http://localhost:8001/api/generate/scene \
  -H "Content-Type: application/json" \
  -d '{
    "project_root": "<项目目录>",
    "scenes": [
      {"name": "咖啡厅", "prompt": "场景全貌...9:16竖屏 空镜", "character_names": ["林若雪", "顾深"]}
    ]
  }'
```

后端自动：查 AssetIndex 获取角色 TOS URL → 作为 reference_images 传即梦 → 生成 → 上传 TOS → 记入索引。

同场景多帧连续性：第一帧（定场广角）生成后作为 anchor，后续帧用它做参考。

### Step 4: 生成镜头视频

遍历 `分镜/第XXXX集-分镜.json` 中的每个镜头，对每个镜头：

1. 按 `references/video-prompt-rules.md` 八维框架组装提示词
2. 查 AssetIndex 获取本镜头需要的角色+场景 TOS URL
3. 调用后端：

```bash
curl -X POST http://localhost:8001/api/generate/video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<八维框架提示词>",
    "reference_images": ["<角色TOS URL>", "<场景TOS URL>"],
    "tail_frame_url": "<上一镜头尾帧URL>"  // Seedance 不需要转素描
  }'
```

轮询状态：
```bash
curl http://localhost:8001/api/generate/status/{task_id}
```

每个镜头生成后：
- 尾帧 URL 传给下一镜头作为参考（Seedance 自动识别尾帧，不需要转素描）
- 视频保存到 `素材/视频/`
- 记入 `.drama/assets.json`

### Step 5: 更新状态

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py update stats.shots_generated <N>
```

---

## 索引查询

随时查看已生成素材：
```bash
curl "http://localhost:8001/api/generate/assets?project_root=<项目目录>"
```
