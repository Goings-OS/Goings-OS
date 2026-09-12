# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: HIGH-RESOLUTION PRINT-READY QR TABLE CARD GENERATION ENGINE
# COMPLIANCE: ZERO EM-DASHES; SECURE COMPLIANT PALETTE SCHEMES
# ==============================================================================

import os
import sys
import qrcode  # type: ignore
from PIL import Image, ImageDraw, ImageFont

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore
    except AttributeError:
        pass


def get_system_font(font_names, size):
    """Dynamically locates and loads a TrueType font from system paths; falls back to default."""
    for name in font_names:
        paths = [
            name,
            os.path.join("C:\\Windows\\Fonts", name),
            os.path.join("C:\\Windows\\Fonts", name.lower()),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", name),
        ]
        for path in paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
    return ImageFont.load_default()


def wrap_text_to_width(text, font, max_width, draw):
    """Splits a text string into multiple lines to fit within a specified maximum width."""
    words = text.split(" ")
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        line_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width > max_width:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return lines


def build_table_card(filename, url, title, subtitle, cta, footer, theme="cream_gold"):
    """Constructs a high-resolution 300 DPI (1500x2100 px) print-ready table card."""
    width, height = 1500, 2100
    
    # Establish Color Palette configurations
    if theme == "sovereign":
        # Sovereign Theme: Ocean Navy (#07162C) and Luxury Gold (#FACC15) values exclusively
        bg_color = "#07162C"
        border_color = "#FACC15"
        title_color = "#FACC15"
        subtitle_color = "#FACC15"
        cta_color = "#FFFFFF"
        footer_color = "#FACC15"
        qr_fill = "#FACC15"
        qr_back = "#07162C"
    else:
        # Standard Premium Cream & Gold Theme (with Ocean Navy text for high contrast readability)
        bg_color = "#FDFBF7"
        border_color = "#D4AF37"
        title_color = "#07162C"
        subtitle_color = "#D4AF37"
        cta_color = "#07162C"
        footer_color = "#07162C"
        qr_fill = "#07162C"
        qr_back = "#FDFBF7"

    # Create master image canvas
    card = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(card)

    # 1. Render Double Borders
    margin_outer = 60
    border_outer_width = 8
    margin_inner = 80
    border_inner_width = 4

    draw.rectangle(
        [margin_outer, margin_outer, width - margin_outer, height - margin_outer],
        outline=border_color,
        width=border_outer_width
    )
    draw.rectangle(
        [margin_inner, margin_inner, width - margin_inner, height - margin_inner],
        outline=border_color,
        width=border_inner_width
    )

    # 2. Setup Font Families
    title_font = get_system_font(["georgiab.ttf", "timesbd.ttf", "arialbd.ttf"], 72)
    subtitle_font = get_system_font(["georgia.ttf", "times.ttf", "arial.ttf"], 36)
    cta_font = get_system_font(["georgia.ttf", "times.ttf", "segoeui.ttf", "arial.ttf"], 38)
    footer_font = get_system_font(["georgiab.ttf", "timesbd.ttf", "segoeuib.ttf", "arialbd.ttf"], 30)

    # 3. Render Header Text (Centered)
    # Title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_w) / 2, 280), title, fill=title_color, font=title_font)

    # Subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((width - subtitle_w) / 2, 390), subtitle, fill=subtitle_color, font=subtitle_font)

    # 4. Generate & Render QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=qr_fill, back_color=qr_back)
    qr_img = qr_img.convert("RGB")  # type: ignore
    qr_size = 650
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    # Center QR Code
    qr_x = (width - qr_size) // 2
    qr_y = 520
    card.paste(qr_img, (qr_x, qr_y))

    # 5. Render CTA Text (Wrapped & Centered)
    cta_max_w = 1100
    cta_lines = wrap_text_to_width(cta, cta_font, cta_max_w, draw)
    
    cta_start_y = 1320
    line_spacing = 60
    
    for i, line in enumerate(cta_lines):
        line_bbox = draw.textbbox((0, 0), line, font=cta_font)
        line_w = line_bbox[2] - line_bbox[0]
        line_y = cta_start_y + (i * line_spacing)
        draw.text(((width - line_w) / 2, line_y), line, fill=cta_color, font=cta_font)

    # 6. Render Footer Text (Centered)
    footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_w) / 2, 1820), footer, fill=footer_color, font=footer_font)

    # Save to disk
    card.save(filename, "PNG", dpi=(300, 300))
    print(f"[{theme.upper()}] Successfully saved card: {filename}")


if __name__ == "__main__":
    cards_data = [
        {
            "filename": "KIG_Report_QR.png",
            "url": "https://myfreescorenow.com/enroll/?AID=KeepItGoingsLLC&PID=49080",
            "title": "KEEP IT GOINGS",
            "subtitle": "3-BUREAU METRIC GATEWAY",
            "cta": "Scan the secure code above to immediately connect your active 3-bureau credit metrics with our auditing board.",
            "footer": "HAMPTON ROADS, VA  |  GOINGS OS SECURE PORT"
        },
        {
            "filename": "KIG_Portal_QR.png",
            "url": "https://keepitgoings.com",
            "title": "KEEP IT GOINGS LLC",
            "subtitle": "SECURE INTAKE PORTAL",
            "cta": "Scan the secure code above to access our Phase 1 Onboarding Form and select your dynamic trajectory.",
            "footer": "HAMPTON ROADS, VA  |  COMPLIANCE LEGISLATIVE INTAKE"
        },
        {
            "filename": "KIG_Checkout_QR.png",
            "url": "https://link.fastpaydirect.com/payment-link/6a3579e2eaa0b5cf5db56498",
            "title": "KEEP IT GOINGS",
            "subtitle": "FASTPAY DIRECT GATEWAY",
            "cta": "Scan the secure code above to process your flat-fee Clarity Kickstart retainer and secure Stage 02 allocation.",
            "footer": "GOINGS OS  |  DYNAMIC LEDGER SETTLEMENT"
        }
    ]

    print("==========================================================")
    print(" GOINGS OS: PRIVATIZED TABLE CARD GENERATOR INITIALIZING  ")
    print("==========================================================")

    # Generate standard theme cards as requested by the parameter inputs
    for data in cards_data:
        build_table_card(
            filename=data["filename"],
            url=data["url"],
            title=data["title"],
            subtitle=data["subtitle"],
            cta=data["cta"],
            footer=data["footer"],
            theme="cream_gold"
        )

    # Generate sovereign theme cards for compliance alignment
    print("\n----------------------------------------------------------")
    print(" GENERATING SOVEREIGN ALIGNED METRIC CARDS                ")
    print("----------------------------------------------------------")
    for data in cards_data:
        sov_filename = data["filename"].replace(".png", "_Sovereign.png")
        build_table_card(
            filename=sov_filename,
            url=data["url"],
            title=data["title"],
            subtitle=data["subtitle"],
            cta=data["cta"],
            footer=data["footer"],
            theme="sovereign"
        )

    print("==========================================================")
    print(" ALL HIGH-RESOLUTION PRINT CARDS COMPILED SUCCESSFUL      ")
    print("==========================================================")
