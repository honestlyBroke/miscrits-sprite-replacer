"""
Move Editor view - Game-Accurate Logic & UI
"""
import streamlit as st
import json
from typing import List, Dict
from datetime import datetime

from data_loader import load_miscrits_raw
from ui_components import display_name

# Base URL for icons
TYPE_ICON_BASE = "https://worldofmiscrits.com"

# Standard Elements (Imply type="Attack")
STANDARD_ELEMENTS = [
    "Physical", "Fire", "Water", "Nature", "Wind", "Earth", 
    "Lightning", "Misc", "FireWind", "FireEarth", "FireLightning", 
    "WaterWind", "WaterEarth", "WaterLightning", "NatureWind",
    "NatureEarth", "NatureLightning"
]

def init_session_state():
    """Initialize session state variables"""
    if "temp_miscrits" not in st.session_state:
        st.session_state["temp_miscrits"] = None
    if "temp_miscrits_source" not in st.session_state:
        st.session_state["temp_miscrits_source"] = "unknown"
    if "_export_json" not in st.session_state:
        st.session_state["_export_json"] = None
    if "edit_history" not in st.session_state:
        st.session_state["edit_history"] = []
    if "unsaved_changes" not in st.session_state:
        st.session_state["unsaved_changes"] = False

def log_edit(miscrit_id: int, ability_id: int, field: str, old_value: str, new_value: str):
    """Log edits for undo functionality"""
    st.session_state["edit_history"].append({
        "timestamp": datetime.now().isoformat(),
        "miscrit_id": miscrit_id,
        "ability_id": ability_id,
        "field": field,
        "old_value": old_value,
        "new_value": new_value
    })
    st.session_state["unsaved_changes"] = True

def get_game_icon_name(ability: Dict) -> str:
    """
    Replicates the logic from models/Ability.gd get_icon() exactly.
    """
    t = ability.get("type", "Attack")
    e = ability.get("element", "Physical")
    ap = ability.get("ap", 0)
    keys = ability.get("keys", [])
    true_dmg = ability.get("true_dmg", False)

    # 1. Status / Special Logic
    if t == "Dot" and e != "Misc":
        return f"{e}_poison"
    if t == "Hot":
        return "heal"
    if t == "ForceSwitch":
        return "confuse"
    if true_dmg:
        return "truedamage"

    # 2. Misc Logic (Buffs/Debuffs)
    if e == "Misc":
        if t == "Buff":
            if ap > 0 and "acc" in keys:
                return "accuracy_buff"
            elif ap < 0 and "acc" in keys:
                return "accuracy_debuff"
            elif ap > 0:
                return "buff"
            elif ap < 0:
                return "debuff"
        elif t == "Bot":
            if ap > 0:
                return "bot_buff"
            else:
                return "bot_debuff"
        elif t == "Heal":
            return "heal"

    # 3. Attack Logic
    if t == "Attack":
        return e

    # 4. Fallback
    return t

def render_moves_editor():
    init_session_state()
    
    # --- CSS ---
    st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; max-width: 1400px; }
    
    .editor-header {
        background: linear-gradient(135deg, #1e1e2f 0%, #252540 100%);
        border-bottom: 2px solid #667eea;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 12px;
        color: white;
    }
    
    .move-card-header-box {
        background: linear-gradient(180deg, #ffd700 0%, #daa520 100%);
        border: 2px solid #b8860b;
        border-radius: 25px;
        padding: 8px 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        height: 55px;
        margin-bottom: 8px;
    }

    .move-icon-img {
        position: absolute;
        left: 8px;
        top: 50%;
        transform: translateY(-50%);
        width: 42px;
        height: 42px;
        filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5));
        z-index: 2;
    }

    .move-name-text {
        font-family: 'Arial Black', sans-serif;
        font-weight: 900;
        text-transform: uppercase;
        font-size: 15px;
        color: #ffffff;
        text-shadow: 2px 2px 0px #5c4202, -1px -1px 0 #5c4202, 1px -1px 0 #5c4202, -1px 1px 0 #5c4202, 1px 1px 0 #5c4202;
        letter-spacing: 0.5px;
        z-index: 1;
        text-align: center;
        width: 100%;
        padding-left: 45px; 
        padding-right: 45px; 
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .unsaved-indicator {
        position: fixed;
        top: 70px;
        right: 20px;
        background: #ff4444;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(255,68,68,0.4);
        animation: pulse 2s infinite;
        z-index: 1000;
    }
    
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    
    .stats-editor-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 2px solid #5a67d8;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin: 20px 0;
    }
    
    .stats-editor-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102,126,234,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### 🎮 Editor Controls")
        
        if st.session_state["temp_miscrits"]:
            total_miscrits = len(st.session_state["temp_miscrits"])
            col1, col2 = st.columns(2)
            with col1: st.metric("Miscrits", total_miscrits)
            with col2:
                total_moves = sum(len(m.get("abilities", [])) for m in st.session_state["temp_miscrits"])
                st.metric("Moves", total_moves)
        
        st.divider()
        st.markdown("#### ⚡ Quick Actions")
        if st.button("💾 Auto-Save", use_container_width=True, help="Clear unsaved flag"):
            st.session_state["unsaved_changes"] = False
            st.toast("✅ Changes saved!")
        
        if st.button("🔄 Reload Data", use_container_width=True):
            st.session_state["temp_miscrits"] = None
            st.rerun()

    # --- Main Content ---
    if st.session_state["unsaved_changes"]:
        st.markdown("""<div class="unsaved-indicator">● Unsaved Changes</div>""", unsafe_allow_html=True)

    # --- Data Loading ---
    if st.session_state["temp_miscrits"] is None:
        with st.spinner("🔄 Loading Miscrits data..."):
            data = load_miscrits_raw("api")
            if data:
                st.session_state["temp_miscrits"] = data
                st.session_state["temp_miscrits_source"] = "server"
                st.success("✅ Data loaded successfully!")

    uploaded = st.file_uploader("📂 Drag and drop miscrits.json here to override", type=["json"])
    if uploaded:
        try:
            st.session_state["temp_miscrits"] = json.loads(uploaded.read().decode("utf-8"))
            st.session_state["temp_miscrits_source"] = "upload"
            st.session_state["unsaved_changes"] = False
            st.success("✅ File imported successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Invalid JSON: {e}")

    miscrits: List[Dict] = st.session_state.get("temp_miscrits")
    if not miscrits:
        st.error("❌ Could not load Miscrits data.")
        return

    # --- 1. Miscrit Selector (Searchable Dropdown) ---
    st.markdown("### 1️⃣ Select Miscrit")
    
    # Logic: Combine "ID", "First Name", and "Last Name" into one string
    # This makes the standard Streamlit dropdown searchable by ANY of those terms.
    miscrit_options = []
    id_map = {}
    miscrits_sorted = sorted(miscrits, key=lambda x: x.get("id", 0))
    
    for m in miscrits_sorted:
        m_id = m.get("id", 0)
        name_list = m.get("names", [])
        
        first_name = name_list[0] if name_list else m.get("name", "Unknown")
        # Find the "Final" evolution name (last in the list)
        final_name = name_list[-1] if len(name_list) > 1 else ""
        
        # Format: "1. Flue / Afterburn"
        if final_name:
            label = f"{m_id}. {first_name} / {final_name}"
        else:
            label = f"{m_id}. {first_name}"
            
        miscrit_options.append(label)
        id_map[label] = m
    
    # Single unified search bar (The dropdown itself)
    selected_label = st.selectbox(
        "Search by ID, First Name, or Final Name...",
        miscrit_options,
        key="miscrit_selector"
    )
    
    if not selected_label:
        return
    
    selected = id_map[selected_label]
    selected_element = selected.get("element", "Physical")

    # --- 2. Edit Moves ---
    st.markdown("### 2️⃣ Edit Moves")
    st.caption(f"Editing moves for **{selected_label}** (Element: {selected_element})")
    
    # Unified UI Types List
    other_types = {
        ability["type"]
        for m in miscrits
        for ability in m.get("abilities", [])
        if ability.get("type") != "Attack"
    }
    ALL_UI_TYPES = sorted(list(set(STANDARD_ELEMENTS))) + sorted(list(other_types))

    ability_order = list(reversed(selected.get("ability_order", [])))
    abilities_by_id = {a["id"]: a for a in selected.get("abilities", [])}
    
    # Filter
    filtered_abilities = []
    for ab_id in ability_order:
        ability = abilities_by_id.get(ab_id)
        if ability:
            filtered_abilities.append((ab_id, ability))
    
    if not filtered_abilities:
        st.info("No moves found for this Miscrit.")
        return
    
    cols = st.columns(2)
    
    for idx, (ab_id, ability) in enumerate(filtered_abilities):
        col = cols[idx % 2]
        
        with col:
            with st.container():
                # --- STATE ---
                key_name = f"name_{selected['id']}_{ab_id}"
                key_ui_type = f"ui_type_{selected['id']}_{ab_id}"

                live_name = st.session_state.get(key_name, ability.get('name', ''))
                
                db_type = ability.get("type", "Attack")
                db_element = ability.get("element", "Physical")
                current_ui_val = db_element if db_type == "Attack" else db_type
                if current_ui_val not in ALL_UI_TYPES: current_ui_val = "Physical"

                # --- ICON PREVIEW ---
                new_ui_sel = st.session_state.get(key_ui_type, current_ui_val)
                temp_ability = ability.copy()
                temp_ability["name"] = live_name
                
                if new_ui_sel in STANDARD_ELEMENTS:
                    temp_ability["type"] = "Attack"
                    temp_ability["element"] = new_ui_sel
                else:
                    temp_ability["type"] = new_ui_sel
                    temp_ability["element"] = "Misc"

                icon_name = get_game_icon_name(temp_ability)
                icon_url = f"{TYPE_ICON_BASE}/{icon_name.lower()}.png"

                # --- RENDER ---
                st.markdown(f"""
                <div class="move-card-header-box">
                    <img src="{icon_url}" class="move-icon-img">
                    <div class="move-name-text" title="{live_name}">{live_name}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c_name, c_type = st.columns([0.65, 0.35], gap="small")
                with c_name:
                    new_name = st.text_input("Name", value=ability.get('name', ''), key=key_name, label_visibility="collapsed")
                with c_type:
                    new_ui_type = st.selectbox("Type", ALL_UI_TYPES, index=ALL_UI_TYPES.index(current_ui_val), key=key_ui_type, label_visibility="collapsed")

                # --- SAVE ---
                if new_ui_type in STANDARD_ELEMENTS:
                    calc_type = "Attack"
                    calc_element = new_ui_type
                else:
                    calc_type = new_ui_type
                    calc_element = "Misc"

                has_changed = False
                if new_name != ability.get("name"):
                    for m in st.session_state["temp_miscrits"]:
                        if m["id"] == selected["id"]:
                            for a in m["abilities"]:
                                if a["id"] == ab_id:
                                    log_edit(selected["id"], ab_id, "name", a.get("name"), new_name)
                                    a["name"] = new_name
                                    has_changed = True
                                    break
                            break

                if calc_type != ability.get("type") or calc_element != ability.get("element"):
                    for m in st.session_state["temp_miscrits"]:
                         if m["id"] == selected["id"]:
                            for a in m["abilities"]:
                                if a["id"] == ab_id:
                                    log_edit(selected["id"], ab_id, "type", f"{a.get('type')}/{a.get('element')}", f"{calc_type}/{calc_element}")
                                    a["type"] = calc_type
                                    a["element"] = calc_element
                                    has_changed = True
                                    break
                            break
                
                if has_changed:
                    st.toast(f"Updated: {new_name}")
                
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    st.divider()
    
    col_ex_1, col_ex_2 = st.columns([3, 1])
    with col_ex_2:
        if st.button("📦 Prepare Download", type="primary", use_container_width=True):
            one_line = json.dumps(st.session_state["temp_miscrits"], separators=(",", ":"), ensure_ascii=False)
            st.session_state["_export_json"] = one_line
            st.session_state["unsaved_changes"] = False
            st.success("Ready!")
        
        if st.session_state.get("_export_json"):
            st.download_button("⬇️ Download .json", data=st.session_state["_export_json"].encode("utf-8"), file_name=f"miscrits_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)