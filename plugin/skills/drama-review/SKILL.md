---
name: drama-review
description: Uses the reviewer agent to evaluate episode quality. Generates structured review reports.
allowed-tools: Read Bash Agent AskUserQuestion
---

Review a specific episode's quality using the reviewer agent.

## Workflow

### Step 1: Determine Target Episode

Ask user which episode to review, or read current state:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py get
```

### Step 2: Load References

Read:
- `references/cinematic-rules.md`
- `references/ai-flavor-checklist.md`
- `references/shot-composition.md`
- The relevant genre knowledge files from `genres/`

### Step 3: Call Reviewer Agent

```
Agent(
  subagent_type: "short-drama-writer:reviewer",
  prompt: "Review: {script_path}, project root: {project_root}, plugin scripts: ${CLAUDE_PLUGIN_ROOT}/scripts"
)
```

### Step 4: Generate Report

Save the review:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/review_saver.py save {episode_number} '<review_json>'
```

### Step 5: Handle Blocking Issues

If blocking issues exist, ask user via AskUserQuestion:
- Fix now (return to drama-write)
- Save for later (continue to next episode)

### Step 6: Update State

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py update stats.episodes_reviewed <N>
```
