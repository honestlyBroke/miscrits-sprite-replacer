# Miscrits Sprite Replacer

*A Streamlit + Godot utility for browsing Miscrits and patching their sprites/avatars*

This tool lets you browse the full Miscripedia, pick a Miscrit, and generate an encrypted cache file that replaces either its **final evolution battle sprite** or its **50×50 avatar**. It uses a clean Streamlit UI on top of a headless Godot 4 encoder, so you never have to touch the raw cache files yourself.

---

## Live App

- **Hosted version:** https://miscrits-sprite-replacer.streamlit.app/

---

## Features

- 🔎 **Miscripedia grid**
  - Browse all Miscrits with **search**, **rarity** and **element** filters.
  - Paged grid with consistent card layout and sprite previews.

- 🧩 **Sprite vs Avatar modes**
  - Replace either the **final evolution battle sprite** (**Sprite** mode), or the **50×50 avatar icon** (**Avatar** mode).
  - Shows the **current in‑game art** pulled from the Miscrits CDN.

- 📐 **Smart resizing**
  - Sprites: resize relative to the original **height** with a `Size multiplier` slider and **“Keep landscape shape”** toggle.
  - Avatars: always encoded at **50×50px** automatically.

- 🔐 **One‑click encrypted output**
  - The app uses Godot + GDScript to **encrypt** your PNG into the format the game expects.
  - Outputs the file with the exact **hash filename** that the game uses for that sprite/avatar.

- 💾 **Drop‑in replacement**
  - Download the encoded file and drop it into the correct `image_cache` folder.
  - As long as the **filename matches exactly**, the game will load your custom art.

---

## ⚠️ Important Notice

This tool is intended **only for personal cosmetic modification**.  
Always consult the game’s Terms of Service, and avoid any use that affects online integrity or fairness.

---

## Requirements

- Python **3.9+**
- Godot **4.x Linux headless/console binary**  
  Example: `Godot_v4.1-stable_linux.x86_64`
- Python packages:
  - `streamlit`
  - `pillow`
  - `requests`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/honestlybroke/miscrits-sprite-replacer.git
cd miscrits-sprite-replacer
```

### 2. Place the Godot binary

Download Godot’s Linux console/headless export and place it at:

```text
bin/Godot_v4.1-stable_linux.x86_64
```

If you use a different name or location, update `GODOT_BIN` in `app.py`.

### 3. Run the app

```bash
streamlit run app.py
```

A browser window should open automatically.

---

## How to Use

### Step 1 — Choose a Miscrit

On the main page:

1. Use **Search Miscrits…** to find a crit by its **first** or **final** evolution name.
2. Filter by **rarity** and/or **element** if you like.
3. Browse the grid and click **“Change Sprite”** on the Miscrit you want to edit.

> The preview sprite comes from the Miscrits CDN and is drawn onto a fixed canvas so all cards stay the same height.

---

### Step 2 — Pick What You Want to Replace

At the top of Step 2, choose:

- **Sprite** – replace the **final evolution battle sprite**, or  
- **Avatar** – replace the **50×50 avatar icon**.

The right side will show:

- The **current in‑game art** (from the CDN).
- The **original size** (for sprites), or `50×50px` for avatars.
- The **cache filename** that the game uses (a long hash like `b6b0c2...`).

---

### Step 3 — Upload Your Replacement Art

On the right side:

1. Upload your PNG/JPG.  
2. The app will show a **preview** on a fixed‑size canvas:

   - For **sprites**, you’ll see:
     - `Size multiplier` slider (0.5–2.0)
     - **Keep landscape shape** checkbox  
       - If checked: matches original **height** and respects your image’s aspect ratio.  
       - If unchecked: stretches based on original **width** and **height**.

   - For **avatars**:
     - Your upload is automatically resized to **50×50px**.
     - Preview is shown centered on a smaller canvas.

3. Tweak the size controls (for sprites) until the preview looks right.

---

### Step 4 — Encode & Download

Once a valid upload + size combo is set:

1. The app calls the **Godot encoder script** to generate the encrypted cache file.
2. When encoding succeeds, a **Download** button appears:
   - **Sprite mode:** `⬇️ Download encrypted sprite`  
   - **Avatar mode:** `⬇️ Download encrypted avatar`

The downloaded file will already have the correct **hash filename** for that Miscrit’s sprite/avatar.

---

### Step 5 — Drop the File into the Game Folder

On **Windows**, the relevant folders are:

- If you are editing **Sprite**:

  ```text
  %USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\sprites
  ```

- If you are editing **Avatar**:

  ```text
  %USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\miscrits
  ```

Then:

1. Sort the folder by **Date modified** so the newest file is on top.
2. Make sure the filename matches **exactly** the one shown in the app (a long hash).
3. Replace the existing file **in place**:
   - If Windows adds things like ` (1)` or changes the extension, rename it back to the exact hash.

If you ever **clear** your `sprites` or `miscrits` cache folders, the game will rebuild originals and you’ll need to drop your patched files back in again.

---

## Tutorial Video

The same video used in the hosted app is included in the repo:

- `assets/spriteguide-real-2.mp4`

If your browser doesn’t show the embedded video, you can open it directly from that file.

---

## Notes & Limitations

- This tool relies on the Miscrits **CDN** to show the current sprites/avatars.
- Replacements are **per cache file**:
  - Clearing the cache folders removes your custom art.
- Currently focuses on:
  - **Final evolution battle sprites**
  - **50×50 avatar icons**

Future improvements might include:

- Support for more UI icons or additional sprite variants.
- Extra layout/preview tools for advanced positioning.

---

## License

This project is released under the **MIT License**. See `LICENSE` for details.
