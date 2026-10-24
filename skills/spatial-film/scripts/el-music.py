"""ElevenLabs Music. Key from env EL. Usage: python el-music.py <out.mp3> <length_ms> "<prompt>" """
import json, os, sys, urllib.request, urllib.error

body = json.dumps({"prompt": sys.argv[3], "music_length_ms": int(sys.argv[2]), "model_id": "music_v1",
                   "force_instrumental": True}).encode()
req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192", data=body,
    headers={"xi-api-key": os.environ["EL"], "Content-Type": "application/json"})
try:
    data = urllib.request.urlopen(req, timeout=600).read()
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:800]); sys.exit(1)
open(sys.argv[1], "wb").write(data)
print("ok", len(data), "bytes")
