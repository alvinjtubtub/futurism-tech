#!/usr/bin/env python3
"""
generate_heartbeat_visuals.py
Generates high-resolution 1376x768 (16:9) medical & sensor engineering diagrams for all 9 scenes of
'How Your Watch Measures Your Heartbeat with Light'.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = "films/how-smartwatch-measures-heartbeat/assets/images"
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

f_title = get_font(34, bold=True)
f_sub = get_font(22, bold=True)
f_label = get_font(18, bold=False)
f_mono = get_font(16, bold=True)
f_big = get_font(44, bold=True)

def draw_tech_grid(d, w, h):
    for x in range(0, w, 40):
        d.line([(x, 0), (x, h)], fill=(230, 238, 248, 255), width=1)
    for y in range(0, h, 40):
        d.line([(0, y), (w, y)], fill=(230, 238, 248, 255), width=1)
    m = 20
    for cx, cy in [(m, m), (w - m, m), (m, h - m), (w - m, h - m)]:
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(140, 165, 190, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(140, 165, 190, 255), width=2)

# ==========================================
# S01: Smartwatch Underside & Glowing Green LED
# ==========================================
def make_s01():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Smartwatch circular ceramic case
    cx, cy = 688, 384
    cr = 280
    d.ellipse([cx - cr - 20, cy - cr - 20, cx + cr + 20, cy + cr + 20], fill="#0F172A", outline="#334155", width=6)
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill="#1E293B", outline="#475569", width=4)

    # Optical sensor cluster ring
    sr = 150
    d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill="#0B132B", outline="#10B981", width=3)

    # Dual Green LEDs (Left & Right)
    for lx in [cx - 85, cx + 85]:
        d.ellipse([lx - 25, cy - 25, lx + 25, cy + 25], fill="#10B981", outline="#34D399", width=3)
        # Intense glowing light cone
        for r in range(30, 90, 15):
            d.ellipse([lx - r, cy - r, lx + r, cy + r], outline=(16, 185, 129, int(180 - r * 1.8)), width=3)

    # Center Photodiode
    d.rectangle([cx - 30, cy - 30, cx + 30, cy + 30], fill="#0284C7", outline="#38BDF8", width=3)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill="#FFFFFF")

    # HUD Card Top Left
    d.rounded_rectangle([60, 60, 520, 210], radius=16, fill="#0B1E3F")
    d.text((90, 80), "OPTICAL BIOSENSOR ARRAY", font=f_sub, fill="#34D399")
    d.text((90, 115), "530nm GREEN LEDs", font=f_title, fill="#FFFFFF")
    d.text((90, 160), "PHOTOPLETHYSMOGRAPHY (PPG) EMITTER", font=f_mono, fill="#6EE7B7")

    # Callout bottom right
    d.rounded_rectangle([860, 560, 1316, 680], radius=16, fill="#F0FDF4", outline="#10B981", width=2)
    d.text((890, 585), "CENTRAL SILICON PHOTODIODE", font=f_sub, fill="#065F46")
    d.text((890, 620), "DETECTS SCATTERED REFLECTED LIGHT", font=f_mono, fill="#047857")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s01_watch_underside_green_led.jpg"), quality=95)
    print("OK: s01_watch_underside_green_led.jpg")

# ==========================================
# S02: Emitter & Photodiode Light Scattering
# ==========================================
def make_s02():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Watch base on top
    d.rectangle([100, 40, W - 100, 180], fill="#1E293B", outline="#0F172A", width=4)
    d.text((140, 65), "SMARTWATCH SENSOR HOUSING (SAPPHIRE GLASS)", font=f_sub, fill="#94A3B8")

    # LED Emitter at x: 420
    d.rectangle([370, 140, 470, 180], fill="#10B981", outline="#34D399", width=3)
    d.text((385, 150), "LED", font=f_mono, fill="#FFFFFF")

    # Photodiode Detector at x: 920
    d.rectangle([870, 140, 970, 180], fill="#0284C7", outline="#38BDF8", width=3)
    d.text((895, 150), "DETECTOR", font=f_mono, fill="#FFFFFF")

    # Skin Layers
    # Epidermis (180 to 260)
    d.rectangle([100, 180, W - 100, 260], fill="#FED7AA", outline="#FDBA74", width=2)
    d.text((140, 210), "EPIDERMIS (STRATUM CORNEUM)", font=f_label, fill="#C2410C")

    # Dermis (260 to 520)
    d.rectangle([100, 260, W - 100, 560], fill="#FDE68A", outline="#FCD34D", width=2)
    d.text((140, 280), "DERMIS (VASCULAR BED & CAPILLARIES)", font=f_label, fill="#B45309")

    # Subcutaneous tissue (560 to 720)
    d.rectangle([100, 560, W - 100, 720], fill="#FEF3C7")
    d.text((140, 620), "SUBCUTANEOUS TISSUE (FAT LAYER)", font=f_label, fill="#92400E")

    # Micro-arteriole in Dermis
    d.ellipse([580, 360, 780, 460], fill="#DC2626", outline="#991B1B", width=4)
    d.text((610, 400), "MICRO-ARTERIOLE", font=f_sub, fill="#FFFFFF")

    # Light Rays: Green light down from LED, scattering in arc up to detector
    d.line([(420, 180), (520, 380)], fill="#10B981", width=8) # incident ray
    d.line([(520, 380), (620, 410)], fill="#34D399", width=6)
    d.line([(680, 410), (820, 340)], fill=(56, 189, 248, 200), width=6) # scattered ray
    d.line([(820, 340), (920, 180)], fill="#0284C7", width=6) # returning ray to photodiode

    # Top Telemetry Banner
    d.rounded_rectangle([440, 60, 940, 130], radius=12, fill="#0B1E3F")
    d.text((465, 85), "PHOTON SCATTERING PATH (BANANA TRAJECTORY)", font=f_sub, fill="#38BDF8")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s02_photodiode_light_scattering.jpg"), quality=95)
    print("OK: s02_photodiode_light_scattering.jpg")

# ==========================================
# S03: Arterial Pressure Wave
# ==========================================
def make_s03():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Cross section of artery branching through wrist
    d.rectangle([120, 300, W - 120, 480], fill="#FEF2F2", outline="#FCA5A5", width=3)
    
    # Pulsing expansion wave (Artery profile with expanding pulse bulge)
    pts = [
        (120, 360), (320, 360), (450, 310), (600, 310), (730, 360),
        (W - 120, 360), (W - 120, 420), (730, 420), (600, 470),
        (450, 470), (320, 420), (120, 420)
    ]
    d.polygon(pts, fill="#EF4444", outline="#B91C1C", width=3)

    # Red blood cells flowing inside
    for rx in range(160, W - 160, 45):
        for ry in [370, 400, 430]:
            d.ellipse([rx - 12, ry - 7, rx + 12, ry + 7], fill="#991B1B")

    # Pressure wave callout
    d.rounded_rectangle([380, 120, 820, 240], radius=16, fill="#0B1E3F")
    d.text((410, 145), "CARDIAC PRESSURE WAVE", font=f_sub, fill="#F87171")
    d.text((410, 180), "ARTERIAL VOLUME PULSE", font=f_title, fill="#FFFFFF")

    # Bottom Pressure Graph
    d.rounded_rectangle([120, 540, W - 120, 700], radius=16, fill="#F8FAFC", outline="#CBD5E1", width=2)
    d.text((150, 560), "MICROVASCULAR PRESSURE PULSE (mmHg)", font=f_sub, fill="#0F172A")
    # Waveform curve
    wave_pts = []
    for x in range(150, W - 150):
        t = (x - 150) / 60
        y = 650 - int(50 * math.sin(t) * (math.exp(-((t % 3.14 - 1.5)**2))))
        wave_pts.append((x, y))
    d.line(wave_pts, fill="#EF4444", width=4)

    im.convert("RGB").save(os.path.join(OUT_DIR, "s03_arterial_pressure_wave.jpg"), quality=95)
    print("OK: s03_arterial_pressure_wave.jpg")

# ==========================================
# S04: Absorption Cycle (Systole vs Diastole)
# ==========================================
def make_s04():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Split screen line
    d.line([(W // 2, 0), (W // 2, H)], fill="#CBD5E1", width=4)

    # LEFT: SYSTOLE (Peak Blood Volume -> High Absorption -> Low Return)
    d.rectangle([60, 80, W // 2 - 30, 680], fill="#FEF2F2", outline="#EF4444", width=3)
    d.text((90, 110), "1. SYSTOLE (PULSE PEAK)", font=f_title, fill="#991B1B")
    d.text((90, 160), "• Heart beats & pumps blood volume surge", font=f_label, fill="#7F1D1D")
    d.text((90, 195), "• Arteries expand with red blood cells", font=f_label, fill="#7F1D1D")
    d.text((90, 230), "• HIGH GREEN LIGHT ABSORPTION", font=f_sub, fill="#DC2626")
    d.text((90, 265), "• LESS LIGHT SCATTERS TO SENSOR", font=f_sub, fill="#DC2626")

    # Visual vessel (Expanded)
    d.ellipse([140, 360, 460, 540], fill="#EF4444", outline="#B91C1C", width=4)
    d.text((220, 440), "MAX EXPANSION", font=f_title, fill="#FFFFFF")
    # Incoming green light blocked/absorbed
    d.line([(300, 310), (300, 360)], fill="#10B981", width=12)
    d.text((250, 580), "SENSOR READING: LOW INTENSITY", font=f_mono, fill="#991B1B")

    # RIGHT: DIASTOLE (Low Blood Volume -> Low Absorption -> High Return)
    d.rectangle([W // 2 + 30, 80, W - 60, 680], fill="#ECFDF5", outline="#10B981", width=3)
    d.text((W // 2 + 60, 110), "2. DIASTOLE (BETWEEN BEATS)", font=f_title, fill="#065F46")
    d.text((W // 2 + 60, 160), "• Blood drains back into venous system", font=f_label, fill="#064E3B")
    d.text((W // 2 + 60, 195), "• Arterioles relax and contract", font=f_label, fill="#064E3B")
    d.text((W // 2 + 60, 230), "• LOW GREEN LIGHT ABSORPTION", font=f_sub, fill="#059669")
    d.text((W // 2 + 60, 265), "• MORE LIGHT BOUNCES TO SENSOR", font=f_sub, fill="#059669")

    # Visual vessel (Contracted)
    d.ellipse([W // 2 + 200, 410, W // 2 + 400, 490], fill="#EF4444", outline="#B91C1C", width=4)
    d.text((W // 2 + 240, 440), "CONTRACTED", font=f_sub, fill="#FFFFFF")
    # High return light ray bouncing back up
    d.line([(W // 2 + 300, 410), (W // 2 + 300, 310)], fill="#0284C7", width=12)
    d.text((W // 2 + 180, 580), "SENSOR READING: HIGH INTENSITY", font=f_mono, fill="#047857")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s04_absorption_cycle_systole_diastole.jpg"), quality=95)
    print("OK: s04_absorption_cycle_systole_diastole.jpg")

# ==========================================
# S05: High-Frequency LED Strobe Sampling
# ==========================================
def make_s05():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Top Card
    d.rounded_rectangle([100, 50, W - 100, 180], radius=16, fill="#0B1E3F")
    d.text((140, 75), "HIGH-SPEED SAMPLING RATE", font=f_sub, fill="#38BDF8")
    d.text((140, 110), "LEDs FLASH 100+ TIMES PER SECOND (NOT 1 FLASH = 1 BEAT)", font=f_title, fill="#FFFFFF")

    # Continuous Pulse Wave (Analog Heartbeat 1 Hz / 60 BPM)
    d.rectangle([100, 230, W - 100, 680], fill="#F8FAFC", outline="#CBD5E1", width=3)
    d.text((140, 255), "CARDIAC PPG CURVE (1 BEAT EVERY 1.0 SEC)", font=f_sub, fill="#0F172A")

    # Draw analog curve
    pts = []
    for x in range(140, W - 140):
        t = (x - 140) / 140
        y = 480 - int(120 * (math.sin(t * 3.14) ** 3))
        pts.append((x, y))
    d.line(pts, fill="#EF4444", width=4)

    # Draw discrete stroboscopic sampling lines (128 Hz sampling representation)
    for x in range(160, W - 160, 24):
        # Sample stem line
        d.line([(x, 620), (x, 340)], fill=(16, 185, 129, 90), width=2)
        # Sample point on wave
        t = (x - 140) / 140
        sy = 480 - int(120 * (math.sin(t * 3.14) ** 3))
        d.ellipse([x - 5, sy - 5, x + 5, sy + 5], fill="#10B981")

    # Callout badge bottom right
    d.rounded_rectangle([860, 560, W - 140, 650], radius=12, fill="#065F46")
    d.text((885, 595), "128 DISCRETE SAMPLES / SEC", font=f_sub, fill="#6EE7B7")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s05_high_speed_strobe_sampling.jpg"), quality=95)
    print("OK: s05_high_speed_strobe_sampling.jpg")

# ==========================================
# S06: Pulse Frequency & BPM Math
# ==========================================
def make_s06():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Card 1: 1 pulse per second = 60 BPM
    d.rounded_rectangle([80, 100, 640, 640], radius=24, fill="#0B1E3F", outline="#1E293B", width=4)
    d.text((120, 140), "RESTING RATE", font=f_sub, fill="#38BDF8")
    d.text((120, 180), "60 BPM", font=f_big, fill="#10B981")
    d.text((120, 245), "1 Pulse Every 1.00 Second (1.0 Hz)", font=f_label, fill="#E2E8F0")

    # 1-second pulse wave box
    d.rectangle([120, 310, 600, 540], fill="#02142B", outline="#0284C7", width=2)
    p1 = []
    for x in range(120, 600):
        t = (x - 120) / 75
        y = 440 - int(60 * (math.sin(t) ** 2))
        p1.append((x, y))
    d.line(p1, fill="#10B981", width=4)
    d.text((140, 580), "FREQUENCY: 1.0 Hz × 60s = 60 BEATS/MIN", font=f_mono, fill="#6EE7B7")

    # Card 2: 2 pulses per second = 120 BPM
    d.rounded_rectangle([736, 100, 1296, 640], radius=24, fill="#0B1E3F", outline="#1E293B", width=4)
    d.text((776, 140), "ACTIVE WORKOUT RATE", font=f_sub, fill="#F59E0B")
    d.text((776, 180), "120 BPM", font=f_big, fill="#EF4444")
    d.text((776, 245), "2 Pulses Every 1.00 Second (2.0 Hz)", font=f_label, fill="#E2E8F0")

    # 2-second pulse wave box
    d.rectangle([776, 310, 1256, 540], fill="#02142B", outline="#F59E0B", width=2)
    p2 = []
    for x in range(776, 1256):
        t = (x - 776) / 38
        y = 440 - int(60 * (math.sin(t) ** 2))
        p2.append((x, y))
    d.line(p2, fill="#EF4444", width=4)
    d.text((796, 580), "FREQUENCY: 2.0 Hz × 60s = 120 BEATS/MIN", font=f_mono, fill="#FCA5A5")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s06_pulse_frequency_bpm_math.jpg"), quality=95)
    print("OK: s06_pulse_frequency_bpm_math.jpg")

# ==========================================
# S07: Real-World Challenges (Fit, Motion, Cold)
# ==========================================
def make_s07():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # 3-Panel Breakdown
    pw = 370
    # Panel 1: Loose Watch Fit
    d.rounded_rectangle([60, 100, 60 + pw, 640], radius=16, fill="#FEF2F2", outline="#EF4444", width=3)
    d.text((85, 130), "1. LOOSE FIT & LIGHT LEAKS", font=f_sub, fill="#991B1B")
    d.text((85, 175), "• Gap between watch & skin", font=f_label, fill="#7F1D1D")
    d.text((85, 210), "• Ambient sunlight floods sensor", font=f_label, fill="#7F1D1D")
    d.text((85, 245), "• Optical signal saturation", font=f_label, fill="#7F1D1D")
    # Diagram of tilted watch
    d.rectangle([110, 360, 380, 420], fill="#1E293B")
    d.line([(110, 470), (380, 470)], fill="#FDBA74", width=8) # skin
    d.text((120, 540), "ERRONEOUS DROPOUTS", font=f_mono, fill="#DC2626")

    # Panel 2: Motion Artifacts
    d.rounded_rectangle([490, 100, 490 + pw, 640], radius=16, fill="#FEF3C7", outline="#F59E0B", width=3)
    d.text((515, 130), "2. WRIST MOTION NOISE", font=f_sub, fill="#92400E")
    d.text((515, 175), "• Running rhythm matches cadence", font=f_label, fill="#78350F")
    d.text((515, 210), "• Watch sliding adds fake spikes", font=f_label, fill="#78350F")
    d.text((515, 245), "• Requires accelerometer filter", font=f_label, fill="#78350F")
    # Jitter wave
    d.line([(520, 420), (560, 370), (600, 450), (640, 360), (680, 440), (720, 380), (760, 430), (800, 400)], fill="#F59E0B", width=4)
    d.text((550, 540), "ADAPTIVE DSP FILTERING", font=f_mono, fill="#B45309")

    # Panel 3: Cold Skin Vasoconstriction
    d.rounded_rectangle([920, 100, 920 + pw, 640], radius=16, fill="#EFF6FF", outline="#3B82F6", width=3)
    d.text((945, 130), "3. COLD SKIN VASOCONSTRICTION", font=f_sub, fill="#1E40AF")
    d.text((945, 175), "• Low temperature constricts vessels", font=f_label, fill="#1E3A8A")
    d.text((945, 210), "• Blood diverted to body core", font=f_label, fill="#1E3A8A")
    d.text((945, 245), "• Microscopic signal amplitude", font=f_label, fill="#1E3A8A")
    # Narrow vessel diagram
    d.ellipse([1020, 410, 1180, 435], fill="#EF4444")
    d.text((980, 540), "REDUCED PERFUSION INDEX", font=f_mono, fill="#2563EB")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s07_real_world_challenges.jpg"), quality=95)
    print("OK: s07_real_world_challenges.jpg")

# ==========================================
# S08: Optical PPG vs Electrical ECG
# ==========================================
def make_s08():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Split screen line
    d.line([(W // 2, 0), (W // 2, H)], fill="#CBD5E1", width=4)

    # LEFT: Optical PPG
    d.rectangle([60, 80, W // 2 - 30, 680], fill="#ECFDF5", outline="#10B981", width=3)
    d.text((90, 110), "OPTICAL PPG (PULSE WAVE)", font=f_title, fill="#065F46")
    d.text((90, 160), "• Measures Mechanical Blood Volume", font=f_label, fill="#047857")
    d.text((90, 195), "• Green Light Absorption & Photodiode", font=f_label, fill="#047857")
    d.text((90, 230), "• Smooth rounded arterial pressure crest", font=f_label, fill="#047857")

    # PPG Waveform
    d.rectangle([90, 300, W // 2 - 60, 540], fill="#0B1E3F", outline="#10B981", width=2)
    ppg_pts = []
    for x in range(90, W // 2 - 60):
        t = (x - 90) / 45
        y = 440 - int(70 * (math.sin(t) ** 2) * (1 + 0.3 * math.sin(t * 2)))
        ppg_pts.append((x, y))
    d.line(ppg_pts, fill="#10B981", width=4)
    d.text((90, 580), "SENSOR: PHOTONS & HEMODYNAMICS", font=f_mono, fill="#065F46")

    # RIGHT: Electrical ECG
    d.rectangle([W // 2 + 30, 80, W - 60, 680], fill="#EFF6FF", outline="#3B82F6", width=3)
    d.text((W // 2 + 60, 110), "ELECTRICAL ECG (CARDIAC VOLTAGE)", font=f_title, fill="#1E40AF")
    d.text((W // 2 + 60, 160), "• Measures Myocardial Depolarization", font=f_label, fill="#1D4ED8")
    d.text((W // 2 + 60, 195), "• Electrodes Detect Cardiac Microvolts", font=f_label, fill="#1D4ED8")
    d.text((W // 2 + 60, 230), "• Sharp P-Q-R-S-T electrical spikes", font=f_label, fill="#1D4ED8")

    # ECG Waveform
    d.rectangle([W // 2 + 60, 300, W - 90, 540], fill="#0B1E3F", outline="#3B82F6", width=2)
    # Sharp P-Q-R-S-T spike
    ecg_base = 440
    ecg_pts = [
        (W // 2 + 80, ecg_base), (W // 2 + 150, ecg_base),
        (W // 2 + 180, ecg_base - 15), (W // 2 + 200, ecg_base), # P
        (W // 2 + 220, ecg_base + 10), # Q
        (W // 2 + 235, ecg_base - 110), # R (sharp peak)
        (W // 2 + 250, ecg_base + 25), # S
        (W // 2 + 270, ecg_base),
        (W // 2 + 310, ecg_base - 30), (W // 2 + 350, ecg_base), # T
        (W - 110, ecg_base)
    ]
    d.line(ecg_pts, fill="#38BDF8", width=4)
    d.text((W // 2 + 60, 580), "SENSOR: MICROVOLTS (μV) & ELECTRODES", font=f_mono, fill="#1E40AF")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s08_optical_ppg_vs_electrical_ecg.jpg"), quality=95)
    print("OK: s08_optical_ppg_vs_electrical_ecg.jpg")

# ==========================================
# S09: Smartwatch Heart Rate Display & CTA
# ==========================================
def make_s09():
    im = Image.new("RGBA", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(im)
    draw_tech_grid(d, W, H)

    # Large Modern Smartwatch Screen
    cx, cy = 688, 384
    w_width, w_height = 440, 520
    d.rounded_rectangle([cx - w_width // 2, cy - w_height // 2, cx + w_width // 2, cy + w_height // 2],
                        radius=48, fill="#000000", outline="#334155", width=8)

    # Screen UI
    d.text((cx - 160, cy - 190), "HEART RATE", font=f_sub, fill="#94A3B8")
    d.text((cx - 160, cy - 130), "72", font=get_font(96, bold=True), fill="#FFFFFF")
    d.text((cx + 10, cy - 80), "BPM", font=f_sub, fill="#EF4444")

    # Animated heart icon
    d.text((cx + 90, cy - 130), "❤️", font=get_font(48, bold=False), fill="#EF4444")

    # Scrolling green PPG line inside screen
    scr_pts = []
    for x in range(cx - 160, cx + 160):
        t = (x - (cx - 160)) / 25
        y = (cy + 60) - int(35 * (math.sin(t) ** 2))
        scr_pts.append((x, y))
    d.line(scr_pts, fill="#10B981", width=4)

    # Bottom Screen Telemetry
    d.text((cx - 160, cy + 140), "RESTING: 68 BPM  |  PEAK: 142", font=f_mono, fill="#64748B")

    # CTA Card at Bottom
    d.rounded_rectangle([280, 660, W - 280, 740], radius=16, fill="#0B1E3F")
    d.text((320, 685), "💬 I-COMMENT: NAPAPANSIN MO BA KAPAG MALUWAG ANG RELO MO?", font=f_sub, fill="#38BDF8")

    im.convert("RGB").save(os.path.join(OUT_DIR, "s09_smartwatch_heart_rate_cta.jpg"), quality=95)
    print("OK: s09_smartwatch_heart_rate_cta.jpg")

if __name__ == "__main__":
    make_s01()
    make_s02()
    make_s03()
    make_s04()
    make_s05()
    make_s06()
    make_s07()
    make_s08()
    make_s09()
    print("ALL 9 HEARTBEAT VISUALS SUCCESSFULLY GENERATED!")
