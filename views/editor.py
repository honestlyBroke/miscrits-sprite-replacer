"""
Sprite/Avatar editor view (Step 2)
"""
import hashlib
import streamlit as st
from io import BytesIO
from PIL import Image
from pathlib import Path
from data_loader import load_miscrits_from_api, get_all_stages_for_miscrit
from image_utils import (
    sprite_cdn_url, avatar_cdn_url, sprite_cache_filename,
    load_sprite_on_canvas, place_on_canvas, get_original_sprite_size,
    show_pil_via_file
)
from ui_components import display_name, render_page_header
from encoder import encode_with_progress
from session_manager import get_workdir, go_back_to_selection, clear_upload_state
from config import AVATAR_SIZE


def render_editor_view():
    """Render the sprite/avatar editing interface"""
    m = st.session_state.get("selected_miscrit")
    if not m:
        st.warning("No Miscrit selected. Please go back and pick one.")
        if st.button("⬅️ Back to Selection"):
            go_back_to_selection()
            st.rerun()
        st.stop()
    
    dataset = st.session_state.get("dataset", "Miscrits")
    
    # Header
    selected_stage_data = get_selected_stage_data(m, dataset)

    # For Miscrits, show evolution stage selector
    if dataset == "Miscrits":
        render_stage_selector(m)
        # Refresh data after rendering selector (in case user clicked something)
        selected_stage_data = get_selected_stage_data(m, dataset)
    
    # --- Check for Selection ---
    if not selected_stage_data:
        # UPDATED: Friendly instruction instead of Error
        st.warning("👆 Choose an evolution to begin")
        return

    # --- Edit Mode Toggle (Sprite vs Avatar) ---
    st.markdown('<div class="section-subhead">1. Choose Target</div>', unsafe_allow_html=True)
    
    current_mode = st.session_state.get("edit_mode", "Sprite")
    mode_options = ["Sprite", "Avatar"]
    
    new_mode = st.radio(
        "Edit mode",
        mode_options,
        horizontal=True,
        label_visibility="collapsed",
        index=0 if current_mode == "Sprite" else 1,
        key="edit_mode_radio"
    )

    if new_mode != current_mode:
        st.session_state["edit_mode"] = new_mode
        clear_upload_state()
        st.rerun()
    
    is_avatar = (new_mode == "Avatar")
    
    if is_avatar:
        st.info("ℹ️ replacing **Avatar** (Profile Picture). Auto-resized to 50×50px.")
    else:
        st.info("ℹ️ replacing **Sprite** (In-Game Model).")
    
    st.divider()

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-subhead">2. Current Original</div>', unsafe_allow_html=True)
        render_current_preview(selected_stage_data, is_avatar)
    
    with col_right:
        st.markdown('<div class="section-subhead">3. Upload Replacement</div>', unsafe_allow_html=True)
        render_upload_section(selected_stage_data, dataset, is_avatar)
    
    st.divider()
    if st.button("⬅️ Back to Selection", use_container_width=True):
        go_back_to_selection()
        st.rerun()


def render_stage_selector(m):
    """Render evolution stage selector for Miscrits"""
    all_miscrits = load_miscrits_from_api()
    stages = get_all_stages_for_miscrit(all_miscrits, m["id"])
    
    # If only 1 stage exists, auto-select it to save time
    if len(stages) == 1:
        st.session_state["selected_stage"] = 1
        return
    
    st.markdown("### Evolution Stage")
    
    cols = st.columns(len(stages))
    for i, stage in enumerate(stages):
        with cols[i]:
            is_selected = st.session_state.get("selected_stage") == stage["evo_stage"]
            
            # Visual styling for selection
            with st.container(border=True):
                if is_selected:
                    st.caption(f"✅ Stage {stage['evo_stage']}")
                else:
                    st.caption(f"Stage {stage['evo_stage']}")

                sprite_url = sprite_cdn_url(stage["evo_name"])
                sprite_img = load_sprite_on_canvas(sprite_url, canvas_size=(128, 128))
                show_pil_via_file(get_workdir(), sprite_img, f"stage_{stage['evo_stage']}.png", width="stretch")
                
                btn_type = "primary" if is_selected else "secondary"
                btn_label = "Selected" if is_selected else "Select"
                
                if st.button(btn_label, key=f"stage_{stage['evo_stage']}", type=btn_type, use_container_width=True):
                    if not is_selected:
                        st.session_state["selected_stage"] = stage["evo_stage"]
                        clear_upload_state()
                        st.rerun()
    
    st.divider()
    
    # UPDATED: Removed the logic that forced "selected_stage = 1" here.
    # This allows the "No Selection" state to exist.


def get_selected_stage_data(m, dataset):
    """Get data for the currently selected stage"""
    if dataset == "Bosses":
        return {
            "name": m.get("first_name", "Unknown"),
            "id": m["id"],
            "stage": 1
        }
    
    # For Miscrits
    # UPDATED: Defaults to None instead of 1 so we know when nothing is picked
    selected_stage = st.session_state.get("selected_stage")
    
    if selected_stage is None:
        return None

    all_miscrits = load_miscrits_from_api()
    stages = get_all_stages_for_miscrit(all_miscrits, m["id"])
    
    for stage in stages:
        if stage["evo_stage"] == selected_stage:
            return {
                "name": stage["evo_name"],
                "id": m["id"],
                "stage": selected_stage,
                "total_stages": len(stages)
            }
    return None


def render_current_preview(stage_data, is_avatar):
    """Render the current sprite or avatar preview"""
    resource_label = "avatar" if is_avatar else "sprite"
    name = stage_data["name"]
    
    if is_avatar:
        url = avatar_cdn_url(name)
        img = load_sprite_on_canvas(url, canvas_size=(128, 128))
        caption = "Original: 50×50px"
    else:
        url = sprite_cdn_url(name)
        img = load_sprite_on_canvas(url, canvas_size=(256, 256))
        orig_w, orig_h = get_original_sprite_size(url)
        caption = f"Original: {orig_w}×{orig_h}px"

    show_pil_via_file(get_workdir(), img, f"current_{resource_label}.png", width="stretch")
    st.caption(caption)
    
    cache_name = sprite_cache_filename(url)
    with st.expander("Filename Details"):
        st.code(cache_name, language="text")


def render_upload_section(stage_data, dataset, is_avatar):
    """Render the upload and editing section"""
    uploaded_bytes = st.session_state.get("uploaded_image_bytes")
    
    if uploaded_bytes is None:
        new_file = st.file_uploader(
            "Upload Image (PNG/JPG)",
            type=["png", "jpg", "jpeg"],
        )
        if new_file:
            st.session_state["uploaded_image_bytes"] = new_file.read()
            st.session_state["uploaded_image_name"] = new_file.name
            st.session_state["needs_reencode"] = True
            st.rerun()
        return
    
    # Process uploaded image
    process_uploaded_image(stage_data, dataset, uploaded_bytes, is_avatar)


def process_uploaded_image(stage_data, dataset, uploaded_bytes, is_avatar):
    """Process and display uploaded image with controls"""
    img = Image.open(BytesIO(uploaded_bytes)).convert("RGBA")
    workdir = get_workdir()
    
    if is_avatar:
        target_w, target_h = 50, 50
        img_resized = img.resize((target_w, target_h), Image.LANCZOS)
        preview_canvas = place_on_canvas(img_resized, canvas_size=(128, 128))
        show_pil_via_file(workdir, preview_canvas, "preview_avatar.png", width="stretch")
        st.caption("Auto-resized to 50×50px")
        
    else:
        sprite_url = sprite_cdn_url(stage_data["name"])
        orig_w, orig_h = get_original_sprite_size(sprite_url)
        
        scale_factor = st.session_state.get("scale_factor", 1.0)
        keep_aspect = st.session_state.get("keep_aspect", True)
        
        if keep_aspect:
            aspect_ratio = img.width / img.height
            target_h = int(orig_h * scale_factor)
            target_w = int(target_h * aspect_ratio)
        else:
            target_w = int(orig_w * scale_factor)
            target_h = int(orig_h * scale_factor)
        
        img_resized = img.resize((target_w, target_h), Image.LANCZOS)
        preview_canvas = place_on_canvas(img_resized, canvas_size=(256, 256))
        show_pil_via_file(
            workdir, preview_canvas, "preview_sprite.png",
            caption=f"New Size: {target_w}×{target_h}px",
            width="stretch"
        )
        
        render_size_controls(scale_factor, keep_aspect)
    
    filename_part = "avatar" if is_avatar else "sprite"
    resized_path = workdir / f"{stage_data['name'].replace(' ', '_')}_{filename_part}.resized.png"
    img_resized.save(resized_path)
    
    st.markdown("---")
    render_download_section(resized_path, stage_data, uploaded_bytes, is_avatar)


def render_size_controls(scale_factor, keep_aspect):
    col_slider, col_check = st.columns([3, 1])
    with col_slider:
        new_scale = st.slider("Scale", 0.5, 2.0, value=scale_factor, step=0.1)
    with col_check:
        st.write("")
        st.write("") 
        new_keep = st.checkbox("Lock Aspect", value=keep_aspect)
    
    if new_scale != scale_factor or new_keep != keep_aspect:
        st.session_state["scale_factor"] = new_scale
        st.session_state["keep_aspect"] = new_keep
        st.session_state["needs_reencode"] = True
        st.rerun()


def render_download_section(resized_path, stage_data, uploaded_bytes, is_avatar):
    workdir = get_workdir()
    
    if is_avatar:
        target_url = avatar_cdn_url(stage_data["name"])
        label_text = "⬇️ Encrypted Avatar"
    else:
        target_url = sprite_cdn_url(stage_data["name"])
        label_text = "⬇️ Encrypted Sprite"
        
    cache_name = sprite_cache_filename(target_url)
    
    current_hash = hashlib.sha256(uploaded_bytes).hexdigest()
    needs_reencode = (
        st.session_state.get("needs_reencode", False) or
        st.session_state.get("upload_hash") != current_hash or
        st.session_state.get("sprite_encoded") is None
    )
    
    if needs_reencode:
        output_path = workdir / cache_name
        encoded_bytes = encode_with_progress(resized_path, output_path, "Encrypting...")
        
        if encoded_bytes:
            st.session_state["sprite_encoded"] = encoded_bytes
            st.session_state["upload_hash"] = current_hash
            st.session_state["needs_reencode"] = False
        else:
            return
    
    encoded_bytes = st.session_state.get("sprite_encoded")
    if encoded_bytes:
        st.download_button(
            label=label_text,
            data=encoded_bytes,
            file_name=cache_name,
            mime="application/octet-stream",
            type="primary",
            use_container_width=True
        )
        
        if st.button("🔄 Reset", use_container_width=True):
            clear_upload_state()
            st.rerun()