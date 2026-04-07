# PathForge

Visual editor for creating interactive choice-based stories. Built with a plugin-based architecture so each feature is isolated and can't break anything else.

Comes with two apps: **PathForge** (story visualizer/editor) and **Nodepad** (node-based note-taking tool).

![PathForge Logo](screenshots/pathforge_logo.png)

> Screenshot of the app coming soon — run it yourself or run `PathForge.exe` directly (Windows, no install needed).

---

## What it does

- Drag-and-drop node editor for mapping out branching stories
- Each node is a story beat — you link them with choices (up to 8 per node: A–H)
- Custom story format: `N:` (node ID), `T:` (title), `S:` (story text), `A:–H:` (choices + where they lead)
- Zoom, pan, branch-drag (move a whole subtree), fit-to-screen
- Auto-layout modes: Grid, Random, or the custom **Tree Reaction** algorithm
- Tree Demo tool — generate test trees from 4 to 8192 nodes instantly
- Integrated file manager for bulk editing nodes
- Story Reader — play through your story like a game to test it
- Export/import projects
- Auto-save for node positions and project state

---

## Story Format

Each story node is a plain `.txt` file:

```
N: 1
T: The Dark Forest
S: You stand at the edge of a dark forest. The path ahead splits in two.
A: Take the left path -> 2
B: Take the right path -> 3
C: Turn back -> 4
```

---

## Running from source

Requires Python 3.x.

```bash
cd pathforge_1.1
python story_visualizer.py
```

For Nodepad:
```bash
cd nodepad_1.1
python nodepad.py
```

Or just run `PathForge.exe` (Windows, no install needed).

---

## Architecture

PathForge uses a plugin system — each feature (drag, zoom, pan, right-click menu, etc.) is its own plugin file. The `PluginManager` handles registration and event routing so plugins can't conflict with each other.

```
story_visualizer.py     # Main app + UI
plugin_manager.py       # Plugin registration + event system
base_plugin.py          # Abstract base class all plugins inherit from
basic_drag_plugin.py    # Node dragging
branch_drag_plugin.py   # Whole-branch dragging
mouse_zoom_plugin.py    # Scroll-to-zoom
pan_plugin.py           # Canvas panning
fit_to_screen_plugin.py # Auto-fit view
right_click_menu_plugin.py  # Context menus
file_creator_plugin.py  # Node file creation
file_explorer_plugin.py # File browser panel
story_format_parser.py  # Parses the N:/T:/S:/A-H: story format
file_manager.py         # Bulk file operations
story_reader.py         # Playtest your story
```

---

## Dev Mode

There's a hidden dev tools panel accessible via a password (`dev1211`). It was used during development for debugging — left in as-is since the source is now open.

---

## Related

The tree layout algorithm used in PathForge was extracted and open-sourced separately:
[tree-reaction-algorithms](https://github.com/iz8nzax05/tree-reaction-algorithms)
