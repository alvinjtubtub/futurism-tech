#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering how-ai-generates-text-faster at 1080x1920 @ 60fps (Hardware GPU) ==="
node render-final.mjs "how-ai-generates-text-faster-1080p60"
echo ""
echo "=== Render complete: renders/how-ai-generates-text-faster-1080p60.mp4 ==="
