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
python {PLUGIN_SCRIPTS}/state_manager.py get
```

### Step 1: Context Research (context-agent)

**MUST delegate to `short-drama-writer:context-agent` via Agent tool.**

```
Agent(
  subagent_type: "short-drama-writer:context-agent",
  prompt: "Episode {episode_number}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

The context-agent outputs a 5-section writing task book. This becomes the creative brief for Step 2.

### Step 2: Draft

Write the episode script following `templates/episode-script.md`. The draft must include:

**For each scene:**
1. Scene header (location, time, characters)
2. ASCII spatial layout diagram
3. Shot flow map (3-5 shots with position/facing/outfit tracking)

**For each shot:**
1. Frame type (WIDE/MS/CU/ECU)
2. Visual description
3. Character position table (position, position_change, facing, outfit)
4. Action description
5. Dialogue (if any)
6. Continuity note (how it connects to the previous shot)

**Writing rules:**
- Show emotion through behavior, not labels
- No AI cliché words (缓缓, 微微, 渐渐, 悄然, 深邃, 璀璨)
- No paragraph-ending reflective/总结 sentences
- No "殊不知/little did he know" constructions
- End each scene with a mini-hook that pushes to the next scene
- End the episode with the hook specified in the task book

Save the draft to `剧本/第{episode_number}集-{title}.md`.

Save the shot flow map to `分镜/第{episode_number}集-分镜.json`.

### Step 3: Review (reviewer agent)

**MUST delegate to `short-drama-writer:reviewer` via Agent tool.**

```
Agent(
  subagent_type: "short-drama-writer:reviewer",
  prompt: "Review episode script: {script_path}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

The reviewer outputs a JSON issue list. Save raw review:
```bash
python {PLUGIN_SCRIPTS}/review_saver.py save {episode_number} '<review_json>'
```

**Blocking gate:** If any issue has `blocking: true`, the draft MUST return to Step 2 for fixes. Non-blocking issues can be handled in Step 4.

### Step 4: Polish

Address all non-blocking issues from review:
1. Fix AI-flavor issues (apply `references/ai-flavor-checklist.md`)
2. Verify shot continuity (apply `references/cinematic-rules.md`)
3. Check dialogue authenticity (apply genre-specific dialogue guide)
4. Format consistency (ensure template structure is clean)

### Step 5: Submit

**5.1 Data Extraction** — delegate to `short-drama-writer:data-agent`:
```
Agent(
  subagent_type: "short-drama-writer:data-agent",
  prompt: "Extract data from: {script_path}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

**5.2 Commit** — run the commit script with the data-agent output:
```bash
python {PLUGIN_SCRIPTS}/chapter_commit.py {episode_number}
```

Then manually update memory files using the data-agent JSON output via Python scripts.

**5.3 Sufficiency Gate:**
- [ ] Episode script file exists at `剧本/第{episode_number}集-*.md`
- [ ] Shot flow map JSON exists at `分镜/第{episode_number}集-分镜.json`
- [ ] Review report exists at `审查报告/第{episode_number}集审查报告.md`
- [ ] ALL blocking issues resolved
- [ ] Memory files updated
