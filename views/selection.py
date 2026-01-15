"""
Miscrit/Boss selection view (Step 1)
"""
import streamlit as st
import concurrent.futures
from data_loader import load_miscrits_from_api, load_boss_catalog
from image_utils import element_icon_url, sprite_cdn_url, load_sprite_on_canvas, show_pil_via_file
from ui_components import display_name, render_pagination, render_page_header
from session_manager import get_workdir
from config import PAGE_SIZE
from views.moves_editor import render_moves_editor

def render_selection_view():
    """Render the main selection interface"""
    st.header("Step 1: Choose Task")
    
    # 1. Main Navigation Tabs
    dataset = st.radio(
        "Mode",
        ["Miscrits", "Bosses", "Moves Editor"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["dataset"] = dataset
    
    # --- ROUTING ---
    
    # A. Move Editor Route
    if dataset == "Moves Editor":
        render_moves_editor()
        return

    # B. Sprite Replacer Route (Miscrits/Bosses)
    if dataset == "Bosses":
        catalog = load_boss_catalog()
        search_ph = "gb, global boss, mizokami, magicite..."
    else:
        catalog = load_miscrits_from_api()
        search_ph = "Flue, Flowerpiller, Afterburn..."
    
    if not catalog:
        st.error(f"Could not load {dataset.lower()} catalog")
        st.stop()
    
    # Filter Catalog for Display
    if dataset == "Miscrits":
        # Group by ID and only show first stage
        seen_ids = set()
        display_catalog = []
        for m in catalog:
            if m["id"] not in seen_ids and m["evo_stage"] == 1:
                seen_ids.add(m["id"])
                display_catalog.append(m)
    else:
        display_catalog = catalog
    
    # Search and filters
    filtered = filter_catalog(display_catalog, dataset, search_ph)
    
    if not filtered:
        st.caption("No results match your filters.")
        return
    
    # Pagination
    page = st.session_state.get("page", 0)
    start_idx, end_idx = render_pagination(page, len(filtered), PAGE_SIZE)
    page_items = filtered[start_idx:end_idx]
    
    # Render grid
    render_miscrit_grid(page_items, dataset)


def filter_catalog(catalog, dataset, placeholder):
    """Apply search and filter criteria"""
    col_search, col_rarity, col_element = st.columns([2, 1, 1])
    
    with col_search:
        search_term = st.text_input(
            f"Search {dataset}...",
            placeholder=placeholder
        )
    
    all_rarities = sorted({m.get("rarity", "Common") for m in catalog})
    all_elements = sorted({m.get("element", "None") for m in catalog})
    
    with col_rarity:
        rarity_filter = st.multiselect(
            "Rarity" if dataset == "Miscrits" else "Location",
            all_rarities,
            default=None,
        )
    
    with col_element:
        element_filter = st.multiselect("Element", all_elements, default=[])
    
    # Apply filters
    filtered = []
    for m in catalog:
        if search_term:
            s = search_term.strip().lower()
            aliases = {"gb": "global boss", "globalboss": "global boss"}
            s = aliases.get(s, s)
            
            haystack = " ".join([
                m.get("base_name", m.get("first_name", "")),
                m.get("evo_name", m.get("final_name", "")),
                m.get("rarity", ""),
            ]).lower()
            
            if s not in haystack:
                continue
        
        if rarity_filter and m.get("rarity") not in rarity_filter:
            continue
        
        if element_filter and m.get("element") not in element_filter:
            continue
        
        filtered.append(m)
    
    return filtered


def fetch_sprite_batch(items, dataset):
    """
    Fetch all sprites for the page in parallel.
    Returns a dictionary: { miscrit_id: image_object }
    """
    results = {}
    
    # Helper to fetch one
    def fetch_one(m):
        sprite_name = m.get("evo_name") if dataset == "Miscrits" else m.get("first_name")
        url = sprite_cdn_url(sprite_name)
        # load_sprite_on_canvas should ideally be cached in image_utils
        return m["id"], load_sprite_on_canvas(url, canvas_size=(256, 256))

    # Run in parallel using threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_id = {executor.submit(fetch_one, m): m["id"] for m in items}
        for future in concurrent.futures.as_completed(future_to_id):
            try:
                mid, img = future.result()
                results[mid] = img
            except Exception:
                pass
                
    return results


def render_miscrit_grid(page_items, dataset):
    """Render the grid of miscrit cards"""
    workdir = get_workdir()
    
    # 1. OPTIMIZATION: Fetch all images in parallel first
    # This prevents the "loading one by one" visual effect
    with st.spinner("Loading sprites..."):
        images_map = fetch_sprite_batch(page_items, dataset)
    
    cols = st.columns(4)
    
    for i, m in enumerate(page_items):
        col = cols[i % 4]
        with col:
            # Pass the pre-loaded image to the card
            img = images_map.get(m["id"])
            render_miscrit_card(m, dataset, workdir, preloaded_img=img)


def render_miscrit_card(m, dataset, workdir, preloaded_img=None):
    """Render a single miscrit card"""
    with st.container(border=True):
        # Header: element icon + name
        icon_url = element_icon_url(m.get("element", "None"))
        c1, c2 = st.columns([1, 3])
        
        with c1:
            st.markdown(
                f'<div class="element-icon-container"><img src="{icon_url}" alt="element"></div>',
                unsafe_allow_html=True
            )
        
        with c2:
            if dataset == "Miscrits":
                title = display_name(m.get("base_name", "Unknown"))
            else:
                title = display_name(m.get("first_name", "Unknown"))
            
            margin = "15px" if dataset == "Bosses" else "5px"
            font_size = "18px" if dataset == "Bosses" else "15px"
            
            st.markdown(
                f"<div style='margin-top: {margin}; font-weight: 700; font-size: {font_size};'>"
                f"{title}</div>",
                unsafe_allow_html=True,
            )
            
        # Sprite preview (Use preloaded image if available)
        if preloaded_img:
            sprite_img = preloaded_img
        else:
            sprite_name = m.get("evo_name") if dataset == "Miscrits" else m.get("first_name")
            sprite_url = sprite_cdn_url(sprite_name)
            sprite_img = load_sprite_on_canvas(sprite_url, canvas_size=(256, 256))
            
        show_pil_via_file(workdir, sprite_img, f"grid_{m['id']}.png", width="stretch")
        
        # Select button
        btn_label = "Select"
        if st.button(btn_label, key=f"sel_{m['id']}", type="primary", use_container_width=True):
            st.session_state["selected_miscrit"] = m
            st.session_state["step"] = 2
            st.rerun()