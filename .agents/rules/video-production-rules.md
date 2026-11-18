# KAPE Pipeline — Production Rules & Guidelines (v2.1 "Built-for-Speed" Visual Storytelling & Explainer Format)

These rules are permanently enforced across all **Tech Explanasyon (TE)** video creation tasks in this workspace.

---

## 1. Immediate Script Provision & AI Studio Kira Voice Prompt
- **Rule:** Whenever Alvin posts, proposes, or selects a new topic, **immediately output the ready-to-copy-paste script** AND the **Google AI Studio Voice Style/Tone Prompt (for Kira)** in the chat response alongside the chapter/beat storyboard.
- **Language & Pacing Law (English-Dominant Fast-Paced Taglish):**
  - **85%–90% Crisp, Punchy English + 10%–15% Natural Tagalog Hooks/Expressions** (just like DYK Stories: short, high-velocity sentences built for speed, with authentic Pinoy phrases, quotes, and local color).
  - Sentences must be short, rhythmic, and punchy (5–12 words per sentence) so captions pop every 1.2–2.0 seconds.
- **Requirement:** Do NOT wait for Alvin to ask "Script" or prompt for the AI Studio tone separately. Always provide:
  1. **Copy-Paste Google AI Studio Tone/Style Prompt (Kira Voice)**
  2. **Copy-Paste Plain-Text Script (English-dominant fast-paced Taglish)**
  3. **Chapter & Visual Micro-Beat Storyboard**

---

## 2. "Built-for-Speed" 3-Zone Vertical Architecture (`1080×1920 @ 60fps`)
Every Tech Explanasyon film uses the **3-Zone DYK-Style Cinema-Window Layout** on the signature **Cream (`#F6F2EA`), Dark Navy (`#0B1E3F`), and Tech Blue (`#2563EB`)** palette:

### Zone 1 — Top Header, Chapter HUD & Segmented Progress Bar (`y: 0 – 650px`)
- **Cold-Open Hook Mode (Scene 1, first ~5–10s):**
  - Displays brand tag `● TECH EXPLANASYON · #<EP>` (`x: 60px, y: 416px`) and **massive stacked uppercase hook text** (`68px–86px` Poppins 700, `#0B1E3F` with `#2563EB` / `#DC2626` / `#D97706` emphasis words) centered at `y: 460–630px`, popping in on the spoken hook words.
- **Chapter HUD Mode (Scenes 2 to N-1, rendered via `m-brand.html` + `.dyk-chapter-row`):**
  - **Brand Row (`y: 416px`, `x: 60–1020px`):** Left shows `● TECH EXPLANASYON · #<EP>` (`24px` Poppins 700); Right shows category/story tag (`TRUE TECH STORY · DIALOGUE DRAMATISED` or `HOW IT WORKS · SCIENCE EXPLAINED`, `19px` Poppins 700, `#5B6478`).
  - **Chapter & Context Row (`y: 500px`, `x: 60–1020px`):**
    - Left: Chapter number + title (e.g., `1 · Bigger Scoops`, `2 · The Bottleneck`, `3 · The 160-Byte Trick` in `38px` Poppins 700, number in `#2563EB`, title in `#0B1E3F`).
    - Right: **Dynamic Context Pill** (`1999 · MANILA`, `STEP 2 · CONTROL CHANNEL`, `TODAY · 1.3B TEXTS`) inside a Dark Navy pill (`background: #0B1E3F; color: #FACC15; border-radius: 999px; padding: 10px 26px; font-size: 22px; font-weight: 700`).
  - **Segmented Timeline Progress Bar (`y: 606px`, `x: 60–1020px`, width `960px`):**
    - Horizontal progress bar with tick marks for each chapter/scene that fills smoothly in Tech Blue (`#2563EB`) with a glowing playhead dot from `0%` to `100%` across the film.

### Zone 2 — Center 16:9 Vector Stage (`y: 650 – 1250px`, `960×600px` `.dyk-stage-window`)
- **100% Pure 2D SVG / HTML+CSS Vector Animations (Zero AI Image Generation):**
  - Do **NOT** call AI image generators or use heavy photorealistic JPEGs.
  - Every scene is a rich 2D vector storytelling canvas using the **7 Signature Visual Storytelling Devices**:
    1. **Chapter Title Card Interstitials (`0.8s–1.2s`):** Clean chapter title card (`Chapter One · The Free Channel`) at chapter transitions.
    2. **Side-by-Side Split-Screen Comparisons:** Left vs. Right visual contrast (e.g., `Competitor` vs. `Our System`, `Voice Call ($)` vs. `Control Beacon (₱0)`, with sunburst multiplier callouts like `×2` or `100x`).
    3. **Chalkboard / Tally & Sliding Matrix Boards:** Chalkboards with animated tally marks (`||||`) or comparison boards where feature pills (`SPEED`, `COST`, `TASTE`, `SECURITY`) slide into the winning column with a green checkmark `✔`.
    4. **Grid Maps & Glowing Network Globes:** Clean 2D maps (Manila / Philippines / World globe) with dropping location pins, animated route paths, and expanding glowing nodes.
    5. **Expressive Flat 2D Characters + Dramatized Micro-Dialogue:** Round-headed 2D vector characters (inventors, engineers, customers, doctors, titos) with expressive eyes/glasses, paired with a colored **Speaker Pill** (`ENGINEER`, `CUSTOMER`, `TITO`, `DOCTOR`) above the caption when a line of dialogue is spoken.
    6. **Tactile Paper Props & Cutaways:** Envelopes sliding open to reveal checks/patents, notebook pages with handwritten formulas being underlined, or `FOR SALE` / `MYTH` signs tearing in half.
    7. **Hardware / Physics Cross-Section Cutaways:** Step-by-step animated pipes, signal waves, packets, and gauges with floating callout pills and angled rubber stamps (`MYTH`, `FACT`, `PATENTED`, `VERIFIED`).
- **Rapid Micro-Beat Pacing:**
  - Every scene (`10s–18s`) MUST contain **4 to 6 distinct visual beats** (a new prop, split-screen reveal, tally stroke, pin drop, character expression, or stamp landing every `1.5s – 2.5s`) synchronized to the narration word timestamps.

### Zone 3 — Bottom Center Punchy Captions & Speaker Pills (`y: 1260 – 1920px`)
- **No Carla Mascot (`m-kape` retired):** The bottom half is completely clean of presenter PNG sprites.
- **Centered Bold Captions (`y: 1350 – 1500px`, centered at `x: 540px`, width `940px`):**
  - Short, punchy **2 to 4 words per caption block** so viewers read at high speed.
  - All-caps `56px` Poppins 700, `#0B1E3F` with key emphasis words/numbers highlighted in **Tech Blue (`#2563EB`)** or **Amber/Red (`#D97706` / `#DC2626`)**.
  - **Speaker Pill (`y: 1300px`, centered):** Pops in above the caption whenever dramatized dialogue or a named quote is spoken (`CUSTOMER`, `FOUNDER`, `DOCTOR`, `ENGINEER`).

---

## 3. Safe Zones & Anti-Text-Overflow Laws
- **Rule:** All text elements must clear Facebook Reels / TikTok / Shorts UI overlays:
  - Top bar danger: `y: 0 – 140px`
  - Right rail danger: `x: 952 – 1080px, y: 860 – 1560px`
  - Bottom block danger: `y: 1560 – 1920px` (all captions stay above `y: 1500px`).
- **Typography CSS:** Never allow unintended clipping or overflow (`white-space: normal; overflow-wrap: break-word;`).

---

## 4. Animation & GSAP Rules
- **Rule:** Every tween MUST use `gsap.fromTo(target, { ...initial }, { ...final })`.
- **Constraint:** Never use `.from()` or `.to()` alone for spatial transforms or state transitions (`fromto-scan.py` must report `0` errors).
- **Seam Law:** Clean exit transition for all stage elements at `D - 0.35s` before the scene cut.
- **Frame Rate:** Locked to `60fps` with `force3D: true` on transforms.

---

## 5. Audio & DYK-Style Closing End Card
- **Audio Mastering:** All voiceover mastered to `-16.0 LUFS` / `-1.5 dBFS True Peak` at `48000Hz` stereo.
- **Closing Sequence (DYK-Style Full-Circle Callback + Follow End Card):**
  - End the narrative with a **full-circle visual callback** to Scene 1 (e.g., returning to the original workshop, first text message, or two small stores) followed by the **Bold Stacked End Card**:
    - Top line: Engagement question or `WHAT SHOULD WE EXPLAIN NEXT?`
    - Center hero text: `FOLLOW` / `TECH EXPLANASYON` (`#0B1E3F` + `#2563EB`)
    - Sub-line: `True tech stories & science, explained fast.`
