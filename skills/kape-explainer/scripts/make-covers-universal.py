#!/usr/bin/env python3
"""
make-covers-universal.py — Universal cross-platform cover generator for KAPE films.
Creates THUMBNAIL.png (1280x720) and TIKTOK-COVER.png (1080x1920) on Mac and Linux.
"""
import sys
import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_font(size, bold=True):
    font_paths = [
        # Linux / Ubuntu (GitHub Actions)
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def make_covers(film_dir):
    film_json_path = os.path.join(film_dir, "film.json")
    if not os.path.exists(film_json_path):
        print(f"make-covers: film.json not found in {film_dir}")
        return

    with open(film_json_path, "r") as f:
        film = json.load(f)

    slug = film.get("name", os.path.basename(film_dir))
    title = slug.replace("-", " ").title()

    # Look for STORYBOARD.md or BRIEF.md for custom title if available
    brief_path = os.path.join(film_dir, "BRIEF.md")
    if os.path.exists(brief_path):
        with open(brief_path, "r") as f:
            for line in f:
                if line.startswith("# "):
                    title = line.replace("#", "").strip()
                    break

    # Look for mascot image
    mascot_candidates = [
        os.path.join(film_dir, "assets", "mascot", "poses", "present.png"),
        os.path.join(film_dir, "assets", "mascot", "poses", "idle.png"),
        os.path.join(film_dir, "assets", "mascot", "originals", "present.png"),
    ]
    mascot_path = next((p for p in mascot_candidates if os.path.exists(p)), None)
    mascot_img = Image.open(mascot_path).convert("RGBA") if mascot_path else None

    font_xl = get_font(72, bold=True)
    font_lg = get_font(52, bold=True)
    font_md = get_font(36, bold=True)
    font_sm = get_font(26, bold=False)
    font_tag = get_font(22, bold=True)

    # ==========================================
    # 1. 16:9 Thumbnail (1280x720)
    # ==========================================
    W1, H1 = 1280, 720
    t1 = Image.new("RGBA", (W1, H1), "#F6F2EA")
    d1 = ImageDraw.Draw(t1)

    # Floor grid
    for gy in range(480, H1, 40):
        d1.line([(0, gy), (W1, gy)], fill=(148, 194, 173, 50), width=2)
    for gx in range(40, W1, 60):
        top_x = int(W1 / 2 + (gx - W1 / 2) * 0.45)
        d1.line([(top_x, 480), (gx, H1)], fill=(148, 194, 173, 40), width=2)

    # Mascot on left
    if mascot_img:
        m1_h = 520
        m1_w = int(mascot_img.width * (m1_h / mascot_img.height))
        m1 = mascot_img.resize((m1_w, m1_h), Image.Resampling.LANCZOS)
        t1.paste(m1, (40, 200), m1)

    # Main Headline Card on right
    cw1, ch1 = 780, 270
    cx1, cy1 = 450, 70

    # Soft drop shadow
    s1 = Image.new("RGBA", (W1, H1), (0, 0, 0, 0))
    s1_d = ImageDraw.Draw(s1)
    s1_d.rounded_rectangle([cx1 + 4, cy1 + 14, cx1 + cw1 - 4, cy1 + ch1 + 14], radius=32, fill=(11, 30, 63, 30))
    s1 = s1.filter(ImageFilter.GaussianBlur(16))
    t1 = Image.alpha_composite(t1, s1)
    d1 = ImageDraw.Draw(t1)

    # Card body
    d1.rounded_rectangle([cx1, cy1, cx1 + cw1, cy1 + ch1], radius=28, fill="#FFFFFF", outline="#ECE5D8", width=3)
    d1.text((cx1 + 36, cy1 + 24), "TECH EXPLANASYON", font=font_tag, fill="#B8500A")

    # Title lines (word wrap)
    words = title.split()
    line1, line2 = "", ""
    for w in words:
        if len(line1 + " " + w) <= 22:
            line1 = (line1 + " " + w).strip()
        else:
            line2 = (line2 + " " + w).strip()

    d1.text((cx1 + 36, cy1 + 60), line1.upper(), font=font_xl, fill="#0B1E3F")
    if line2:
        d1.text((cx1 + 36, cy1 + 140), line2.upper(), font=font_xl, fill="#2563EB")

    # Brand badge bottom right
    d1.rounded_rectangle([cx1 + 36, cy1 + ch1 - 50, cx1 + 280, cy1 + ch1 - 16], radius=8, fill="#F0FDF4")
    d1.text((cx1 + 50, cy1 + ch1 - 46), "60-SECOND DEEP DIVE", font=font_tag, fill="#166534")

    # Save Thumbnail
    thumb_path = os.path.join(film_dir, "THUMBNAIL.png")
    t1.convert("RGB").save(thumb_path, "PNG", optimize=True)
    print(f"make-covers: saved {thumb_path} (1280x720)")

    # ==========================================
    # 2. 9:16 TikTok / Shorts Cover (1080x1920)
    # ==========================================
    W2, H2 = 1080, 1920
    t2 = Image.new("RGBA", (W2, H2), "#F6F2EA")
    d2 = ImageDraw.Draw(t2)

    # Dot grid
    for gy in range(40, H2, 40):
        for gx in range(40, W2, 40):
            d2.ellipse([gx-2, gy-2, gx+2, gy+2], fill=(229, 222, 201, 140))

    # Center card (TikTok Safe Zone between y=400 and y=1500)
    cw2, ch2 = 960, 680
    cx2 = (W2 - cw2) // 2
    cy2 = 560

    s2 = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    s2_d = ImageDraw.Draw(s2)
    s2_d.rounded_rectangle([cx2 + 6, cy2 + 20, cx2 + cw2 - 6, cy2 + ch2 + 20], radius=40, fill=(11, 30, 63, 35))
    s2 = s2.filter(ImageFilter.GaussianBlur(24))
    t2 = Image.alpha_composite(t2, s2)
    d2 = ImageDraw.Draw(t2)

    d2.rounded_rectangle([cx2, cy2, cx2 + cw2, cy2 + ch2], radius=36, fill="#FFFFFF", outline="#E5DEC9", width=4)
    d2.text((cx2 + 48, cy2 + 48), "TECH EXPLANASYON", font=font_tag, fill="#B8500A")
    d2.text((cx2 + 48, cy2 + 100), line1.upper(), font=font_xl, fill="#0B1E3F")
    if line2:
        d2.text((cx2 + 48, cy2 + 185), line2.upper(), font=font_xl, fill="#2563EB")

    # Mascot on TikTok cover
    if mascot_img:
        m2_h = 420
        m2_w = int(mascot_img.width * (m2_h / mascot_img.height))
        m2 = mascot_img.resize((m2_w, m2_h), Image.Resampling.LANCZOS)
        t2.paste(m2, ((W2 - m2_w) // 2, cy2 + 250), m2)

    # Save TikTok cover
    tiktok_path = os.path.join(film_dir, "TIKTOK-COVER.png")
    t2.convert("RGB").save(tiktok_path, "PNG", optimize=True)
    print(f"make-covers: saved {tiktok_path} (1080x1920)")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    make_covers(target_dir)
