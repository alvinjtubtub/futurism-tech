#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering how-nfc-works at 1080x1920 @ 60fps (Hardware GPU) ==="
node render-final.mjs "how-nfc-works-1080p60"
echo ""
echo "=== Render complete: renders/how-nfc-works-1080p60.mp4 ==="
