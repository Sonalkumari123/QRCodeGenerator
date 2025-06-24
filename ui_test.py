import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw
import qrcode
import qrcode.image.svg
import re
import os

def validate_hex_color(color: str, default: str) -> str:
    if isinstance(color, str) and re.fullmatch(r"#([0-9a-fA-F]{6})", color):
        return color
    return default

def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def make_qr(url: str,
            file_path: str,
            fg_color: str = "#1A3258",
            bg_color: str = "#FFFFFF",
            box_size: int = 50,
            border: int = 4,
            logo_path: str = None,
            logo_scale: float = 0.2,
            fmt: str = "png") -> str:

    fg_color = validate_hex_color(fg_color, "#1A3258")
    bg_color = validate_hex_color(bg_color, "#FFFFFF")

    if fmt == "svg":
        factory = qrcode.image.svg.SvgImage
        qr = qrcode.QRCode(
            version=6,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=border,
            image_factory=factory
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image()
        img.save(file_path)
        return file_path

    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGBA")
    width, height = img.size

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")

        logo = remove_white_background(logo)
        logo_size = int(min(width, height) * logo_scale)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        pos = ((width - logo_size) // 2, (height - logo_size) // 2)
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [pos[0], pos[1], pos[0] + logo_size, pos[1] + logo_size],
            fill=bg_color
        )
        img.paste(logo, pos, mask=logo)

    img = img.convert("RGB")
    img.save(file_path)
    return file_path


def generate_qr():
    url = url_entry.get().strip()
    filename = filename_entry.get().strip()
    fmt = format_combo.get().lower().strip()
    theme = theme_combo.get().strip()

    if not url:
        messagebox.showerror("Input Error", "URL cannot be empty.")
        return
    if not filename:
        filename = "qr_code"
    if not filename.lower().endswith(f".{fmt}"):
        filename += f".{fmt}"

    # Color and logo selection logic
    theme_map = {
        "Blue (fg) + White (bg)": ("#1A3258", "#FFFFFF", "usaa_blue.png"),
        "Black (fg) + White (bg)": ("#000000", "#FFFFFF", "usaa_black.png"),
        "White (fg) + Blue (bg)": ("#FFFFFF", "#1A3258", "usaa_white.png"),
        "White (fg) + Black (bg)": ("#FFFFFF", "#000000", "usaa_white.png")
    }

    fg_color, bg_color, logo_filename = theme_map.get(theme, ("#1A3258", "#FFFFFF", "usaa_blue.png"))
    
    # Make logo path absolute and check existence
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_logo_path = os.path.join(script_dir, logo_filename)
    if not os.path.exists(full_logo_path):
        messagebox.showwarning("Warning", f"Logo file not found: {full_logo_path}\nQR will be generated without logo.")
        full_logo_path = None

    try:
        output_path = make_qr(
            url,
            filename,
            fg_color=fg_color,
            bg_color=bg_color,
            logo_path=full_logo_path,
            fmt=fmt
        )
        messagebox.showinfo("Success", f"QR code saved as: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def create_context_menu(entry):
    menu = tk.Menu(entry, tearoff=0)
    menu.add_command(label="Paste", command=lambda: entry.insert(tk.INSERT, root.clipboard_get()))
    entry.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

# GUI setup
root = tk.Tk()
root.title("QR Code Generator")

tk.Label(root, text="Enter URL:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
url_entry = tk.Entry(root, width=40)
url_entry.grid(row=0, column=1, padx=5)

tk.Label(root, text="Output filename:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
filename_entry = tk.Entry(root, width=40)
filename_entry.grid(row=1, column=1, padx=5)

tk.Label(root, text="File format:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
format_combo = ttk.Combobox(root, values=["png", "svg", "pdf", "eps"], state="readonly")
format_combo.current(0)
format_combo.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Color theme:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
theme_combo = ttk.Combobox(
    root,
    values=["Blue (fg) + White (bg)","Black (fg) + White (bg)", "White (fg) + Blue (bg)", "White (fg) + Black (bg)"],
    state="readonly"
)
theme_combo.current(0)
theme_combo.grid(row=3, column=1, padx=5, pady=5)

create_context_menu(url_entry)
create_context_menu(filename_entry)

generate_button = tk.Button(root, text="Generate QR Code", command=generate_qr)
generate_button.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
