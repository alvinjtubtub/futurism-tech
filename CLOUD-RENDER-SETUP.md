# GitHub Actions (Standard Free Tier) + Google Drive Setup

This setup offloads Stage 7 (`1080p60` video rendering) and Stage 8 (`ffprobe` + `faster-whisper` word-sync proof) from your MacBook to **GitHub Actions** ([`alvinjtubtub/futurism-tech`](https://github.com/alvinjtubtub/futurism-tech)) and delivers your verified upload pack directly to **Google Drive**.

---

## Why Use a Public Repo (or Release Repo) for 2 Videos/Day?
- **Private GitHub Repo (Free Tier):** Capped at **2,000 minutes/month**. Since CPU rendering on a 4-core GitHub runner takes ~35–40 minutes per 2-minute video, 2 videos/day (~60 videos/month) uses ~2,100–2,400 minutes/month (just hitting the cap).
- **Public GitHub Repo (Free Tier):** **Unlimited free minutes (100% $0)** on `ubuntu-latest` runners—easily handles 2, 5, or 10 videos every day without ever hitting a billing limit.

---

## 1. Your Connected Repositories & Google Drive Folders

- **GitHub Repository:** [github.com/alvinjtubtub/futurism-tech](https://github.com/alvinjtubtub/futurism-tech)
  - **Actions Workflow:** [github.com/alvinjtubtub/futurism-tech/actions](https://github.com/alvinjtubtub/futurism-tech/actions) (`.github/workflows/render-film.yml`)
- **Root Google Drive Pipeline Folder:** [Tech Explanasyon - Video Pipeline](https://drive.google.com/drive/folders/12IEJ33CU_AnlOhtFqpkMf3Z1z_H1c0si)
  - **[01-Audio-Intake](https://drive.google.com/drive/folders/1BZcjqcHBWL64o1CC26tjdIFMu8nwjqoz):** Drop your recorded ElevenLabs `vo.mp3` narration files here.
  - **[02-Render-Packages](https://drive.google.com/drive/folders/1Y4IoOTi40SOkpWwJqPI5iuikDkMT71Pm):** Holds packaged `<slug>-project.zip` backups ready for rendering.
  - **[03-Completed-Videos](https://drive.google.com/drive/folders/1z5082Iq5JgOC4vYgirMim9vOYMcUhDRe):** Receives your verified `<slug>-1080p60.mp4`, `render-proof.json`, `CAPTIONS.srt`, `UPLOAD-PACK.md`, `THUMBNAIL.png`, and `TIKTOK-COVER.png`.

---

## 2. Optional: Add Your Google Drive Token Secret for Direct Runner Uploads
The workflow (`.github/workflows/render-film.yml`) always saves your verified MP4 + upload pack as a **GitHub Actions Artifact** (`<slug>-verified-upload-pack`), and if you add an `RCLONE_GDRIVE_TOKEN` secret to your GitHub repo (`Settings -> Secrets and variables -> Actions -> New repository secret` on [alvinjtubtub/futurism-tech](https://github.com/alvinjtubtub/futurism-tech/settings/secrets/actions)), the runner also uploads the finished folder directly into **[03-Completed-Videos](https://drive.google.com/drive/folders/1z5082Iq5JgOC4vYgirMim9vOYMcUhDRe)**.
*(Even without the secret, Gemini can download the artifact or sync the files straight to your Google Drive using its built-in Drive tools!)*

---

## 3. How to Trigger a Cloud Render (2 Videos/Day)

Once your scenes pass Stage 5–6 Quality Gates, run one command:

```bash
node skills/kape-explainer/scripts/cloud-render.mjs --dir films/<slug>
```

### What Happens Automatically:
1. **Local Quality Gates & Packaging (Takes ~30s):**
   - Verifies `.hyperframes/gates-report.json` passed all 5 gates.
   - Runs `package-film.mjs` to create `CAPTIONS.srt`, verify `THUMBNAIL.png` & `TIKTOK-COVER.png`, and bundle `films/<slug>/package/<slug>-project.zip`.
2. **Git Push Dispatch to `alvinjtubtub/futurism-tech`:**
   - Commits and pushes `films/<slug>/package/<slug>-project.zip` and `film.json` to `main`, automatically triggering `.github/workflows/render-film.yml`.
3. **In the Cloud (GitHub Actions Runner):**
   - Installs Node 22, FFmpeg, Headless Chrome + Mesa Vulkan/SwiftShader libraries, `hyperframes@0.8.117`, and `faster-whisper` (cached across runs).
   - Renders `renders/<slug>-1080p60.mp4` at 60fps.
   - Runs `verify-render.mjs` (`ffprobe` + `faster-whisper` word-sync check against `vo-words.json` + scene midpoint frame pulls).
   - Publishes `<slug>-verified-upload-pack` to GitHub Artifacts and uploads to **[03-Completed-Videos](https://drive.google.com/drive/folders/1z5082Iq5JgOC4vYgirMim9vOYMcUhDRe)**.
