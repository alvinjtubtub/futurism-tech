#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering how-pasaload-changed-telecoms at 1080x1920 @ 60fps (Hardware GPU) ==="
node render-final.mjs "how-pasaload-changed-telecoms-1080p60"
echo ""
echo "=== Render complete: renders/how-pasaload-changed-telecoms-1080p60.mp4 ==="
