"""
Configuration constants for the Miscrits Sprite Replacer
(added MISCRITS_LOCAL_PATH for Move Editor)
"""
from pathlib import Path
import os

# Paths
ROOT = Path(__file__).parent.resolve()

# Updated: Point to the Windows executable
GODOT_BIN = ROOT / "bin" / "Godot_v4.1-stable_linux.x86_64"

ENCODE_SCRIPT = ROOT / "gd_scripts" / "crits_single_encode.gd"
FAVICON_PATH = ROOT / "assets" / "favicon.ico"
BOSSES_CATALOG_PATH = ROOT / "assets" / "bosses.json"

# CDN URLs
MISCRITS_JSON_URL = "https://worldofmiscrits.com/miscrits.json"
ELEMENT_ICON_BASE = "https://worldofmiscrits.com"
SPRITE_CDN_BASE = "https://cdn.worldofmiscrits.com/miscrits"
AVATAR_CDN_BASE = "https://cdn.worldofmiscrits.com/avatars"

# Local Windows default miscrits.json path (where the game's cache is usually stored)
# This resolves %USERPROFILE% correctly on Windows.
MISCRITS_LOCAL_PATH = Path(os.path.expandvars(r"%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\miscrits.json"))

# UI Constants
PAGE_SIZE = 16
CANVAS_SIZE = (256, 256)
AVATAR_SIZE = (50, 50)
PREVIEW_CANVAS_SIZE = (256, 256)
AVATAR_PREVIEW_SIZE = (128, 128)

# Timeouts
FETCH_TIMEOUT = 5
