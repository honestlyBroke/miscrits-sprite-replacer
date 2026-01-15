"""
Session state management utilities
(added temp_miscrits and relevant keys for Move Editor)
"""
import tempfile
import shutil
from pathlib import Path
import streamlit as st


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "step": 1,
        "selected_miscrit": None,
        "selected_stage": None,
        "edit_mode": "Sprite",  # Added: Track Sprite vs Avatar mode
        "workdir": tempfile.mkdtemp(prefix="miscrits_sprites_"),
        "page": 0,
        "uploaded_image_bytes": None,
        "uploaded_image_name": None,
        "scale_factor": 10.0,
        "keep_aspect": True,
        "sprite_encoded": None,
        "needs_reencode": False,
        "prev_scale_factor": None,
        "prev_keep_aspect": None,
        "upload_hash": None,
        "dataset": "Miscrits",

        # Move Editor additions
        # temp_miscrits contains the working copy of the entire miscrits JSON (as Python list/dict)
        # when user chooses to edit moves we deep copy the loaded JSON here and mutate it.
        "temp_miscrits": None,
        # original source info (api/local/upload)
        "temp_miscrits_source": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_workdir():
    """Delete current workdir and create a fresh one"""
    old_dir = Path(st.session_state.get("workdir", tempfile.gettempdir()))
    shutil.rmtree(old_dir, ignore_errors=True)
    new_dir = tempfile.mkdtemp(prefix="miscrits_sprites_")
    st.session_state["workdir"] = new_dir
    return Path(new_dir)


def clear_upload_state():
    """Clear all upload-related state"""
    keys_to_clear = [
        "uploaded_image_bytes",
        "uploaded_image_name",
        "sprite_encoded",
        "needs_reencode",
        "scale_factor",
        "keep_aspect",
        "prev_scale_factor",
        "prev_keep_aspect",
        "upload_hash",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            if key in ["scale_factor"]:
                st.session_state[key] = 1.0
            elif key in ["keep_aspect"]:
                st.session_state[key] = True
            else:
                st.session_state[key] = None


def go_back_to_selection():
    """Reset state to go back to miscrit selection"""
    reset_workdir()
    st.session_state["selected_miscrit"] = None
    st.session_state["selected_stage"] = None
    st.session_state["step"] = 1
    st.session_state["edit_mode"] = "Sprite"
    # Clear move editor temp data when returning
    st.session_state["temp_miscrits"] = None
    st.session_state["temp_miscrits_source"] = None
    clear_upload_state()


def get_workdir() -> Path:
    """Get current working directory"""
    return Path(st.session_state.get("workdir", tempfile.gettempdir()))
