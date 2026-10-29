# STORYBOARD: How Starlink Actually Routes Data to Moving Satellites in Low-Earth Orbit
**Film Slug:** `how-starlink-routes-data`  
**Profile:** Tech Explanasyon (TE)  
**Presenter:** Carla (scale: 0.30, x: 245, y: 1540)  
**Visual Style:** Real authentic engineering cutaways, aerospace CAD diagrams, 960x600 hero viewports, active moving laser/radio waves.

---

### SCENE 1: The 27,000 km/h Satellite Problem (0:00 - 0:12)
- **Kicker:** ORBITAL KINETICS
- **Title:** 27,000 KM/H MOVING TARGET
- **Hero Visual (960x600):** Side-by-side or layered view of Earth's curved atmosphere with a Starlink satellite racing at 7.5 km/s (Mach 22), with an active ground terminal pointing upward.
- **Active Moving Effects:**
  - Fast-moving orbital velocity vector line with glowing particle contrail
  - Sweeping cyan radio beam locking onto the moving satellite
  - Live HUD badge showing `SPEED: 27,360 KM/H` and `ALTITUDE: 550 KM`

### SCENE 2: The LEO Advantage vs High Latency GEO (0:12 - 0:26)
- **Kicker:** ORBITAL MECHANICS
- **Title:** 550 KM (LEO) VS 35,786 KM (GEO)
- **Hero Visual (960x600):** Scale cutaway of Earth showing Geostationary Orbit (35,786 km away) with a huge 600ms latency ping delay vs Low-Earth Orbit (550 km) with a snappy 25ms ping wave.
- **Active Moving Effects:**
  - Pulsing electromagnetic signal traveling up and bouncing back (slow 600ms vs instant 25ms)
  - Concentric radar range rings expanding from Earth's surface
  - Dynamic latency bar comparison graph animating from 0 to 600ms

### SCENE 3: The 3-Minute Horizon Window (0:26 - 0:40)
- **Kicker:** PASSING WINDOW
- **Title:** 3 MINUTES BEFORE HORIZON CUTOFF
- **Hero Visual (960x600):** Earth sky dome with an orbital plane trajectory line. A satellite enters from 25° elevation, reaches peak zenith, and descends across the opposite horizon in 180 seconds.
- **Active Moving Effects:**
  - Satellite icon gliding across the curved sky arc
  - Active countdown timer HUD badge: `TIME-IN-VIEW: 02:59`
  - Radar sweep cone pivoting across the sky

### SCENE 4: Phased Array Beamforming Physics (0:40 - 0:56)
- **Kicker:** HARDWARE ARCHITECTURE
- **Title:** PHASED ARRAY: ZERO MOVING PARTS
- **Hero Visual (960x600):** Macro internal cutaway of the Starlink user terminal (Dishy McFlatface) showing the hexagonal PCB lattice of 1,000+ tiny copper patch micro-antennas.
- **Active Moving Effects:**
  - Expanding wavefront rings emanating from each individual micro-antenna
  - Constructive interference wave crest aligning into a concentrated 14 GHz pencil beam
  - The focused radio beam electronically steering across angles without physical tilt

### SCENE 5: Millisecond Satellite Handoff (0:56 - 1:10)
- **Kicker:** SEAMLESS TRANSITION
- **Title:** MICROSECOND SATELLITE HANDOFF
- **Hero Visual (960x600):** The user terminal dish simultaneously tracking Satellite A dipping toward the horizon while establishing a lock on rising Satellite B.
- **Active Moving Effects:**
  - Dual beam split: Red beam fading on Satellite A, vibrant green beam locking onto Satellite B
  - Zero-packet-loss buffer meter showing smooth 100% data throughput
  - Animated network packet stream smoothly shifting tracks

### SCENE 6: The Bent-Pipe Limitation (1:10 - 1:24)
- **Kicker:** TERRESTRIAL BACKBONE
- **Title:** BENT-PIPE & THE OCEAN DEAD ZONE
- **Hero Visual (960x600):** Global map showing a Starlink satellite reflecting data straight down to a terrestrial ground gateway radome connected to fiber cables, showing the 500km radius dead zone in mid-ocean.
- **Active Moving Effects:**
  - Pulsing signal bounce (Dish -> Satellite -> Gateway)
  - Ground station radome radar dish pulsing
  - Flashing red warning boundary over mid-ocean area showing "NO GROUND STATION IN RANGE"

### SCENE 7: Space Lasers (OISL) in Vacuum (1:24 - 1:40)
- **Kicker:** OPTICAL INTER-SATELLITE LINKS
- **Title:** SPACE LASERS: FASTER THAN FIBER
- **Hero Visual (960x600):** Extreme macro cutaway of a Starlink V2 satellite bus showing the optical laser transceiver firing a neon infrared laser across hundreds of kilometers of vacuum to another satellite.
- **Active Moving Effects:**
  - Glowing laser beam firing through space with collimated photonic wavefronts
  - Speed comparison callout: `LIGHT IN VACUUM: 300,000 KM/S` vs `LIGHT IN FIBER: 200,000 KM/S` (+47% speed advantage)
  - Live optic gimbal tracking reticle locking onto the peer satellite

### SCENE 8: The Dynamic Orbital Mesh (1:40 - 1:52)
- **Kicker:** AUTONOMOUS ROUTING
- **Title:** GLOBAL CONSTELLATION MESH
- **Hero Visual (960x600):** 3D globe surrounded by a dense shell of interconnected Starlink satellites, with laser lines connecting adjacent orbital planes in a self-healing mesh.
- **Active Moving Effects:**
  - Laser routing paths flashing across 5 satellite hops around the curvature of the Earth
  - Dynamic routing algorithm rerouting packets around an obstructed node
  - Real-time data stream flowing from New York to London via space laser hops

### SCENE 9: Call To Action & Closing Gate (1:52 - 2:04)
- **Kicker:** FUTURE OF CONNECTIVITY
- **Title:** SUBSEA CABLE VS SPACE LASERS?
- **Hero Visual (960x600):** Split comparison of deep sea undersea fiber optic cables on the ocean floor vs glowing Starlink laser constellation orbiting above the globe.
- **Active Moving Effects:**
  - Floating glowing question card
  - Rotating Starlink constellation ring
  - Carla presenter asking the engagement question and delivering verbatim sign-off:
    `"Follow me for more tech explained. See yah."`
