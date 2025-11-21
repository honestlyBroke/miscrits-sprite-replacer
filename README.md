# Miscrits Sprite Replacer

*A Streamlit + Godot utility for customizing Miscrits battle sprites*

This tool allows you to **decrypt, preview, replace, and re-encrypt** Miscrits battle sprites using a clean Streamlit interface and a headless Godot 4 engine.
It is designed for simple, cosmetic sprite modding—ideal for replacing the appearance of **up to four crits in your party**.

---

## 🌟 Features

* **Upload encrypted sprite cache files** directly from the game
* **Automatic decryption** via Godot + GDScript
* **Visual previews** for all decrypted sprites
* **Upload your own replacement art** (PNG/JPG)
* **Automatic resizing** to match original dimensions
* **Re-encoding** into the same encrypted sprite cache format
* **One-click download** of the patched file ready to drop back into the game

---

## ⚠️ Important Notice

This tool is intended **only for personal cosmetic modification**.
Always consult the game’s Terms of Service, and avoid any use that affects online integrity or fairness.

---

## 📦 Requirements

* Python **3.9+**
* Godot **4.x Linux headless/console binary**
  Example: `Godot_v4.1-stable_linux.x86_64`
* Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔧 Setup

### 1. Place the Godot binary

Download Godot’s Linux console export and place it in:

```
bin/Godot_v4.1-stable_linux.x86_64
```

If you use a different name or location, update `GODOT_BIN` in the script.

### 2. Run the tool

```bash
streamlit run app.py
```

A browser window will launch automatically.

---

## 🎮 How to Replace Your Miscrits Sprites

### **Step 1 — Prepare your game files**

1. Navigate to your Miscrits sprite cache folder:

   ```
   C:\Users\<YOU>\AppData\Roaming\Godot\app_userdata\Miscrits\image_cache\sprites
   ```

2. Delete everything inside the `sprites` directory.

3. Launch Miscrits, add **up to 4 crits** to your **party**, then **close the game**.
   The folder should now contain **1–4 encrypted sprite files**.

---

### **Step 2 — Upload your encrypted files**

Open the web app → Step 1 → Upload the `.sprite` cache files.
The tool will decrypt them and show the extracted PNGs.

---

### **Step 3 — Choose a sprite and swap the art**

For each crit:

* Preview the original sprite
* Upload your replacement image (PNG/JPG, any size)
* The tool automatically resizes it to match the original dimensions

---

### **Step 4 — Download your patched file**

After encoding, download the new encrypted sprite file and save it back into:

```
.../Miscrits/image_cache/sprites
```

Overwrite the original when prompted.

---

## 📌 Notes & Limitations

* Only sprites for **current party crits** can be modified (max 4).
* If you later clear the `sprites` folder, the game rebuilds originals—you’ll need to rerun this tool to reapply your custom art.
* Tool currently supports **battle sprites only**, not UI icons or thumbnails.

---
