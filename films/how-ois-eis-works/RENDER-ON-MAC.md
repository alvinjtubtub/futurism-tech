# Render how-ois-eis-works on Mac (Apple Silicon GPU)

## One-Click Render
Double-click `render.command` in Finder (or run `./render.command` in Terminal).

## Direct CLI Command
```bash
npx --prefer-offline --yes hyperframes@0.8.117 render --fps 60 --browser-gpu --workers 6 -o renders/how-ois-eis-works-1080p60.mp4
```

## Output
- Rendered MP4: `renders/how-ois-eis-works-1080p60.mp4`
- Render log: `renders/how-ois-eis-works-1080p60.log`

Once rendered, hand `renders/how-ois-eis-works-1080p60.mp4` to Baet for the **Stage 8 word-sync proof** (`verify-render.mjs`) before uploading.
