---
name: drama-generate
description: Reads prompt JSON files and calls backend API to generate character reference images, scene images, and shot videos.
allowed-tools: Read Bash
---

Generate visual assets by calling the backend API with prepared prompt JSON files.

## Workflow

### Step 1: Determine Scope

Ask user what to generate:
- Character reference images only
- Scene reference images only
- Shot videos only
- Full pipeline (characters → scenes → videos)

### Step 2: Load Prompts

Read the relevant prompt JSON files from `提示词/`.

### Step 3: Generate Character Images

For each character prompt file:
```bash
curl -X POST http://localhost:8001/api/generate/image \
  -H "Content-Type: application/json" \
  -d @提示词/{episode}-角色图提示词.json
```

Save returned asset references to `素材/角色/`.

### Step 4: Generate Scene Images

For each scene prompt file:
```bash
curl -X POST http://localhost:8001/api/generate/image \
  -H "Content-Type: application/json" \
  -d @提示词/{episode}-场景图提示词.json
```

### Step 5: Generate Shot Videos

For each shot in the video prompt file:
```bash
curl -X POST http://localhost:8001/api/generate/video \
  -H "Content-Type: application/json" \
  -d '<shot_prompt_json>'
```

Poll status:
```bash
curl http://localhost:8001/api/generate/status/{task_id}
```

Save completed video references to `素材/视频/`.

### Step 6: Update State

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py update stats.shots_generated <N>
```
