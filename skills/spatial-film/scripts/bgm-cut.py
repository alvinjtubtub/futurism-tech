"""Cuts a music bed to the film length on bar lines, optionally splicing in a later segment (the track's own
fill/outro) so the ending lands under the lockup. Times come from music-bars.py: t = first_beat + bar * bar_len.
Usage: python <skill>/scripts/bgm-cut.py <source> <out.wav> --len 60 --a START END [--b START END]
                                          [--xfade 0.04] [--fade-out 1.1]
Example (worked example): --a 11.3891 67.0618 --b 104.0791 108.48 --len 60  (A = bars 5..30, B = fill -> outro)."""
import argparse, subprocess

p = argparse.ArgumentParser()
p.add_argument('src'); p.add_argument('out')
p.add_argument('--len', type=float, required=True)
p.add_argument('--a', type=float, nargs=2, required=True)
p.add_argument('--b', type=float, nargs=2)
p.add_argument('--xfade', type=float, default=0.04)
p.add_argument('--fade-out', type=float, default=1.1)
a = p.parse_args()
tail = f'atrim=end={a.len},afade=t=in:st=0:d=0.02,afade=t=out:st={a.len - a.fade_out:.3f}:d={a.fade_out}[o]'
if a.b:
    fc = (f'[0:a]atrim=start={a.a[0]}:end={a.a[1]},asetpts=PTS-STARTPTS[a];'
          f'[0:a]atrim=start={a.b[0]}:end={a.b[1]},asetpts=PTS-STARTPTS[b];'
          f'[a][b]acrossfade=d={a.xfade}:c1=qsin:c2=qsin,{tail}')
else:
    fc = f'[0:a]atrim=start={a.a[0]}:end={a.a[1]},asetpts=PTS-STARTPTS,{tail}'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.src, '-filter_complex', fc, '-map', '[o]',
                '-ar', '48000', '-ac', '2', a.out], check=True)
d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.out],
                   capture_output=True, text=True).stdout.strip()
print(f'{a.out}: {d}s - check it with music-bars.py <out> <bpm> 0.0 (bar 0 should be a downbeat)')
