# Platform canvases - rebuild specs (GHL, n8n, Zapier)

Load only when a film shows one of these builders. Ready-made HTML rebuilds of all three (fictional Northwind
Dental data) are in `<skill>/surfaces/` - copy them into `src/captures/` and re-skin the data instead of starting over.
Ground truth for any NEW platform: the user's own real screenshots of it; measure them, never draw from memory.
Real captures are reference only - never embed them or copy their node names (they hold real client work).
These are visual rebuilds for demonstration, with no logos and fictional data. GoHighLevel, n8n and Zapier are
trademarks of their owners.

## GoHighLevel workflow builder (2026)

- **Canvas:** `#f8f9fb` with a faint square grid, 1px lines `#eceef2` every 20px.
- **Action card:** 228 x 66, white, radius 8, border 1px `#e4e7ec`, shadow `0 1px 2px rgba(16,24,40,.06)`.
  Left icon tile 34 x 34, radius 6, tinted fill + colored glyph. Title 13px `#344054` regular, one or
  two lines. Grey "···" menu at the right edge.
  - Icon tints: blue (`#eff4ff` / `#155eef`) for find/condition/webhook/tag; green (`#ecfdf3` / `#067647`)
    for SMS, email, notifications; purple (`#f4f3ff` / `#6938ef`) for pipeline/opportunity ("list-plus" glyph).
- **Trigger card:** 228 wide, three zones. Header: green tile (clipboard) + title "Form submitted" 13px
  semibold `#079455` + subtitle grey truncated with "...". Divider. Filter line "Form is any of ...".
  Footer: copy + trash icons left, blue bar-chart icon + "Stats" right (`#155eef`).
- **Add new trigger:** card beside the trigger, dashed 1px `#84adff`, fill `#f5f8ff`, blue "+" and
  "Add new trigger" `#155eef`. Its connector joins the trigger's below them.
- **Connectors:** 1px `#d0d5dd`, square elbows with small rounded corners. Between every two nodes a
  white 18px "+" circle with a dashed `#d0d5dd` ring.
- **Find-opportunity split:** grey pill labels (fill `#eaecf0`, 12px `#344054`) "Opportunity Found" /
  "Opportunity Not Found" on each branch.
- **If/Else branch cards:** 228 x 62, white, radius 8, **3px bottom border `#7a5af8`**, centered
  purple branch glyph + bold title `#6938ef` ("Replied"), grey subtitle ("If "Reply" is ...").
  The fallback branch is titled "None" / "When none of the conditions are met".
- **END:** grey pill 44 x 22, fill `#e4e7ec`, "END" 11px `#475467`.
- No dark left sidebar or top bar in the capture: worked example captures the canvas only. In the browser
  viewport (before capture) show the builder top bar: "Back to Workflows", workflow name, tabs
  "Builder · Settings · Enrollment History · Execution Logs", a Draft/Publish toggle and a blue "Save".

## n8n editor (v1, light theme)

- **Canvas:** `#f5f5f5` with a dot grid, 1.5px dots `#cfcfcf` every 20px.
- **Node:** 100 x 100 square, white, radius 8, border 1.5px `#dcdfe6`. Glyph centered ~40px.
  Label **below** the node, 14px `#222` medium, centered; parameter subtitle 12px `#9a9a9a`
  ("combine", "manual", "GET: https://api.northwind...").
- **Trigger node:** D-shape (left side fully rounded, radius 36 on the left corners). A coral lightning
  bolt `#ff6d5a` sits just left of it.
- **Wide node** (AI / model): 200 x 80 rectangle, glyph left, title + grey subtitle right.
- **Handles:** white 12px circles, 1.5px `#b5b5b5` ring, centered on the left (input) and right (output)
  edges. Merge has two inputs labelled "Input 1" / "Input 2" (11px grey). Switch has outputs 0-3.
- **Connectors:** 1.5px `#b8b8b8` cubic beziers, small grey arrowhead at the input handle. Edge labels
  ("Kept", "true", "false") 11px grey on the line.
- **Glyph colors (core nodes only, no third-party logos):** Schedule clock teal `#14b8a6`, Webhook
  rose `#e8466a`, HTTP Request globe indigo `#4f46e5`, Merge teal `#22a5b5`, Split Out purple `#8b5cf6`,
  Edit Fields pen indigo `#4338ca`, If / Filter / Switch blue `#3b82f6`, Send Email slate envelope.
- **Chrome (viewport only):** top bar with workflow name left, "Editor | Executions" toggle center,
  Inactive switch + "Share" + "Save" right; coral `#ff6d5a` "Test workflow" button bottom center.

## Zapier editor (2026)

- **Canvas:** warm off-white `#f8f6f2` with a dot grid, 1.5px dots `#ddd8ce` every 16px.
- **Step card:** 245 x 58, fill `#fffdf9`, border 1px `#e6e1d6`, radius 6, soft shadow. Row 1: an app
  chip (1px `#e6e1d6` border, radius 4, 16px app glyph + app name 13px bold `#2d2e2e`) and a ⋮ kebab at
  the right. Row 2: "**1.** Catch Hook": bold step number + title 14px; unconfigured title is grey
  `#7a7a7a` ("Select the event").
- **Empty Action step:** same card with a 2px **dotted** `#2d2e2e` border; chip is a dark-grey filled
  pill with a bolt glyph "Action".
- **Warning:** olive outlined "!" circle `#9a8f2a` left of the chip on incomplete steps.
- **Connectors:** vertical **dashed** line `#5b4cdb` (purple), with a purple "+" centered between steps.
- **Paths:** chip with orange border + orange split glyph, text "Paths" (`#ff4f00`). Branch labels are
  pills with a 1.5px purple border `#6e60f0`: "Path A ⌄ ⋮". Horizontal purple rail joins the branches.
- **Apps used (Zapier's own, no third-party logos):** Webhooks (orange hook), Formatter, Filter,
  Paths, Email by Zapier, Delay.
- **Chrome (viewport only):** top bar with the Zap name and an orange `#ff4f00` "Publish" button.

## Fictional data per canvas

- **GHL - "New lead nurture":** Form submitted / "Form Submitted: Contact Us" / "Form is any of "Contact
  Us"" -> Add Tag: new-lead -> Wait 5 Minutes -> Send SMS to (555) 014-2290 -> Notify frontdesk@northwind.co
  -> If/Else "Replied?" -> [Replied] Create Opportunity: New patient + END · [None] Send Email:
  lead@northwind.co + Custom Webhook (key sk_live_4f...) + END.
- **n8n - "Appointment reminders":** Schedule Trigger -> Get Appointments (GET: https://api.northwind.co/...)
  + Get Patients -> Merge (combine) -> Split Out Appointments -> Edit Fields (manual) -> If (true/false)
  -> Send Reminder Email · Flag for Front Desk.
- **Zapier - "Review request":** 1. Webhooks · Catch Hook -> 2. Formatter · Text -> 3. Filter · Only
  continue if... -> 4. Paths · Split into paths -> Path A: 5. Email by Zapier · Send Outbound Email ·
  Path B: 6. Delay · Delay For.
