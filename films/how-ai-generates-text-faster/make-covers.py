#!/usr/bin/env python3
"""
Generate THUMBNAIL.png (1280x720) and TIKTOK-COVER.png (1080x1920)
for how-shazam-works.
"""
from PIL import Image
import os, sys

film_dir = os.path.dirname(os.path.abspath(__file__))
snap_dir = os.path.join(film_dir, "snapshots", "composite")

# We look for a composite frame showing Kape + Scene 1 hook radar
# Typically frame-01-at-*.png
candidates = [f for f in os.listdir(snap_dir) if f.startswith("frame-01-") and f.endswith(".png")]
if not candidates:
    candidates = [f for f in os.listdir(snap_dir) if f.endswith(".png")]

if not candidates:
    print("Error: No snapshots in snapshots/composite/", file=sys.stderr)
    sys.exit(1)

hook_snap = os.path.join(snap_dir, sorted(candidates)[0])
print(f"Using {hook_snap} as base cover frame...")

im_hook = Image.open(hook_snap)

# 1. 16:9 Thumbnail (1280x720)
thumb = im_hook.resize((1280, 720), Image.Resampling.LANCZOS)
thumb_path = os.path.join(film_dir, "THUMBNAIL.png")
thumb.save(thumb_path, "PNG", optimize=True)
print(f"Created {thumb_path} (1280x720)")

# 2. 9:16 Vertical TikTok Cover (1080x1920)
tiktok = Image.new("RGBA", (1080, 1920), "#F6F2EA")
center_crop = im_hook.crop((120, 80, 1800, 1020))
center_scaled = center_crop.resize((1080, 604), Image.Resampling.LANCZOS)
tiktok.paste(center_scaled, (0, 620))

cover_path = os.path.join(film_dir, "TIKTOK-COVER.png")
tiktok.convert("RGB").save(cover_path, "PNG", optimize=True)
print(f"Created {cover_path} (1080x1920)")
