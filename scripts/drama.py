#!/usr/bin/env python3
"""short-drama-writer CLI entry point."""

import sys
import os


def resolve_project_root() -> str:
    """Walk up from cwd to find .drama/state.json."""
    cwd = os.getcwd()
    for _ in range(20):
        if os.path.isfile(os.path.join(cwd, ".drama", "state.json")):
            return cwd
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    raise FileNotFoundError(
        "No .drama/state.json found. Run from a drama project directory."
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: drama.py <command> [args]")
        print("Commands: init, state, character, memory, commit, outline, review")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        from project_init import init_project
        init_project(sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == "state":
        from state_manager import StateManager
        root = resolve_project_root()
        sm = StateManager(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "get"
        if sub == "get":
            print(sm.get_state_json())
        elif sub == "update":
            key = sys.argv[3]
            value = sys.argv[4]
            sm.update(key, value)
    elif command == "character":
        from character_manager import CharacterManager
        root = resolve_project_root()
        cm = CharacterManager(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "list"
        if sub == "list":
            for name in cm.list_characters():
                print(name)
        elif sub == "get":
            print(cm.get_character(sys.argv[3]))
        elif sub == "set":
            cm.save_character(sys.argv[3], sys.argv[4])
    elif command == "memory":
        from memory_manager import MemoryManager
        root = resolve_project_root()
        mm = MemoryManager(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "summary"
        if sub == "summary":
            print(mm.get_summary())
        elif sub == "character_state":
            print(mm.get_character_states_json())
        elif sub == "foreshadowing":
            print(mm.get_foreshadowing_json())
    elif command == "commit":
        from chapter_commit import commit_episode
        root = resolve_project_root()
        commit_episode(root, sys.argv[2])
    elif command == "outline":
        from outline_loader import OutlineLoader
        root = resolve_project_root()
        ol = OutlineLoader(root)
        ep_num = sys.argv[2] if len(sys.argv) > 2 else None
        if ep_num:
            print(ol.get_episode_outline(ep_num))
        else:
            print(ol.get_all_outlines_json())
    elif command == "review":
        from review_saver import ReviewSaver
        root = resolve_project_root()
        rs = ReviewSaver(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "save"
        if sub == "save":
            rs.save_review(sys.argv[3], sys.argv[4])
        elif sub == "get":
            print(rs.get_review(sys.argv[3]))


if __name__ == "__main__":
    main()
