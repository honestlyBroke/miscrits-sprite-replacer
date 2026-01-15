"""
Sprite encoding utilities using Godot
"""
import subprocess
import streamlit as st
from pathlib import Path
from config import GODOT_BIN, ENCODE_SCRIPT


def encode_sprite(input_path: Path, output_path: Path) -> bool:
    """
    Encode a sprite using Godot's encryption.
    Returns True on success, False on failure.
    """
    try:
        cmd = [
            str(GODOT_BIN),
            "--headless",
            "--script",
            str(ENCODE_SCRIPT),
            "--",
            str(input_path),
            str(output_path),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0 or not output_path.exists():
            st.error(f"Encoding failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        st.error(f"Encoding error: {e}")
        return False


def encode_with_progress(input_path: Path, output_path: Path, progress_text: str = "Encrypting...") -> bytes:
    """
    Encode a sprite with a progress indicator.
    Returns the encoded bytes, or None on failure.
    """
    with st.spinner(progress_text):
        success = encode_sprite(input_path, output_path)
        
        if not success:
            return None
        
        try:
            with open(output_path, "rb") as f:
                return f.read()
        except Exception as e:
            st.error(f"Failed to read encoded file: {e}")
            return None
