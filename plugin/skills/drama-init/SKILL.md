---
name: drama-init
description: Deep initialization of short drama projects. Collects creative info through interactive dialogue, generates project skeleton with worldbuilding, character profiles, and visual style ready for planning.
allowed-tools: Read Write Edit Bash AskUserQuestion Agent
---

Initialize a new short drama project. Gather creative direction through structured questioning, then generate the complete project skeleton.

## Project Root

Ask the user for the project directory or use current working directory. Run:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/project_init.py "<Project Title>"
```
where `${CLAUDE_PLUGIN_ROOT}/scripts` is the `scripts/` directory of this plugin.

## Workflow

### Step 1: Story Core & Commercial Positioning

Ask the user (use AskUserQuestion, one at a time):

1. **选题方向**: What type of story? Offer the 6 genre options + "Other"
   - 都市爽文 / 古装剧 / 甜宠 / 家庭伦理 / 复仇逆袭 / 悬疑

2. **一句话梗概**: Ask user to describe the story in one sentence.

3. **目标平台**: 抖音 / 快手 / 微短剧小程序 / 其他

4. **目标量级**: How many episodes total? (Default: 100)

### Step 2: Character Skeleton

Ask about:
1. **主角**: Name, core desire, core flaw. What makes them compelling?
2. **反派结构**: Single antagonist or layered (跳脸小丑 → 地方势力 → 主要对手 → 幕后黑手)?
3. **关键配角**: Key supporting characters and their relationship to the protagonist.

### Step 3: Worldbuilding

Ask about:
1. **世界观类型**: Modern urban? Ancient架空? Near future?
2. **特殊规则**: Any special rules or power systems?
3. **核心冲突**: What drives the central conflict?

### Step 4: Creative Constraints

Ask about:
1. **卖点**: What's the unique hook? (one sentence)
2. **反套路**: Any tropes to deliberately AVOID?
3. **硬约束**: Any hard constraints (e.g., no romantic subplot, no character deaths before episode 50)?

### Step 5: Visual Style Reference

Ask:
1. **视觉参考**: Any reference dramas/films for visual style?
2. **色调偏好**: Cold tones? Warm tones? High contrast? Natural?

### Step 6: Generate Project Files

Based on all collected information, generate these files using the Write tool:

1. `{project_root}/设定集/世界观.md` — from `templates/world-setting.md`
2. `{project_root}/设定集/视觉风格.md` — from style inference + user preferences
3. `{project_root}/设定集/角色档案/主角-{name}.md` — from `templates/character-card.md`
4. `{project_root}/设定集/角色档案/反派-{name}.md`
5. Character cards for key supporting characters
6. `{project_root}/大纲/总纲.md` — from `templates/master-outline.md`

### Step 7: Review & Confirm

Present a summary of everything generated. Ask user to confirm before proceeding.

## Sufficiency Gate (6 conditions — ALL must pass before generation)

1. [ ] 选题方向明确
2. [ ] 主角核心欲望+缺陷清晰
3. [ ] 反派结构有层次
4. [ ] 世界观有至少1条特殊规则
5. [ ] 一句话卖点存在
6. [ ] 视觉风格有明确参考

## Reference Deconstruction (Optional)

If the user wants to analyze reference works, delegate to `short-drama-writer:deconstruction-agent` via the Agent tool:

```
Agent(
  subagent_type: "short-drama-writer:deconstruction-agent",
  prompt: "Analyze this reference: <text>"
)
```

Apply extracted patterns to the creative constraints, NOT as direct copies.
