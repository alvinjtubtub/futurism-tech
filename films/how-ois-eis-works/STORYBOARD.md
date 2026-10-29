# Storyboard: OIS & EIS: Why Is Phone Video Shake-Free While Running?
**Profile:** Tech Explanasyon (`TE`) | **Format:** 9:16 Vertical ($1080 \times 1920\text{px}$) @ 60fps  
**Presenter:** Carla (scale: `0.30`, home $x: 245$, feet $y: 1540$)  
**Target Duration:** ~90s–100s | **Audio Gate:** Voiceover `-16.0 LUFS` / `-1.5 dBFS` True Peak

---

### Scene 1: The Running Shaky vs Smooth Split Test
- **Audio Cue:** `"Kapag tumatakbo ka habang nagvi-video gamit ang phone mo, bakit hindi masakit sa mata o parang lumilindol ang footage? Kung titingnan mo ang loob ng camera module, may physical suspension system at matinding algorithm na nagtutulungan para magmukhang lumulutang ang camera mo."`
- **Headline:** `BAKIT HINDI LUMILINDOL ANG VIDEO?` (52px, max-width 872px, wrap)
- **Kicker:** `REAL-TIME STABILIZATION ENGINE`
- **Technical Visual:** Dual-split live camera view of someone running:
  - Left panel: Jittery handheld camera simulation with red crosshairs swinging wildly, shake telemetry at `±14.2° Tilt`.
  - Right panel: Ultra-smooth stabilized glide footage with green locked horizon reticle and active `OIS + EIS ACTIVE` badge.
  - Center divider with glowing cyan scan line.
- **Presenter Pose:** `s01` - Pointing up right to compare the two test runs.

---

### Scene 2: Inside the Camera Bump: The Floating Lens Barrel
- **Audio Cue:** `"Paano gumagana ang OIS o Optical Image Stabilization? Sa loob ng camera bump, hindi nakadikit nang diretso ang lens. Sa totoo lang, lumulutang ito sa microscopic suspension springs at napapalibutan ng four-pole voice coil electromagnets o VCMs."`
- **Headline:** `OPTICAL IMAGE STABILIZATION (OIS)`
- **Kicker:** `PHYSICAL FLOATING HARDWARE`
- **Technical Visual:** High-resolution macro cutaway illustration of a smartphone multi-element lens barrel suspended inside a voice-coil motor (VCM) housing.
  - Four copper wire electromagnetic coils highlighted at 90-degree intervals.
  - Micro-spring suspension wires glowing in bright cyan.
  - Magnetic flux lines visualized via animated GSAP pulses.
- **Presenter Pose:** `s02` - Explaining / Open hands.

---

### Scene 3: The 1,000Hz Gyroscope & Physical Counter-Movement
- **Audio Cue:** `"Kapag kumalog ang kamay mo, agad itong nararamdaman ng microscopic MEMS gyroscope sa bilis na 1,000 times per second. Kung tumagilid ang phone pakanan, agad hihilahin ng electromagnets ang lens pakaliwa. Pisikal nitong kinakansela ang pag-alog sa bilis ng liwanag. Sa mga bagong flagship tulad ng iPhone, hindi lang lens ang gumagalaw—Sensor-Shift OIS ang gamit, kung saan mismong CMOS sensor ang lumulutang."`
- **Headline:** `1,000Hz MEMS GYRO & COUNTER-SHIFT`
- **Kicker:** `SPEED OF LIGHT COMPENSATION`
- **Technical Visual:**
  - Microscopic silicon MEMS gyroscope chip diagram measuring real-time angular velocity (Pitch, Yaw, Roll).
  - Dynamic telemetry dial showing `1,000 SAMPLES / SEC`.
  - Side-by-side motion physics demonstration: Phone chassis tilts $+3.5^\circ$ right $\rightarrow$ VCM electromagnets pull lens $-3.5^\circ$ left $\rightarrow$ light ray hits CMOS sensor dead center.
  - Callout badge highlighting `SENSOR-SHIFT OIS` with floating sensor package.
- **Presenter Pose:** `s03` - Thoughtful gesture shifting focus to internal microchips.

---

### Scene 4: The Physical Limit of Magnets
- **Audio Cue:** `"Pero may limitasyon ang OIS. Kaya lang nitong mag-compensate ng hanggang isa o dalawang degrees ng tilt. Kapag tumatakbo ka o tumatalon, kulang ang physical movement ng magnets. Dito na papasok ang EIS o Electronic Image Stabilization."`
- **Headline:** `PHYSICAL LIMIT: ±2° TILT MAXIMUM`
- **Kicker:** `HARDWARE BOUNDARY REACHED`
- **Technical Visual:** Cross-section showing the lens barrel hitting the physical chassis perimeter stops (`COLLISION ZONE`).
  - Red warning boundary line with angle meter pegging out at `> 5° PEAK SHAKE`.
  - Signal alert flashing `OIS LIMIT EXCEEDED`.
  - Transition arrow pointing toward the digital processing pipeline (EIS).
- **Presenter Pose:** `s04` - Warning / Halting gesture.

---

### Scene 5: EIS & The Virtual 20% Crop Margin
- **Audio Cue:** `"Ang EIS ay purong software at math. Sa halip na gamitin ang buong 4K sensor, magka-crop ang phone ng 10 hanggang 20 percent buffer margin sa paligid ng video. Isipin mo na may virtual camera window sa loob ng mas malaking canvas."`
- **Headline:** `ELECTRONIC STABILIZATION (EIS)`
- **Kicker:** `20% SENSOR BUFFER CROP`
- **Technical Visual:** Large 4K CMOS sensor representation ($3840 \times 2160\text{px}$) with an animated glowing viewport rectangle (the 80% active frame).
  - Darker buffer margin surrounding the frame with dimension callouts: `15% DIGITAL BUFFER MARGIN`.
  - When the phone jiggles, the active viewport smoothly slides within the larger sensor area, absorbing external movement.
- **Presenter Pose:** `s05` - Framing gesture (showing window within canvas).

---

### Scene 6: Motion Vectors & Homography Mesh Warping
- **Audio Cue:** `"Gamit ang gyro data at frame-by-frame motion vector analysis, hinuhulaan ng algorithm kung saan gagalaw ang susunod na frame. Ini-shift at wina-warp nito ang virtual window pixel-by-pixel para magmukhang steady ang horizon kahit nagtatalbog ang phone mo."`
- **Headline:** `MOTION VECTORS & MESH WARPING`
- **Kicker:** `FRAME-BY-FRAME PERSPECTIVE CORRECTION`
- **Technical Visual:** Real-time homography perspective grid ($8 \times 8$ mesh points) superimposed over a city running scene.
  - Motion vector arrows (quiver plot) calculating optical flow between Frame $N$ and Frame $N+1$.
  - Corner pinning and barrel distortion correction warping in real time to lock the horizon line perfectly horizontal.
- **Presenter Pose:** `s06` - Pointing to algorithmic mesh.

---

### Scene 7: Hybrid Stabilization: The Ultimate Glide
- **Audio Cue:** `"Kapag pinagsama ang OIS at EIS—tinatawag itong Hybrid Stabilization o Action Mode—smooth na cinematic glide ang resulta kahit mag-sprint ka sa hagdan."`
- **Headline:** `HYBRID STABILIZATION (ACTION MODE)`
- **Kicker:** `OIS HARDWARE + EIS ALGORITHM`
- **Technical Visual:** Exploded 3D dual-layer architecture:
  - Layer 1 (Bottom): Physical OIS cancels high-frequency micro-jitters ($> 50\text{Hz}$, small amplitude).
  - Layer 2 (Top): Digital EIS algorithm absorbs low-frequency heavy walking/running strides ($1-3\text{Hz}$, large amplitude).
  - Result output: Silky smooth steadycam glide curve shown on a real-time oscilloscope waveform graph.
- **Presenter Pose:** `s07` - Thumbs up / Confident stance.

---

### Scene 8: The Dark Side: Why EIS Struggles at Night
- **Audio Cue:** `"Pero may trade-off ito. Dahil naka-crop ang sensor at kailangan ng mabilis na shutter speed para maiwasan ang motion blur, madilim at grainy ang EIS video sa gabi. Kaya sa low light, madalas nanginginig o nagiging jelly ang video dahil nag-i-struggle ang algorithm."`
- **Headline:** `THE LOW-LIGHT JELLY EFFECT`
- **Kicker:** `SHUTTER SPEED & CROP PENALTY`
- **Technical Visual:** Macro comparison of a low-light sensor frame:
  - Shutter speed gauge dropping to $1/30\text{s}$ causing streaky motion blur across pixels.
  - The stabilized frame showing the notorious "jelly effect" / warping artifact around streetlights.
  - Technical diagnostic badge: `MOTION BLUR MISALIGNMENT`.
- **Presenter Pose:** `s08` - Puzzled / Explaining trade-off.

---

### Scene 9: Closing Gate & Community Prompt
- **Audio Cue:** `"Kaya ito ang tanong ko sa inyo: Naranasan mo na ba mag-video habang tumatakbo at napansin mo ba ang pagkakaiba ng may OIS sa wala? I-comment mo sa baba. Follow me for more tech explained. See yah."`
- **Headline:** `ANONG MAS GUSTO MO: OIS O EIS?`
- **Kicker:** `TECH EXPLANASYON COMMUNITY`
- **Technical Visual:** Clean branded end card featuring:
  - Carla in friendly waving pose.
  - Tech Explanasyon official wordmark and animated follow badge.
  - Interactive comment box mockup with glowing thumbs-up and reply icon.
- **Closing Gate Audit:**
  - Tagalog question ending in `?` using approved words: `"Naranasan mo na ba mag-video habang tumatakbo at napansin mo ba ang pagkakaiba ng may OIS sa wala?"`
  - Verbatim closing line: `"Follow me for more tech explained. See yah."`
- **Presenter Pose:** `s09` - Friendly wave & point to CTA.
