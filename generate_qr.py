import qrcode
from PIL import Image, ImageDraw
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
            new_data.append((255, 255, 255, 0))  # make transparent
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def make_qr(url: str,
            file_path: str = "qr_clean_logo.png",
            fg_color: str = "#000000",
            bg_color: str = "#FFFFFF",
            box_size: int = 50,
            border: int = 4,
            logo_path: str = None,
            logo_scale: float = 0.2) -> str:
    
    fg_color = validate_hex_color(fg_color, "#000000")
    bg_color = validate_hex_color(bg_color, "#FFFFFF")

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

        # Resize logo
        logo_size = int(min(width, height) * logo_scale)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # Calculate position
        pos = ((width - logo_size) // 2, (height - logo_size) // 2)

        # Draw white rectangle under logo to clear QR area
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [pos[0], pos[1], pos[0] + logo_size, pos[1] + logo_size],
            fill=bg_color
        )

        # Paste logo on top
        img.paste(logo, pos, mask=logo)

    img.save(file_path)
    return file_path


def get_qr_filename_from_url(url: str, prefix: str = "qr") -> str:
    parsed = urlparse(url)
    # Extract domain part before `.com`
    domain = parsed.netloc.replace("www.", "")
    domain_base = domain.split(".")[0]  # e.g., 'usaa'
    
    # Extract first path component after /
    path = parsed.path.strip("/")
    path_part = path.split("/")[0] if path else ""
    
    # Construct filename
    if path_part:
        filename = f"{prefix}_{domain_base}_{path_part}.png"
    else:
        filename = f"{prefix}_{domain_base}.png"
    return filename



if __name__ == "__main__":
    url=input("=> Enter the URL to encode in QR: ").strip()
    fg = "#1A3258"
    bg = "#FFFFFF"
    logo_path = "usaa-logo.png"  # Place your
    
    filename_input = input("=> Enter output QR filename (without .png): ").strip()
    if not filename_input:
        filename_input = "qr_code"  # fallback default

    output_filename = filename_input + ".png"
    print('Generating ...')


    out_path = make_qr(url,output_filename, fg, bg, logo_path=logo_path)
    print(f"***  QR code saved to: {out_path}  ***")
