---
name: drama-write
description: Produces a single episode script. Full execution: context research → draft → review → polish → submit. Includes shot flow map and ASCII spatial layout generation.
allowed-tools: Read Write Edit Bash Agent
---

Produce one episode script with full shot flow map and spatial layout. This is the core creative pipeline.

## Modes

| Mode | Flow |
|------|------|
| Default | Steps 1-2-3-4-5 |
| `--fast` | Steps 1-2-3(light check only)-4-5 |
| `--minimal` | Steps 1-2-4(format fix only)-5 |

## Workflow

### Preflight

Determine episode number (ask user or read current state):
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py get
```

### Step 1: Context Research (context-agent)

**MUST delegate to `short-drama-writer:context-agent` via Agent tool.**

```
Agent(
  subagent_type: "short-drama-writer:context-agent",
  prompt: "Episode {episode_number}, project root: {project_root}, plugin scripts: ${CLAUDE_PLUGIN_ROOT}/scripts"
)
```

The context-agent outputs a 5-section writing task book. This becomes the creative brief for Step 2.

### Step 2: Draft

Write the episode script following `templates/episode-script.md`. The draft must include:

**For each scene:**
1. Scene header (location, time, characters)
2. ASCII spatial layout diagram
3. Shot flow map (镜头数按场景功能决定，参考 `cinematic-rules.md` 的「单场景镜头密度」)

**For each shot:**
1. Frame type (WIDE/MS/CU/ECU)
2. Visual description
3. Character position table (position, position_change, facing, outfit)
4. Action description
5. Dialogue (if any)
6. Continuity note (how it connects to the previous shot)

**Writing rules:** Follow `references/script-generation-rules.md` for all constraints. Key points:
- 钩子：前5秒必须有异常/冲突/悬念
- 每场戏必须有冲突，情绪不能平
- 每集至少一次认知反转，结尾必须未闭合
- Show emotion through behavior, not labels
- No AI cliché words (缓缓, 微微, 渐渐, 悄然, 深邃, 璀璨)
- No paragraph-ending reflective/总结 sentences
- No "殊不知/little did he know" constructions
- 每Scene至少1句"子弹台词"
- 对白短句为主，禁止纯信息播报模式
- 角色状态和空间位置必须跨场景延续

Save the draft to `剧本/第{episode_number}集-{title}.md`.

Save the shot flow map to `分镜/第{episode_number}集-分镜.json`.

### 合并审查（写视频提示词前必做）

> **目的**：防止同场景连续镜头被过度拆分，避免多段 4s 视频拼接导致的站位漂移。

**对每对同场景连续镜头**，用 `video-prompt-rules.md` §7.1 五问逐对判定：

| # | 问题 | 答"是"→保留切 | 答"否"→考虑合并 |
|---|------|-------------|--------------|
| 1 | 轴线变了？（180° 切到另一侧） | 切 | → |
| 2 | 空间/机位变了？（换位置/角度） | 切 | → |
| 3 | 时间跳了？（切完是新时间点） | 切 | → |
| 4 | 新信息揭示了？（新人物/新道具/新画面） | 切 | → |
| 5 | 情绪升档了？（从平→紧，更近景别+更快节奏） | 切 | → |

**5 问全否 → 合并**。合并后时长 = 各镜头时长之和（不超过 15s，超过则分段）。
合并后重新编号（如 F01+F02+F03 → F01，后续递补）。

**反模式速查**（以下情况必须合并）：
- 同空间同组人 MCU→MCU→MCU 连切（只是台词推进，空间没变）
- 动作链切碎（走→站→转→看 切成 4 个，应合并为 1 个 8-10s）
- 情绪过程切碎（眼眶涩→湿→红 分成 3 个，应合并为 1 个 6-8s）

### 空间站位一致性检查（同场景连续镜头）

> **目的**：防止 Seedance 在每个 4s 短片中重新"猜"人物和物体位置，导致拼接后人物跳位、道具漂移。

对每个同场景连续镜头，逐项检查：

**人物站位**：
- 上一镜结束时的角色位置/姿势/朝向 = 下一镜开始时的角色位置/姿势/朝向
- 如有位置变化，必须有明确的动作过渡（走位、转身等）

**固定物体**（吧台、门窗、楼梯、大型家具——同场景不变）：
- 首镜头建立固定物空间骨架，后续镜头必须沿用
- 不得出现"上镜有的吧台本镜消失"或"落地窗变成砖墙"
- 摄影机切角度时，固定物的相对空间关系不变（只是视角变化）

**道具**（杯子、手机、文件、包等——可被角色移动）：
- 每个镜头必须追踪道具的当前状态（在谁手里 / 在哪个固定物上）
- 道具跨镜位移必须有动作交代：上一镜在桌上 → 本镜角色拿起
- 禁止凭空出现或消失

**空间参照**：
- 每个镜头的 `spatial_anchors` 字段必须写入场景关键地标（包括固定物名称+画面位置）
- 同场景所有镜头共用相同的 `spatial_anchors` 键名集合，仅位置描述按镜头变化

### 生成视频提示词 JSON

For every shot in the **合并后**的 flow map, assemble a video generation prompt following `references/video-prompt-rules.md` 8-dimension framework (主体描述/动作运动/场景环境/镜头语言/光影色调/风格情绪/时间节奏/叙事约束). Save to `提示词/第{episode_number}集-视频提示词.json` using `templates/shot-prompt.json` format. Each shot entry must include:
- `positive`: full 8-dimension prompt in Chinese, **必须包含空间定位语句**（角色位于画面X位置，与Y物体的Z关系）
- `negative`: negative prompt (avoid abstract terms, faces, text, watermarks)
- `spatial_anchors`: scene key landmarks — **同场景所有镜头共用相同的 landmarks 键名**（如 `bar_counter`, `window_seat`），仅位置描述按镜头变化
- `lighting_mood`: from the scene's lighting setup
- `character_references`: [{name, outfit}] — characters and their current outfit in this shot
- `scene_reference`: {scene_name, frame_id} — which shot frame to use as background
- `prop_references`: [string] — 道具名列表，仅录入本镜头作为特写主体或手持交互的道具（纯背景陈设不列）
- `duration_sec`: **按实际内容复杂度取值（4-15s），禁止一律 4s**。参考 `video-prompt-rules.md` §7 时长估算表

**Extract shot frames, variants, and prop refs:** From all shots across all scenes, derive three lists:

1. **取景框清单**（去重）：对每个 `{scene_name, frame_id}` 组合，查询 `assets.json` 是否已存在。缺失项写入 `提示词/第{episode_number}集-缺失取景框.json`：
```json
[{"scene_name": "咖啡厅", "frame_id": "coffee_bar_2shot", "frame_type": "two_shot",
  "prompt": "吧台中景：木质吧台占画面下1/3，酒架背景。空镜无人物。"}]
```

2. **变装清单**（去重）：对每个 `{character, outfit}` 组合，查询 `assets.json` 是否已有该着装版本。缺失项写入 `提示词/第{episode_number}集-缺失变装.json`：
```json
[{"name": "林若雪", "outfit": "晚宴礼服",
  "prompt": "CG游戏角色原画风格...新着装：黑色晚礼服长裙..."}]
```

3. **道具参考图清单**（去重）：从所有 shot 的 `prop_references` 汇总去重。对每个道具名，查询 `assets.json` 的 props 段是否已有。缺失项写入 `提示词/第{episode_number}集-缺失道具.json`：
```json
[{"name": "祖传项链", "scene": "客厅",
  "prompt": "CG游戏原画风格，半写实渲染。一条古旧的银质项链，心形吊坠上刻有藤蔓花纹，表面有细微划痕和氧化痕迹。吊坠直径约3cm，银链长约45cm。纯白背景，无人物，正上方俯拍产品图视角，展示全部细节。"}]
```

道具参考图判定标准（满足任一即需生成）：
- 在 3+ 镜头中出现，且至少 1 次为 CU/ECU 特写
- 有独特辨识度（特定花纹/刻字/造型），不是通用物件
- 剧情关键物（信物/线索/凶器/遗物/标志性配饰）
- 不需要生成：通用咖啡杯、路人手机、背景花瓶、一闪而过的物件

取景框类型判断依据（从 shot 的 frame_type + 角色数量反推）：

| shot 特征 | frame_id 后缀 | frame_type |
|----------|-------------|------------|
| 本场景第1个镜头 | `_{场景}_master` | establishing |
| frame_type=MS 且 characters≥2 | `_{区域}_2shot` | two_shot |
| frame_type=CU/MCU 且 characters=1 | `_{区域}_cu` | single_closeup |
| facing 中一方看向另一方 | `_{区域}_os` | over_shoulder |
| frame_type=ECU 拍物体 | `_{物体}_ecu` | insert_cu |

### Step 3: Review (reviewer agent)

**MUST delegate to `short-drama-writer:reviewer` via Agent tool.**

```
Agent(
  subagent_type: "short-drama-writer:reviewer",
  prompt: "Review episode script: {script_path}, project root: {project_root}, plugin scripts: ${CLAUDE_PLUGIN_ROOT}/scripts"
)
```

The reviewer outputs a JSON issue list. Save raw review:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/review_saver.py save {episode_number} '<review_json>'
```

**Blocking gate:** If any issue has `blocking: true`, the draft MUST return to Step 2 for fixes. Non-blocking issues can be handled in Step 4.

### Step 4: Polish

Address all non-blocking issues from review:
1. Fix AI-flavor issues (apply `references/ai-flavor-checklist.md`)
2. Verify against `references/script-generation-rules.md` (DNA, dialogue, continuity)
3. Verify shot continuity (apply `references/cinematic-rules.md`)
4. Check dialogue authenticity (apply genre-specific dialogue guide)
5. Format consistency (ensure template structure is clean)

### Step 5: Submit

**5.1 Data Extraction** — delegate to `short-drama-writer:data-agent`:
```
Agent(
  subagent_type: "short-drama-writer:data-agent",
  prompt: "Extract data from: {script_path}, project root: {project_root}, plugin scripts: ${CLAUDE_PLUGIN_ROOT}/scripts"
)
```

**5.2 Commit** — run the commit script with the data-agent output:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/chapter_commit.py {episode_number}
```

Then manually update memory files using the data-agent JSON output via Python scripts.

**5.3 Sufficiency Gate:**
- [ ] Episode script file exists at `剧本/第{episode_number}集-*.md`
- [ ] Shot flow map JSON exists at `分镜/第{episode_number}集-分镜.json`
- [ ] Video prompt JSON exists at `提示词/第{episode_number}集-视频提示词.json`
- [ ] Missing shot frames JSON exists at `提示词/第{episode_number}集-缺失取景框.json`（空数组=全就绪）
- [ ] Missing variants JSON exists at `提示词/第{episode_number}集-缺失变装.json`（空数组=全就绪）
- [ ] Missing prop refs JSON exists at `提示词/第{episode_number}集-缺失道具.json`（空数组=全就绪）
- [ ] Review report exists at `审查报告/第{episode_number}集审查报告.md`
- [ ] ALL blocking issues resolved
- [ ] Memory files updated
