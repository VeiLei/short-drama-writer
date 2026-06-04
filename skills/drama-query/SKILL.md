---
name: drama-query
description: Queries project settings, characters, scene profiles, episode states, and foreshadowing status.
allowed-tools: Read Bash
---

Query any aspect of the current drama project.

## Query Types

### Character Query
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/character_manager.py list
python ${CLAUDE_PLUGIN_ROOT}/scripts/character_manager.py get <name>
```

### Episode Query
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/outline_loader.py <episode_number>
```

### Memory Query
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/memory_manager.py summary
python ${CLAUDE_PLUGIN_ROOT}/scripts/memory_manager.py character_state
python ${CLAUDE_PLUGIN_ROOT}/scripts/memory_manager.py foreshadowing
```

### State Query
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/state_manager.py get
```

### Review Query
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/review_saver.py get <episode_number>
```

## Output

Present results in structured markdown. For foreshadowing, highlight:
- URGENT: Active foreshadowing with approaching deadline
- OVERDUE: Foreshadowing past its expected resolution episode
