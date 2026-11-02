#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering how-liquid-thermometer-works at 1080x1920 @ 60fps (Hardware GPU) ==="
node render-final.mjs "how-liquid-thermometer-works-1080p60"
echo ""
echo "=== Render complete: renders/how-liquid-thermometer-works-1080p60.mp4 ==="
