"""
Data loading utilities for Miscrits catalog
(added raw miscrits loader that supports local/upload/server)
"""
import json
import requests
import streamlit as st
from pathlib import Path
from typing import List, Dict, Optional, Union
from config import BOSSES_CATALOG_PATH, MISCRITS_JSON_URL, FETCH_TIMEOUT, MISCRITS_LOCAL_PATH


@st.cache_data(ttl=1800)
def load_miscrits_from_api() -> List[Dict]:
    """
    Load miscrits.json from the API and process into evolution stages (existing behaviour).
    Returns a list of miscrits with all evolution stages.
    """
    try:
        response = requests.get(MISCRITS_JSON_URL, timeout=FETCH_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Process the data to extract evolution information
        processed = []
        for miscrit in data:
            # Get the names array (evolution stages)
            names = miscrit.get("names", [miscrit.get("name", "Unknown")])

            # Create entries for each evolution stage
            for evo_idx, evo_name in enumerate(names):
                processed.append({
                    "id": miscrit.get("id"),
                    "base_name": names[0] if names else "Unknown",
                    "evo_stage": evo_idx + 1,
                    "evo_name": evo_name,
                    "total_stages": len(names),
                    "element": miscrit.get("element", "None"),
                    "rarity": miscrit.get("rarity", "Common"),
                    "image": miscrit.get("image"),
                    "locations": miscrit.get("locations", []),
                    "all_names": names
                })

        return processed
    except Exception as e:
        st.error(f"Failed to load miscrits from API: {e}")
        return []


@st.cache_data
def load_boss_catalog() -> List[Dict]:
    """Load the bosses catalog"""
    if not BOSSES_CATALOG_PATH.exists():
        return []

    with open(BOSSES_CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_miscrit_by_id_and_stage(miscrits: List[Dict], miscrit_id: int, stage: int) -> Optional[Dict]:
    """Get a specific evolution stage of a miscrit"""
    for m in miscrits:
        if m["id"] == miscrit_id and m["evo_stage"] == stage:
            return m
    return None


def get_all_stages_for_miscrit(miscrits: List[Dict], miscrit_id: int) -> List[Dict]:
    """Get all evolution stages for a given miscrit ID"""
    stages = [m for m in miscrits if m["id"] == miscrit_id]
    return sorted(stages, key=lambda x: x["evo_stage"])


# ------------------------------
# New helpers for Move Editor
# ------------------------------
def load_miscrits_raw(source: str = "auto", uploaded_bytes: Optional[bytes] = None) -> Optional[List[Dict]]:
    """
    Load the raw miscrits.json as a Python list of dicts.
    source: "auto" (tries local -> uploaded -> api), "local", "upload", "api"
    uploaded_bytes: bytes provided by uploader (if source == "upload")
    """
    try:
        # Upload path provided?
        if source == "upload" and uploaded_bytes is not None:
            return json.loads(uploaded_bytes.decode("utf-8"))

        # Local file check
        if source in ("auto", "local"):
            try:
                if MISCRITS_LOCAL_PATH.exists():
                    with open(MISCRITS_LOCAL_PATH, "r", encoding="utf-8") as f:
                        return json.load(f)
            except Exception:
                # swallow here and try fallback
                pass

            if source == "local":
                # explicit local requested but failed: return None
                return None

        # API fallback
        if source in ("auto", "api"):
            resp = requests.get(MISCRITS_JSON_URL, timeout=FETCH_TIMEOUT)
            resp.raise_for_status()
            return resp.json()

    except Exception as e:
        st.error(f"Failed to load miscrits.json ({source}): {e}")
        return None

    return None
