---
name: drama-generate
description: 生成角色四视图、变装四视图、场景全景图、场景取景框、镜头视频。自动管理 TOS 上传和素材索引。
allowed-tools: Read Bash AskUserQuestion Agent
---

生成视觉素材。四个阶段，按需触发。

## 前置条件

- 后端 `.env` 已配置即梦 API Key
- 以下用 `CLI` 代指后端 CLI 入口。**按顺序查找**：

  ```
  1. cd d:/PersonalFiles/Project_Space/short-drama-writer/backend && .venv/Scripts/python -m app.cli  ← 本地开发后端（优先）
  2. unix: cd ${CLAUDE_PLUGIN_ROOT}/../backend/backend && .venv/bin/python -m app.cli
  3. win:  cd ${CLAUDE_PLUGIN_ROOT}/../backend/backend && .venv/Scripts/python -m app.cli
  ```

  路径 1 的 .venv 存在则直接用；不存在则依次尝试 2/3。均不存在时报错，不要 clone。

---

## 素材生成时序

```
阶段1（drama-init后）：角色基础四视图 + 场景全景图
阶段2（drama-write后）：按需生成取景框 + 变装四视图 + 道具参考图
阶段3（drama-write后）：生成每镜头的视频提示词 JSON
阶段4（提示词就绪）：逐镜头调 Seedance 生成视频（自动注入道具参考图）
阶段5：查询素材索引
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

调用（逐个角色执行，一次一个）：
```bash
CLI four-views --project <项目目录> --name <角色名> --prompt "..."
```

自动记入 `.drama/assets.json`，outfit="基础"。

---

## 阶段2：场景全景图

读取 `设定集/场景档案/`，对每个场景拼装全景 prompt：

```
{场景类型}，{关键地标}，{空间尺寸}。{氛围基调}，{色调/光照方向}。空镜，无人物。
竖屏9:16构图，展示场景全貌。
```

调用（逐个场景执行）：
```bash
CLI scene-master --project <项目目录> --name <场景名> --prompt "..."
```

---

## 阶段3：按需生成取景框 + 变装

**时机**：drama-write 完成后。由 drama-write 输出的"缺失素材清单"驱动。

### 3a. 缺失取景框

drama-write 的分镜流图指定了每个镜头使用的取景框。Claude 提取去重后的取景框清单，逐个检查 `assets.json`，缺失的调用：

```bash
CLI shot-frame --project <项目目录> --scene <场景名> --frame-id <frame_id> --frame-type <type> --prompt "..."
```

CLI 自动以场景 master 图为 reference_image。

### 3b. 缺失变装四视图

data-agent 输出中 `costume_updates` 标注了新着装。对每个新着装：

```bash
CLI variant --project <项目目录> --name <角色名> --outfit <着装名> --prompt "..."
```

CLI 自动以基础四视图为 reference_image，保持角色面容和体型一致。

### 3c. 缺失道具参考图

**时机**：drama-write 完成后，读取 `提示词/第{episode_number}集-缺失道具.json`。

对每个缺失道具，生成参考图：

```
CG游戏原画风格，半写实渲染，{道具描述}。
纯白背景，无人物，正上方或侧45°产品图视角，展示全部细节。
```
道具名示例：`祖传项链`、`加密U盘`、`订婚戒指`

调用（逐个道具执行）：
```bash
CLI prop-ref --project <项目目录> --name <道具名> --prompt "..." --scene <关联场景>
```

CLI 自动记入 `.drama/assets.json` 的 `props` 段，同道具名替换旧条目。

---

## 阶段4：视频生成

**时机**：视频提示词 JSON 就绪后。

### 4a. 查看视频提示词

```bash
CLI video-prompt --project <项目目录> --episode 0001
```

### 4b. 逐镜头生成视频

对每个镜头的 prompt，调用（`--duration` 从视频提示词 JSON 的 `video_params.duration_sec` 读取，**不要写死**）：

```bash
CLI video-generate --project <项目目录> --episode <集号> --shot-id <shot_id> --scene <场景名> --frame-id <frame_id>
```

CLI 自动从 JSON 读取 duration/ratio/refs、submit → poll → download 到 `素材/视频/`。

---

## 阶段5：查询素材索引

随时查看已有素材：
```bash
CLI assets --project <项目目录>
```

---

## 关键约束

- 取景框 = 空镜，没有人
- 角色四视图 = 角色+白底，没有场景背景
- 视频生成时取景框(TOS) + 角色(TOS) + 站位指令 → Seedance
- 每个素材生成前 CLI 自动检查 assets.json，已存在则跳过
- prompt 超长时用临时文件传入：`--prompt @/tmp/prompt.txt`
- **严禁在项目目录创建 .py 脚本**，始终使用 CLI
