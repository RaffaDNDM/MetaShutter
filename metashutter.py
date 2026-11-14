import piexif
from PIL import Image, ImageTk, ImageOps
from PIL.ExifTags import TAGS
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BG_MAIN = "#121212"        # Deep charcoal background
BG_CARD = "#1E1E24"        # Elevated row surface
BG_HEADER = "#18181D"      # Top/Bottom bar background
BORDER_COLOR = "#2E2E38"   # Subtle divider lines
TEXT_PRIMARY = "#F3F4F6"   # Crisp off-white text
TEXT_MUTED = "#9CA3AF"     # Secondary metadata text
ACCENT_BLUE = "#3B82F6"    # Primary action button
ACCENT_HOVER = "#2563EB"   # Primary button hover
TAG_OFF_BG = "#2A2A34"     # Unchecked toggle pill
TAG_ON_BG = "#10B981"      # Checked toggle pill (Emerald green)

import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


def read_photo_caption(image_path):
    img = Image.open(image_path)
    exif_data = img.getexif()

    if not exif_data:
        print("No metadata found in this image.")
        return None

    metadata = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
    caption = metadata.get("ImageDescription")

    if caption:
        print(f"Caption found (ImageDescription): {caption}")
        return caption
    else:
        print("No caption field found in the metadata.")
        return None


def get_shooting_parameters(image_path):
    img = Image.open(image_path)
    exif_data = img.getexif()

    if not exif_data:
        return None

    # 1. Main EXIF fields
    readable_exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
    camera = readable_exif.get("Model", "Unknown Camera")

    # 2. Sub-EXIF fields
    ifd_data = exif_data.get_ifd(34665)
    readable_ifd = {TAGS.get(tag_id, tag_id): value for tag_id, value in ifd_data.items()}

    shutter_speed = readable_ifd.get("ExposureTime")
    aperture = readable_ifd.get("FNumber")
    iso = readable_ifd.get("ISOSpeedRatings")
    lens = readable_ifd.get("LensModel", "Unknown Lens")

    if shutter_speed and shutter_speed < 1:
        shutter_str = f"1/{int(1/shutter_speed)}s"
    elif shutter_speed:
        shutter_str = f"{shutter_speed}s"
    else:
        shutter_str = "Unknown Shutter"

    return {
        "camera": camera,
        "lens": lens,
        "aperture": f"f/{aperture}" if aperture else "Unknown Aperture",
        "shutter": shutter_str,
        "iso": f"ISO {iso}" if iso else "Unknown ISO",
    }


def write_photo_caption(image_path, new_caption):
    img = Image.open(image_path)

    if "exif" in img.info:
        exif_dict = piexif.load(img.info["exif"])
    else:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = new_caption.encode("utf-8")

    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, exif=exif_bytes)
    print(f"-> Successfully updated caption to: '{new_caption}'")


def update_single_caption(image_path, exposure_bracketing=False, focus_stacking=False):
    print(f"\nProcessing: {Path(image_path).name}")
    read_photo_caption(image_path)
    params = get_shooting_parameters(image_path)

    if params:
        auto_caption = (
            f"{params['camera']}, {params['lens']} @ "
            f"{params['shutter']}, {params['iso']}, {params['aperture']}"
        )

        techniques = []
        if exposure_bracketing:
            techniques.append("Exposure Bracketing")
        if focus_stacking:
            techniques.append("Focus Stacking")

        if techniques:
            auto_caption += f" ({', '.join(techniques)})"

        write_photo_caption(image_path, auto_caption)
    else:
        print("-> Skipped: Could not extract EXIF shooting parameters.")


def get_target_files(include_subfolders=False):
    root = tk.Tk()
    root.title("Select Input")
    root.configure(bg=BG_CARD)
    root.resizable(False, False)

    # Center the popup on screen and force focus
    w, h = 420, 210
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)

    files_to_process = []

    def pick_files():
        nonlocal files_to_process
        selected = filedialog.askopenfilenames(
            parent=root,
            title="Select JPEG files",
            filetypes=[("JPEG Images", "*.jpg;*.jpeg")],
        )
        if selected:
            files_to_process = [str(Path(f).resolve()) for f in selected]
            root.destroy()

    def pick_folder():
        nonlocal files_to_process
        folder = filedialog.askdirectory(parent=root, title="Select a folder")
        if folder:
            folder_path = Path(folder)
            pattern = folder_path.rglob("*") if include_subfolders else folder_path.glob("*")
            files_to_process = sorted(
                [
                    str(f.resolve())
                    for f in pattern
                    if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg"]
                ]
            )
            root.destroy()

    tk.Label(
        root,
        text="Select Images to Tag",
        font=("Segoe UI", 12, "bold"),
        fg=TEXT_PRIMARY,
        bg=BG_CARD,
    ).pack(pady=(22, 6))

    tk.Label(
        root,
        text="Choose individual JPEG files or scan an entire folder.",
        font=("Segoe UI", 9),
        fg=TEXT_MUTED,
        bg=BG_CARD,
    ).pack(pady=(0, 20))

    btn_frame = tk.Frame(root, bg=BG_CARD)
    btn_frame.pack()

    tk.Button(
        btn_frame,
        text="Select Files...",
        font=("Segoe UI", 9, "bold"),
        fg="#FFFFFF",
        bg=ACCENT_BLUE,
        activebackground=ACCENT_HOVER,
        activeforeground="#FFFFFF",
        relief="flat",
        padx=16,
        pady=8,
        cursor="hand2",
        command=pick_files,
    ).pack(side="left", padx=8)

    tk.Button(
        btn_frame,
        text="Select Folder...",
        font=("Segoe UI", 9, "bold"),
        fg=TEXT_PRIMARY,
        bg=TAG_OFF_BG,
        activebackground="#363642",
        activeforeground=TEXT_PRIMARY,
        relief="flat",
        padx=16,
        pady=8,
        cursor="hand2",
        command=pick_folder,
    ).pack(side="left", padx=8)

    root.mainloop()
    return files_to_process


class ModernToggleButton(tk.Label):
    """A sleek pill-style toggle button that replaces dated native checkboxes."""
    def __init__(self, parent, variable, label_off="Off", label_on="✓ Active", **kwargs):
        super().__init__(
            parent,
            text=label_off,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=TAG_OFF_BG,
            width=12,
            pady=6,
            cursor="hand2",
            **kwargs,
        )
        self.variable = variable
        self.label_off = label_off
        self.label_on = label_on
        self.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        new_val = not self.variable.get()
        self.variable.set(new_val)
        if new_val:
            self.config(text=self.label_on, bg=TAG_ON_BG, fg="#FFFFFF")
        else:
            self.config(text=self.label_off, bg=TAG_OFF_BG, fg=TEXT_MUTED)

class CaptionTaggerGUI:
    def __init__(self, root, file_paths):
        self.root = root
        self.root.title("EXIF Studio — Technique & Caption Tagger")
        self.root.configure(bg=BG_MAIN)

        # Center main window on screen
        w, h = 880, 640
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Bring window to front and steal focus reliably
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(150, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

        self.file_rows = []
        self.thumbnail_refs = []

        self.configure_styles()
        self.setup_ui()
        self.populate_rows(file_paths)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Vertical.TScrollbar",
            gripcount=0,
            background="#32323E",
            darkcolor=BG_MAIN,
            lightcolor=BG_MAIN,
            troughcolor=BG_MAIN,
            bordercolor=BG_MAIN,
            arrowcolor=TEXT_MUTED,
        )
        style.map("Dark.Vertical.TScrollbar", background=[("active", "#4B4B5C")])

    def create_thumbnail(self, image_path, size=(72, 72)):
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Could not create thumbnail for {image_path}: {e}")
            return None

    def setup_ui(self):
        # Top Header Bar
        top_bar = tk.Frame(self.root, bg=BG_HEADER, pady=14, padx=20)
        top_bar.pack(fill="x")

        tk.Label(
            top_bar,
            text="EXIF Caption & Technique Tagger",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_HEADER,
        ).pack(side="left")

        self.count_badge = tk.Label(
            top_bar,
            text="0 FILES",
            font=("Segoe UI", 8, "bold"),
            fg=ACCENT_BLUE,
            bg="#1E293B",
            padx=10,
            pady=4,
        )
        self.count_badge.pack(side="right")

        tk.Frame(self.root, height=1, bg=BORDER_COLOR).pack(fill="x")

        # Column Headers
        col_header = tk.Frame(self.root, bg=BG_MAIN, pady=10, padx=28)
        col_header.pack(fill="x")

        tk.Label(col_header, text="PREVIEW", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_MAIN, width=10, anchor="center").pack(side="left")
        tk.Label(col_header, text="IMAGE & CAMERA METADATA", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_MAIN, width=36, anchor="w").pack(side="left", padx=(14, 0))
        tk.Label(col_header, text="EXPOSURE BRACKETING", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_MAIN, width=20, anchor="center").pack(side="left")
        tk.Label(col_header, text="FOCUS STACKING", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_MAIN, width=18, anchor="center").pack(side="left")

        # Scrollable Card List
        container = tk.Frame(self.root, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview, style="Dark.Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_MAIN)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Bottom Footer Bar
        tk.Frame(self.root, height=1, bg=BORDER_COLOR).pack(fill="x")
        bottom_bar = tk.Frame(self.root, bg=BG_HEADER, pady=14, padx=20)
        bottom_bar.pack(fill="x")

        tk.Label(
            bottom_bar,
            text="Click pills to toggle techniques before writing EXIF tags",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_HEADER,
        ).pack(side="left")

        apply_btn = tk.Button(
            bottom_bar,
            text="Apply & Write EXIF",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg=ACCENT_BLUE,
            activebackground=ACCENT_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=18,
            pady=7,
            cursor="hand2",
            command=self.apply_updates,
        )
        apply_btn.pack(side="right")

    def populate_rows(self, file_paths):
        for file_str in file_paths:
            path = Path(file_str)
            eb_var = tk.BooleanVar(value=False)
            fs_var = tk.BooleanVar(value=False)

            card_border = tk.Frame(self.scrollable_frame, bg=BORDER_COLOR, padx=1, pady=1)
            card_border.pack(fill="x", pady=4, padx=4)

            card = tk.Frame(card_border, bg=BG_CARD, padx=10, pady=8)
            card.pack(fill="x")

            # 1. Thumbnail Box
            thumb_box = tk.Frame(card, width=76, height=76, bg="#141418")
            thumb_box.pack_propagate(False)
            thumb_box.pack(side="left")

            thumb_img = self.create_thumbnail(file_str, size=(72, 72))
            if thumb_img:
                self.thumbnail_refs.append(thumb_img)
                tk.Label(thumb_box, image=thumb_img, bg="#141418").pack(expand=True)
            else:
                tk.Label(thumb_box, text="No Preview", font=("Segoe UI", 7), fg=TEXT_MUTED, bg="#141418").pack(expand=True)

            # 2. File Info + Live EXIF Preview Subtext
            info_frame = tk.Frame(card, bg=BG_CARD, width=265)
            info_frame.pack_propagate(False)
            info_frame.pack(side="left", fill="y", padx=(14, 0))

            display_name = path.name if len(path.name) <= 30 else path.name[:27] + "..."
            tk.Label(
                info_frame,
                text=display_name,
                font=("Segoe UI", 10, "bold"),
                fg=TEXT_PRIMARY,
                bg=BG_CARD,
                anchor="w",
            ).pack(fill="x", pady=(12, 2))

            params = get_shooting_parameters(file_str)
            exif_summary = (
                f"{params['shutter']}  •  {params['aperture']}  •  {params['iso']}"
                if params
                else "No EXIF metadata"
            )
            tk.Label(
                info_frame,
                text=exif_summary,
                font=("Segoe UI", 8),
                fg=TEXT_MUTED,
                bg=BG_CARD,
                anchor="w",
            ).pack(fill="x")

            # 3. Modern Toggle Pills
            eb_container = tk.Frame(card, bg=BG_CARD)
            eb_container.pack(side="left", padx=(24, 20))
            ModernToggleButton(eb_container, variable=eb_var, label_off="Off", label_on="✓ Bracketing").pack()

            fs_container = tk.Frame(card, bg=BG_CARD)
            fs_container.pack(side="left", padx=(16, 0))
            ModernToggleButton(fs_container, variable=fs_var, label_off="Off", label_on="✓ Stacking").pack()

            self.file_rows.append({
                "path": file_str,
                "eb_var": eb_var,
                "fs_var": fs_var,
            })

        self.count_badge.config(text=f"{len(self.file_rows)} FILE{'S' if len(self.file_rows) != 1 else ''}")

    def apply_updates(self):
        for row in self.file_rows:
            update_single_caption(
                image_path=row["path"],
                exposure_bracketing=row["eb_var"].get(),
                focus_stacking=row["fs_var"].get(),
            )

        # Dark-themed completion popup
        done_win = tk.Toplevel(self.root)
        done_win.title("Complete")
        done_win.configure(bg=BG_CARD)
        done_win.resizable(False, False)
        done_win.transient(self.root)
        done_win.grab_set()

        w, h = 340, 150
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)
        done_win.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(
            done_win,
            text=f"✓ Updated {len(self.file_rows)} file(s)!",
            font=("Segoe UI", 11, "bold"),
            fg=TAG_ON_BG,
            bg=BG_CARD,
        ).pack(pady=(28, 16))

        tk.Button(
            done_win,
            text="Close",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg=ACCENT_BLUE,
            relief="flat",
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.root.destroy,
        ).pack()



def main():
    target_files = get_target_files(include_subfolders=False)

    if not target_files:
        print("No JPEG files selected or operation canceled.")
        return

    print(f"Found {len(target_files)} file(s). Opening preview...")
    root = tk.Tk()
    app = CaptionTaggerGUI(root, target_files)
    root.mainloop()


if __name__ == "__main__":
    main()