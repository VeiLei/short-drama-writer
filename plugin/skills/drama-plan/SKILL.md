---
name: drama-plan
description: Generates episode outlines based on the master outline. Breaks the series into episodes with emotion curves, beats, and scene briefs. Writes new settings incrementally back to existing setting files.
allowed-tools: Read Write Edit Bash Agent
---

Generate the episode-by-episode outline based on the master outline and creative constraints.

## Prerequisites

- Master outline exists at `大纲/总纲.md`
- World setting exists at `设定集/世界观.md`
- Character profiles exist in `设定集/角色档案/`

Run preflight:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py get
```

## Workflow

### Step 1: Load Context

Read:
- `大纲/总纲.md`
- `设定集/世界观.md`
- All files in `设定集/角色档案/`
- `设定集/视觉风格.md`

### Step 2: Fill Setting Baseline (Incremental)

If any character cards or world settings are incomplete, fill them NOW before generating outlines. This ensures outlines reference complete information.

### Step 3: Volume Planning

Divide the series into volumes (~10 episodes each). For each volume:
- Core conflict for this volume
- Which antagonist tier is active
- Protagonist's stage in their character arc

Write to `大纲/卷规划.md`.

### Step 4: Generate Episode Outline

For each episode, write to `大纲/分集大纲.md` following `templates/episode-outline.md`. Each episode must have:

- 情绪基调 (emotional tone)
- 时长分配 (timing breakdown)
- 情绪曲线 (emotion curve)
- 节拍序列 (beat sequence: hook → development → climax → new hook)
- 场景梗概 (scene briefs with location, characters, core event, frame count)
- 出场角色状态 (character states entering and leaving)
- 伏笔操作 (foreshadowing operations)

### Constraints

1. **Emotion curve variety**: No two consecutive episodes should end on the same emotional peak type
2. **Scene variety**: Each episode should have 2-4 scenes; avoid single-scene episodes
3. **Frame requirement**: Each scene needs 3-5 shot frames (at least 1 wide + 1 medium + 1 close-up)
4. **Hook requirement**: Every episode must end with a hook (immediate suspense, medium mystery, or emotional cliffhanger)
5. **Genre-specific pacing**: Follow the rhythm template from the relevant genre knowledge base

### Step 5: Validate & Save

Validate:
- [ ] All episodes have beat sequences
- [ ] All episodes have time fields  
- [ ] All episodes have character state entries
- [ ] Hooks exist for every episode
- [ ] No BLOCKER-level contradictions with settings

Update state:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py update phase plan
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py update total_episodes <N>
```
