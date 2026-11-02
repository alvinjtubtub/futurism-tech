# STORYBOARD: How Your Watch Measures Your Heartbeat with Light
**Film Slug:** `how-smartwatch-measures-heartbeat`  
**Profile:** Tech Explanasyon (TE)  
**Presenter:** Carla (scale: 0.30, x: 245, y: 1540)  
**Visual Style:** Real medical-grade engineering cutaways, optical sensors, skin cross-sections, 960x600 hero viewports, active moving light pulses and blood flow dynamics.

---

### SCENE 1: Hook & Look Underneath Your Watch (0:00 - 0:14)
- **Kicker:** OPTICAL BIOSENSORS
- **Title:** PAANO NALALAMAN ANG TIBOK NG PUSO GAMIT ANG ILAW?
- **Voiceover:** *"Paano nalalaman ng smartwatch ang tibok ng puso mo, gamit lang ang ilaw? Look underneath your watch. Those green lights are part of a system called photoplethysmography, or PPG. Mahabang pangalan, pero simple ang idea: your pulse changes how much light comes back from your skin."*
- **Hero Visual (960x600):** Underside macro view of smartwatch ceramic sapphire backing with glowing green LEDs penetrating skin layers.
- **Active Moving Effects:**
  - Pulsing emerald green LED light cones (530 nm)
  - Concentric photon radiation ripples entering skin
  - Live HUD badge: `SYSTEM: PHOTOPLETHYSMOGRAPHY (PPG)` | `STATUS: ACTIVE SENSING`

### SCENE 2: The Emitter and the Photodiode (0:14 - 0:26)
- **Kicker:** OPTICAL ARCHITECTURE
- **Title:** LIGHT INTENSITY, NOT A PICTURE OF VEINS
- **Voiceover:** *"The watch shines light into your wrist. Some gets absorbed, and some scatters back toward a light detector called a photodiode. It measures light intensity, not a picture of your veins."*
- **Hero Visual (960x600):** Cross-section diagram showing green LED shooting light downwards, photons scattering through dermal tissue, and returning upward into central silicon photodiode.
- **Active Moving Effects:**
  - Downward green photon streams scattering through tissue
  - Returning scattered light rays bouncing up into the photodiode
  - Telemetry HUD: `SENSOR: SILICON PIN PHOTODIODE` | `MEASUREMENT: INTENSITY (LUX)`

### SCENE 3: The Heartbeat Pressure Wave (0:26 - 0:38)
- **Kicker:** HEMODYNAMICS
- **Title:** ARTERIAL PRESSURE WAVE & BLOOD VOLUME
- **Voiceover:** *"With each heartbeat, a pressure wave travels through your arteries. Blood volume in the small vessels under your skin rises and falls. Because blood absorbs green light, those changes affect the amount returning to the sensor."*
- **Hero Visual (960x600):** Cutaway of micro-arterioles in skin expanding and contracting as red blood cells surge with cardiac pressure waves.
- **Active Moving Effects:**
  - Arteriolar wall expanding and contracting in real-time rhythm
  - Pulsing pressure wave ripple traveling along the artery
  - Real-time pressure wave readout graph ($\text{mmHg}$)

### SCENE 4: The Absorption Cycle (0:38 - 0:50)
- **Kicker:** LIGHT ABSORPTION
- **Title:** MORE BLOOD = MORE GREEN LIGHT ABSORBED
- **Voiceover:** *"More blood generally means more green light absorbed, so less returns. Between pulses, the pattern reverses. Tiny changes, repeated over time, create a wave the watch can analyze."*
- **Hero Visual (960x600):** Split comparison: Systole (High blood volume -> Heavy green absorption -> Low return) vs Diastole (Low blood volume -> Less absorption -> High return).
- **Active Moving Effects:**
  - Synchronized absorption meter swinging from peak to trough
  - Returning photon counter fluctuating with cardiac cycles
  - Continuous PPG waveform scrolling smoothly across the bottom

### SCENE 5: Strobe Sampling (0:50 - 1:02)
- **Kicker:** SAMPLING RATE
- **Title:** LEDS FLASH FASTER THAN YOUR PULSE
- **Voiceover:** *"Hindi ibig sabihin na bawat flash ng ilaw ay isang heartbeat. The LEDs can flash much faster than your pulse. The watch takes many samples, and software looks for the repeating pulse pattern."*
- **Hero Visual (960x600):** High-speed stroboscopic timing diagram showing LED flashes at 100 Hz to 256 Hz capturing discrete sample points along a single 1 Hz heartbeat curve.
- **Active Moving Effects:**
  - High-frequency pulsing LED strobes
  - Sample dots appearing rapidly along the analog wave
  - Telemetry display: `LED STROBE: 128 Hz` | `SAMPLES PER SECOND: 128`

### SCENE 6: Pulse Frequency & BPM Math (1:02 - 1:14)
- **Kicker:** BEATS PER MINUTE
- **Title:** 1 PULSE/SEC = 60 BPM | 2 PULSES/SEC = 120 BPM
- **Voiceover:** *"If that pattern repeats once every second, that corresponds to sixty beats per minute. Twice every second would be one hundred twenty. These are examples, not target numbers."*
- **Hero Visual (960x600):** Dual digital frequency counter and animated heart icon comparing $1.0\text{ Hz}$ ($60\text{ BPM}$) resting rate vs $2.0\text{ Hz}$ ($120\text{ BPM}$) active workout rate.
- **Active Moving Effects:**
  - Animated pulsing heart beat synchronized with clock ticks
  - Dynamic frequency conversion bar calculating $\text{Frequency (Hz)} \times 60 = \text{BPM}$
  - Digital readout transitioning: `60 BPM (1 Hz)` -> `120 BPM (2 Hz)`

### SCENE 7: Real-World Challenges: Fit, Motion, & Cold (1:14 - 1:28)
- **Kicker:** REAL-WORLD ACCURACY
- **Title:** FIT, MOVEMENT, & COLD TEMPERATURE
- **Voiceover:** *"Pero may challenge. Moving your wrist or letting the watch slide can also change the light signal. Cold skin can reduce blood flow near the surface, making the pulse harder to detect. That is why fit, movement, and the algorithm affect the estimate."*
- **Hero Visual (960x600):** Three-panel engineering analysis: 1) Loose watch sliding producing light leaks, 2) Wrist motion noise with accelerometer compensation, 3) Vasoconstriction (narrowing vessels in cold skin).
- **Active Moving Effects:**
  - Animated watch tilt demonstrating optical gap and ambient light leakage
  - Vasoconstriction animation showing vessel constricting under cold temp ($15^\circ\text{C}$)
  - Adaptive algorithm filter smoothing the noisy signal into clean pulse line

### SCENE 8: Optical PPG vs Electrical ECG (1:28 - 1:38)
- **Kicker:** SENSOR TYPES
- **Title:** OPTICAL PPG (BLOOD PULSE) VS ELECTRICAL ECG
- **Voiceover:** *"And this optical pulse signal is different from an ECG, which measures electrical activity. Different sensors, different information."*
- **Hero Visual (960x600):** Side-by-side medical technology comparison: Optical PPG (smooth volumetric pulse curve from wrist) vs Clinical ECG (sharp P-Q-R-S-T electrical depolarization wave).
- **Active Moving Effects:**
  - Dual synchronized oscilloscopes: Smooth rounded PPG wave vs Sharp spiked ECG wave
  - Sensor callout: `PPG: PHOTONS & BLOOD VOLUME` vs `ECG: MICROVOLTS & MYOCARDIAL CHARGE`

### SCENE 9: Call to Action & Closing Gate (1:38 - 1:48)
- **Kicker:** WEARABLE TECH
- **Title:** NAGBABAGO BA ANG READING KAPAG MALUWAG?
- **Voiceover:** *"Ikaw, napansin mo na bang nagbabago ang reading kapag maluwag ang relo mo? Follow me for more tech explained. See yah."*
- **Hero Visual (960x600):** Close-up of smartwatch showing heart rate display with animated glowing sensor ring and engagement card.
- **Active Moving Effects:**
  - Floating glassmorphism comment card: `💬 I-SHARE ANG EXPERIENCE MO SA BABA!`
  - Carla presenter (scale: 0.30, home $x: 245$, feet $y: 1540$) with synchronized mouth flap and blinks
  - Verbatim closing sign-off: `"Follow me for more tech explained. See yah."`
