"""
Miscrits Sprite Replacer - Main Application
"""
import os
import logging
import streamlit as st
import platform  # Added for OS check
import stat      # Added for permission fixing

# Silence noisy media handler logs
logging.getLogger('streamlit.web.server.media_file_handler').setLevel(logging.CRITICAL)
logging.getLogger('streamlit.runtime.memory_media_file_storage').setLevel(logging.CRITICAL)

# Import configuration
from config import GODOT_BIN, ENCODE_SCRIPT, FAVICON_PATH

# Import utilities
from session_manager import initialize_session_state
from ui_components import apply_custom_css, render_sidebar

# Import views
from views.selection import render_selection_view
from views.editor import render_editor_view

# =====================================================================
# Page Configuration
# =====================================================================

st.set_page_config(
    page_title="Miscrits Sprite Tool",
    layout="wide",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🎮",
    initial_sidebar_state="expanded",
)

# =====================================================================
# Initialize
# =====================================================================

# Apply styling
apply_custom_css()

# Initialize session state
initialize_session_state()

# Render sidebar
render_sidebar()

# =====================================================================
# Main App Header
# =====================================================================

st.title("Miscrits Sprite Tool")

# =====================================================================
# Linux Permission Fix (Critical for Streamlit Cloud)
# =====================================================================
# This block ensures the Linux binary has +x permissions
if platform.system() != "Windows" and GODOT_BIN.exists():
    try:
        # Get current file permissions
        st_mode = os.stat(GODOT_BIN).st_mode
        # If not executable by user, add execution rights
        if not (st_mode & stat.S_IEXEC):
            st.toast(f"🔧 Setting executable permissions for: {GODOT_BIN.name}")
            os.chmod(GODOT_BIN, st_mode | stat.S_IEXEC)
    except Exception as e:
        # We warn but don't stop yet; let the verification block handle failure
        st.warning(f"Could not set executable permissions: {e}")

# =====================================================================
# Verify Required Files
# =====================================================================

if not GODOT_BIN.exists() or not os.access(GODOT_BIN, os.X_OK):
    st.error(f"❌ Godot binary missing or not executable at: `{GODOT_BIN}`")
    st.info("If on Streamlit Cloud, verify you uploaded the Linux binary to `bin/` and that `config.py` is selecting it.")
    st.stop()

if not ENCODE_SCRIPT.exists():
    st.error(f"❌ Encode script missing at: `{ENCODE_SCRIPT}`")
    st.stop()

# =====================================================================
# Route to Appropriate View
# =====================================================================

current_step = st.session_state.get("step", 1)

if current_step == 1:
    render_selection_view()
elif current_step == 2:
    render_editor_view()
else:
    st.error("Unknown step in session state. Resetting.")
    st.session_state["step"] = 1
    st.rerun()

# =====================================================================
# Footer
# =====================================================================

if current_step == 2:
    st.info(
        "💡 These replacements work per cache file. If you clear your sprites folder, "
        "you'll need to place the patched file back in again."
    )