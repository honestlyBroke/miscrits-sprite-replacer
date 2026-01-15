# Miscrits Sprite Replacer & Moves Editor

A modular Streamlit application for replacing Miscrit sprites/avatars and editing in-game moves.

## 📁 Project Structure


```

miscrits-sprite-replacer/
├── app.py                      # Main application entry point
├── config.py                   # Configuration constants
├── data_loader.py              # Data loading utilities
├── image_utils.py              # Image processing functions
├── ui_components.py            # Reusable UI components & Styling
├── encoder.py                  # Sprite encoding with Godot
├── session_manager.py          # Session state management
├── views/
│   ├── **init**.py
│   ├── selection.py            # Step 1: Mode selection (Miscrits/Bosses/Moves)
│   ├── editor.py               # Step 2: Sprite/Avatar editing interface
│   └── moves_editor.py         # Step 2: Moves/Abilities editor interface
├── bin/
│   └── Godot_v4.4.1-stable_win64.exe  # Godot binary (Adjust name/platform as needed)
├── gd_scripts/
│   └── crits_single_encode.gd
└── assets/
├── favicon.ico
└── bosses.json

```

## 🆕 What's New

### 1. **Moves Editor Pro**
- **Edit Abilities:** Modify move names, types, and elements for any Miscrit.
- **Game-Accurate Logic:** Auto-calculates icons based on move type (e.g., Physical, Dot, Buff) just like the game.
- **Searchable Dropdown:** Quickly find Miscrits by ID, first name, or final name.
- **JSON Export:** Download a patched `miscrits.json` ready for the game cache.

### 2. **Modern UI Overhaul**
- **Sleek Interface:** New gradient headers, card-based layouts, and a dark theme matching the game's aesthetic.
- **Improved Sidebar:** Detailed, step-by-step instructions and file path guides built right into the app.

### 3. **Refined Sprite/Avatar Workflow**
- **Dedicated Modes:** Distinct toggle between "Sprite" (Battle Art) and "Avatar" (Profile Icon) editing.
- **Smart Resizing:**
  - **Sprites:** Flexible scaling with aspect ratio locking.
  - **Avatars:** Auto-resized to strict 50x50px dimensions.

### 4. **API-Based Loading**
- Fetches data directly from `https://worldofmiscrits.com/miscrits.json` ensuring you always edit the latest game data.

## 🚀 Quick Start

```bash
# Install dependencies
pip install streamlit pillow requests

# Run the app
streamlit run app.py

```

## 📦 Module Overview

### `views/moves_editor.py`

* Handles the logic for the Moves Editor.
* Manages state for unsaved changes and undo history.
* Generates game-accurate icon previews.

### `views/editor.py`

* Handles the Sprite and Avatar editing logic.
* Manages image uploading, resizing canvas, and Godot encoding calls.

### `ui_components.py`

* Centralized CSS styling (Gradients, Cards, Headers).
* Reusable UI elements like the detailed Sidebar instructions and Pagination.

### `encoder.py` & `gd_scripts/`

* Bridges Python and Godot to encrypt images into the game's proprietary format.

## 🎯 Usage Flow

### A. Replacing Images (Sprites/Avatars)

1. **Select Target** (Step 1)
* Choose **Miscrits** or **Bosses** mode.
* Search and select your target.


2. **Configure** (Step 2)
* **Stage:** (Miscrits only) Select evolution stage (1-4).
* **Mode:** Toggle between **Sprite** or **Avatar**.


3. **Edit & Install**
* Upload your image.
* Adjust scale (Sprites) or review auto-resize (Avatars).
* Click **Download Encrypted File**.
* Place the file in the folder specified in the sidebar.



### B. Editing Moves

1. **Select Tool** (Step 1)
* Select **Moves Editor** mode.


2. **Edit**
* Search for a Miscrit.
* Modify ability names, types, or elements.
* Visual icons update in real-time.


3. **Install**
* Click **Prepare Download**.
* Download the `miscrits.json` file.
* Place it in the `image_cache` folder (path provided in sidebar).



## 🔧 Making Changes

### Adding New Filters

* Modify `filter_catalog()` in `views/selection.py`.

### Changing Game Logic

* Edit `views/moves_editor.py` to change how icons are calculated or how data is exported.

### Modifying Styles

* Edit `MISCRITS_CSS` in `ui_components.py`.

## 📝 Notes

* **Cache Files:** The game prioritizes files in the `image_cache` folder. Ensure filenames match exactly (e.g., hash for sprites, `miscrits.json` for moves).
* **Windows vs Mac/Linux:** The `bin/` folder currently expects a Windows Godot binary. Update `config.py` if running on other platforms.

## 🐛 Troubleshooting

**"Encoding failed"**

* Verify the Godot binary path in `config.py` matches your actual file in `bin/`.
* Ensure the binary is executable.

**"Changes not showing in game"**

* **Sprites:** Ensure you pasted the file into the `sprites` subfolder.
* **Avatars:** Ensure you pasted the file into the `miscrits` subfolder.
* **Moves:** Ensure `miscrits.json` is in the root `image_cache` folder.
* Restart the game client.
