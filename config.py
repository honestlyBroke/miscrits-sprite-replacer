"""
Configuration constants for the Miscrits Sprite Replacer
"""
from pathlib import Path
import os
import platform

# Paths
ROOT = Path(__file__).parent.resolve()

# Determine OS and select correct binary
system = platform.system()
if system == "Windows":
    GODOT_BIN_NAME = "Godot_v4.4.1-stable_win64.exe"
else:
    # Linux (Streamlit Cloud)
    # Ensure this filename matches EXACTLY what you upload to the bin/ folder
    GODOT_BIN_NAME = "Godot_v4.1-stable_linux.x86_64" 

GODOT_BIN = ROOT / "bin" / GODOT_BIN_NAME

ENCODE_SCRIPT = ROOT / "gd_scripts" / "crits_single_encode.gd"
FAVICON_PATH = ROOT / "assets" / "favicon.ico"
BOSSES_CATALOG_PATH = ROOT / "assets" / "bosses.json"

# CDN URLs
MISCRITS_JSON_URL = "https://miscrits-proxy.yatosquare.workers.dev/"
ELEMENT_ICON_BASE = "https://worldofmiscrits.com"
SPRITE_CDN_BASE = "https://cdn.worldofmiscrits.com/miscrits"
AVATAR_CDN_BASE = "https://cdn.worldofmiscrits.com/avatars"

# Local miscrits.json path
if system == "Windows":
    MISCRITS_LOCAL_PATH = Path(os.path.expandvars(r"%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\miscrits.json"))
else:
    # Linux fallback (e.g., for Streamlit Cloud or local Linux dev)
    MISCRITS_LOCAL_PATH = Path.home() / ".local/share/godot/app_userdata/Miscrits/image_cache/miscrits.json"

# UI Constants
PAGE_SIZE = 16
CANVAS_SIZE = (256, 256)
AVATAR_SIZE = (50, 50)
PREVIEW_CANVAS_SIZE = (256, 256)
AVATAR_PREVIEW_SIZE = (128, 128)

# Timeouts
FETCH_TIMEOUT = 5
