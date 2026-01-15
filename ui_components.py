"""
Reusable UI components and styling
"""
import streamlit as st
from config import ROOT

# =====================================================================
# THEME: Gold/Brown/Black (Structure: Modern/Neon)
# =====================================================================
MISCRITS_CSS = """
<style>
/* ==== Base reset ==== */
*,:before,:after{box-sizing:border-box;border-width:0;border-style:solid;border-color:#e5e7eb}
html,body{margin:0;line-height:1.5;font-family:BorisBlackBloxx,sans-serif;-webkit-text-size-adjust:100%}
img,svg,video,canvas,audio,iframe,embed,object{display:block;vertical-align:middle}

/* ==== STRICT COLOR PALETTE VARIABLES ==== */
:root{
  /* The Hex codes you requested */
  --background: #050507;       /* Almost-black background */
  --foreground: #FFE7AA;       /* Warm yellow-ish text */
  --card-bg: #1D1510;          /* Dark brown-ish card */
  --primary: #FFC842;          /* Gold accent */
  --primary-dim: #b8860b;      /* Darker Gold for borders */
  
  --radius: .5rem;
}

body {
  background-color: var(--background);
  color: var(--foreground);
  font-family: BorisBlackBloxx, sans-serif;
}

/* ==== Scrollbars ==== */
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background-color: var(--background)}
::-webkit-scrollbar-thumb{border-radius:9999px;background-color: var(--primary)}
::-webkit-scrollbar-thumb:hover{background-color: var(--primary-dim)}

/* ==== Streamlit Overrides ==== */
.stApp { background-color: var(--background); }
div[data-testid="stSidebar"] { background-color: var(--background); border-right: 1px solid #333; }
div[data-testid="stExpander"] { border: none; box-shadow: none; background: transparent; }
.main .block-container { padding-top: 2rem; max-width: 1400px; }

/* ==== Themed Utility Classes (Refitted for Gold/Brown) ==== */

/* 1. Glass Card - Now Dark Brown with Gold Tint */
.glass-card {
  border-radius: var(--radius);
  border: 1px solid rgba(255, 200, 66, 0.3); /* Gold border with opacity */
  background-color: rgba(29, 21, 16, 0.9);   /* Dark Brown with slight opacity */
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  margin-bottom: 1rem;
}

/* 2. Neon Border - Glowing Gold */
.neon-border {
  border-radius: var(--radius);
  border: 2px solid var(--primary);
  box-shadow: 0 0 10px rgba(255, 200, 66, 0.6);
}

/* 3. Headings */
.heading-1 {
  font-family: BorisBlackBloxx, sans-serif;
  font-size: 2.5rem;
  line-height: 1.1;
  color: #fff;
  /* Gold Glow Shadow */
  filter: drop-shadow(0 0 8px rgba(255, 200, 66, 0.6));
  margin-bottom: 1rem;
}

.heading-2 {
  font-family: sans-serif; /* Fallback or specific font */
  font-weight: bold;
  font-size: 1.5rem;
  color: var(--primary);
  margin-top: 0;
}

/* 4. Modern Card Header (Pill Style) - Gold Theme Default */
.modern-card-header {
    background: linear-gradient(180deg, #ffd700 0%, #daa520 100%);
    border: 2px solid #b8860b;
    border-radius: 25px;
    padding: 8px 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    height: 55px;
    margin-bottom: 8px;
}

/* Inner elements for cards */
.modern-icon-img {
    position: absolute;
    left: 8px;
    top: 50%;
    transform: translateY(-50%);
    width: 42px;
    height: 42px;
    filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5));
    z-index: 2;
    object-fit: contain;
}

.modern-name-text {
    font-family: 'Arial Black', sans-serif;
    font-weight: 900;
    text-transform: uppercase;
    font-size: 14px;
    color: #ffffff;
    text-shadow: 2px 2px 0px #5c4202, -1px -1px 0 #5c4202, 1px -1px 0 #5c4202, -1px 1px 0 #5c4202, 1px 1px 0 #5c4202;
    z-index: 1;
    text-align: center;
    width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 45px;
}
</style>
"""

def apply_custom_css():
    st.markdown(MISCRITS_CSS, unsafe_allow_html=True)


def render_page_header(title: str, icon: str = None):
    """Render a consistent page header using the .heading-1 style"""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f"""
        <div style="margin-bottom: 20px; border-bottom: 2px solid var(--primary); padding-bottom: 10px;">
            <h1 class="heading-1">{icon_html}{title}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_name(raw: str) -> str:
    if not raw:
        return ""
    return raw.replace("_", " ").title()


def short_name(name: str, max_len: int = 14) -> str:
    if len(name) <= max_len:
        return name
    return name[:max_len - 3] + "..."


def render_sidebar():
    with st.sidebar:
        st.markdown(f"<h2 class='heading-2'>🎮 Sprite Replacer</h2>", unsafe_allow_html=True)

        # Instructions - Using Glass Card Style with Gold Text
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin-top:0; color: var(--primary); margin-bottom: 10px;">📝 Quick Guide</h4>
                <ol style="padding-left: 20px; font-size: 0.9em; color: var(--foreground); margin-bottom: 0;">
                    <li style="margin-bottom:8px;">
                        <strong style="color: var(--primary);">Select Target:</strong> Find your Miscrit or Boss.
                    </li>
                    <li style="margin-bottom:8px;">
                        <strong style="color: var(--primary);">Pick Stage:</strong> (Miscrits) Choose stage 1-4.
                    </li>
                    <li style="margin-bottom:8px;">
                        <strong style="color: var(--primary);">Mode:</strong> Sprite (Battle) or Avatar (Icon).
                    </li>
                    <li style="margin-bottom:8px;">
                        <strong style="color: var(--primary);">Upload:</strong> Drop image & Resize.
                    </li>
                    <li>
                        <strong style="color: var(--primary);">Install:</strong> Download & move to folder.
                    </li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 📂 Installation Paths")
        st.info("Copy the path below:")
        
        st.caption("**Sprites (Battle Art):**")
        st.code(r"%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\sprites", language="text")
        
        st.caption("**Avatars (Profile Icons):**")
        st.code(r"%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\miscrits", language="text")

        st.markdown('<h4 style="color:#fff; margin-top:1.5rem;">🎥 Tutorial</h4>', unsafe_allow_html=True)
        video_path = ROOT / "assets" / "spriteguide-real-2.mp4"
        if video_path.exists():
            st.video(str(video_path))
        else:
            st.warning("Tutorial video not found.")

        st.divider()
        if st.button("🔄 Reset Session", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_pagination(page: int, total_items: int, page_size: int):
    max_page = max((total_items - 1) // page_size, 0)
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, total_items)

    st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_items}")

    col_prev, col_page, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️ Prev", disabled=page == 0, use_container_width=True):
            st.session_state["page"] = max(page - 1, 0)
            st.rerun()

    with col_page:
        st.markdown(
            f"<div style='text-align:center; padding-top: 5px; font-weight:bold; color: var(--foreground);'>Page {page + 1} / {max_page + 1}</div>",
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button("Next ➡️", disabled=page >= max_page, use_container_width=True):
            st.session_state["page"] = min(page + 1, max_page)
            st.rerun()

    return start_idx, end_idx