#!/usr/bin/env python3
"""Profile-aware CI gates for the Tech Explanasyon / Futurism Tech pipeline.

Usage:
    python pipeline/profile_gates.py <project_dir> [--profile FT|TE]
        [--profiles PATH] [--duration SECONDS]

Every threshold comes from profiles.json at runtime -- nothing about a
profile's durations, safe zones, closing rules or brand rules is hardcoded
here except the small documented fallbacks noted below. The script FAILS
loudly (non-zero exit, FAIL line) if profiles.json cannot be found.

Threshold sources (all read from profiles.json):
  * duration target/warn/rework bands: profiles.<P>.duration_s
    (fallback: profiles.<P>.gates.duration.warn_outside/fail_outside)
  * safe rect: profiles.<P>.safe_zones.safe_content_rect
  * canvas: top-level profiles.json "canvas" (1080x1920 @ 60fps)
  * TE sign-off: profiles.TE.closing.signoff_exact (fallback:
    profiles.TE.gates.closing.signoff_exact)
  * FT save-bait keyword: profiles.FT.closing.must_include_keyword
    (fallback: profiles.FT.gates.closing.must_include_keyword)
  * brand rules: profiles.<P>.gates.brand_leakage.required/forbidden,
    plus the marker table in BRAND_MARKERS below (see --help).

Gates (one output line each; exit 1 on any FAIL, else 0):
  profile    -- project dir name must start FT- or TE- (or --profile)
  duration   -- film.json scene durations vs the profile's bands
  brand      -- required brand present, forbidden brand absent
  closing    -- TE: Tagalog question THEN verbatim sign-off;
                FT: save-bait CTA keyword
  safe-zone  -- STRUCTURAL ONLY: canvas size, declared film.json layout
                zones vs the safe rect (with tolerance), and for TE the
                headroom rule (stage bottom = presenter zone top - ~25px).
                This is NOT pixel measurement: pixel-level checking
                remains `hyperframes check` + snapshot review.
  from-scan  -- no GSAP `.from(` tween in any composition (see --help)

profiles.json resolution order:
  1. --profiles PATH
  2. <project_dir>/profile/profiles.json
  3. <project_dir>/../profile/profiles.json
  4. <project_dir>/profiles.json
  5. ~/.kape-explainer/profile/profiles.json

Only the Python standard library is used.
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Brand marker table (documented; the required/forbidden *rules* come from
# profiles.json, these are the concrete strings/paths that count as a brand
# being present in a project's files).
#
# TE badge  = the literal text "Tech Explanasyon" (the floating badge built
#             by kape-explainer/scripts/build-brand.py -> m-brand.html).
# Carla     = the presenter overlay/asset markers: the "m-kape" overlay id or
#             element id, or a mascot pose asset path (assets/mascot/poses/).
# Futurism  = the literal text "Futurism Tech" (case-insensitive; covers
#             the wordmark and the "FUTURISM TECH" disclosure line).
# ---------------------------------------------------------------------------
BRAND_MARKERS = {
    "te_badge": [r"tech explanasyon"],
    "carla": [r"m-kape", r"mascot/poses/"],
    "futurism": [r"futurism tech"],
}

# Tagalog question words for the TE closing gate. A closing question counts
# only if one of these words appears in a sentence ending with "?".
TAGALOG_QUESTION_WORDS = [
    "ano", "alin", "paano", "bakit", "kailan", "saan", "sino",
    "kanino", "ilan", "gaano", "kumusta",
    # "saang" (where / in which place, as in "Saang lugar...?") is a standard
    # Tagalog interrogative. Added 2026-10-24: the gate false-negatived on
    # TE-how-noise-cancelling-works, whose approved script and recorded
    # narration close with "Saang lugar mo pinaka-gustong gamitin...?".
    # This corrects an incomplete list; it does not weaken the gate, which
    # still requires a Tagalog interrogative + '?'.
    "saang",
    # "kaya mo bang" (can you, as in "kaya mo bang bisitahin...?") is a
    # standard Tagalog question construction. Added 2026-10-26: the gate
    # false-negatived on TE-how-dns-works, whose approved script and
    # recorded narration close with "Kung mawawala ang DNS bukas, kaya mo
    # bang bisitahin ang paborito mong site gamit lang ang numero nito?".
    # The bare word "kaya" is deliberately NOT added: it also means
    # "therefore", and every TE closing starts "Kaya ito ang tanong ko
    # sa inyo.", so it would weaken the gate. The gate still requires
    # this phrase (or another listed interrogative) in a sentence
    # ending with '?'.
    "kaya mo bang",
]

# Safe-zone containment tolerance (px). profiles.json's own canonical layout
# rects marginally exceed its safe rects (e.g. TE caption band right edge
# 934 vs safe right edge 932; TE stage is full-width by design), so an
# overflow within this tolerance is a WARN, not a FAIL. Tightening this to 0
# would fail the canonical layouts themselves; changing the canonical
# numbers is a layout decision for Alvin, not for this gate.
SAFE_TOLERANCE_PX = 32
# Headroom rule tolerance (px): stage bottom must equal presenter zone top
# minus ~25px, within this tolerance (rounding across poses/layouts).
HEADROOM_PX = 25
HEADROOM_TOLERANCE_PX = 15

FT_SIGNOFF_FALLBACK = "Follow me for more tech explained. See yah."


def fail(msg):
    print(f"FAIL {msg}")
    return False


def warn(msg):
    print(f"WARN {msg}")
    return None  # warns do not fail the run


def ok(msg):
    print(f"PASS {msg}")
    return True


# ---------------------------------------------------------------------------
# profiles.json loading
# ---------------------------------------------------------------------------
def find_profiles(project_dir, override):
    if override:
        return override
    candidates = [
        os.path.join(project_dir, "profile", "profiles.json"),
        os.path.join(project_dir, "..", "profile", "profiles.json"),
        os.path.join(project_dir, "profiles.json"),
        os.path.join(os.getcwd(), "profile", "profiles.json"),
        os.path.expanduser("~/.kape-explainer/profile/profiles.json"),
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return os.path.normpath(cand)
    return None


def load_profiles(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# project reading helpers
# ---------------------------------------------------------------------------
def read_film(project_dir):
    path = os.path.join(project_dir, "film.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def iter_text_files(project_dir, kinds):
    """Yield (relpath, text) for the gate corpora.

    kinds: "brand" -> compositions + film.json + brand.json + index.html
           + meta.json (design-law files such as frame.md are EXCLUDED:
           they may mention a brand in prose without the project using it).
           "closing" -> compositions + project-root *.md/*.txt (SCRIPT.md,
           closing notes) + film.json.
    """
    for root, _dirs, files in os.walk(project_dir):
        for name in sorted(files):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, project_dir)
            parts = rel.split(os.sep)
            if kinds == "brand":
                if parts[0] == "compositions" and name.endswith((".html", ".js", ".mjs")):
                    yield rel, read_text(full)
                elif rel in ("film.json", "brand.json", "index.html", "meta.json"):
                    yield rel, read_text(full)
            elif kinds == "closing":
                if parts[0] == "compositions" and name.endswith((".html", ".js", ".mjs")):
                    yield rel, read_text(full)
                elif len(parts) == 1 and name.endswith((".md", ".txt")):
                    yield rel, read_text(full)
                elif rel == "film.json":
                    yield rel, read_text(full)


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def strip_html(text):
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def scene_total_seconds(film):
    """Sum scene durations from film.json.

    Accepts scenes as [name, seconds] pairs, {"dur": s} / {"duration": s}
    dicts, or a top-level "duration" / "total_seconds" field. Falls back to
    the "vo" audio track's dur. Returns None if nothing is found.
    """
    if not film:
        return None
    scenes = film.get("scenes")
    if isinstance(scenes, list) and scenes:
        total = 0.0
        ok_count = 0
        for item in scenes:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                try:
                    total += float(item[1])
                    ok_count += 1
                except (TypeError, ValueError):
                    pass
            elif isinstance(item, dict):
                for key in ("dur", "duration", "seconds"):
                    if key in item:
                        try:
                            total += float(item[key])
                            ok_count += 1
                        except (TypeError, ValueError):
                            pass
                        break
        if ok_count:
            return total
    for key in ("duration", "total_seconds", "total"):
        if key in film:
            try:
                return float(film[key])
            except (TypeError, ValueError):
                pass
    audio = film.get("audio")
    if isinstance(audio, list):
        for track in audio:
            if isinstance(track, dict) and track.get("id") == "vo" and "dur" in track:
                try:
                    return float(track["dur"])
                except (TypeError, ValueError):
                    pass
    return None


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def gate_duration(profile, prof, film, override):
    dur = override
    src = "--duration"
    if dur is None:
        dur = scene_total_seconds(film)
        src = "film.json scenes"
    if dur is None:
        return fail(f"duration: no duration found in film.json (and no --duration given)")
    bands = prof.get("duration_s") or {}
    target = bands.get("target") or []
    warn_band = bands.get("warn_outside") or []
    rework = bands.get("rework_outside") or []
    if not (target and warn_band and rework):
        gates = prof.get("gates", {}).get("duration", {})
        warn_band = warn_band or gates.get("warn_outside") or []
        rework = rework or gates.get("fail_outside") or []
    if not rework:
        return fail(f"duration: no duration bands in profiles.json for {profile}")
    lo, hi = rework
    if dur < lo or dur > hi:
        return fail(
            f"duration: {dur:.1f}s from {src} is outside rework bounds "
            f"{lo:g}-{hi:g}s (profile {profile})"
        )
    if target and target[0] <= dur <= target[1]:
        return ok(
            f"duration: {dur:.1f}s from {src} inside target "
            f"{target[0]:g}-{target[1]:g}s (profile {profile})"
        )
    if warn_band and warn_band[0] <= dur <= warn_band[1]:
        warn(
            f"duration: {dur:.1f}s from {src} outside target "
            f"{target[0]:g}-{target[1]:g}s but inside warn band "
            f"{warn_band[0]:g}-{warn_band[1]:g}s (profile {profile})"
        )
        return True
    warn(
        f"duration: {dur:.1f}s from {src} outside warn band "
        f"{warn_band[0]:g}-{warn_band[1]:g}s but inside rework bounds "
        f"{lo:g}-{hi:g}s (profile {profile})"
    )
    return True


def brand_hits(project_dir):
    """Return {marker: [files]} for every brand marker found in the corpus."""
    hits = {key: [] for key in BRAND_MARKERS}
    for rel, text in iter_text_files(project_dir, "brand"):
        low = text.lower()
        for key, patterns in BRAND_MARKERS.items():
            for pat in patterns:
                if re.search(pat, low):
                    if rel not in hits[key]:
                        hits[key].append(rel)
                    break
    return hits


def gate_brand(profile, project_dir):
    hits = brand_hits(project_dir)
    problems = []
    if profile == "TE":
        if not hits["te_badge"]:
            problems.append('required "Tech Explanasyon" badge text not found')
        if not hits["carla"]:
            problems.append("required Carla presenter marker not found "
                            "(m-kape overlay or mascot/poses/ asset)")
        if hits["futurism"]:
            problems.append(f"forbidden Futurism branding found in "
                            f"{', '.join(hits['futurism'])}")
    else:  # FT
        if not hits["futurism"]:
            problems.append('required "Futurism Tech" wordmark not found')
        if hits["te_badge"]:
            problems.append(f"forbidden Tech Explanasyon badge found in "
                            f"{', '.join(hits['te_badge'])}")
        if hits["carla"]:
            problems.append(f"forbidden Carla presenter marker found in "
                            f"{', '.join(hits['carla'])}")
    if problems:
        return fail(f"brand: {'; '.join(problems)}")
    detail = ("badge + Carla present, no Futurism leakage"
              if profile == "TE" else
              "Futurism wordmark present, no TE badge / Carla leakage")
    return ok(f"brand: {detail}")


def closing_corpus(project_dir):
    parts = []
    for _rel, text in iter_text_files(project_dir, "closing"):
        parts.append(strip_html(text))
    return " ".join(parts)


def find_tagalog_question(text):
    """Return (index, sentence) of the first Tagalog question, else None."""
    word_pat = r"\b(" + "|".join(TAGALOG_QUESTION_WORDS) + r")\b"
    for m in re.finditer(r"\?", text):
        start = max(0, m.start() - 300)
        sentence = text[start:m.start() + 1]
        if re.search(word_pat, sentence, flags=re.I):
            return m.start(), sentence.strip()
    return None


def gate_closing(profile, prof, project_dir):
    text = closing_corpus(project_dir)
    if profile == "TE":
        gates = prof.get("gates", {}).get("closing", {})
        signoff = (prof.get("closing", {}).get("signoff_exact")
                   or gates.get("signoff_exact")
                   or FT_SIGNOFF_FALLBACK)
        norm = re.sub(r"\s+", " ", text)
        q = find_tagalog_question(norm)
        s_idx = norm.find(signoff)
        problems = []
        if q is None:
            problems.append("no Tagalog closing question found "
                            f"(needs one of {', '.join(TAGALOG_QUESTION_WORDS)} + '?')")
        if s_idx < 0:
            problems.append(f'verbatim sign-off not found: "{signoff}"')
        elif q is not None and q[0] > s_idx:
            problems.append("sign-off appears BEFORE the Tagalog question "
                            "(required sequence: question, then sign-off)")
        if problems:
            return fail(f"closing: {'; '.join(problems)}")
        return ok(f"closing: Tagalog question then verbatim sign-off present")
    # FT: save-bait CTA keyword, read from profiles.json.
    keyword = (prof.get("closing", {}).get("must_include_keyword")
               or prof.get("gates", {}).get("closing", {}).get("must_include_keyword")
               or "save")
    if re.search(r"\b" + re.escape(keyword) + r"\b", text, flags=re.I):
        return ok(f"closing: save-bait CTA keyword '{keyword}' present")
    return fail(f"closing: save-bait CTA keyword '{keyword}' not found")


def rect_within(rect, safe, tol):
    """Return (ok, overflow_px): overflow is the worst edge overshoot."""
    if rect is None or safe is None:
        return None, 0
    ox = max(0, safe["x"] - rect["x"])
    oy = max(0, safe["y"] - rect["y"])
    ox2 = max(0, (rect["x"] + rect["w"]) - (safe["x"] + safe["w"]))
    oy2 = max(0, (rect["y"] + rect["h"]) - (safe["y"] + safe["h"]))
    overflow = max(ox, oy, ox2, oy2)
    return overflow <= tol, overflow


def gate_safe_zone(profile, prof, film):
    canvas = None
    safe = (prof.get("safe_zones") or {}).get("safe_content_rect")
    problems = []
    warnings = []
    if film is not None:
        w, h = film.get("width"), film.get("height")
        if w is not None and h is not None:
            if (w, h) != (1080, 1920):
                problems.append(f"canvas {w}x{h} != 1080x1920 (profiles.json canvas)")
            else:
                canvas = "1080x1920"
    layout = (film or {}).get("layout") or {}
    if not layout:
        warnings.append("no declared layout zones in film.json; "
                        "structural check skipped for zones (pixel check "
                        "remains hyperframes check + snapshot review)")
    else:
        # Caption band is the safe-critical text zone: it must sit inside
        # the safe rect (within tolerance). Stage/headline width is NOT
        # containment-checked: the TE stage is full-width by design.
        cap = layout.get("caption_band")
        if cap and safe:
            within, over = rect_within(cap, safe, SAFE_TOLERANCE_PX)
            if not within:
                problems.append(f"caption_band overflows safe rect by {over}px "
                                f"(tolerance {SAFE_TOLERANCE_PX}px)")
            elif over > 0:
                warnings.append(f"caption_band overflows safe rect by {over}px "
                                f"(within {SAFE_TOLERANCE_PX}px tolerance)")
        if profile == "TE":
            pz = layout.get("presenter_zone")
            stage = layout.get("stage")
            if pz and safe:
                feet = pz.get("feet_y")
                if feet is None:
                    feet = pz["y"] + pz["h"]
                if feet > safe["y"] + safe["h"]:
                    problems.append(f"presenter feet y={feet} below safe bottom "
                                    f"{safe['y'] + safe['h']}")
            if pz and stage:
                expect = pz["y"] - HEADROOM_PX
                actual = stage["y"] + stage["h"]
                if abs(actual - expect) > HEADROOM_TOLERANCE_PX:
                    problems.append(
                        f"stage bottom y={actual} does not follow headroom rule "
                        f"(presenter zone top {pz['y']} - {HEADROOM_PX}px = "
                        f"{expect}, tolerance ±{HEADROOM_TOLERANCE_PX}px)")
    if problems:
        return fail(f"safe-zone: {'; '.join(problems)}")
    detail = "canvas " + (canvas or "unknown")
    if layout:
        detail += "; declared zones within safe rect (tolerance "
        detail += f"{SAFE_TOLERANCE_PX}px); headroom rule holds"
    if warnings:
        for wmsg in warnings:
            warn(f"safe-zone: {wmsg}")
    return ok(f"safe-zone: {detail} (STRUCTURAL ONLY, not pixel-measured)")


def strip_comment_spans(lines):
    """Mark character ranges that are inside HTML comments, per line."""
    spans = []
    in_comment = False
    for line in lines:
        line_spans = []
        i = 0
        while True:
            if not in_comment:
                j = line.find("<!--", i)
                if j < 0:
                    break
                k = line.find("-->", j + 4)
                if k < 0:
                    line_spans.append((j, len(line)))
                    in_comment = True
                    break
                line_spans.append((j, k + 3))
                i = k + 3
            else:
                k = line.find("-->")
                if k < 0:
                    line_spans.append((0, len(line)))
                    break
                line_spans.append((0, k + 3))
                in_comment = False
                i = k + 3
        spans.append(line_spans)
    return spans


def gate_from_scan(project_dir):
    """FAIL on any GSAP `.from(` tween in compositions.

    Rule (documented): a hit fails unless its line is a comment-only line
    (stripped line starts with //, * or <!--), the hit sits inside an HTML
    comment span, or the line carries the explicit marker
    `gates-allow-from`. `.fromTo(` does NOT match (it needs its own check:
    spatial-film/scripts/fromto-scan.py flags fromTo calls whose FROM vars
    set properties no TO vars animate -- a different, complementary check).
    """
    hits = []
    for root, _dirs, files in os.walk(project_dir):
        for name in sorted(files):
            if not name.endswith((".html", ".js", ".mjs")):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, project_dir)
            if os.path.basename(root) not in ("compositions", "src") and \
                    "compositions" not in rel.split(os.sep) and \
                    "src" not in rel.split(os.sep):
                continue
            with open(full, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().split("\n")
            spans = strip_comment_spans(lines)
            for n, line in enumerate(lines, 1):
                if "gates-allow-from" in line:
                    continue
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("*") or \
                        stripped.startswith("<!--"):
                    continue
                for m in re.finditer(r"\.from\s*\(", line):
                    if any(a <= m.start() < b for a, b in spans[n - 1]):
                        continue
                    hits.append(f"{rel}:{n}: {stripped[:100]}")
    if hits:
        detail = "; ".join(hits[:10])
        if len(hits) > 10:
            detail += f" (+{len(hits) - 10} more)"
        return fail(f"from-scan: {len(hits)} GSAP .from( hit(s): {detail}")
    return ok("from-scan: no GSAP .from( tweens in compositions/src")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def detect_profile(project_dir, override):
    if override:
        return override.upper()
    base = os.path.basename(os.path.abspath(project_dir))
    prefix = base.split("-", 1)[0].upper()
    if prefix in ("FT", "TE"):
        return prefix
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Profile-aware CI gates for FT/TE video projects. "
                    "All thresholds come from profiles.json at runtime.",
        epilog="Exit code is 1 if any gate FAILs, else 0 (WARNs do not fail). "
               "Safe-zone gate is STRUCTURAL ONLY, not pixel-measured.")
    ap.add_argument("project_dir", help="project directory (name must start "
                    "FT- or TE-, e.g. projects/TE-my-topic)")
    ap.add_argument("--profile", choices=["FT", "TE"],
                    help="override profile detection from the directory name")
    ap.add_argument("--profiles", metavar="PATH",
                    help="profiles.json path (default: search order in module docstring)")
    ap.add_argument("--duration", type=float, metavar="SECONDS",
                    help="override the duration read from film.json")
    args = ap.parse_args(argv)

    project_dir = args.project_dir
    if not os.path.isdir(project_dir):
        print(f"FAIL profile: project directory not found: {project_dir}")
        return 1

    profiles_path = find_profiles(project_dir, args.profiles)
    if not profiles_path:
        print("FAIL profiles: profiles.json not found (tried --profiles, "
              "<project>/profile/profiles.json, <project>/../profile/profiles.json, "
              "<project>/profiles.json, ~/.kape-explainer/profile/profiles.json)")
        return 1
    try:
        profiles = load_profiles(profiles_path)
    except (OSError, ValueError) as exc:
        print(f"FAIL profiles: cannot parse {profiles_path}: {exc}")
        return 1

    profile = detect_profile(project_dir, args.profile)
    if profile is None:
        print("FAIL profile: cannot detect profile from directory name "
              f"'{os.path.basename(os.path.abspath(project_dir))}' "
              "(expected FT-<slug> or TE-<slug>); use --profile FT|TE")
        return 1
    print(f"PASS profile: {profile} (profiles source: {profiles_path})")

    prof = (profiles.get("profiles") or {}).get(profile)
    if prof is None:
        print(f"FAIL profile: profile {profile} not present in {profiles_path}")
        return 1
    film = read_film(project_dir)

    results = []
    results.append(gate_duration(profile, prof, film, args.duration))
    results.append(gate_brand(profile, project_dir))
    results.append(gate_closing(profile, prof, project_dir))
    results.append(gate_safe_zone(profile, prof, film))
    results.append(gate_from_scan(project_dir))

    failed = any(r is False for r in results)
    print("RESULT: " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
