# Render how-starlink-routes-data on Mac (Apple Silicon GPU)

## One-Click Render
Double-click `render.command` in Finder (or run `./render.command` in Terminal).

## Direct CLI Command
```bash
npx --prefer-offline --yes hyperframes@0.8.117 render --fps 60 --browser-gpu --workers 6 -o renders/how-starlink-routes-data-1080p60.mp4
```

## Output
- Rendered MP4: `renders/how-starlink-routes-data-1080p60.mp4`
- Render log: `renders/how-starlink-routes-data-1080p60.log`

Once rendered, hand `renders/how-starlink-routes-data-1080p60.mp4` to Baet for the **Stage 8 word-sync proof** (`verify-render.mjs`) before uploading.
