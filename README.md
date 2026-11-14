# MetaShutter

**MetaShutter** is a dark-themed Python desktop utility for photographers that automatically extracts camera shooting parameters from JPEG files and writes clean, standardized captions directly into the image's EXIF `ImageDescription` metadata—with per-photo toggles for **Exposure Bracketing** and **Focus Stacking**.

---

## ✨ Features

* **Flexible Input Selection:** Choose individual `.jpg` / `.jpeg` files or scan an entire folder in one click.
* **Modern Dark-Mode GUI:** Clean, card-based charcoal interface with high-DPI display scaling support for crisp rendering on 1080p and 4K monitors.
* **Auto-Rotated Thumbnail Previews:** Displays properly oriented thumbnails (`ImageOps.exif_transpose`) alongside live camera metadata previews (`shutter speed`, `aperture`, and `ISO`).
* **Per-Image Technique Tagging:** Interactive pill toggles let you mark individual photos for **Exposure Bracketing** and/or **Focus Stacking** before saving.
* **Non-Destructive Metadata Injection:** Preserves existing EXIF headers (`0th`, `Exif`, `GPS`, `Interop`, `1st`, and embedded thumbnails) while updating the `ImageDescription` tag.

---

## 📋 Example Output

When processed, MetaShutter formats and writes the following string into each file's EXIF `ImageDescription` field:

* **Standard Photo:**
  ```text
  ILCE-7M4, FE 24-70mm F2.8 GM II @ 1/250s, ISO 100, f/2.8
  ```
* **Tagged Photo (Single or Combined Techniques):**
  ```text
  ILCE-7M4, FE 24-70mm F2.8 GM II @ 1/250s, ISO 100, f/2.8 (Exposure Bracketing)
  ILCE-7M4, FE 24-70mm F2.8 GM II @ 1/60s, ISO 200, f/8.0 (Exposure Bracketing, Focus Stacking)
  ```

---

## 🛠️ Requirements

* **Python 3.8+**
* **Pillow** (`PIL`) — for image loading, EXIF extraction, and thumbnail generation
* **piexif** — for reading and injecting binary EXIF dictionaries into JPEGs
* **Tkinter** — included with standard Python installations on Windows and macOS *(Linux users may need `sudo apt install python3-tk`)*

---

## 🚀 Installation & Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run MetaShutter:**
   ```bash
   python metashutter.py
   ```

3. **Tag & Apply:**
   * Click **Select Files...** or **Select Folder...** in the startup modal.
   * Review your selected photos and click the **Exposure Bracketing** or **Focus Stacking** pills on any applicable cards.
   * Click **Apply & Write EXIF** to update the metadata across all loaded images.

---

## ⚙️ Configuration

* **Include Subfolders:** By default, folder selection scans only the top-level directory. To scan nested subfolders recursively, update `main()` in `metashutter.py`:
  ```python
  target_files = get_target_files(include_subfolders=True)
  ```
* **Supported Formats:** Currently restricted to `.jpg` and `.jpeg` files due to EXIF binary injection requirements.