"""Commit an episode after write+review+polish: update state, write memory deltas."""

import json
import os
from datetime import datetime
from state_manager import StateManager


def commit_episode(project_root: str, episode_id: str,
                   memory_deltas: dict | None = None):
    """Update state.json and write memory deltas after episode is finalized.

    memory_deltas should be the JSON output from data-agent, with keys:
    - character_states: list of {character, state, changes}
    - scene_changes: list of {scene, changes}
    - foreshadowing: list (replaces current)
    - costume_updates: dict of {character: {outfit, episode}}
    """
    sm = StateManager(project_root)
    sm.update("current_episode", episode_id)
    sm.update("stats.episodes_written",
              sm.get_state()["stats"]["episodes_written"] + 1)
    sm.update("phase", "writing")
    sm.update("last_updated", datetime.now().isoformat())

    if memory_deltas:
        from memory_manager import MemoryManager
        mm = MemoryManager(project_root)

        for cs in memory_deltas.get("character_states", []):
            mm.update_character_state(
                episode_id, cs["character"], cs["state"], cs.get("changes", [])
            )

        for sc in memory_deltas.get("scene_changes", []):
            mm.update_scene_state(sc["scene"], episode_id, sc.get("changes", {}))

        if "foreshadowing" in memory_deltas:
            mm.update_foreshadowing(memory_deltas["foreshadowing"])

        for char, info in memory_deltas.get("costume_updates", {}).items():
            mm.update_costume(char, info["outfit"], episode_id)

    print(f"Episode {episode_id} committed.")


if __name__ == "__main__":
    import sys
    commit_episode(sys.argv[1], sys.argv[2])
