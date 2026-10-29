#!/usr/bin/env python3
"""
generate_starlink_visuals.py
Generates high-resolution 1376x768 (16:9) aerospace CAD/technical diagrams for Starlink scenes 2 to 9.
Pure vector/Pillow drawing with crisp anti-aliasing, glows, telemetry HUDs, and hardware cutaways.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = "films/how-starlink-routes-data/assets/images"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1376, 768

def get_font(size, bold=True):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

f_title = get_font(36, bold=True)
f_sub = get_font(22, bold=True)
f_label = get_font(18, bold=False)
f_mono = get_font(16, bold=True)
f_big = get_font(48, bold=True)

def draw_tech_grid(d, w, h):
    # Blueprint/CAD grid lines
    for x in range(0, w, 40):
        d.line([(x, 0), (x, h)], fill=(230, 238, 248, 255), width=1)
    for y in range(0, h, 40):
        d.line([(0, y), (w, y)], fill=(230, 238, 248, 255), width=1)
    # Corner registration marks
    m = 20
    for cx, cy in [(m, m), (w - m, m), (m, h - m), (w - m, h - m)]:
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(140, 165, 190, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(140, 165, 190, 255), width=2)

# ==========================================
# S02: LEO vs GEO Orbital Scale
# ==========================================
def make_s02():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Earth at bottom left
    earth_center = (-100, 950)
    earth_r = 700
    d.ellipse([earth_center[0] - earth_r, earth_center[1] - earth_r, earth_center[0] + earth_r, earth_center[1] + earth_r],
              fill="#E0F2FE", outline="#0284C7", width=4)
    # Atmosphere glow ring
    d.ellipse([earth_center[0] - earth_r - 25, earth_center[1] - earth_r - 25, earth_center[0] + earth_r + 25, earth_center[1] + earth_r + 25],
              outline="#38BDF8", width=3)
    d.text((120, 560), "EARTH SURFACE (SEA LEVEL)", font=f_sub, fill="#0369A1")

    # LEO Orbit ring (550 km)
    leo_r = earth_r + 140
    d.arc([earth_center[0] - leo_r, earth_center[1] - leo_r, earth_center[0] + leo_r, earth_center[1] + leo_r],
          start=-80, end=10, fill="#10B981", width=5)

    # Starlink satellite in LEO
    sx, sy = 480, 290
    d.line([(sx - 45, sy), (sx + 45, sy)], fill="#0F172A", width=8) # body
    d.rectangle([sx - 15, sy - 10, sx + 15, sy + 10], fill="#334155")
    # Solar panel array
    d.rectangle([sx + 45, sy - 20, sx + 130, sy + 20], fill="#0284C7", outline="#0F172A", width=2)
    for px in range(sx + 65, sx + 130, 20):
        d.line([(px, sy - 20), (px, sy + 20)], fill="#38BDF8", width=1)
    
    # LEO Badge
    d.rounded_rectangle([sx - 40, sy - 90, sx + 220, sy - 30], radius=8, fill="#ECFDF5", outline="#10B981", width=2)
    d.text((sx - 25, sy - 84), "LOW-EARTH ORBIT (LEO)", font=f_sub, fill="#065F46")
    d.text((sx - 25, sy - 58), "ALTITUDE: 550 KM  |  PING: 25 MS", font=f_mono, fill="#047857")

    # Ping wave lines down to earth
    for r in range(40, 200, 30):
        d.arc([sx - r, sy - r, sx + r, sy + r], start=90, end=170, fill="#10B981", width=3)

    # GEO Orbit at far right (35,786 km)
    gx, gy = 1150, 140
    d.arc([earth_center[0] - 1300, earth_center[1] - 1300, earth_center[0] + 1300, earth_center[1] + 1300],
          start=-75, end=0, fill="#EF4444", width=3)
    # GEO satellite
    d.line([(gx - 30, gy), (gx + 30, gy)], fill="#64748B", width=6)
    d.rectangle([gx - 60, gy - 15, gx - 30, gy + 15], fill="#64748B")
    d.rectangle([gx + 30, gy - 15, gx + 60, gy + 15], fill="#64748B")

    # GEO Badge
    d.rounded_rectangle([gx - 260, gy + 40, gx + 80, gy + 130], radius=8, fill="#FEF2F2", outline="#EF4444", width=2)
    d.text((gx - 245, gy + 48), "GEOSTATIONARY (GEO)", font=f_sub, fill="#991B1B")
    d.text((gx - 245, gy + 74), "ALTITUDE: 35,786 KM", font=f_mono, fill="#B91C1C")
    d.text((gx - 245, gy + 98), "HIGH LATENCY PING: 600+ MS", font=f_mono, fill="#EF4444")

    # Huge speed comparison callout
    d.rounded_rectangle([80, 80, 520, 200], radius=16, fill="#0B1E3F")
    d.text((110, 100), "ORBITAL DISTANCE & LATENCY", font=f_sub, fill="#38BDF8")
    d.text((110, 135), "LEO: 25ms  vs  GEO: 600ms", font=f_title, fill="#FFFFFF")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s02_leo_vs_geo_orbit_scale.jpg"), quality=95)
    print("OK: s02_leo_vs_geo_orbit_scale.jpg")

# ==========================================
# S03: 3-Minute Sky Dome Horizon Pass
# ==========================================
def make_s03():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Ground line & sky dome
    cx, cy = 688, 620
    r = 500
    d.arc([cx - r, cy - r, cx + r, cy + r], start=180, end=0, fill="#2563EB", width=4)
    # Degree angle ticks (15, 30, 45, 60, 75, 90)
    for deg in range(0, 181, 15):
        rad = math.radians(deg)
        x1 = cx - r * math.cos(rad)
        y1 = cy - r * math.sin(rad)
        x2 = cx - (r - 20) * math.cos(rad)
        y2 = cy - (r - 20) * math.sin(rad)
        d.line([(x1, y1), (x2, y2)], fill="#93C5FD", width=2)
        if deg in [25, 90, 155]:
            d.text((x1 + (20 if deg > 90 else -40), y1 - 25), f"{deg}°", font=f_mono, fill="#1E40AF")

    # Horizon cutoff mask
    d.rectangle([0, cy, W, H], fill="#F8FAFC")
    d.line([(0, cy), (W, cy)], fill="#64748B", width=4)
    d.text((60, cy + 20), "LOCAL HORIZON (25° ELEVATION MINIMUM CUTOFF)", font=f_sub, fill="#475569")

    # Dish at center
    dx, dy = cx, cy
    d.ellipse([dx - 35, dy - 15, dx + 35, dy + 5], fill="#0F172A")
    d.line([(dx, dy), (dx, dy - 30)], fill="#334155", width=6) # pole
    d.ellipse([dx - 50, dy - 55, dx + 50, dy - 35], fill="#E2E8F0", outline="#0F172A", width=3) # dish face
    d.text((dx - 60, dy + 25), "STARLINK DISH", font=f_sub, fill="#0F172A")

    # Satellite pass positions along arc
    pts = [
        (cx - int(r * math.cos(math.radians(25))), cy - int(r * math.sin(math.radians(25))), "00:00 - ACQUISITION"),
        (cx - int(r * math.cos(math.radians(55))), cy - int(r * math.sin(math.radians(55))), "01:00"),
        (cx - int(r * math.cos(math.radians(90))), cy - int(r * math.sin(math.radians(90))), "01:30 - ZENITH"),
        (cx - int(r * math.cos(math.radians(125))), cy - int(r * math.sin(math.radians(125))), "02:15"),
        (cx - int(r * math.cos(math.radians(155))), cy - int(r * math.sin(math.radians(155))), "03:00 - LOSS OF SIGNAL"),
    ]
    for px, py, label in pts:
        d.ellipse([px - 14, py - 14, px + 14, py + 14], fill="#0284C7", outline="#0369A1", width=3)
        d.line([(dx, dy - 45), (px, py)], fill=(56, 189, 248, 120), width=2)
        d.text((px - 50, py - 35), label, font=f_mono, fill="#0C4A6E")

    # Countdown badge at top right
    d.rounded_rectangle([W - 460, 60, W - 60, 200], radius=16, fill="#0B1E3F")
    d.text((W - 430, 80), "TRANSIT TIME IN VIEW", font=f_sub, fill="#38BDF8")
    d.text((W - 430, 115), "3 MINUTES", font=f_big, fill="#F59E0B")
    d.text((W - 430, 165), "VELOCITY: 7.5 KM/S (MACH 22)", font=f_mono, fill="#FFFFFF")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s03_starlink_sky_pass_arc.jpg"), quality=95)
    print("OK: s03_starlink_sky_pass_arc.jpg")

# ==========================================
# S04: Phased Array Hexagonal Lattice
# ==========================================
def make_s04():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Large Circular Dish Aperture Cutaway
    cx, cy = 480, 384
    rad = 310
    d.ellipse([cx - rad - 20, cy - rad - 20, cx + rad + 20, cy + rad + 20], fill="#F1F5F9", outline="#0F172A", width=8)
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill="#0284C7", outline="#0369A1", width=4)

    # Hexagonal grid of micro-antennas
    hex_r = 16
    for row in range(-11, 12):
        for col in range(-12, 13):
            hx = cx + col * 28 + (14 if row % 2 else 0)
            hy = cy + row * 24
            dist = math.hypot(hx - cx, hy - cy)
            if dist < rad - 30:
                # Copper patch antenna
                d.rectangle([hx - 7, hy - 7, hx + 7, hy + 7], fill="#FBBF24", outline="#B45309", width=1)
                # Central probe feed
                d.ellipse([hx - 2, hy - 2, hx + 2, hy + 2], fill="#0F172A")

    # Highlighting beam steering angle
    d.arc([cx - 100, cy - 100, cx + 100, cy + 100], start=-60, end=20, fill="#00E5FF", width=4)
    # Focused radio beam
    d.polygon([(cx, cy), (cx + 340, cy - 260), (cx + 390, cy - 210)], fill=(0, 229, 255, 60), outline="#00E5FF", width=2)
    d.line([(cx, cy), (cx + 365, cy - 235)], fill="#0284C7", width=4)

    # Info card on right
    rx = 850
    d.rounded_rectangle([rx, 100, rx + 460, 660], radius=16, fill="#0B1E3F")
    d.text((rx + 36, 140), "PHASED ARRAY ARCHITECTURE", font=f_sub, fill="#38BDF8")
    d.text((rx + 36, 180), "1,000+ PATCHES", font=f_title, fill="#FFFFFF")
    
    pts = [
        "• Hexagonal Micro-Antenna Lattice",
        "• Nanosecond Silicon Phase Delays",
        "• Constructive Wave Interference",
        "• Electronic Beam Steering",
        "• 0 Moving Mechanical Parts",
        "• Frequency: 10.7 - 14.5 GHz (Ku/Ka)",
    ]
    for idx, p in enumerate(pts):
        d.text((rx + 36, 250 + idx * 46), p, font=f_label, fill="#E2E8F0")

    d.rounded_rectangle([rx + 36, 560, rx + 424, 620], radius=8, fill="#065F46")
    d.text((rx + 60, 580), "BEAM ANGLE STEER: < 100 MICROSECONDS", font=f_mono, fill="#6EE7B7")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s04_phased_array_hex_lattice.jpg"), quality=95)
    print("OK: s04_phased_array_hex_lattice.jpg")

# ==========================================
# S05: Satellite Handoff Dual Beam
# ==========================================
def make_s05():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Earth arc
    d.arc([-200, 550, W + 200, 1600], start=200, end=340, fill="#0284C7", width=4)

    # Ground Dish
    dx, dy = 688, 540
    d.ellipse([dx - 50, dy - 20, dx + 50, dy + 10], fill="#E2E8F0", outline="#0F172A", width=3)
    d.line([(dx, dy), (dx, dy + 50)], fill="#334155", width=8)

    # Outgoing Satellite A (Left)
    ax, ay = 250, 180
    d.rectangle([ax - 40, ay - 15, ax + 40, ay + 15], fill="#64748B", outline="#0F172A", width=2)
    d.rectangle([ax - 90, ay - 25, ax - 40, ay + 25], fill="#0284C7")
    d.rectangle([ax + 40, ay - 25, ax + 90, ay + 25], fill="#0284C7")
    d.line([(dx, dy - 10), (ax, ay + 10)], fill=(239, 68, 68, 160), width=3) # fading red link
    
    d.rounded_rectangle([ax - 130, ay + 45, ax + 130, ay + 105], radius=8, fill="#FEF2F2", outline="#EF4444", width=2)
    d.text((ax - 110, ay + 52), "SATELLITE A (SETTING)", font=f_sub, fill="#991B1B")
    d.text((ax - 110, ay + 78), "ELEVATION: 24° -> DISCONNECT", font=f_mono, fill="#DC2626")

    # Incoming Satellite B (Right)
    bx, by = 1120, 180
    d.rectangle([bx - 40, by - 15, bx + 40, by + 15], fill="#0F172A", outline="#10B981", width=3)
    d.rectangle([bx - 90, by - 25, bx - 40, by + 25], fill="#10B981")
    d.rectangle([bx + 40, by - 25, bx + 90, by + 25], fill="#10B981")
    d.line([(dx, dy - 10), (bx, by + 10)], fill="#10B981", width=6) # active green link

    d.rounded_rectangle([bx - 130, by + 45, bx + 130, by + 105], radius=8, fill="#ECFDF5", outline="#10B981", width=2)
    d.text((bx - 110, by + 52), "SATELLITE B (RISING)", font=f_sub, fill="#065F46")
    d.text((bx - 110, by + 78), "ACQUIRED LOCK -> ACTIVE BEAM", font=f_mono, fill="#059669")

    # Top Central Telemetry Card
    d.rounded_rectangle([420, 50, 956, 170], radius=16, fill="#0B1E3F")
    d.text((450, 70), "SEAMLESS SATELLITE HANDOFF", font=f_sub, fill="#38BDF8")
    d.text((450, 105), "SWITCH TIME: < 1 MILLISECOND", font=f_title, fill="#10B981")
    d.text((450, 140), "PACKET LOSS: 0.00%  |  ZERO CALL DROPS", font=f_mono, fill="#FFFFFF")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s05_satellite_handoff_dual_beam.jpg"), quality=95)
    print("OK: s05_satellite_handoff_dual_beam.jpg")

# ==========================================
# S06: Bent-Pipe Routing vs Ocean Void
# ==========================================
def make_s06():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Land vs Ocean map cutaway
    d.rectangle([60, 480, 550, 720], fill="#DCFCE7", outline="#16A34A", width=3) # Land
    d.text((100, 660), "CONTINENTAL LANDMASS", font=f_sub, fill="#15803D")

    d.rectangle([550, 480, 1316, 720], fill="#E0F2FE", outline="#0284C7", width=3) # Ocean
    d.text((700, 660), "PACIFIC OCEAN (DEAD ZONE)", font=f_sub, fill="#0369A1")

    # Ground Gateway station (Radome dome) on land
    gx, gy = 300, 480
    d.ellipse([gx - 45, gy - 60, gx + 45, gy], fill="#F8FAFC", outline="#334155", width=3)
    d.line([(gx, gy), (gx, gy + 30)], fill="#334155", width=6)
    d.text((gx - 90, gy + 40), "TERRESTRIAL GATEWAY", font=f_sub, fill="#1E293B")
    d.text((gx - 90, gy + 65), "FIBER OPTIC BACKBONE", font=f_mono, fill="#64748B")

    # Satellite overhead on land
    sx1, sy1 = 300, 180
    d.rectangle([sx1 - 35, sy1 - 15, sx1 + 35, sy1 + 15], fill="#0F172A")
    d.line([(gx, gy - 50), (sx1, sy1)], fill="#10B981", width=4) # uplink/downlink

    # Bent pipe bounce wave
    d.arc([sx1 - 60, sy1 - 40, sx1 + 60, sy1 + 60], start=180, end=0, fill="#10B981", width=4)
    d.text((sx1 + 50, sy1 - 10), "BENT-PIPE BOUNCE", font=f_mono, fill="#047857")

    # Satellite over ocean
    sx2, sy2 = 980, 180
    d.rectangle([sx2 - 35, sy2 - 15, sx2 + 35, sy2 + 15], fill="#475569")
    
    # 500km radius circle showing lack of ground station
    r = 220
    d.ellipse([sx2 - r, sy2 + 180 - r, sx2 + r, sy2 + 180 + r], outline=(239, 68, 68, 120), width=3)
    d.text((sx2 - 120, sy2 + 170), "500 KM RANGE LIMIT", font=f_mono, fill="#EF4444")
    d.line([(sx2, sy2), (sx2, sy2 + 250)], fill=(239, 68, 68, 150), width=3)
    d.text((sx2 - 100, sy2 + 270), "X NO GROUND STATION", font=f_sub, fill="#DC2626")

    # Top Card
    d.rounded_rectangle([320, 40, 1056, 120], radius=16, fill="#0B1E3F")
    d.text((360, 60), "EARLY STARLINK V1.0: BENT-PIPE LIMITATION", font=f_sub, fill="#F59E0B")
    d.text((360, 85), "Signal MUST reflect directly to a ground station within 500km", font=f_label, fill="#E2E8F0")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s06_bent_pipe_ground_station.jpg"), quality=95)
    print("OK: s06_bent_pipe_ground_station.jpg")

# ==========================================
# S07: Space Lasers (OISL) in Vacuum
# ==========================================
def make_s07():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Left Satellite Optical Gimbal Head
    lx, ly = 240, 384
    d.rectangle([lx - 140, ly - 90, lx, ly + 90], fill="#1E293B", outline="#0F172A", width=4)
    # Optical turret cylinder
    d.ellipse([lx - 40, ly - 60, lx + 40, ly + 60], fill="#334155", outline="#00E5FF", width=3)
    # Collimating lens aperture
    d.ellipse([lx + 10, ly - 35, lx + 50, ly + 35], fill="#00E5FF")

    # Right Satellite Optical Receiver Head
    rx, ry = 1136, 384
    d.rectangle([rx, ry - 90, rx + 140, ry + 90], fill="#1E293B", outline="#0F172A", width=4)
    d.ellipse([rx - 40, ry - 60, rx + 40, ry + 60], fill="#334155", outline="#00E5FF", width=3)
    d.ellipse([rx - 50, ry - 35, rx - 10, ry + 35], fill="#00E5FF")

    # Intense glowing space laser beam across vacuum
    d.line([(lx + 30, ly), (rx - 30, ry)], fill=(0, 229, 255, 100), width=18)
    d.line([(lx + 30, ly), (rx - 30, ry)], fill=(125, 245, 255, 180), width=8)
    d.line([(lx + 30, ly), (rx - 30, ry)], fill="#FFFFFF", width=3)

    # Telemetry Badges
    d.rounded_rectangle([320, 90, 1056, 230], radius=16, fill="#0B1E3F")
    d.text((360, 115), "OPTICAL INTER-SATELLITE LINKS (OISL)", font=f_sub, fill="#00E5FF")
    d.text((360, 145), "LIGHT SPEED IN VACUUM: 300,000 KM/S", font=f_title, fill="#FFFFFF")
    d.text((360, 190), "47% FASTER THAN TERRESTRIAL FIBER OPTIC GLASS (200,000 KM/S)", font=f_mono, fill="#6EE7B7")

    # Distance Callout bottom
    d.rounded_rectangle([450, 520, 926, 620], radius=12, fill="#F0FDF4", outline="#10B981", width=3)
    d.text((490, 545), "SPACE LASER RANGE: 1,000+ KM", font=f_title, fill="#065F46")
    d.text((490, 585), "THROUGHPUT: 100 GBPS PER LINK  |  ZERO RESISTANCE IN VACUUM", font=f_mono, fill="#047857")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s07_space_laser_optical_gimbal.jpg"), quality=95)
    print("OK: s07_space_laser_optical_gimbal.jpg")

# ==========================================
# S08: Global Orbital Laser Mesh
# ==========================================
def make_s08():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # 3D Globe at center
    cx, cy = 688, 384
    gr = 240
    d.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill="#E0F2FE", outline="#0284C7", width=4)
    # Continents silhouette hints
    d.arc([cx - gr, cy - gr, cx + gr, cy + gr], start=-45, end=135, fill="#38BDF8", width=12)

    # Orbital laser mesh constellation ring
    or_r = 310
    num_sats = 16
    coords = []
    for i in range(num_sats):
        angle = i * (2 * math.pi / num_sats)
        sx = cx + int(or_r * math.cos(angle))
        sy = cy + int((or_r - 60) * math.sin(angle))
        coords.append((sx, sy))

    # Draw laser mesh crosslinks
    for i in range(num_sats):
        p1 = coords[i]
        p2 = coords[(i + 1) % num_sats]
        d.line([p1, p2], fill="#00E5FF", width=3)
        # Trans-orbital crosslink
        p3 = coords[(i + 4) % num_sats]
        d.line([p1, p3], fill=(0, 229, 255, 60), width=1)

    # Satellite nodes
    for idx, (sx, sy) in enumerate(coords):
        color = "#10B981" if idx in [2, 3, 4, 5, 6] else "#0284C7"
        d.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=color, outline="#0F172A", width=2)

    # Active dynamic routing path highlight (e.g., London to Tokyo)
    path = [coords[2], coords[3], coords[4], coords[5], coords[6]]
    for i in range(len(path) - 1):
        d.line([path[i], path[i + 1]], fill="#F59E0B", width=6)

    # HUD Card
    d.rounded_rectangle([80, 80, 520, 220], radius=16, fill="#0B1E3F")
    d.text((110, 105), "DYNAMIC ORBITAL ROUTING", font=f_sub, fill="#F59E0B")
    d.text((110, 135), "AUTONOMOUS MESH", font=f_title, fill="#FFFFFF")
    d.text((110, 175), "SHORTEST PATH VACUUM HOPS ACROSS GLOBE", font=f_mono, fill="#6EE7B7")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s08_orbital_laser_mesh_constellation.jpg"), quality=95)
    print("OK: s08_orbital_laser_mesh_constellation.jpg")

# ==========================================
# S09: Subsea Cables vs Space Lasers
# ==========================================
def make_s09():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Split screen line
    d.line([(W // 2, 0), (W // 2, H)], fill="#CBD5E1", width=4)

    # LEFT HALF: Subsea Cables (Dark Ocean Abyss)
    d.rectangle([40, 80, W // 2 - 20, 680], fill="#0F172A", outline="#1E293B", width=3)
    d.text((80, 120), "DEEP SEA FIBER CABLES", font=f_title, fill="#38BDF8")
    d.text((80, 165), "• 1.4 Million KM of Undersea Glass", font=f_label, fill="#94A3B8")
    d.text((80, 205), "• Speed: 200,000 km/s (Glass Refraction)", font=f_label, fill="#94A3B8")
    d.text((80, 245), "• Vulnerable to Anchors & Earthquakes", font=f_label, fill="#F87171")
    # Subsea cable graphic
    for y in range(400, 600, 40):
        d.arc([60, y - 100, W // 2 - 40, y + 100], start=30, end=150, fill="#0284C7", width=6)
    d.text((80, 620), "OCEAN FLOOR TRENCH", font=f_mono, fill="#0369A1")

    # RIGHT HALF: Space Laser Constellation
    d.rectangle([W // 2 + 20, 80, W - 40, 680], fill="#0B1E3F", outline="#1E293B", width=3)
    d.text((W // 2 + 60, 120), "STARLINK SPACE LASERS", font=f_title, fill="#00E5FF")
    d.text((W // 2 + 60, 165), "• 300,000 km/s in Pure Vacuum", font=f_label, fill="#6EE7B7")
    d.text((W // 2 + 60, 205), "• 47% Faster Global Transit", font=f_label, fill="#6EE7B7")
    d.text((W // 2 + 60, 245), "• Autonomous Orbital Re-routing", font=f_label, fill="#FDE047")
    # Space laser graphic
    d.line([(W // 2 + 80, 520), (W - 80, 380)], fill="#00E5FF", width=5)
    d.ellipse([W // 2 + 70, 510, W // 2 + 90, 530], fill="#10B981")
    d.ellipse([W - 90, 370, W - 70, 390], fill="#10B981")
    d.text((W // 2 + 60, 620), "LOW-EARTH ORBIT VACUUM", font=f_mono, fill="#00E5FF")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s09_subsea_cables_vs_lasers.jpg"), quality=95)
    print("OK: s09_subsea_cables_vs_lasers.jpg")

if __name__ == "__main__":
    make_s02()
    make_s03()
    make_s04()
    make_s05()
    make_s06()
    make_s07()
    make_s08()
    make_s09()
    print("ALL STARLINK TECHNICAL VISUALS GENERATED SUCCESSFULLY!")
