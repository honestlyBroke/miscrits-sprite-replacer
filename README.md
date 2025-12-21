# Miscrits Sprite Tool

This utility is a **Streamlit + Godot** application designed for browsing the Miscrits catalog and patching sprites or avatars with custom images. It provides a clean interface to generate encrypted cache files that the game requires for local cosmetic modifications.

---

## 🚀 Features

* 🔎 **Extended Catalog Support:** Browse and search through **Regular Miscrits**, **Local Bosses**, and **Global Bosses** (e.g., Mizokami or Magicite).
* 🧩 **Dual-Mode Editing:** Replace either the **final evolution battle sprite** or the **50×50 profile avatar**.
* 🎨 **Visual Previews:** View current in-game art pulled directly from the CDN alongside your replacement art.
* 📐 **Advanced Resizing:** * **Sprites:** Use a size multiplier (0.5x to 2.0x) and a "Keep landscape shape" toggle to ensure your custom art fits perfectly.
* **Avatars:** Automatically forces a 50×50px resolution for game compatibility.


* 🔐 **Automated Encryption:** Uses a headless Godot binary to encrypt your PNG into the game's specific `.patched` format.
* 🌈 **Element Support:** Full support for single and dual-element icons.

---

## 🛠️ Requirements

* **Python:** 3.9+
* **Godot Binary:** Godot v4.1 (Linux headless/console version) placed in `bin/`.
* **Dependencies:** `streamlit`, `pillow`, `requests`.

---

## 📥 Setup & Installation

1. **Clone the Repository:**
```bash
git clone https://github.com/honestlybroke/miscrits-sprite-replacer.git
cd miscrits-sprite-replacer

```


2. **Install Python Packages:**
```bash
pip install streamlit pillow requests

```


3. **Godot Binary:** Ensure your Godot headless binary is located at `bin/Godot_v4.1-stable_linux.x86_64`.
4. **Run the App:**
```bash
streamlit run app.py

```



---

## 📖 How to Use

### Step 1: Choose Your Target

* Toggle between the **Miscrits** and **Bosses** catalogs.
* Search by name, element, or rarity/location.
* Click **"Change Sprite"** or **"Change Boss Sprite"** to begin editing.

### Step 2: Upload & Configure

* Select **Sprite** or **Avatar** mode at the top.
* Upload your new image (PNG/JPG).
* **For Sprites:** Adjust the `Size multiplier` slider. If "Keep landscape shape" is checked, the app matches the original height while maintaining your image's aspect ratio.
* **For Avatars:** The app handles the 50x50px resizing automatically.

### Step 3: Encrypt & Download

* Click the **Download** button to receive the encrypted file.
* The filename will be a unique hash (e.g., `b6b0c2...`)—**do not rename it**.

### Step 4: Apply to Game

Copy and paste the downloaded file into the corresponding Windows directory:

| Mode | Windows Path (Paste into Explorer) |
| --- | --- |
| **Sprite** | `%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\sprites` |
| **Avatar** | `%USERPROFILE%\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\miscrits` |

> **Pro Tip:** Sort the destination folder by **Date modified** to quickly find and replace the existing file.

---

## ⚠️ Important Notice

This tool is intended for **personal cosmetic modification only**. Always adhere to the game’s Terms of Service. If you clear your game cache, you will need to re-apply your custom files.
