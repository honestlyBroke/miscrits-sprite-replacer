import os
import subprocess
import tempfile
from pathlib import Path
import hashlib
import json
import requests
from io import BytesIO
import shutil
from typing import Literal, Union

import streamlit as st

import logging

# Silence noisy 'Missing file <media_id>.png' tracebacks that can occur when the browser
# requests a stale /media/<id>.png during reruns/hot-reload. This does not affect app behavior.
logging.getLogger('streamlit.web.server.media_file_handler').setLevel(logging.CRITICAL)
logging.getLogger('streamlit.runtime.memory_media_file_storage').setLevel(logging.CRITICAL)

from PIL import Image

# =====================================================================
# Custom CSS Styling
# =====================================================================
MISCRITS_CSS = """
<style>
/* ==== Base reset (from provided CSS) ==== */
*,:before,:after{box-sizing:border-box;border-width:0;border-style:solid;border-color:#e5e7eb}
:before,:after{--tw-content:""}
html,body{margin:0;line-height:1.5;font-family:BorisBlackBloxx,sans-serif;-webkit-text-size-adjust:100%}
img,svg,video,canvas,audio,iframe,embed,object{display:block;vertical-align:middle}
img,video{max-width:100%;height:auto}

/* ==== Theme tokens (from provided CSS) ==== */
:root{
  --background: 0 0% 0%;
  --foreground: 72 50% 49%;
  --card: 0 0% 5%;
  --card-foreground: 72 50% 49%;
  --popover: 0 0% 0%;
  --popover-foreground: 72 50% 49%;
  --primary: 72 50% 49%;
  --primary-foreground: 0 0% 0%;
  --secondary: 0 0% 0%;
  --secondary-foreground: 72 50% 49%;
  --muted: 0 0% 10%;
  --muted-foreground: 72 50% 39%;
  --accent: 72 50% 49%;
  --accent-foreground: 0 0% 0%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 0 0% 98%;
  --border: 72 50% 49%;
  --input: 72 50% 49%;
  --ring: 72 50% 49%;
  --radius: .5rem;
}

/* Apply theme */
body{
  overflow-x:hidden;
  background-color: rgb(0 0 0 / 1);
  color: rgb(165 188 62 / 1);
  font-family:BorisBlackBloxx,sans-serif;
  font-feature-settings:"rlig" 1,"calt" 1;
}
*{border-color:hsl(var(--border))}

/* Scrollbar (from provided CSS) */
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background-color:rgb(0 0 0 / 1)}
::-webkit-scrollbar-thumb{border-radius:9999px;background-color:rgb(165 188 62 / 1)}
::-webkit-scrollbar-thumb:hover{background-color:rgb(131 150 48 / 1)}

/* Utility classes used by the app */
.container{width:100%;margin-right:auto;margin-left:auto;padding-right:2rem;padding-left:2rem}
@media (min-width:1400px){.container{max-width:1400px}}

.glass-card{
  border-radius:var(--radius);
  border-width:1px;
  border-color:#a5bc3e66;
  background-color:#000000b3;
  padding:1.5rem;
  box-shadow:0 10px 15px -3px rgb(0 0 0 / .1), 0 4px 6px -4px rgb(0 0 0 / .1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.neon-border{
  border-radius:var(--radius);
  border-width:2px;
  border-color:rgb(165 188 62 / 1);
  box-shadow:0 0 10px rgba(165,188,62,.7);
}
.yellow-border{
  border-radius:var(--radius);
  border-width:2px;
  border-color:rgb(239 191 75 / 1);
  box-shadow:0 0 10px rgba(239,191,75,.7);
}
.heading-1{
  font-family:BorisBlackBloxx,sans-serif;
  font-size:2.25rem;
  line-height:2.5rem;
  color:#fff;
  filter: drop-shadow(0 0 8px rgba(165,188,62,.5));
}
@media (min-width:768px){.heading-1{font-size:3rem;line-height:1}}
@media (min-width:1024px){.heading-1{font-size:3.75rem;line-height:1}}
.heading-2{
  font-family:Miscria,sans-serif;
  font-size:1.875rem;
  line-height:2.25rem;
  color:rgb(165 188 62 / 1);
}
.heading-yellow{
  font-family:Miscria,sans-serif;
  font-size:1.875rem;
  line-height:2.25rem;
  color:rgb(239 191 75 / 1);
}

/* Streamlit component adjustments (keep minimal) */
main .block-container{padding-top:2rem;padding-bottom:2rem}
</style>
"""

# =====================================================================
# Paths & Config
# =====================================================================

ROOT = Path(__file__).parent.resolve()

GODOT_BIN = ROOT / "bin" / "Godot_v4.1-stable_linux.x86_64"
ENCODE_SCRIPT = ROOT / "gd_scripts" / "crits_single_encode.gd"
FAVICON_PATH = ROOT / "assets" / "favicon.ico"

# Stripped catalog: id, element, rarity, first_name, final_name
MISCRIT_CATALOG_PATH = ROOT / "assets" / "miscrits_first_final_names.json"

BOSSES_CATALOG_PATH = ROOT / "assets" / "bosses.json"

PAGE_SIZE = 16  # how many Miscrits to render at once

st.set_page_config(
    page_title="Miscrits Sprite Replacer",
    layout="wide",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🎮",
    initial_sidebar_state="expanded",
)

# =====================================================================
# Styling & Helpers
# =====================================================================

st.markdown(MISCRITS_CSS, unsafe_allow_html=True)

def local_css():
    st.markdown(
        """
    <style>
        body {
            background-color: #000000;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
        }
        .stProgress > div > div > div > div {
            background-color: #ffcc33;
        }
        div[data-testid="caption"] {
            text-align: center;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

def display_name(raw: str) -> str:
    """
    Convert internal names like:
    - 'magicite_novice' -> 'Magicite Novice'
    - 'ylil nosaj' -> 'Ylil Nosaj'
    - 'FireWind' -> 'Firewind' (not used for names, but safe)
    """
    if not raw:
        return ""

    return raw.replace("_", " ").title()

def short_name(name: str, max_len: int = 14) -> str:
    if len(name) <= max_len:
        return name
    return name[: max_len - 3] + "..."

@st.cache_data
def load_miscrit_catalog():
    if not MISCRIT_CATALOG_PATH.exists():
        return []

    with open(MISCRIT_CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_boss_catalog():
    if not BOSSES_CATALOG_PATH.exists():
        return []
    with open(BOSSES_CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

ELEMENT_ICON_BASE = "https://worldofmiscrits.com"

def element_icon_url(element: str) -> str:
    """
    Rules:
    - Physical => physical.png
    - Dual elements (FireWind) => firewind.png
    - Single elements (Fire) => fire.png
    """
    if not element:
        return ""

    slug = element.strip().lower().replace(" ", "")
    return f"{ELEMENT_ICON_BASE}/{slug}.png"


def sprite_cdn_url(name: str) -> str:
    """
    Build CDN URL for a miscrit back sprite given an evo name.
    Mirrors: miscrit.names[evo_id].replace(" ", "_").to_lower() + "_back.png"
    """
    slug = name.replace(" ", "_").lower()
    return f"https://cdn.worldofmiscrits.com/miscrits/{slug}_back.png"


AVATAR_BASE = "https://cdn.worldofmiscrits.com/avatars"


def avatar_cdn_url(name: str) -> str:
    """Build CDN URL for a Miscrit avatar icon (50x50)."""
    slug = name.replace(" ", "_").lower()
    return f"{AVATAR_BASE}/{slug}_avatar.png"


def sprite_cache_filename(url: str) -> str:
    """
    Cache filename is SHA256 of the full CDN URL (hex, no extension).
    """
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def load_sprite_on_canvas(url: str, canvas_size=(256, 256)):
    """
    Load a Miscrit sprite from the CDN, scale it down to fit inside
    `canvas_size` while keeping aspect ratio, and center it on a
    transparent canvas. This makes all card boxes the same size.
    """
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except Exception:
        # If fetch fails, return an empty transparent canvas
        return Image.new("RGBA", canvas_size, (0, 0, 0, 0))

    img = Image.open(BytesIO(resp.content)).convert("RGBA")

    # Scale down to fit inside canvas while preserving aspect ratio
    img.thumbnail(canvas_size, Image.LANCZOS) # type: ignore

    # Center on a transparent canvas
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_size[0] - img.width) // 2
    y = (canvas_size[1] - img.height) // 2
    canvas.paste(img, (x, y), img)

    return canvas


def place_on_canvas(img: Image.Image, canvas_size=(256, 256)) -> Image.Image:
    """Center an image on a transparent canvas of fixed size for display."""
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_size[0] - img.width) // 2
    y = (canvas_size[1] - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


def get_original_sprite_size(url: str):
    """
    Download the original final-evo sprite from the CDN and return (width, height).
    If anything goes wrong, fall back to a reasonable default.
    """
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        return img.size  # (w, h)
    except Exception:
        return (256, 256)


def reset_workdir():
    """Delete the current workdir and create a fresh one."""
    old_dir = Path(st.session_state.get("workdir", tempfile.gettempdir()))
    shutil.rmtree(old_dir, ignore_errors=True)
    new_dir = tempfile.mkdtemp(prefix="miscrits_sprites_")
    st.session_state["workdir"] = new_dir
    return Path(new_dir)

def show_pil_via_file(
    img: Image.Image,
    filename: str,
    *,
    caption: str | None = None,
    # Use Literal to restrict the string to values Streamlit expects
    width: Union[int, Literal["stretch", "content"]] = "stretch",
) -> None:
    """Save a PIL image to the workdir and display it via file path."""
    workdir = Path(st.session_state.get("workdir", tempfile.gettempdir()))
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / filename
    img.save(path)
    st.image(
        str(path),
        caption=caption,
        width=width,
    )



# =====================================================================
# State Management
# =====================================================================

if "step" not in st.session_state:
    st.session_state["step"] = 1
    st.session_state["selected_miscrit"] = None
    st.session_state["workdir"] = tempfile.mkdtemp(prefix="miscrits_sprites_")
    st.session_state["page"] = 0
    st.session_state["patched_path"] = None
    st.session_state["resized_path"] = None
    st.session_state["uploaded_image_bytes"] = None
    st.session_state["uploaded_image_name"] = None
    st.session_state["patched_bytes"] = None
    st.session_state["needs_reencode"] = False
    st.session_state["prev_scale_factor"] = None
    st.session_state["prev_keep_aspect"] = None
    st.session_state["upload_hash"] = None
    st.session_state["scale_factor"] = 1.0
    st.session_state["keep_aspect"] = True
    st.session_state["edit_mode"] = "Sprite"
    st.session_state["prev_edit_mode"] = "Sprite"

workdir = Path(st.session_state["workdir"])

# =====================================================================
# UI: Sidebar
# =====================================================================

with st.sidebar:
    st.title("🎮 Sprite Replacer")

    st.markdown(
        """
        <div class="sidebar-box">
            <h3>How this tool works:</h3>
            <ol>
                <li>Pick a Miscrit or Boss from the grid.</li>
                <li>Choose whether you want to replace the <b>Sprite</b> or the <b>Avatar</b>.</li>
                <li>Upload your replacement image and resize it if needed.</li>
                <li>Download the generated encrypted cache file.</li>
                <li>Drop that file into the correct folder and overwrite the existing one.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📁 Where to put the file")
    st.markdown(
        r"""
**Windows path (copy-paste into Explorer):**

- **If you are editing a Sprite:**
```text
%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\sprites
```

- **If you are editing an Avatar:**
```text
%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\miscrits
```

**Once you’re there:**

1. Sort the folder by **Date modified** so the newest file is on top.
2. Make sure the filename matches **exactly** what the app shows (a long hash like `b6b0c2...`).
3. Replace the existing file **in place**.
4. ⚠️ If Windows adds `(1)` or extra extensions, it will **not** work — rename it back to the exact hash.
""",
        unsafe_allow_html=False,
    )

    st.markdown("### 🎥 Tutorial Video")
    if (ROOT / "assets" / "spriteguide-real-2.mp4").exists():
        st.video("assets/spriteguide-real-2.mp4")

    if st.button("🔄 Reset Session", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# =====================================================================
# UI: Main Header
# =====================================================================

local_css()
st.title("Miscrits Sprite Tool")
st.markdown(
    """
Browse Miscrits and Bosses by name, element, rarity, or location — then replace their sprite or avatar with your own custom image.
"""
)

# --- CHECK BINARY ---

if not GODOT_BIN.exists() or not os.access(GODOT_BIN, os.X_OK):
    st.error(f"❌ Godot binary missing or not executable at: `{GODOT_BIN}`")
    st.stop()

if not ENCODE_SCRIPT.exists():
    st.error(f"❌ Encode script missing at: `{ENCODE_SCRIPT}`")
    st.stop()

# =====================================================================
# STEP 1: MISCRIPEDIA GRID
# =====================================================================

if st.session_state["step"] == 1:
    st.header("Step 1: Choose a Miscrit or Local Boss")

    dataset = st.radio(
        "Catalog",
        ["Miscrits", "Bosses"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["dataset"] = dataset
    if dataset == "Bosses":
        catalog = load_boss_catalog()
        search_label = "Search Bosses..."
        search_ph = "gb, global boss, mizokami, magicite..."
    else:
        catalog = load_miscrit_catalog()
        search_label = "Search Miscrits..."
        search_ph = "Flue, Flowerpiller, Afterburn..."
    if not catalog:
        st.error("Could not load bosses.json" if dataset == "Bosses" else "Could not load miscrits_first_final_names.json")
        st.stop()

    # --- Search & Filters ---
    search_term = st.text_input(search_label, placeholder=search_ph)

    col_rarity, col_element = st.columns([1, 1])
    all_rarities = sorted({m["rarity"] for m in catalog})
    all_elements = sorted({m["element"] for m in catalog})
    rarity_label = "All Rarities" if dataset == "Miscrits" else "All Locations"
    rarity_placeholder = "Select rarities" if dataset == "Miscrits" else "Select locations"

    with col_rarity:
        rarity_filter = st.multiselect(
            rarity_label,
            all_rarities,
            default=None,
            placeholder=rarity_placeholder,
        )

    with col_element:
        element_filter = st.multiselect(
            "All Elements", all_elements, default=[]
        )

    # --- Apply filtering ---
    filtered = []
    for m in catalog:
        # Search by first/final evo name + rarity (+ small aliases)
        if search_term:
            s = search_term.strip().lower()
        
            # Allow short aliases
            aliases = {
                "gb": "global boss",
                "globalboss": "global boss",
            }
            s = aliases.get(s, s)
        
            haystack = " ".join([
                m.get("first_name", ""),
                m.get("final_name", ""),
                m.get("rarity", ""),      # so "global boss" matches
            ]).lower()
        
            if s not in haystack:
                continue

        if rarity_filter and m["rarity"] not in rarity_filter:
            continue

        if element_filter and m["element"] not in element_filter:
            continue

        filtered.append(m)

    total = len(filtered)
    if total == 0:
        st.caption("No Miscrits match your filters.")
    else:
        # Pagination
        page = st.session_state.get("page", 0)
        max_page = max((total - 1) // PAGE_SIZE, 0)
        if page > max_page:
            page = max_page
            st.session_state["page"] = page

        start_idx = page * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total)
        page_items = filtered[start_idx:end_idx]

        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total} Miscrits")

        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ Previous", disabled=page == 0):
                st.session_state["page"] = max(page - 1, 0)
                st.rerun()
        with col_page:
            st.markdown(f"<p style='text-align:center;'>Page {page + 1} of {max_page + 1}</p>", unsafe_allow_html=True)
        with col_next:
            if st.button("Next ➡️", disabled=page >= max_page):
                st.session_state["page"] = min(page + 1, max_page)
                st.rerun()

        # --- Card grid ---
        cols = st.columns(4)
        for i, m in enumerate(page_items):
            col = cols[i % 4]
            with col:
                with st.container(border=True):
                    # Top row: element icon + name
                    icon_url = element_icon_url(m["element"])
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.image(icon_url, width='stretch')
                    with c2:
                        title = display_name(m["first_name"])

                        margin = "15px" if dataset == "Bosses" else "5px"
                        font_size = "18px" if dataset == "Bosses" else "15px"

                        st.markdown(
                            f"<div style='margin-top: {margin}; font-weight: 700; font-size: {font_size};'>"
                            f"{title}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )


                        if dataset == "Miscrits":
                            st.caption(f"Final: {display_name(m['final_name'])}")
                    # Sprite preview = FIRST evo back sprite
                    sprite_url = sprite_cdn_url(m["first_name"])

                    # Draw sprite on a fixed-size canvas so every card is the same height
                    sprite_img = load_sprite_on_canvas(sprite_url, canvas_size=(256, 256))
                    show_pil_via_file(
                        sprite_img,
                        f"grid_{m['id']}.png",
                        width="stretch",
                    )

                    # Meta row
                    st.caption(f"{m['element']} • {m['rarity']}")
                    btn_label = "Change Sprite" if dataset == "Miscrits" else "Change Boss Sprite"
                    # Select button
                    if st.button(
                        btn_label,
                        key=f"sel_{m['id']}",
                        type="primary",
                        width='stretch',
                    ):
                        st.session_state["selected_miscrit"] = m
                        st.session_state["step"] = 2
                        # reset per-edit paths
                        st.session_state["patched_path"] = None
                        st.session_state["resized_path"] = None
                        st.rerun()

# =====================================================================
# STEP 2: EDIT + ENCODE + DOWNLOAD
# =====================================================================

elif st.session_state["step"] == 2:
    m = st.session_state.get("selected_miscrit")
    if not m:
        st.warning("No Miscrit selected. Please go back and pick one.")
        if st.button("⬅️ Back to Miscrits"):
            st.session_state["step"] = 1
            st.rerun()
        st.stop()

    first_name = m["first_name"]
    final_name = m["final_name"]

    st.markdown(
        '<p class="replace-label">What do you want to replace?</p>',
        unsafe_allow_html=True,
    )
    
    edit_mode = st.radio(
        "Edit mode",
        ["Sprite", "Avatar"],
        horizontal=True,
        label_visibility="collapsed",
        index=0 if st.session_state.get("edit_mode", "Sprite") == "Sprite" else 1,
    )



    st.session_state["edit_mode"] = edit_mode

    prev_mode = st.session_state.get("prev_edit_mode", "Sprite")
    if edit_mode != prev_mode:
        # Switching between sprite/avatar: clear per-mode state
        st.session_state["patched_path"] = None
        st.session_state["resized_path"] = None
        st.session_state["uploaded_image_bytes"] = None
        st.session_state["uploaded_image_name"] = None
        st.session_state["patched_bytes"] = None
        st.session_state["needs_reencode"] = False
        st.session_state["scale_factor"] = 1.0
        st.session_state["keep_aspect"] = True
        st.session_state["prev_scale_factor"] = None
        st.session_state["prev_keep_aspect"] = None
        st.session_state["upload_hash"] = None
        st.session_state["prev_edit_mode"] = edit_mode
        st.rerun()
    else:
        st.session_state["prev_edit_mode"] = edit_mode

    is_avatar = edit_mode == "Avatar"

    if is_avatar:
        resource_label = "avatar"
        current_url = avatar_cdn_url(final_name)
    else:
        resource_label = "sprite"
        current_url = sprite_cdn_url(final_name)

    cache_name = sprite_cache_filename(current_url)
    orig_w, orig_h = get_original_sprite_size(current_url)

    st.header(f"Step 2 · Upload new {resource_label} for **{display_name(final_name)}**")
    if is_avatar:
        st.caption(
            f"This will replace the profile avatar for: **{final_name}**.\n\n"
            "Avatars are always **50×50px**. We'll resize your upload automatically."
        )
    else:
        st.caption(
            f"This will replace the final evolution sprite: **{final_name}**.\n\n"
            "Download the encrypted file and drop it into your `sprites` folder. "
            "Keep the filename exactly as is."
        )

    col_left, col_right = st.columns(2)

    # Left column: current sprite/avatar info
    with col_left:
        st.subheader(f"Current in-game {resource_label}")
        canvas_size = (256, 256) if not is_avatar else (128, 128)
        final_img = load_sprite_on_canvas(current_url, canvas_size=canvas_size)
        show_pil_via_file(
            final_img,
            f"current_{resource_label}_{cache_name}.png",
            caption=final_name,
            width="stretch",
        )

        if is_avatar:
            st.caption("Original avatar size: 50×50px")
        else:
            st.caption(f"Original sprite size: {orig_w}×{orig_h}px")
        st.info(
            f"Game cache filename for this {resource_label}:\n`{cache_name}`",
            icon="💾",
        )

    # Right column: upload + controls + download
    with col_right:
        st.subheader("Your replacement art")

        uploaded_bytes = st.session_state.get("uploaded_image_bytes")
        uploaded_name = st.session_state.get("uploaded_image_name")

        if uploaded_bytes is None:
            new_file = st.file_uploader(
                "Upload PNG/JPG (we'll resize and encode it for you)",
                type=["png", "jpg", "jpeg"],
            )
            if new_file is not None:
                uploaded_bytes = new_file.read()
                st.session_state["uploaded_image_bytes"] = uploaded_bytes
                st.session_state["uploaded_image_name"] = new_file.name
                # Reset dependent state
                st.session_state["resized_path"] = None
                st.session_state["patched_path"] = None
                st.session_state["patched_bytes"] = None
                st.session_state["needs_reencode"] = True
                st.session_state["prev_scale_factor"] = None
                st.session_state["prev_keep_aspect"] = None
                st.session_state["upload_hash"] = None
                st.session_state["scale_factor"] = 1.0
                st.session_state["keep_aspect"] = True
                st.rerun()

        patched_bytes = None

        if uploaded_bytes is not None:
            img = Image.open(BytesIO(uploaded_bytes)).convert("RGBA")

            # --- Compute resized image first ---
            if is_avatar:
                # Force 50×50, no size controls
                target_w, target_h = 50, 50
                img_resized = img.resize((target_w, target_h), Image.LANCZOS)# type: ignore
                scale_factor = 1.0
                keep_aspect = True
            else:
                # Use current size settings from state
                scale_factor = st.session_state.get("scale_factor", 1.0)
                keep_aspect = st.session_state.get("keep_aspect", True)

                # Detect if size or source image changed, to trigger re-encode
                current_hash = hashlib.sha256(uploaded_bytes).hexdigest()
                prev_scale = st.session_state.get("prev_scale_factor")
                prev_keep = st.session_state.get("prev_keep_aspect")
                prev_hash = st.session_state.get("upload_hash")

                if (
                    prev_scale is None
                    or prev_keep is None
                    or prev_hash is None
                    or scale_factor != prev_scale
                    or keep_aspect != prev_keep
                    or current_hash != prev_hash
                ):
                    st.session_state["needs_reencode"] = True
                    st.session_state["prev_scale_factor"] = scale_factor
                    st.session_state["prev_keep_aspect"] = keep_aspect
                    st.session_state["upload_hash"] = current_hash

                # Calculate new dimensions using original sprite size as baseline
                if orig_w == 50 and orig_h == 50:
                    # Special-case tiny 50x50 sprites
                    target_w, target_h = 50, 50
                else:
                    if keep_aspect:
                        # Match original HEIGHT * scale, adjust width by replacement's aspect ratio
                        aspect_ratio = img.width / img.height
                        target_h = int(orig_h * scale_factor)
                        target_w = int(target_h * aspect_ratio)
                    else:
                        # Stretch based on the original WIDTH/HEIGHT * scale
                        target_w = int(orig_w * scale_factor)
                        target_h = int(orig_h * scale_factor)

                img_resized = img.resize((target_w, target_h), Image.LANCZOS)# type: ignore

            # Save resized sprite/avatar
            resized_path = workdir / f"{(final_name if not is_avatar else first_name).replace(' ', '_')}.resized.png"
            img_resized.save(resized_path)
            st.session_state["resized_path"] = str(resized_path)

            # Display preview centered in a fixed-size canvas so it stays in the container
            preview_canvas_size = (256, 256) if not is_avatar else (128, 128)
            preview_canvas = place_on_canvas(img_resized, canvas_size=preview_canvas_size)
            # For avatars we don't show the size in the image caption so that
            # the filename and final size text can appear in the desired order below.
            # Display preview centered in a fixed-size canvas so it stays in the container
            preview_canvas_size = (256, 256) if not is_avatar else (128, 128)
            preview_canvas = place_on_canvas(img_resized, canvas_size=preview_canvas_size)

            if is_avatar:
                show_pil_via_file(
                    preview_canvas,
                    "preview_avatar.png",
                    width="stretch",
                )
            else:
                show_pil_via_file(
                    preview_canvas,
                    "preview_sprite.png",
                    caption=(
                        f"Final size: {target_w}×{target_h}px "
                        f"(original: {orig_w}×{orig_h}px)"
                    ),
                    width="stretch",
                )



            # File name and controls now sit *below* the preview for better alignment
            if uploaded_name:
                st.caption(uploaded_name)

            if is_avatar:
                st.caption("Final avatar size: 50×50px")
            else:
                if st.session_state.get("dataset") == "Miscrits":
                    st.markdown("#### 📏 Size")
                    col_slider, col_checkbox = st.columns([4, 2])
                    with col_slider:
                        new_scale = st.slider(
                            "Size multiplier",
                            min_value=0.5,
                            max_value=2.0,
                            value=scale_factor,
                            step=0.1,
                            help="1.0 = original height. 2.0 = double height.",
                        )
                    with col_checkbox:
                        new_keep = st.checkbox(
                            "Keep landscape shape",
                            value=keep_aspect,
                            help="If checked, we only match the height and let the width follow the image's aspect ratio.",
                        )

                    if new_scale != scale_factor or new_keep != keep_aspect:
                        st.session_state["scale_factor"] = new_scale
                        st.session_state["keep_aspect"] = new_keep
                        st.rerun()
                else:
                    # Reserve space so layout does NOT move
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)



            # Encode automatically whenever resized image changes
            resized_path_str = st.session_state.get("resized_path")
            if resized_path_str is not None and Path(resized_path_str).exists():
                resized_path = Path(resized_path_str)
                patched_bytes = st.session_state.get("patched_bytes")

                needs_reencode = st.session_state.get("needs_reencode", False)
                if is_avatar:
                    # For avatars, re-encode whenever the uploaded image changes
                    current_hash = hashlib.sha256(uploaded_bytes).hexdigest()
                    prev_hash = st.session_state.get("upload_hash")
                    if prev_hash is None or current_hash != prev_hash:
                        needs_reencode = True
                        st.session_state["upload_hash"] = current_hash

                if needs_reencode or patched_bytes is None:
                    patched_path = workdir / cache_name
                    with st.spinner("Encrypting for the game..."):
                        cmd = [
                            str(GODOT_BIN),
                            "--headless",
                            "--script",
                            str(ENCODE_SCRIPT),
                            "--",
                            str(resized_path),
                            str(patched_path),
                        ]
                        res = subprocess.run(cmd, capture_output=True, text=True)

                    if res.returncode != 0 or not patched_path.exists():
                        st.error("Encoding failed. Please try again.")
                        st.session_state["patched_bytes"] = None
                    else:
                        with open(patched_path, "rb") as f:
                            patched_bytes = f.read()
                        st.session_state["patched_bytes"] = patched_bytes
                        st.session_state["needs_reencode"] = False

            patched_bytes = st.session_state.get("patched_bytes")
            if patched_bytes:
                col_dl, col_restart = st.columns([2, 1])
                with col_dl:
                    st.download_button(
                        label="⬇️ Download encrypted sprite" if not is_avatar else "⬇️ Download encrypted avatar",
                        data=patched_bytes,
                        file_name=cache_name,
                        mime="application/octet-stream",
                        type="primary",
                        help="Save this file, then drop it into your sprites folder.",
                    )
                with col_restart:
                    if st.button("🔄 Start over (same Miscrit)"):
                        # Delete only temp files for this edit, keep selection
                        workdir = Path(st.session_state["workdir"])
                        for pattern in ("*.patched", "*.resized.png", "*.replacement.png"):
                            for f in workdir.glob(pattern):
                                try:
                                    f.unlink()
                                except FileNotFoundError:
                                    pass
                        st.session_state["patched_path"] = None
                        st.session_state["resized_path"] = None
                        st.session_state["uploaded_image_bytes"] = None
                        st.session_state["uploaded_image_name"] = None
                        st.session_state["patched_bytes"] = None
                        st.session_state["needs_reencode"] = False
                        st.session_state["scale_factor"] = 1.0
                        st.session_state["keep_aspect"] = True
                        st.session_state["prev_scale_factor"] = None
                        st.session_state["prev_keep_aspect"] = None
                        st.session_state["upload_hash"] = None
                        st.rerun()


    st.divider()
    if st.button("⬅️ Back to Miscrits"):
        # Clear workdir/cache like the original app's Back behaviour
        reset_workdir()
        st.session_state["selected_miscrit"] = None
        st.session_state["patched_path"] = None
        st.session_state["resized_path"] = None
        st.session_state["uploaded_image_bytes"] = None
        st.session_state["uploaded_image_name"] = None
        st.session_state["patched_bytes"] = None
        st.session_state["needs_reencode"] = False
        st.session_state["scale_factor"] = 1.0
        st.session_state["keep_aspect"] = True
        st.session_state["prev_scale_factor"] = None
        st.session_state["prev_keep_aspect"] = None
        st.session_state["upload_hash"] = None
        st.session_state["step"] = 1
        st.rerun()
# =====================================================================
# FOOTER
# =====================================================================

st.info(
    "These replacements work per cache file. If you clear your sprites folder, "
    "you'll need to place the patched file back in again."
)