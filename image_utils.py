"""
Image processing and display utilities
"""
import hashlib
import requests
import streamlit as st
from io import BytesIO
from PIL import Image
from pathlib import Path
from typing import Tuple, Union, Literal
from config import FETCH_TIMEOUT


def sprite_cdn_url(name: str, suffix: str = "_back") -> str:
    """Build CDN URL for a miscrit sprite"""
    slug = name.replace(" ", "_").lower()
    return f"https://cdn.worldofmiscrits.com/miscrits/{slug}{suffix}.png"


def avatar_cdn_url(name: str) -> str:
    """Build CDN URL for a Miscrit avatar icon (50x50)"""
    slug = name.replace(" ", "_").lower()
    return f"https://cdn.worldofmiscrits.com/avatars/{slug}_avatar.png"


def element_icon_url(element: str) -> str:
    """Get the element icon URL"""
    if not element:
        return ""
    slug = element.strip().lower().replace(" ", "")
    return f"https://worldofmiscrits.com/{slug}.png"


def sprite_cache_filename(url: str) -> str:
    """Cache filename is SHA256 of the full CDN URL"""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


# OPTIMIZATION: Cache this function to prevent re-downloading on every click
@st.cache_data(show_spinner=False, ttl=3600)
def load_sprite_on_canvas(url: str, canvas_size: Tuple[int, int] = (256, 256)) -> Image.Image:
    """
    Load a sprite from CDN, scale to fit canvas while keeping aspect ratio,
    and center on a transparent canvas.
    """
    try:
        resp = requests.get(url, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
    except Exception:
        return Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    
    try:
        img = Image.open(BytesIO(resp.content)).convert("RGBA")
        img.thumbnail(canvas_size, Image.LANCZOS)
        
        canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        x = (canvas_size[0] - img.width) // 2
        y = (canvas_size[1] - img.height) // 2
        canvas.paste(img, (x, y), img)
        
        return canvas
    except Exception:
        return Image.new("RGBA", canvas_size, (0, 0, 0, 0))


def place_on_canvas(img: Image.Image, canvas_size: Tuple[int, int] = (256, 256)) -> Image.Image:
    """Center an image on a transparent canvas of fixed size"""
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_size[0] - img.width) // 2
    y = (canvas_size[1] - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


@st.cache_data(show_spinner=False)
def get_original_sprite_size(url: str) -> Tuple[int, int]:
    """Download sprite and return its original dimensions"""
    try:
        resp = requests.get(url, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        return img.size
    except Exception:
        return (256, 256)


def show_pil_via_file(
    workdir: Path,
    img: Image.Image,
    filename: str,
    *,
    caption: str = None,
    width: Union[int, Literal["stretch", "content"]] = "stretch",
) -> None:
    """Save a PIL image to workdir and display it via file path"""
    # OPTIMIZATION: Only save if file doesn't exist to reduce disk writes
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / filename
    
    # We save anyway to ensure the displayed image matches the current state (in case of edits),
    # but for the grid (which uses constant filenames like grid_123.png) we could skip.
    # For safety/simplicity in editing, we keep the save, but OS disk caching handles it well.
    img.save(path)
    st.image(str(path), caption=caption, width=width)