# Lift Plan PDF Generation Brief

## Objective
Generate 10 professional engineering-grade lift plan PDFs for JMR Lifting Solutions.
Each PDF must look like a real deliverable from a LEEA Appointed Person.

## Output Directory
`/home/user/workspace/jmr-lifting/lift-plans/pdfs/`

Filename pattern: `LP-01-vessel-lift.pdf`, `LP-02-wind-nacelle.pdf`, etc.

## PDF Structure (Each Plan — 10-12 pages)

### Page 1 — Cover
- JMR triangle logo (SVG converted or simple triangle drawn on canvas)
- "LIFT PLAN" title, big
- Project title (e.g., "Refinery Reactor Tandem Lift")
- Plan number: LP-YYYY-XXX
- Client (anonymized): "[CLIENT CONFIDENTIAL]"
- Location (anonymized): "[LOCATION CONFIDENTIAL — AFRICA]"
- Revision: "Rev 0 — SAMPLE"
- Date: current date
- Prepared by: "Muthuraj Jeyabal, LEEA Certified Appointed Person"
- Reviewed by: "JMR Lifting Engineering"
- Standards: "BS 7121 · LOLER 1998 · ASME B30"
- Footer: "SAMPLE DOCUMENT — For demonstration purposes. Actual project plans include site-specific data."

### Page 2 — Executive Summary / Scope
- Scope of work (3-4 lines)
- Key parameters table:
  | Parameter | Value |
  | Load weight (t) | ... |
  | Dimensions (L × W × H) | ... |
  | Lift radius (m) | ... |
  | Lift height (m) | ... |
  | Duration (est.) | ... |
- Critical risks (bullets)

### Page 3 — Load Data
- Load description
- Weight breakdown table (structural weight, contents, accessories, uncertainty %, total)
- Center of Gravity: X, Y, Z coordinates
- Lift points: location, sling angles
- Dimensional sketch (ASCII/simple drawn box with dims)

### Page 4 — Crane Selection & Configuration
- Selected crane model (real Liebherr/Manitowoc specs)
- Configuration: boom length, jib, counterweight
- Load chart reference: capacity at working radius
- Utilization: (load ÷ capacity) × 100 — must be < 85%
- Ground bearing pressure calculation
- Standing/pick radius

### Page 5 — Load Chart & Calculations
- Table: Radius (m) vs Capacity (t) at chosen boom config
- Working point highlighted
- Dynamic load factor (DAF): 1.10 typical, 1.25 offshore
- Total lifted load including DAF
- Ground pressure calc: (crane wt + load × DAF) / mat area

### Page 6 — Rigging Configuration
- Rigging schematic (simple text/table)
- Sling type: WSR / WLL / grade
- Sling length calculation from sling angle
- Sling angle: 60° minimum (safe)
- Shackle grade (D-shackles, Green Pin or Crosby)
- Master link / spreader beam specs

### Page 7 — Rigging Load Calculations
- Individual sling load = (Load × DAF) / (n × sin θ)
- Utilization on each sling: WLL vs actual load
- Safety factor: 5:1 for slings, 4:1 for shackles

### Page 8 — Ground Bearing & Site Layout
- Ground bearing pressure required vs allowable
- Crane pad dimensions
- Outrigger loads (if mobile crane)
- Site plan sketch (text/box)

### Page 9 — Risk Assessment (BS 7121 Format)
- Table: Hazard | Risk (before) | Controls | Risk (after)
- Rows: overload, crane failure, load drop, weather, personnel, ground failure, sling failure, overhead obstruction
- Risk score: L×S (Likelihood × Severity, 1-5 each)

### Page 10 — Method Statement
- Step-by-step procedure (numbered)
- Pre-lift checks
- Rigging up
- Trial lift (25% load hold)
- Main lift
- Set-down
- De-rigging

### Page 11 — Roles & Responsibilities
- Appointed Person: Muthuraj Jeyabal — LEEA certified, overall responsibility
- Lift Supervisor: [TBD]
- Crane Operator: [certified]
- Slinger/Signaller: [certified]
- Banksman
- Contact info: contact@jmrlifting.com

### Page 12 — Approvals & References
- Signature block: AP / Client rep / HSE / Client PM
- References list:
  - BS 7121-1:2016 Safe use of cranes
  - LOLER 1998 (UK)
  - ASME B30.5 Mobile Cranes
  - LEEA COPSULE
  - Crane manufacturer load chart
- SAMPLE watermark disclaimer

## Design Specifications

### Typography
- Body: Inter, downloaded from Google Fonts
- Headings: DM Sans Bold
- Numbers/tables: Inter with tabular-nums
- Fallback: Helvetica

### Colors
- Body: #1a1a1a
- Muted: #666666
- Accent: #ff6a1a (JMR orange)
- Table header bg: #f5f5f0
- Alt row bg: #fafafa
- Border: #d4d1ca
- Warning: #964219

### Layout
- Page size: A4
- Margins: 20mm top/bottom, 18mm left/right
- Header on every page: JMR logo (top-left) + "LP-XX Plan Title" (top-right)
- Footer on every page: page N of M + "SAMPLE" watermark + "contact@jmrlifting.com"

### Watermark
Add faint diagonal "SAMPLE" text at 45°, gray 15% opacity, on every page.

## The 10 Scenarios (Detailed Numbers)

### LP-01: Refinery Reactor Tandem Lift
- Load: 285 t hydrocracker reactor, 42m × 5.2m dia
- Cranes: 2 × Liebherr LR 1600/2 (600t each)
- Working radius: 15m each
- Boom: 84m main
- Capacity at radius: 425t each
- Utilization: 285/2 = 142.5t + DAF 1.1 = 157t per crane; 157/425 = 37%
- Sling angle: 65°, 4 slings per crane
- Individual sling load: (157×1.1)/(4×sin65°) = 47.6 t → 60t WLL grommet sling
- Duration: 8 hrs
- Location: Petrochemical facility

### LP-02: Wind Turbine Nacelle 130m
- Load: 82 t nacelle, 12m × 4.5m × 4.5m
- Crane: Liebherr LR 11000 (1000t)
- Config: SL13DFB, main boom 138m + luffing jib 60m
- Working radius: 22m
- Hub height: 130m, tip height 176m
- Capacity: 128t at radius
- Utilization: (82×1.15)/128 = 74%
- Sling angle: 70°, 4 slings
- Individual sling: (82×1.15)/(4×sin70°) = 25.1t → 32t WLL
- Duration: 6 hrs (weather permitting)
- Wind speed limit: 8 m/s at hub

### LP-03: Elevated Tank at 100m
- Load: 45 t tank shell, 8m dia × 6m ht
- Crane: Liebherr LTM 1750-9.1 (750t)
- Config: Main boom 91m + fixed jib 21m
- Working radius: 24m
- Lift height: 100m tank bottom, 106m top
- Capacity: 65t at radius
- Utilization: (45×1.1)/65 = 76%
- Sling angle: 60°, 4 slings
- Individual sling: (45×1.1)/(4×sin60°) = 14.3t → 20t WLL
- Duration: 5 hrs

### LP-04: Power Plant Generator
- Load: 195 t generator + stator, 8.5m × 4m × 4.2m
- Crane: Liebherr LR 1750/2 (750t)
- Config: Main boom 42m, indoor lift through roof opening
- Working radius: 10m
- Capacity: 380t at radius
- Utilization: (195×1.1)/380 = 56%
- Sling: 4-leg with spreader beam, angle 75°
- Individual sling: (195×1.1)/(4×sin75°) = 55.5t → 63t WLL
- Positioning tolerance: ±10mm
- Duration: 10 hrs including alignment

### LP-05: Offshore LQ Module
- Load: 380 t Living Quarters module, 22m × 18m × 8m
- Vessel: HLV Saipem 7000 (semi-sub crane vessel)
- Crane: Main hook 7000t capacity, aux 2500t
- Sea state: Hs < 2.0m
- DAF: 1.25 (offshore)
- Utilization: (380×1.25)/7000 = 6.8%
- 4-point spreader beam, sling angle 70°
- Individual sling: (380×1.25)/(4×sin70°) = 126t → 150t WLL
- Weather window: 12 hr calm
- Duration: 8 hrs total

### LP-06: Bridge Girder Tandem
- Load: 65 t steel plate girder, 48m long
- Cranes: 2 × Liebherr LTM 1500-8.1 (500t)
- Config: Main boom 60m each
- Working radius: 20m each
- Capacity: 88t each at radius
- Utilization: (65/2 × 1.1)/88 = 41%
- Sling angle: 55° (girder length constraint)
- Individual sling: (32.5×1.1)/(2×sin55°) = 21.8t → 32t WLL
- Traffic mgmt: full roadway closure, 6 hr window
- Duration: 6 hrs (night)

### LP-07: Subsea Xmas Tree
- Load: 78 t XT + spanner joint
- Deployment: Rig moonpool, drill floor crane 100t + guidewires
- Depth: 1500m water
- DAF splash zone: 1.3
- Water entry velocity: <0.5 m/s
- Utilization at surface: (78×1.3)/100 = 101% ⚠ Requires main hoist compensator
- Alternative: Vessel with 250t AHC crane
- Duration: 12 hrs deployment

### LP-08: 400kV Substation Transformer
- Load: 340 t transformer with fluid
- Crane: Liebherr LG 1750 lattice truck (750t)
- Config: SL2DB main boom 63m
- Working radius: 12m
- Capacity: 510t at radius
- Utilization: (340×1.1)/510 = 73%
- Sling angle: 65°, 4-leg
- Individual sling: (340×1.1)/(4×sin65°) = 103t → 120t WLL
- Foundation loading: check bearing capacity
- Duration: 8 hrs

### LP-09: LNG Tank Roof Air-Raise
- Load: 220 t aluminium inner roof, 82m diameter
- Method: Pneumatic (air-raise), NOT crane lift
- Air pressure: 300 Pa differential
- Backup crane: Liebherr LR 1400/2 (400t) — emergency only
- Rise speed: 0.3 m/min
- Total rise: 42m
- Duration: 3 hrs raise + 2 hrs lock-in
- Critical: Pressure control, roof guidance system

### LP-10: Column Tandem Lift & Turn
- Load: 165 t distillation column, 45m × 3.5m dia
- Main crane: Liebherr LTM 1500-8.1 (500t) — head
- Tail crane: LTM 1200-5.1 (200t) — tail
- Head crane radius: 18m, capacity 105t
- Tail crane radius: 15m at start, walks in during upending
- Head sling load at horizontal: 122t (73% of column wt due to COG offset)
- Head sling load at vertical: 165t (full weight)
- Tail load reduces from 43t → 0 during upending
- Utilization head: (165×1.1)/105 = ⚠ need bigger head crane
- REVISED: Use LTM 1750-9.1 (750t) as head, capacity 168t at 18m
- Utilization head revised: (165×1.1)/168 = 108% ⚠
- Reduce radius to 15m: capacity 205t, util = 89% ✓
- Duration: 8 hrs

## Cover Illustration
For each PDF cover, draw a simple SVG-style illustration in ReportLab:
- Silhouette of relevant equipment (crane + load)
- Monochrome, orange accent line
- Size ~60mm × 40mm

## Implementation Notes

1. Use ReportLab Platypus for layout
2. Register Inter + DM Sans fonts from Google Fonts
3. Create reusable functions:
   - `make_header(canvas, doc, plan_id, title)`
   - `make_footer(canvas, doc)`
   - `make_watermark(canvas, doc)`
   - `create_parameter_table(data)`
   - `create_risk_table()`
   - `draw_load_sketch(canvas, x, y, params)`
4. Loop through 10 scenarios, build each PDF
5. Verify file size 200-800 KB per PDF
6. Cross-check: page count 10-12, no orphan headings

## Success Criteria

- All 10 PDFs generated in /home/user/workspace/jmr-lifting/lift-plans/pdfs/
- Each PDF has all 12 sections
- Numbers/calculations engineering-consistent (utilization, sling loads)
- SAMPLE watermark visible on every page
- Clean typography, no rendering errors
- Metadata: author="Perplexity Computer", title=plan title
