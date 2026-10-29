#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering how-starlink-routes-data at 1080x1920 @ 60fps (Hardware GPU) ==="
node render-final.mjs "how-starlink-routes-data-1080p60"
echo ""
echo "=== Render complete: renders/how-starlink-routes-data-1080p60.mp4 ==="
