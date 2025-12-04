import os
import subprocess
import tempfile
from pathlib import Path
import streamlit as st
from PIL import Image

# =====================================================================
# Paths & Config
# =====================================================================

ROOT = Path(__file__).parent.resolve()
# Adjust these paths if your folder structure is different
GODOT_BIN = ROOT / "bin" / "Godot_v4.1-stable_linux.x86_64"
DECODE_SCRIPT = ROOT / "gd_scripts" / "crits_single_decode.gd"
ENCODE_SCRIPT = ROOT / "gd_scripts" / "crits_single_encode.gd"

st.set_page_config(
    page_title="Miscrits Sprite Replacer",
    layout="wide",
    page_icon="🎮",
    initial_sidebar_state="expanded"
)

# =====================================================================
# Styling & Helpers
# =====================================================================

def local_css():
    st.markdown("""
    <style>
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
        }
        .stProgress > div > div > div > div {
            background-color: #ff4b4b;
        }
        /* Fix for image captions alignment */
        div[data-testid="caption"] {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

def short_name(name: str, max_len: int = 12) -> str:
    if len(name) <= max_len:
        return name
    return name[:max_len] + "..."

def render_progress_bar(current_step: int):
    """
    Updated progress bar that maintains consistent height 
    to prevent UI jumping/shifting.
    """
    steps = {
        1: "Upload",
        2: "Select",
        3: "Replace",
        4: "Download"
    }
    
    cols = st.columns(len(steps))
    for i, (step_num, label) in enumerate(steps.items()):
        with cols[i]:
            # REMOVED the '####' header which caused the vertical shift
            if step_num == current_step:
                st.markdown(f":blue[**🔵 {label}**]") 
                st.progress(100)
            elif step_num < current_step:
                st.markdown(f"**✅ {label}**")
                st.progress(100)
            else:
                st.markdown(f":grey[{label}]")
                st.progress(0)
    st.divider()

# =====================================================================
# State Management
# =====================================================================

if "workdir" not in st.session_state:
    st.session_state["workdir"] = tempfile.mkdtemp(prefix="miscrits_sprites_")
    st.session_state["step"] = 1
    st.session_state["decoded_sprites_meta"] = [] 
    st.session_state["selected_idx"] = None
    st.session_state["resized_path"] = None

workdir = Path(st.session_state["workdir"])

# Reconstruct objects
decoded_sprites = []
for slot_idx, full_name, enc_path_str, decoded_png_str in st.session_state["decoded_sprites_meta"]:
    enc = Path(enc_path_str)
    dec = Path(decoded_png_str)
    if dec.exists():
        decoded_sprites.append((slot_idx, full_name, enc, dec))

# =====================================================================
# UI: Sidebar
# =====================================================================

with st.sidebar:
    st.title("🎮 Sprite Replacer")
    st.info(
        "**Quick Guide:**\n"
        "1. Clear `image_cache/sprites`.\n"
        "2. Put crits in party & close game.\n"
        "3. Upload encrypted files.\n"
        "4. Swap art & download."
    )
    st.markdown("## 🎥 Tutorial Video")
    st.video("assets/spriteguide-real-2.mp4")
    
    if st.button("🔄 Reset All", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.markdown("## 🧾 How it works")
    st.markdown(
        """
1. **Prep your sprites folder on your PC:**
   - Go to your Miscrits sprites folder (example below).
   - Delete everything inside it.
   - Open the game and put the crits you want to change into your **party** (max 4).
   - Close the game. That `sprites` folder should now contain only 1 to 4 encrypted files.

2. **Upload those encrypted files** in **Step 1**.

3. The app will:
   - **Decrypt** and preview each sprite.
   - Let you **upload replacement art** for any sprite.
   - **Auto-resize** to the original dimensions.
   - **Re-encrypt** into a new file you can drop back into the game.

4. Replace the files in `image_cache\\sprites` and start the game 🎉
"""
    )

    st.markdown("### 📁 Example sprites folder path (Windows)")
    st.markdown(
        """
Your path will look something like:

```text
C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\Godot\\app_userdata\\Miscrits\\image_cache\\sprites
````

Replace `YOUR_USERNAME` with your own Windows username
(e.g. `appy` in `C:\\Users\\appy\\...`).
"""
)
# =====================================================================
# UI: Main Content
# =====================================================================

local_css()
st.title("Miscrits Sprite Tool")
st.caption("Refer to the panel on the left for instructions first.")
render_progress_bar(st.session_state["step"])

# --- CHECK BINARY ---
if not GODOT_BIN.exists() or not os.access(GODOT_BIN, os.X_OK):
    st.error(f"❌ Godot binary missing or not executable at: `{GODOT_BIN}`")
    st.stop()

# =====================================================================
# STEP 1: UPLOAD & DECODE
# =====================================================================
if st.session_state["step"] == 1:
    st.header("Step 1: Upload Encrypted Files")
    
    uploaded_files = st.file_uploader(
        "Drop your encrypted sprite files here",
        accept_multiple_files=True,
        key="uploader"
    )

    if uploaded_files:
        if st.button("🚀 Decrypt Files", type="primary"):
            decode_errors = []
            decoded_temp = []
            
            progress_bar = st.progress(0)
            
            for i, enc_file in enumerate(uploaded_files):
                enc_path = workdir / enc_file.name
                with open(enc_path, "wb") as f:
                    f.write(enc_file.getbuffer())

                decoded_png = workdir / f"{enc_file.name}.decoded.png"
                cmd = [str(GODOT_BIN), "--headless", "--script", str(DECODE_SCRIPT), "--", str(enc_path), str(decoded_png)]
                res = subprocess.run(cmd, capture_output=True, text=True)

                if res.returncode == 0 and decoded_png.exists():
                    slot_idx = len(decoded_temp)
                    decoded_temp.append((slot_idx, enc_file.name, str(enc_path), str(decoded_png)))
                else:
                    decode_errors.append(enc_file.name)
                
                progress_bar.progress((i + 1) / len(uploaded_files))

            if decoded_temp:
                st.session_state["decoded_sprites_meta"] = decoded_temp
                st.session_state["step"] = 2
                st.toast(f"✅ Successfully decoded {len(decoded_temp)} sprites!", icon="🎉")
                st.rerun()
            elif decode_errors:
                st.error("Could not decode files. Are they valid Miscrit sprite files?")

# =====================================================================
# STEP 2: VISUAL SELECTION
# =====================================================================
elif st.session_state["step"] == 2:
    st.header("Step 2: Select Sprite to Edit")
    st.caption("Here are the sprites currently in your party. Choose one to replace.")

    # 4-Column Grid
    cols = st.columns(4)
    for i, (slot_idx, full_name, _, png_path) in enumerate(decoded_sprites):
        col = cols[i % 4]
        with col:
            with st.container(border=True):
                st.image(str(png_path), width='stretch')
                st.markdown(f"**{short_name(full_name)}**")
                if st.button(f"Edit", key=f"sel_{i}", type="primary", width='stretch'):
                    st.session_state["selected_idx"] = i
                    st.session_state["step"] = 3
                    st.rerun()

    if st.button("⬅️ Back to Upload"):
        import shutil

        # Delete the whole working directory (all encrypted + decoded files)
        workdir = Path(st.session_state["workdir"])
        shutil.rmtree(workdir, ignore_errors=True)

        # Create a fresh empty workdir
        new_dir = tempfile.mkdtemp(prefix="miscrits_sprites_")
        st.session_state["workdir"] = new_dir

        # Reset all sprite-related state
        st.session_state["decoded_sprites_meta"] = []
        st.session_state["selected_idx"] = None
        st.session_state["resized_path"] = None

        # Go back to upload step
        st.session_state["step"] = 1
        st.rerun()

# =====================================================================
# STEP 3: REPLACE ART
# =====================================================================
elif st.session_state["step"] == 3:
    idx = st.session_state["selected_idx"]
    _, full_name, _, original_png = decoded_sprites[idx]
    
    # Load original dims
    orig_img_obj = Image.open(original_png)
    orig_w, orig_h = orig_img_obj.size

    st.header(f"Step 3: Edit `{short_name(full_name)}`")
    
    # 1. Upload Section First (Keeps UI stable)
    new_file = st.file_uploader("Upload Replacement Art (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    st.divider()

    # 2. Comparison Grid
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Original")
        with st.container(border=True):
            st.image(str(original_png), width='stretch')
            st.caption(f"Size: {orig_w}x{orig_h}px")

    with col_right:
            st.subheader("Replacement")
            with st.container(border=True):
                if new_file:
                    # Process immediate
                    save_path = workdir / f"{full_name}.replacement.png"
                    with open(save_path, "wb") as f:
                        f.write(new_file.getbuffer())
                    
                    # --- NEW RESIZE LOGIC START ---
                    st.markdown("#### 📏 Size Controls")
                    scale_factor = st.slider(
                        "Size Multiplier", 
                        min_value=0.5, 
                        max_value=2.0, 
                        value=1.0, 
                        step=0.1,
                        help="1.0 = Original height. 2.0 = Double size."
                    )
                    keep_aspect = st.checkbox("Keep Landscape Shape?", value=True, help="If checked, we only match the height and let the width be whatever it needs to be.")

                    img = Image.open(save_path).convert("RGBA")
                    
                    # Calculate new dimensions
                    if orig_w == 50 and orig_h == 50:
                        # Force 50x50 if decrypted/original sprite was 50x50
                        target_w, target_h = 50, 50
                    else:
                        if keep_aspect:
                            # Logic: Match the Original Height * Scale, and calculate Width automatically
                            aspect_ratio = img.width / img.height
                            target_h = int(orig_h * scale_factor)
                            target_w = int(target_h * aspect_ratio)
                        else:
                            # Logic: Stretch both dimensions based on Original * Scale
                            target_w = int(orig_w * scale_factor)
                            target_h = int(orig_h * scale_factor)

                    img_resized = img.resize((target_w, target_h), Image.LANCZOS)
                    # --- NEW RESIZE LOGIC END ---

                    resized_save_path = workdir / f"{full_name}.resized.png"
                    img_resized.save(resized_save_path)
                    st.session_state["resized_path"] = str(resized_save_path)
                    
                    st.image(img_resized, width='stretch')
                    st.caption(f"Final Size: {target_w}x{target_h}px (Original: {orig_w}x{orig_h})")
                else:
                    st.info("Waiting for upload...")
                    # Placeholder to keep grid aligned
                    st.image("https://placehold.co/200x200?text=Preview", width='stretch')
    st.divider()

    # Action Buttons
    if new_file:
        if st.button("⚡ Encode & Finish", type="primary"):
            st.session_state["step"] = 4
            st.rerun()
    
    if st.button("⬅️ Choose different sprite"):
        st.session_state["step"] = 2
        st.rerun()

# =====================================================================
# STEP 4: DOWNLOAD
# =====================================================================
elif st.session_state["step"] == 4:
    idx = st.session_state["selected_idx"]
    _, full_name, _, _ = decoded_sprites[idx]
    resized_path = st.session_state.get("resized_path")

    st.header("Step 4: Download Patched File")
    
    patched_path = workdir / f"{full_name}.patched"
    
    # Perform Encoding
    if not patched_path.exists():
        with st.spinner("Encrypting for Godot engine..."):
            cmd = [str(GODOT_BIN), "--headless", "--script", str(ENCODE_SCRIPT), "--", str(resized_path), str(patched_path)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode != 0:
                st.error("Encoding failed!")
                st.code(res.stderr)
                st.stop()

    
    with open(patched_path, "rb") as f:
        file_data = f.read()
        
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success("✅ **Sprite Patched Successfully! Place this file back into your sprites folder.**")
        st.download_button(
            label="⬇️ Download Encrypted File",
            data=file_data,
            file_name=full_name,
            mime="application/octet-stream",
            type="primary",
            help="Place this file back into your sprites folder"
        )
    
    st.divider()
    if st.button("🔄 Start Over (Edit another sprite)"):
        # --- DELETE ONLY RE-ENCRYPTED / TEMP OUTPUT FILES ---
        workdir = Path(st.session_state["workdir"])

        # Remove any patched (re-encrypted) files so we don't accidentally reuse them
        for f in workdir.glob("*.patched"):
            try:
                f.unlink()
            except FileNotFoundError:
                pass

        # Optional but tidy: remove per-edit temp images
        for f in workdir.glob("*.replacement.png"):
            try:
                f.unlink()
            except FileNotFoundError:
                pass

        for f in workdir.glob("*.resized.png"):
            try:
                f.unlink()
            except FileNotFoundError:
                pass

        # Reset per-edit state, but KEEP decoded_sprites_meta
        st.session_state["resized_path"] = None
        st.session_state["selected_idx"] = None

        # Jump back to sprite-selection step, using the same decoded sprites
        st.session_state["step"] = 2
        st.rerun()



# --- Final info ------------------------------------------------------------
st.info(
    "Reminder: these replacements only work for crits currently in your party "
    "and will reset if you clear your sprites folder again."
)
