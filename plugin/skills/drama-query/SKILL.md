---
name: drama-query
description: Queries project settings, characters, scene profiles, episode states, and foreshadowing status.
allowed-tools: Read Bash
---

Query any aspect of the current drama project.

## Query Types

### Character Query
```bash
python {PLUGIN_SCRIPTS}/character_manager.py list
python {PLUGIN_SCRIPTS}/character_manager.py get <name>
```

### Episode Query
```bash
python {PLUGIN_SCRIPTS}/outline_loader.py <episode_number>
```

### Memory Query
```bash
python {PLUGIN_SCRIPTS}/memory_manager.py summary
python {PLUGIN_SCRIPTS}/memory_manager.py character_state
python {PLUGIN_SCRIPTS}/memory_manager.py foreshadowing
```

### State Query
```bash
python {PLUGIN_SCRIPTS}/state_manager.py get
```

### Review Query
```bash
python {PLUGIN_SCRIPTS}/review_saver.py get <episode_number>
```

## Output

Present results in structured markdown. For foreshadowing, highlight:
- URGENT: Active foreshadowing with approaching deadline
- OVERDUE: Foreshadowing past its expected resolution episode
