# Phase 4 - Music bed + SFX cue sheet

Goal: a bed at the film's NATIVE tempo cut on bar lines (no time-stretch), and SFX that land on the picture.

## Music (HeyGen catalog, Windows-safe)

One-time auth: the user runs `npx hyperframes auth login` in their own terminal (it fails headless). It writes
`~/.heygen/credentials`; the scripts read it through media-use's REST helper - no `heygen` CLI needed (it has no
Windows build; don't install it in WSL).

```bash
node <skill>/scripts/music-search.mjs "minimal electronic beat, <BPM> bpm, clean modern tech, crisp percussion, product film" 40 6 58
<py> <skill>/scripts/music-analyze.py ".media/candidates/*.mp3"       # tempo, first beat, loudness shape
<py> <skill>/scripts/music-bars.py .media/candidates/<id>.mp3 <BPM> <first_beat>   # per-bar energy
```

- Search 2-3 phrasings, `minDuration` >= film length. Pick a track whose analyzed tempo IS the film BPM
  (b6dd7fc6 read 110.0). If none fits, change the film BPM before the storyboard locks, never stretch the track.
- From the bar map choose: film bar 0 = a track downbeat after the intro; a riser/drop landing on the biggest seam;
  the track's own fill -> outro spliced in under the lockup. Bar time = first_beat + bar x bar_len.
- librosa often breaks on NumPy 2.x (numba). Do not pip-fix it in a shared Python (it can clobber torch) - the
  numpy-only scripts are the replacement.

```bash
cp .media/candidates/<id>.mp3 assets/audio/source-<id>.mp3
<py> <skill>/scripts/bgm-cut.py assets/audio/source-<id>.mp3 assets/audio/bgm-edit.wav --len <TOTAL> --a <start> <end> [--b <start> <end>]
<py> <skill>/scripts/music-bars.py assets/audio/bgm-edit.wav <BPM> 0.0     # bar 0 must be a downbeat
```

## SFX

- Small palette, 6-9 sounds: click, tick (the click at lower volume), pop, whoosh, punch whoosh, impact, stamp,
  ping, keys burst. hyperframes-audio ships bundled click/pop/whoosh/impact/ping; fill the rest with
  `node <skill>/scripts/sfx-search.mjs "stamp=rubber stamp hit" "keys=mechanical keyboard typing burst"`.
- Trim long ones to a burst: `ffmpeg -y -ss 2 -t 0.7 -i keys.mp3 -af "afade=t=in:d=0.02,afade=t=out:st=0.55:d=0.15" keys-burst.mp3`.

## Cue sheet (`film.json` `sfx` + `cues`)

- `sfx`: name -> [file in assets/audio/sfx/, default volume]. Volumes 0.22-0.55 under a 0.62 bed.
- `cues`: `[scene, time, sfx, volume|null, [kFrom, kTo]?]`, time scene-local: seconds or `"4*b"`, `"6*b+0.05"`,
  `"2*b*k"` with a k range for repeats. Take times from the storyboard beats; clicks on the press beat, whooshes
  on camera legs, pops/stamps on landings. Keep two hits 60ms+ apart.
- `assemble.py` writes each cue with its real `data-duration` (ffprobe) and a free track lane. Without durations
  every cue "runs to the end" and floods `duplicate_audio_track` (worked example: 853 warnings -> 0).
