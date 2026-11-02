#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering how-smartwatch-measures-heartbeat at 1080x1920 @ 60fps (Hardware GPU) ==="
node render-final.mjs "how-smartwatch-measures-heartbeat-1080p60"
echo ""
echo "=== Render complete: renders/how-smartwatch-measures-heartbeat-1080p60.mp4 ==="
