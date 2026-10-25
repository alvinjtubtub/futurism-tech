"""Master a narrated film's audio: voice to -16 LUFS / -1.5 dBTP, music bed sidechain-ducked under it.

usage (film root): <py> <skill>/scripts/master-audio.py --len 83.2 [--vo assets/audio/vo.mp3]
                   [--bed assets/audio/bgm-edit.wav] [--bed-gain -12]
Writes assets/audio/vo-master.wav and assets/audio/bgm-duck.wav and prints the loudness of each + the mix.
Why: one cloned-voice narration came in at -24 LUFS; a plain +8 dB lift clipped at +4.6 dBTP, loudnorm doesn't. The bed at
-12 dB + 5:1 sidechain sits ~17 dB under the voice and breathes up in the pauses. The final render measured -14.5 LUFS.
"""
import argparse, os, re, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("--len", type=float, required=True)
ap.add_argument("--dir", default=".")
ap.add_argument("--vo", default="assets/audio/vo.mp3")
ap.add_argument("--bed", default="assets/audio/bgm-edit.wav")
ap.add_argument("--bed-gain", type=float, default=-12)
a = ap.parse_args()

root = os.path.abspath(a.dir)
vo_input = a.vo if os.path.isabs(a.vo) or os.path.exists(a.vo) else os.path.join(root, a.vo)
bed_input = a.bed if os.path.isabs(a.bed) or os.path.exists(a.bed) else os.path.join(root, a.bed)

VO = os.path.join(root, "assets", "audio", "vo-master.wav")
BED = os.path.join(root, "assets", "audio", "bgm-duck.wav")
os.makedirs(os.path.join(root, "assets", "audio"), exist_ok=True)
os.makedirs(os.path.join(root, ".media"), exist_ok=True)

def ff(*x): subprocess.run(["ffmpeg", "-v", "error", "-y", *x], check=True)
def lufs(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i, pk = re.findall(r"I:\s+(-?[\d.]+) LUFS", o), re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)
    return f"{i[-1] if i else '?'} LUFS, peak {pk[-1] if pk else '?'} dBFS"

ff("-i", vo_input, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-ar", "48000", VO)
if a.bed and os.path.exists(bed_input):
    ff("-i", bed_input, "-i", VO, "-filter_complex",
       f"[0:a]aresample=48000,volume={a.bed_gain}dB[bed];[1:a]aresample=48000,apad[key];"
       "[bed][key]sidechaincompress=threshold=0.02:ratio=5:attack=25:release=400:makeup=1[o]",
       "-map", "[o]", "-t", str(a.len), "-ar", "48000", BED)
    mix_path = os.path.join(root, ".media", "mix-check.wav")
    ff("-i", VO, "-i", BED, "-filter_complex", "amix=inputs=2:normalize=0", "-t", str(a.len), mix_path)
    print(f"voice {lufs(VO)} | bed {lufs(BED)} | mix {lufs(mix_path)}")
    print('film.json: "audio": [{"id": "vo", "src": "assets/audio/vo-master.wav", ...}], "bgm": {"src": "assets/audio/bgm-duck.wav", "volume": 1}')
else:
    print(f"voice {lufs(VO)} | bed none (narration-only)")
    print('film.json: "audio": [{"id": "vo", "src": "assets/audio/vo-master.wav", ...}], "bgm": null')
