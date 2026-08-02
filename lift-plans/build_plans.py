#!/usr/bin/env python3
"""
JMR Lifting Solutions — Lift Plan PDF Generator
Generates 10 professional engineering-grade lift plan PDFs.
"""
import os
import math
import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable, Frame
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_DIR = Path("/tmp/fonts")

pdfmetrics.registerFont(TTFont("Inter", str(FONT_DIR / "Inter-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Bold", str(FONT_DIR / "Inter-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Medium", str(FONT_DIR / "Inter-Medium.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Italic", str(FONT_DIR / "Inter-Italic.static.ttf")))
pdfmetrics.registerFont(TTFont("DMSans", str(FONT_DIR / "DMSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("DMSans-Bold", str(FONT_DIR / "DMSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DMSans-Medium", str(FONT_DIR / "DMSans-Medium.ttf")))

pdfmetrics.registerFontFamily(
    "Inter", normal="Inter", bold="Inter-Bold",
    italic="Inter-Italic", boldItalic="Inter-Bold",
)
pdfmetrics.registerFontFamily(
    "DMSans", normal="DMSans", bold="DMSans-Bold",
    italic="DMSans", boldItalic="DMSans-Bold",
)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BODY = HexColor("#1a1a1a")
MUTED = HexColor("#666666")
ACCENT = HexColor("#ff6a1a")
TABLE_HEAD_BG = HexColor("#f5f5f0")
ALT_ROW_BG = HexColor("#fafafa")
BORDER = HexColor("#d4d1ca")
WARN = HexColor("#964219")
WHITE = colors.white
DARK_NAVY = HexColor("#12181f")

OUT_DIR = Path("/home/user/workspace/jmr-lifting/lift-plans/pdfs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_W, PAGE_H = A4
MARGIN_TOP = 20 * mm
MARGIN_BOTTOM = 20 * mm
MARGIN_LR = 18 * mm

PREPARED_BY = "Muthuraj Jeyabal, LEEA Certified Appointed Person"
CERT_NO = "8234-13608-8667-27-1"
REVIEWED_BY = "JMR Lifting Engineering"
STANDARDS_LINE = "BS 7121 \u00b7 LOLER 1998 \u00b7 ASME B30"
CONTACT_EMAIL = "contact@jmrlifting.com"
TODAY = datetime.date(2026, 8, 2).strftime("%d %B %Y")

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------
def build_styles():
    s = {}
    s["Body"] = ParagraphStyle(
        "Body", fontName="Inter", fontSize=9.5, leading=14,
        textColor=BODY, spaceAfter=6, alignment=TA_JUSTIFY,
    )
    s["BodyLeft"] = ParagraphStyle(
        "BodyLeft", parent=s["Body"], alignment=TA_LEFT,
    )
    s["Small"] = ParagraphStyle(
        "Small", fontName="Inter", fontSize=8, leading=11,
        textColor=MUTED, spaceAfter=4,
    )
    s["Muted"] = ParagraphStyle(
        "Muted", fontName="Inter", fontSize=9, leading=13,
        textColor=MUTED, spaceAfter=4,
    )
    s["H1"] = ParagraphStyle(
        "H1", fontName="DMSans-Bold", fontSize=16, leading=20,
        textColor=DARK_NAVY, spaceBefore=0, spaceAfter=10,
    )
    s["H2"] = ParagraphStyle(
        "H2", fontName="DMSans-Bold", fontSize=11.5, leading=15,
        textColor=DARK_NAVY, spaceBefore=4, spaceAfter=6,
    )
    s["H3"] = ParagraphStyle(
        "H3", fontName="DMSans-Medium", fontSize=10, leading=13,
        textColor=ACCENT, spaceBefore=2, spaceAfter=4,
    )
    s["TableCell"] = ParagraphStyle(
        "TableCell", fontName="Inter", fontSize=8.3, leading=11,
        textColor=BODY,
    )
    s["TableCellBold"] = ParagraphStyle(
        "TableCellBold", fontName="Inter-Bold", fontSize=8.3, leading=11,
        textColor=BODY,
    )
    s["TableHead"] = ParagraphStyle(
        "TableHead", fontName="DMSans-Medium", fontSize=8.3, leading=11,
        textColor=DARK_NAVY,
    )
    s["Bullet"] = ParagraphStyle(
        "Bullet", parent=s["Body"], leftIndent=12, bulletIndent=0,
        alignment=TA_LEFT, spaceAfter=4,
    )
    s["Caption"] = ParagraphStyle(
        "Caption", fontName="Inter-Italic", fontSize=8, leading=11,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=8,
    )
    s["CoverTitleSmall"] = ParagraphStyle(
        "CoverTitleSmall", fontName="DMSans-Medium", fontSize=12, leading=15,
        textColor=ACCENT,
    )
    s["Warn"] = ParagraphStyle(
        "Warn", fontName="Inter-Bold", fontSize=9.5, leading=13,
        textColor=WARN, spaceAfter=6,
    )
    return s

STYLES = build_styles()

# ---------------------------------------------------------------------------
# Scenario data — numbers taken verbatim from BRIEF.md
# ---------------------------------------------------------------------------
SCENARIOS = [
    dict(
        code="LP-01", filename="LP-01-refinery-reactor-tandem.pdf",
        title="Refinery Reactor Tandem Lift",
        icon="tandem_crawler",
        scope=(
            "Tandem lift of a hydrocracker reactor from delivery trailer to its "
            "final foundation within an operating petrochemical facility. Two "
            "crawler cranes work in coordinated tandem to control centre-of-gravity "
            "shift as the reactor is raised from horizontal transport to a "
            "near-vertical set position."
        ),
        load_desc=(
            "Hydrocracker reactor pressure vessel, cylindrical shell with domed "
            "heads, delivered by SPMT trailer and lifted directly onto a concrete "
            "ring foundation."
        ),
        load_t=285, dims="42 m x 5.2 m dia", radius_m=15, lift_height_m=38,
        duration="8 hrs", location="Petrochemical facility",
        weight_breakdown=[
            ("Structural shell & heads", "268.0 t"),
            ("Internals (trays/packing)", "12.5 t"),
            ("Lifting attachments", "2.0 t"),
            ("Uncertainty allowance (0.9%)", "2.5 t"),
            ("Total", "285.0 t"),
        ],
        cog=("21.0 m from tail (X)", "0.0 m off centreline (Y)", "2.6 m above shell base (Z)"),
        lift_points="4 no. trunnion lugs, 2 per crane, symmetric about mid-length",
        cranes=[
            dict(model="Liebherr LR 1600/2", capacity_t=600, boom_m=84,
                 config="Main boom 84 m, tandem symmetric spread",
                 radius_m=15, capacity_at_radius_t=425),
            dict(model="Liebherr LR 1600/2", capacity_t=600, boom_m=84,
                 config="Main boom 84 m, tandem symmetric spread",
                 radius_m=15, capacity_at_radius_t=425),
        ],
        daf=1.10,
        util_calc=(
            "285 t / 2 cranes = 142.5 t/crane; with DAF 1.10 = 156.75 t (approx 157 t) "
            "per crane. Utilization = 157 / 425 = 37%."
        ),
        util_pct=37,
        load_chart=[
            (10, 560), (15, 425), (20, 340), (25, 275), (30, 225),
        ],
        working_radius_highlight=15,
        rigging=dict(
            sling_type="Wire rope grommet sling, 6x36 IWRC, EIPS grade",
            angle_deg=65, n_slings=4,
            wll_each_t=60,
            calc_text="(157 x 1.10) / (4 x sin 65deg) = 47.6 t per sling -> select 60 t WLL grommet sling",
            sling_load_t=47.6,
            shackle="Crosby G-2140 100 t bow shackle",
            spreader="4-point trunnion spreader frame, rated 200 t",
        ),
        ground_bearing=dict(
            crane_wt_t=180, mat_area_m2=48,
            calc_text="Ground bearing = (crane wt 180 t + load x DAF 157 t) x 9.81 / 48 sqm mat area = 68.9 kPa",
            pressure_kpa=68.9, allowable_kpa=150,
            pad="6.0 m x 2.4 m steel mats, 2 per crawler track, per crane",
        ),
        risks_extra=[],
        method_notes="Coordinated tandem lift with radio-linked crane operators; upending sequence controlled by lead rigger.",
    ),
    dict(
        code="LP-02", filename="LP-02-wind-nacelle-130m.pdf",
        title="Wind Turbine Nacelle Installation - 130 m Hub",
        icon="tower_crane",
        scope=(
            "Single-crane lift of a wind turbine nacelle assembly to a 130 m hub "
            "height on a completed tower, using a main boom plus luffing jib "
            "configuration to achieve the required tip height and radius."
        ),
        load_desc="Nacelle assembly including gearbox, generator, and yaw system, lifted as a single unit onto the tower flange.",
        load_t=82, dims="12 m x 4.5 m x 4.5 m", radius_m=22, lift_height_m=130,
        duration="6 hrs (weather permitting)", location="Wind farm (greenfield)",
        weight_breakdown=[
            ("Nacelle housing & drivetrain", "74.5 t"),
            ("Yaw system & bedplate", "5.8 t"),
            ("Lifting beam/attachments", "1.0 t"),
            ("Uncertainty allowance (0.9%)", "0.7 t"),
            ("Total", "82.0 t"),
        ],
        cog=("6.0 m from tower centreline (X)", "0.0 m (Y)", "2.1 m above bedplate (Z)"),
        lift_points="4 no. certified lifting points on bedplate, dedicated nacelle lifting beam",
        cranes=[
            dict(model="Liebherr LR 11000", capacity_t=1000, boom_m=138,
                 config="SL13DFB - main boom 138 m + luffing jib 60 m",
                 radius_m=22, capacity_at_radius_t=128),
        ],
        daf=1.15,
        util_calc="(82 x 1.15) / 128 = 74%. Hub height 130 m, tip height 176 m.",
        util_pct=74,
        load_chart=[
            (15, 195), (18, 162), (22, 128), (26, 102), (30, 84),
        ],
        working_radius_highlight=22,
        rigging=dict(
            sling_type="Dedicated nacelle lifting beam with wire rope drops",
            angle_deg=70, n_slings=4,
            wll_each_t=32,
            calc_text="(82 x 1.15) / (4 x sin 70deg) = 25.1 t per sling -> select 32 t WLL sling set",
            sling_load_t=25.1,
            shackle="Green Pin G-2130 35 t bow shackle",
            spreader="Purpose-built nacelle lifting beam, rated 100 t",
        ),
        ground_bearing=dict(
            crane_wt_t=420, mat_area_m2=90,
            calc_text="Ground bearing = (crane wt 420 t + load x DAF 94.3 t) x 9.81 / 90 sqm = 56.0 kPa",
            pressure_kpa=56.0, allowable_kpa=120,
            pad="Compacted crane hardstand, 30 m x 30 m graded pad",
        ),
        risks_extra=[("Wind speed exceedance", 3, 4, "Continuous anemometer monitoring; lift limit 8 m/s at hub height", 1, 4)],
        method_notes="Wind speed limit 8 m/s at hub height; live monitoring via nacelle-mounted anemometer feed to crane cab.",
        wind_limit="8 m/s at hub",
    ),
    dict(
        code="LP-03", filename="LP-03-elevated-tank-100m.pdf",
        title="Elevated Storage Tank Placement - 100 m",
        icon="mobile_crane",
        scope=(
            "Placement of a water storage tank shell onto a structural support "
            "tower at 100 m elevation using a mobile crane with fixed jib "
            "configuration for extended reach."
        ),
        load_desc="Cylindrical tank shell (empty), lifted from ground assembly area onto tower-mounted support ring.",
        load_t=45, dims="8 m dia x 6 m ht", radius_m=24, lift_height_m=100,
        duration="5 hrs", location="Industrial facility",
        weight_breakdown=[
            ("Tank shell plate", "39.0 t"),
            ("Roof structure", "4.2 t"),
            ("Lifting lugs/attachments", "0.8 t"),
            ("Uncertainty allowance (2.2%)", "1.0 t"),
            ("Total", "45.0 t"),
        ],
        cog=("0.0 m from tank centreline (X)", "0.0 m (Y)", "3.0 m above shell base (Z)"),
        lift_points="4 no. lifting lugs, equally spaced on top shell ring",
        cranes=[
            dict(model="Liebherr LTM 1750-9.1", capacity_t=750, boom_m=91,
                 config="Main boom 91 m + fixed jib 21 m",
                 radius_m=24, capacity_at_radius_t=65),
        ],
        daf=1.10,
        util_calc="(45 x 1.10) / 65 = 76%. Lift height 100 m tank bottom, 106 m top.",
        util_pct=76,
        load_chart=[
            (18, 92), (20, 81), (24, 65), (28, 52), (32, 41),
        ],
        working_radius_highlight=24,
        rigging=dict(
            sling_type="Wire rope sling set, 6x36 IWRC EIPS",
            angle_deg=60, n_slings=4,
            wll_each_t=20,
            calc_text="(45 x 1.10) / (4 x sin 60deg) = 14.3 t per sling -> select 20 t WLL sling",
            sling_load_t=14.3,
            shackle="Crosby G-2130 25 t bow shackle",
            spreader="4-leg bridle direct to lifting lugs (no spreader required)",
        ),
        ground_bearing=dict(
            crane_wt_t=120, mat_area_m2=36,
            calc_text="Ground bearing = (crane wt 120 t + load x DAF 49.5 t) x 9.81 / 36 sqm = 46.1 kPa",
            pressure_kpa=46.1, allowable_kpa=100,
            pad="Outrigger mats 1.2 m x 1.2 m x 50 mm steel, 4 no.",
        ),
        risks_extra=[],
        method_notes="Fixed jib configuration optimized for radius/height combination; verify jib offset angle prior to pick.",
    ),
    dict(
        code="LP-04", filename="LP-04-power-generator.pdf",
        title="Large Industrial Generator Installation",
        icon="crawler_indoor",
        scope=(
            "Indoor placement of a combined-cycle plant generator and stator "
            "through a roof opening, requiring precise positioning tolerance "
            "and controlled boom geometry for confined overhead clearance."
        ),
        load_desc="Generator and stator assembly, lifted through a purpose-built roof opening onto foundation base plates.",
        load_t=195, dims="8.5 m x 4 m x 4.2 m", radius_m=10, lift_height_m=22,
        duration="10 hrs including alignment", location="Power plant (indoor)",
        weight_breakdown=[
            ("Generator body", "148.0 t"),
            ("Stator assembly", "42.0 t"),
            ("Lifting attachments", "3.0 t"),
            ("Uncertainty allowance (1.0%)", "2.0 t"),
            ("Total", "195.0 t"),
        ],
        cog=("4.25 m from drive end (X)", "0.0 m (Y)", "2.0 m above base (Z)"),
        lift_points="4 no. integral lifting trunnions with spreader beam attachment",
        cranes=[
            dict(model="Liebherr LR 1750/2", capacity_t=750, boom_m=42,
                 config="Main boom 42 m, indoor lift through roof opening",
                 radius_m=10, capacity_at_radius_t=380),
        ],
        daf=1.10,
        util_calc="(195 x 1.10) / 380 = 56%. Positioning tolerance +/-10 mm.",
        util_pct=56,
        load_chart=[
            (6, 520), (8, 440), (10, 380), (12, 325), (14, 280),
        ],
        working_radius_highlight=10,
        rigging=dict(
            sling_type="4-leg wire rope sling with spreader beam",
            angle_deg=75, n_slings=4,
            wll_each_t=63,
            calc_text="(195 x 1.10) / (4 x sin 75deg) = 55.5 t per sling -> select 63 t WLL sling",
            sling_load_t=55.5,
            shackle="Crosby G-2140 85 t bow shackle",
            spreader="Fabricated spreader beam, rated 250 t, 4 drop points",
        ),
        ground_bearing=dict(
            crane_wt_t=210, mat_area_m2=40,
            calc_text="Ground bearing = (crane wt 210 t + load x DAF 214.5 t) x 9.81 / 40 sqm = 104.1 kPa",
            pressure_kpa=104.1, allowable_kpa=180,
            pad="Reinforced concrete slab, verified 180 kPa allowable bearing",
        ),
        risks_extra=[("Positioning misalignment", 3, 3, "Laser alignment guides; taglines on all four corners; +/-10 mm tolerance verified by survey", 1, 3)],
        method_notes="Positioning tolerance +/-10 mm verified by total-station survey during final set-down.",
    ),
    dict(
        code="LP-05", filename="LP-05-offshore-lq-module.pdf",
        title="Offshore Platform Living Quarters Module Lift",
        icon="offshore_hlv",
        scope=(
            "Single lift installation of a Living Quarters (LQ) module from "
            "cargo barge onto a fixed jacket platform using a semi-submersible "
            "heavy-lift vessel within a defined weather window."
        ),
        load_desc="Fully outfitted Living Quarters module, lifted from transport barge and set directly onto jacket support structure.",
        load_t=380, dims="22 m x 18 m x 8 m", radius_m=32, lift_height_m=45,
        duration="8 hrs total", location="Offshore fixed platform (West Africa)",
        weight_breakdown=[
            ("Module structural steel", "298.0 t"),
            ("Outfitting & equipment", "70.0 t"),
            ("Lifting padeyes/attachments", "4.0 t"),
            ("Uncertainty allowance (2.1%)", "8.0 t"),
            ("Total", "380.0 t"),
        ],
        cog=("11.0 m from module centreline (X)", "9.0 m (Y)", "4.0 m above base (Z)"),
        lift_points="4 no. heavy padeyes at module corners, rated for offshore dynamic loading",
        cranes=[
            dict(model="HLV Saipem 7000 (semi-sub)", capacity_t=7000, boom_m=0,
                 config="Main hook 7000 t capacity, aux hook 2500 t",
                 radius_m=32, capacity_at_radius_t=7000),
        ],
        daf=1.25,
        util_calc="(380 x 1.25) / 7000 = 6.8%. Sea state Hs < 2.0 m required.",
        util_pct=6.8,
        load_chart=[
            (20, 7000), (32, 7000), (40, 6200), (48, 5100), (56, 4300),
        ],
        working_radius_highlight=32,
        rigging=dict(
            sling_type="4-point wire rope spreader beam sling set, offshore-rated",
            angle_deg=70, n_slings=4,
            wll_each_t=150,
            calc_text="(380 x 1.25) / (4 x sin 70deg) = 126 t per sling -> select 150 t WLL sling",
            sling_load_t=126,
            shackle="Crosby G-2140 200 t bow shackle, offshore certified",
            spreader="4-point spreader beam, rated 600 t, dynamic-load certified",
        ),
        ground_bearing=dict(
            crane_wt_t=None, mat_area_m2=None,
            calc_text="Not applicable - floating heavy-lift vessel; hull ballast and mooring system react all lift loads.",
            pressure_kpa=None, allowable_kpa=None,
            pad="N/A - vessel dynamic positioning + 8-point mooring spread",
        ),
        risks_extra=[("Sea state exceedance", 3, 5, "Weather window forecast 12 hr calm; Hs < 2.0 m hard limit; DP2 vessel station-keeping", 1, 5)],
        method_notes="Weather window: 12 hr calm required before lift commencement. Dynamic amplification factor 1.25 applied per offshore lifting standard.",
        weather_window="12 hr calm, Hs < 2.0 m",
    ),
    dict(
        code="LP-06", filename="LP-06-bridge-girder-tandem.pdf",
        title="Bridge Girder Erection - Tandem Lift",
        icon="tandem_mobile",
        scope=(
            "Tandem lift and placement of a steel plate girder spanning a live "
            "highway overpass, executed during a scheduled night closure to "
            "minimize traffic disruption."
        ),
        load_desc="Fabricated steel plate girder, lifted from staging area and placed onto bridge bearing pads.",
        load_t=65, dims="48 m long", radius_m=20, lift_height_m=14,
        duration="6 hrs (night)", location="Live traffic corridor",
        weight_breakdown=[
            ("Girder plate steel", "58.0 t"),
            ("Stiffeners & bracing", "5.5 t"),
            ("Lifting attachments", "0.7 t"),
            ("Uncertainty allowance (1.2%)", "0.8 t"),
            ("Total", "65.0 t"),
        ],
        cog=("24.0 m from tail end (X)", "0.0 m (Y)", "1.1 m above bottom flange (Z)"),
        lift_points="4 no. lifting lugs, 2 per crane, positioned at 1/4-span points",
        cranes=[
            dict(model="Liebherr LTM 1500-8.1", capacity_t=500, boom_m=60,
                 config="Main boom 60 m, tandem over roadway",
                 radius_m=20, capacity_at_radius_t=88),
            dict(model="Liebherr LTM 1500-8.1", capacity_t=500, boom_m=60,
                 config="Main boom 60 m, tandem over roadway",
                 radius_m=20, capacity_at_radius_t=88),
        ],
        daf=1.10,
        util_calc="(65 / 2 x 1.10) / 88 = 41%. Sling angle 55deg due to girder length constraint.",
        util_pct=41,
        load_chart=[
            (14, 130), (17, 106), (20, 88), (23, 73), (26, 61),
        ],
        working_radius_highlight=20,
        rigging=dict(
            sling_type="Wire rope sling set, 6x36 IWRC EIPS",
            angle_deg=55, n_slings=2,
            wll_each_t=32,
            calc_text="(32.5 x 1.10) / (2 x sin 55deg) = 21.8 t per sling -> select 32 t WLL sling",
            sling_load_t=21.8,
            shackle="Green Pin G-2130 35 t bow shackle",
            spreader="Direct 2-leg bridle per crane pick point (no spreader)",
        ),
        ground_bearing=dict(
            crane_wt_t=140, mat_area_m2=30,
            calc_text="Ground bearing = (crane wt 140 t + load x DAF 35.75 t) x 9.81 / 30 sqm = 57.5 kPa",
            pressure_kpa=57.5, allowable_kpa=110,
            pad="Roadway steel trackway mats, 3 m x 6 m, per outrigger",
        ),
        risks_extra=[("Traffic incursion", 3, 5, "Full roadway closure with traffic management plan; police-controlled diversion during 6 hr window", 1, 5)],
        method_notes="Full roadway closure required; traffic management plan enforced for entire 6 hr night window.",
        traffic_mgmt="Full roadway closure, 6 hr window",
    ),
    dict(
        code="LP-07", filename="LP-07-subsea-xmas-tree.pdf",
        title="Subsea Christmas Tree Deployment",
        icon="rig_moonpool",
        scope=(
            "Deployment of a subsea Christmas tree (XT) and spanner joint "
            "through the drill floor moonpool to 1500 m water depth, using "
            "the rig crane with guidewire-assisted lowering through the "
            "splash zone."
        ),
        load_desc="Subsea Christmas tree assembly with spanner joint, lowered through moonpool on guidewires to the seabed wellhead.",
        load_t=78, dims="XT + spanner joint, approx. 6 m x 4 m x 5 m", radius_m=8, lift_height_m=1500,
        duration="12 hrs deployment", location="Offshore drilling rig",
        weight_breakdown=[
            ("XT body & valves", "61.0 t"),
            ("Spanner joint", "14.5 t"),
            ("Running tool/attachments", "1.5 t"),
            ("Uncertainty allowance (1.3%)", "1.0 t"),
            ("Total", "78.0 t"),
        ],
        cog=("0.0 m from vertical centreline (X)", "0.0 m (Y)", "2.4 m above tree base (Z)"),
        lift_points="Single running tool interface on tree cap, guidewire posts at 4 corners",
        cranes=[
            dict(model="Rig floor crane", capacity_t=100, boom_m=0,
                 config="Drill floor crane, moonpool deployment, guidewire-assisted",
                 radius_m=8, capacity_at_radius_t=100),
        ],
        daf=1.30,
        util_calc="(78 x 1.30) / 100 = 101% - exceeds safe working limit at surface - requires main hoist compensator. See revision note.",
        util_pct=101,
        revision_note=(
            "WARNING: Initial utilization of 101% exceeds the safe working limit at "
            "the surface using the rig floor crane alone. REVISED APPROACH: deploy using "
            "a construction support vessel fitted with a 250 t Active Heave Compensated "
            "(AHC) crane, which reduces effective dynamic loading through the splash zone "
            "and provides adequate margin. Revised utilization = (78 x 1.30) / 250 = 41%, "
            "well within the 85% threshold."
        ),
        load_chart=[
            (4, 100), (6, 95), (8, 100), (10, 88), (12, 78),
        ],
        working_radius_highlight=8,
        rigging=dict(
            sling_type="Wire rope running tool sling with guidewire posts",
            angle_deg=90, n_slings=1,
            wll_each_t=110,
            calc_text="Single-point lift: (78 x 1.30) = 101.4 t -> select 110 t WLL running tool sling; splash-zone DAF 1.30 applied",
            sling_load_t=101.4,
            shackle="Crosby G-2150 150 t bow shackle, subsea rated",
            spreader="N/A - single-point running tool interface",
        ),
        ground_bearing=dict(
            crane_wt_t=None, mat_area_m2=None,
            calc_text="Not applicable - floating drilling unit; deployment loads reacted through derrick/crane pedestal structure.",
            pressure_kpa=None, allowable_kpa=None,
            pad="N/A - floating unit, DP-assisted station-keeping",
        ),
        risks_extra=[
            ("Splash-zone dynamic loading", 4, 4, "AHC crane required (revised from 100 t rig crane); water entry velocity limited to <0.5 m/s", 2, 4),
            ("Overload at surface (101% util.)", 4, 5, "REVISED: switch to 250 t AHC vessel crane; utilization reduced to 41%", 1, 5),
        ],
        method_notes="Water entry velocity limited to <0.5 m/s; splash-zone DAF of 1.30 applied per API RP 2A guidance.",
        water_depth="1500 m",
    ),
    dict(
        code="LP-08", filename="LP-08-substation-transformer.pdf",
        title="400kV Substation Transformer Placement",
        icon="lattice_truck",
        scope=(
            "Placement of a 400kV power transformer, filled with insulating "
            "fluid, onto its foundation plinth within an operating grid "
            "substation using a lattice boom truck crane."
        ),
        load_desc="400kV power transformer with fluid, delivered by rail/road transporter and lifted onto foundation plinth.",
        load_t=340, dims="Approx. 9 m x 4.5 m x 5.5 m", radius_m=12, lift_height_m=8,
        duration="8 hrs", location="Grid substation",
        weight_breakdown=[
            ("Transformer tank & core", "268.0 t"),
            ("Insulating fluid", "58.0 t"),
            ("Bushings/radiators/fittings", "10.5 t"),
            ("Uncertainty allowance (1.0%)", "3.5 t"),
            ("Total", "340.0 t"),
        ],
        cog=("4.5 m from LV end (X)", "0.0 m (Y)", "2.3 m above tank base (Z)"),
        lift_points="4 no. certified lifting lugs on tank top, per manufacturer lifting drawing",
        cranes=[
            dict(model="Liebherr LG 1750 lattice truck", capacity_t=750, boom_m=63,
                 config="SL2DB main boom 63 m",
                 radius_m=12, capacity_at_radius_t=510),
        ],
        daf=1.10,
        util_calc="(340 x 1.10) / 510 = 73%. Foundation bearing capacity to be verified.",
        util_pct=73,
        load_chart=[
            (8, 640), (10, 570), (12, 510), (14, 455), (16, 405),
        ],
        working_radius_highlight=12,
        rigging=dict(
            sling_type="4-leg wire rope sling set, 6x36 IWRC EIPS",
            angle_deg=65, n_slings=4,
            wll_each_t=120,
            calc_text="(340 x 1.10) / (4 x sin 65deg) = 103.0 t per sling -> select 120 t WLL sling",
            sling_load_t=103.0,
            shackle="Crosby G-2140 150 t bow shackle",
            spreader="4-leg direct bridle to tank lugs (no spreader beam)",
        ),
        ground_bearing=dict(
            crane_wt_t=260, mat_area_m2=54,
            calc_text="Ground bearing = (crane wt 260 t + load x DAF 374 t) x 9.81 / 54 sqm = 115.2 kPa",
            pressure_kpa=115.2, allowable_kpa=200,
            pad="Reinforced hardstand, foundation bearing capacity verified by geotech report",
        ),
        risks_extra=[("Foundation overload", 2, 4, "Geotechnical bearing verification completed prior to mobilization; steel mats under crane tracks", 1, 4)],
        method_notes="Foundation and rail transport interface loading checked against geotechnical bearing capacity prior to lift.",
    ),
    dict(
        code="LP-09", filename="LP-09-lng-tank-air-raise.pdf",
        title="LNG Storage Tank Roof Air-Raise",
        icon="air_raise",
        scope=(
            "Pneumatic air-raise of the aluminium inner roof of an LNG storage "
            "tank, using controlled air pressure differential rather than a "
            "crane lift, with a backup crane on standby for emergency "
            "intervention only."
        ),
        load_desc="Aluminium dome inner roof assembly, raised from tank floor level to final roof position using air pressure.",
        load_t=220, dims="82 m diameter", radius_m=None, lift_height_m=42,
        duration="3 hrs raise + 2 hrs lock-in", location="LNG terminal",
        weight_breakdown=[
            ("Aluminium roof plate", "185.0 t"),
            ("Roof structural framing", "28.0 t"),
            ("Guidance/attachment hardware", "4.0 t"),
            ("Uncertainty allowance (1.4%)", "3.0 t"),
            ("Total", "220.0 t"),
        ],
        cog=("0.0 m from tank centreline (X)", "0.0 m (Y)", "1.8 m above roof apex datum (Z)"),
        lift_points="N/A - pneumatic raise; roof guided by perimeter guidance system, not crane rigging",
        cranes=[
            dict(model="Liebherr LR 1400/2 (backup, emergency only)", capacity_t=400, boom_m=None,
                 config="Standby crane - not used for primary lift method",
                 radius_m=None, capacity_at_radius_t=None),
        ],
        daf=None,
        util_calc="Not applicable - pneumatic air-raise method; no crane load chart utilization for primary lift.",
        util_pct=None,
        load_chart=None,
        working_radius_highlight=None,
        rigging=dict(
            sling_type="N/A - no slings used in primary air-raise method",
            angle_deg=None, n_slings=None,
            wll_each_t=None,
            calc_text="Not applicable - roof raised on air pressure differential of 300 Pa; backup crane rigging held on standby only.",
            sling_load_t=None,
            shackle="N/A",
            spreader="N/A",
        ),
        ground_bearing=dict(
            crane_wt_t=None, mat_area_m2=None,
            calc_text="Not applicable to air-raise method. Backup crane (if mobilized) ground bearing to be assessed per standard mobile crane siting procedure.",
            pressure_kpa=None, allowable_kpa=None,
            pad="Backup crane standby pad, location per site crane matting plan",
        ),
        risks_extra=[
            ("Loss of air pressure control", 3, 5, "Continuous pressure monitoring at 300 Pa differential; redundant blower units; emergency vent procedure", 1, 5),
            ("Roof guidance failure", 2, 4, "Roof guidance system inspected pre-raise; backup crane on standby for emergency intervention", 1, 4),
        ],
        method_notes="Air pressure differential of 300 Pa maintained throughout; rise speed 0.3 m/min; total rise 42 m.",
        air_pressure="300 Pa differential", rise_speed="0.3 m/min",
    ),
    dict(
        code="LP-10", filename="LP-10-column-tandem-turn.pdf",
        title="Pressure Vessel Tandem Lift & Turn",
        icon="tandem_turn",
        scope=(
            "Tandem lift and upending (turn from horizontal to vertical) of a "
            "distillation column using a head crane and a walking tail crane, "
            "with the tail crane trolleying inward as the column rotates to "
            "the vertical set position."
        ),
        load_desc="Distillation column, upended from horizontal transport orientation to vertical operating position on foundation skirt.",
        load_t=165, dims="45 m x 3.5 m dia", radius_m=15, lift_height_m=46,
        duration="8 hrs", location="Petrochemical plant",
        weight_breakdown=[
            ("Column shell", "148.0 t"),
            ("Internals & trays", "13.0 t"),
            ("Lifting lugs/attachments", "1.5 t"),
            ("Uncertainty allowance (1.5%)", "2.5 t"),
            ("Total", "165.0 t"),
        ],
        cog=("18.5 m from tail (X)", "0.0 m (Y)", "1.75 m above shell base (Z)"),
        lift_points="Head lug at top tangent line; tail trunnions at base skirt, walking tail crane engagement",
        cranes=[
            dict(model="Liebherr LTM 1750-9.1 (revised head crane)", capacity_t=750, boom_m=None,
                 config="Head crane - radius reduced to 15 m after revision (see note)",
                 radius_m=15, capacity_at_radius_t=205),
            dict(model="Liebherr LTM 1200-5.1", capacity_t=200, boom_m=None,
                 config="Tail crane - walks in during upending, radius starts at 15 m",
                 radius_m=15, capacity_at_radius_t=None),
        ],
        daf=1.10,
        util_calc=(
            "Head sling load at horizontal: 122 t (73% of column weight due to COG offset). "
            "Head sling load at vertical: 165 t (full weight). Tail load reduces from 43 t to 0 t during upending."
        ),
        util_pct=89,
        revision_accepted=True,
        revision_note=(
            "INITIAL DESIGN ISSUE: With Liebherr LTM 1500-8.1 (500 t) as head crane at 18 m "
            "radius (capacity 105 t), utilization = (165 x 1.10) / 105 = 173% - far exceeds safe "
            "limit; bigger head crane required.\n\n"
            "REVISION STEP 1: Substitute Liebherr LTM 1750-9.1 (750 t) as head crane, capacity "
            "168 t at 18 m radius. Utilization = (165 x 1.10) / 168 = 108% - still exceeds the "
            "85% threshold.\n\n"
            "REVISION STEP 2 (FINAL): Reduce working radius to 15 m, increasing capacity to "
            "205 t. Utilization = (165 x 1.10) / 205 = 89% - ACCEPTED, within safe working limit."
        ),
        load_chart=[
            (12, 260), (15, 205), (18, 168), (21, 138), (24, 115),
        ],
        working_radius_highlight=15,
        rigging=dict(
            sling_type="4-leg wire rope bridle, head end direct to trunnion",
            angle_deg=90, n_slings=4,
            wll_each_t=60,
            calc_text="Head sling load at vertical = 165 t / 4 legs x 1.10 DAF = 45.4 t per leg -> select 60 t WLL sling",
            sling_load_t=45.4,
            shackle="Crosby G-2140 85 t bow shackle",
            spreader="Head trunnion direct bridle; tail crane uses dedicated tailing lug (no spreader)",
        ),
        ground_bearing=dict(
            crane_wt_t=310, mat_area_m2=64,
            calc_text="Ground bearing (head crane, revised) = (crane wt 310 t + load x DAF 181.5 t) x 9.81 / 64 sqm = 75.4 kPa",
            pressure_kpa=75.4, allowable_kpa=150,
            pad="Steel trackway mats under head crane outriggers; tail crane on prepared walking path",
        ),
        risks_extra=[
            ("Head crane overload (pre-revision)", 4, 5, "REVISED: increased head crane to 750 t class and reduced radius to 15 m; utilization confirmed 89%", 1, 5),
            ("Tail crane travel/trolley error", 3, 4, "Pre-surveyed walking path; radio-coordinated trolley movement synced to upending angle", 1, 4),
        ],
        method_notes="Tail crane trolleys inward continuously during upending as tail load reduces from 43 t to 0 t; head crane radius fixed at revised 15 m throughout.",
    ),
]

assert len(SCENARIOS) == 10

print(f"Loaded {len(SCENARIOS)} scenarios OK")

# ---------------------------------------------------------------------------
# Canvas drawing helpers — logo, watermark, header, footer, cover art
# ---------------------------------------------------------------------------

def draw_jmr_logo(c, x, y, size=10 * mm, mono=False):
    """Draw the JMR triangle logo (orange triangle with 'JMR' wordmark)."""
    c.saveState()
    c.setFillColor(ACCENT if not mono else WHITE)
    c.setStrokeColor(ACCENT if not mono else WHITE)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x + size, y)
    p.lineTo(x + size / 2, y + size * 0.92)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    # inner cut-out line to suggest a crane boom/rigging notch
    c.setStrokeColor(WHITE if not mono else DARK_NAVY)
    c.setLineWidth(0.8)
    c.line(x + size * 0.5, y + size * 0.30, x + size * 0.5, y + size * 0.92 * 0.62)
    c.restoreState()


def draw_watermark(c, page_w, page_h):
    c.saveState()
    c.setFont("DMSans-Bold", 82)
    c.setFillColor(HexColor("#000000"))
    c.setFillAlpha(0.045)
    c.translate(page_w / 2, page_h / 2)
    c.rotate(38)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()


def make_header_footer(plan_code, plan_title, total_pages_hint=12):
    """Returns a callback usable as onFirstPage/onLaterPages."""

    def _draw(c, doc):
        c.saveState()
        page_w, page_h = A4
        draw_watermark(c, page_w, page_h)

        # Header
        header_y = page_h - MARGIN_TOP + 6 * mm
        draw_jmr_logo(c, MARGIN_LR, header_y - 3.2 * mm, size=5.5 * mm)
        c.setFont("DMSans-Medium", 8.5)
        c.setFillColor(DARK_NAVY)
        c.drawString(MARGIN_LR + 8 * mm, header_y - 1.2 * mm, "JMR LIFTING SOLUTIONS")
        c.setFont("Inter", 8)
        c.setFillColor(MUTED)
        header_right = f"{plan_code} \u00b7 {plan_title}"
        c.drawRightString(page_w - MARGIN_LR, header_y - 1.2 * mm, header_right)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.6)
        c.line(MARGIN_LR, header_y - 5 * mm, page_w - MARGIN_LR, header_y - 5 * mm)

        # Footer
        footer_y = MARGIN_BOTTOM - 8 * mm
        c.setStrokeColor(BORDER)
        c.line(MARGIN_LR, footer_y + 5 * mm, page_w - MARGIN_LR, footer_y + 5 * mm)
        c.setFont("Inter-Italic", 7.5)
        c.drawRightString(page_w - MARGIN_LR, footer_y, "SAMPLE \u2014 For demonstration purposes only")
        c.restoreState()

    return _draw


# ---------------------------------------------------------------------------
# Cover-page line-art silhouettes (equipment icons), drawn with primitives
# ---------------------------------------------------------------------------

def _crawler_crane(c, x, y, w, h, boom_angle=62):
    """Draw a simple crawler crane silhouette: tracks, body, boom, load line."""
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    # tracks
    track_w = w * 0.30
    track_h = h * 0.10
    c.rect(x, y, track_w, track_h, fill=0, stroke=1)
    # body / house
    body_w = w * 0.20
    body_h = h * 0.16
    body_x = x + track_w * 0.25
    body_y = y + track_h
    c.rect(body_x, body_y, body_w, body_h, fill=0, stroke=1)
    # boom
    boom_len = w * 0.85
    boom_base_x = body_x + body_w * 0.7
    boom_base_y = body_y + body_h * 0.75
    rad = math.radians(boom_angle)
    boom_tip_x = boom_base_x + boom_len * math.cos(rad)
    boom_tip_y = boom_base_y + boom_len * math.sin(rad)
    c.line(boom_base_x, boom_base_y, boom_tip_x, boom_tip_y)
    c.line(boom_base_x, boom_base_y, boom_base_x - body_w * 0.4, boom_base_y - body_h * 0.3)
    # hoist line + load hook
    c.setLineWidth(0.8)
    c.line(boom_tip_x, boom_tip_y, boom_tip_x - w * 0.05, y + h * 0.02)
    c.circle(boom_tip_x - w * 0.05, y + h * 0.02, 1.6, fill=0, stroke=1)


def _mobile_crane(c, x, y, w, h, boom_angle=58):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    chassis_w = w * 0.55
    chassis_h = h * 0.10
    c.rect(x, y, chassis_w, chassis_h, fill=0, stroke=1)
    # wheels
    for wx in (x + chassis_w * 0.18, x + chassis_w * 0.5, x + chassis_w * 0.82):
        c.circle(wx, y, 1.8, fill=0, stroke=1)
    cab_x = x
    cab_w = chassis_w * 0.22
    cab_h = h * 0.12
    c.rect(cab_x, y + chassis_h, cab_w, cab_h, fill=0, stroke=1)
    boom_base_x = x + chassis_w * 0.55
    boom_base_y = y + chassis_h + h * 0.03
    boom_len = w * 0.85
    rad = math.radians(boom_angle)
    tip_x = boom_base_x + boom_len * math.cos(rad)
    tip_y = boom_base_y + boom_len * math.sin(rad)
    c.line(boom_base_x, boom_base_y, tip_x, tip_y)
    c.setLineWidth(0.8)
    c.line(tip_x, tip_y, tip_x - w * 0.04, y + h * 0.02)
    c.circle(tip_x - w * 0.04, y + h * 0.02, 1.6, fill=0, stroke=1)


def _tandem(c, x, y, w, h, base_fn):
    base_fn(c, x, y, w * 0.5, h, boom_angle=64)
    base_fn(c, x + w * 0.48, y, w * 0.5, h, boom_angle=116)
    # load between them
    c.setStrokeColor(DARK_NAVY)
    c.setLineWidth(1.1)
    load_w = w * 0.30
    load_x = x + w * 0.5 - load_w / 2
    load_y = y + h * 0.55
    c.rect(load_x, load_y, load_w, h * 0.10, fill=0, stroke=1)


def _tower_crane(c, x, y, w, h):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    mast_x = x + w * 0.35
    c.line(mast_x, y, mast_x, y + h * 0.85)
    c.line(mast_x, y + h * 0.85, x + w * 0.05, y + h * 0.80)
    c.line(mast_x, y + h * 0.85, x + w * 0.95, y + h * 0.90)
    c.setLineWidth(0.8)
    c.line(x + w * 0.85, y + h * 0.90, x + w * 0.85, y + h * 0.55)
    c.circle(x + w * 0.85, y + h * 0.55, 1.6, fill=0, stroke=1)
    # tower/turbine hint
    c.setStrokeColor(MUTED)
    c.setLineWidth(1.0)
    c.line(x + w * 0.15, y, x + w * 0.15, y + h * 0.72)
    c.circle(x + w * 0.15, y + h * 0.75, 2.2, fill=0, stroke=1)


def _lattice_truck(c, x, y, w, h):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.3)
    chassis_w = w * 0.55
    c.rect(x, y, chassis_w, h * 0.10, fill=0, stroke=1)
    for wx in (x + chassis_w * 0.2, x + chassis_w * 0.42, x + chassis_w * 0.64, x + chassis_w * 0.86):
        c.circle(wx, y, 1.6, fill=0, stroke=1)
    boom_base_x = x + chassis_w * 0.5
    boom_base_y = y + h * 0.12
    boom_len = w * 0.82
    rad = math.radians(55)
    tip_x = boom_base_x + boom_len * math.cos(rad)
    tip_y = boom_base_y + boom_len * math.sin(rad)
    # lattice zig-zag boom
    n = 6
    for i in range(n):
        t0 = i / n
        t1 = (i + 1) / n
        bx0 = boom_base_x + (tip_x - boom_base_x) * t0
        by0 = boom_base_y + (tip_y - boom_base_y) * t0
        bx1 = boom_base_x + (tip_x - boom_base_x) * t1
        by1 = boom_base_y + (tip_y - boom_base_y) * t1
        c.line(bx0, by0, bx1, by1)
    c.setLineWidth(0.8)
    c.line(tip_x, tip_y, tip_x - w * 0.04, y + h * 0.02)
    c.circle(tip_x - w * 0.04, y + h * 0.02, 1.6, fill=0, stroke=1)


def _offshore_hlv(c, x, y, w, h):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    hull_w = w * 0.9
    hull_h = h * 0.14
    hull_x = x + (w - hull_w) / 2
    c.rect(hull_x, y, hull_w, hull_h, fill=0, stroke=1)
    # two crane pedestals
    for px in (hull_x + hull_w * 0.2, hull_x + hull_w * 0.8):
        c.line(px, y + hull_h, px, y + hull_h + h * 0.45)
        c.line(px, y + hull_h + h * 0.45, hull_x + hull_w * 0.5, y + hull_h + h * 0.25)
    # module load suspended between
    load_w = w * 0.28
    load_x = hull_x + hull_w * 0.5 - load_w / 2
    c.setStrokeColor(DARK_NAVY)
    c.setLineWidth(1.0)
    c.rect(load_x, y + hull_h + h * 0.05, load_w, h * 0.12, fill=0, stroke=1)
    # waves
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.7)
    wy = y - h * 0.03
    c.line(x, wy, x + w, wy)


def _rig_moonpool(c, x, y, w, h):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.3)
    # derrick triangle
    base_l = x + w * 0.15
    base_r = x + w * 0.55
    apex_x = x + w * 0.35
    apex_y = y + h * 0.85
    c.line(base_l, y, apex_x, apex_y)
    c.line(base_r, y, apex_x, apex_y)
    c.line(base_l, y, base_r, y)
    # cross braces
    for f in (0.3, 0.55, 0.75):
        c.line(base_l + (apex_x - base_l) * f, y + (apex_y - y) * f,
               base_r + (apex_x - base_r) * f, y + (apex_y - y) * f)
    # deployment line to seabed (kept within the illustration box)
    c.setLineWidth(0.7)
    c.setStrokeColor(MUTED)
    c.line(apex_x, y + h * 0.35, apex_x, y + h * 0.06)
    c.circle(apex_x, y + h * 0.04, 1.8, fill=0, stroke=1)
    c.setDash(2, 2)
    c.line(x, y + h * 0.10, x + w, y + h * 0.10)
    c.setDash()


def _air_raise(c, x, y, w, h):
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.4)
    tank_w = w * 0.7
    tank_h = h * 0.55
    tank_x = x + (w - tank_w) / 2
    c.rect(tank_x, y, tank_w, tank_h, fill=0, stroke=1)
    # dome roof, mid-raise (dashed to show motion)
    c.setDash(2, 2)
    c.ellipse(tank_x, y + tank_h * 0.55, tank_x + tank_w, y + tank_h * 0.85, fill=0, stroke=1)
    c.setDash()
    c.ellipse(tank_x, y + tank_h, tank_x + tank_w, y + tank_h * 1.30, fill=0, stroke=1)
    # up arrows
    c.setLineWidth(0.9)
    for ax in (tank_x + tank_w * 0.3, tank_x + tank_w * 0.7):
        c.line(ax, y + tank_h * 0.3, ax, y + tank_h * 0.75)
        c.line(ax, y + tank_h * 0.75, ax - 1.6, y + tank_h * 0.68)
        c.line(ax, y + tank_h * 0.75, ax + 1.6, y + tank_h * 0.68)


ICON_DRAW_FUNCS = {
    "tandem_crawler": lambda c, x, y, w, h: _tandem(c, x, y, w, h, _crawler_crane),
    "tandem_mobile": lambda c, x, y, w, h: _tandem(c, x, y, w, h, _mobile_crane),
    "tandem_turn": lambda c, x, y, w, h: _tandem(c, x, y, w, h, _mobile_crane),
    "tower_crane": _tower_crane,
    "mobile_crane": _mobile_crane,
    "crawler_indoor": _crawler_crane,
    "offshore_hlv": _offshore_hlv,
    "rig_moonpool": _rig_moonpool,
    "lattice_truck": _lattice_truck,
    "air_raise": _air_raise,
}


def draw_cover_illustration(c, cx, cy, width=60 * mm, height=40 * mm, icon="mobile_crane"):
    """Draw equipment silhouette centered at (cx, cy)."""
    x = cx - width / 2
    y = cy - height / 2
    c.saveState()
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(x, y, width, height, fill=0, stroke=0)
    fn = ICON_DRAW_FUNCS.get(icon, _mobile_crane)
    fn(c, x, y, width, height)
    c.restoreState()


def draw_load_sketch(c, x, y, w, h, dims_text, cog_labels):
    """Simple dimensional box sketch with COG marker, drawn on canvas at (x,y) origin (bottom-left), size w x h."""
    c.saveState()
    c.setStrokeColor(DARK_NAVY)
    c.setLineWidth(1.1)
    box_w = w * 0.62
    box_h = h * 0.5
    box_x = x + w * 0.06
    box_y = y + h * 0.28
    c.rect(box_x, box_y, box_w, box_h, fill=0, stroke=1)
    # COG marker (circle with cross)
    cogx = box_x + box_w * 0.55
    cogy = box_y + box_h * 0.5
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.0)
    r = 2.6 * mm
    c.circle(cogx, cogy, r, fill=0, stroke=1)
    c.line(cogx - r, cogy, cogx + r, cogy)
    c.line(cogx, cogy - r, cogx, cogy + r)
    c.setFont("Inter", 7)
    c.setFillColor(ACCENT)
    c.drawString(cogx + r + 1.5, cogy - 2, "COG")
    # dimension lines
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.5)
    dim_y = box_y - 4 * mm
    c.line(box_x, dim_y, box_x + box_w, dim_y)
    c.line(box_x, dim_y - 1, box_x, dim_y + 1)
    c.line(box_x + box_w, dim_y - 1, box_x + box_w, dim_y + 1)
    c.setFont("Inter", 7.5)
    c.setFillColor(MUTED)
    c.drawCentredString(box_x + box_w / 2, dim_y - 8, dims_text)
    c.restoreState()

# ---------------------------------------------------------------------------
# Reusable table builders
# ---------------------------------------------------------------------------

def _p(text, style_key="TableCell"):
    return Paragraph(str(text), STYLES[style_key])


def standard_table_style(header_rows=1, col0_bold=False):
    style = [
        ("BACKGROUND", (0, 0), (-1, header_rows - 1), TABLE_HEAD_BG),
        ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), DARK_NAVY),
        ("FONTNAME", (0, 0), (-1, header_rows - 1), "DMSans-Medium"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.3),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, header_rows), (-1, -1), [WHITE, ALT_ROW_BG]),
    ]
    return TableStyle(style)


def create_parameter_table(rows, col_widths=None):
    """rows: list of (label, value) tuples. First row is header pair."""
    data = [[_p("Parameter", "TableHead"), _p("Value", "TableHead")]]
    for label, value in rows:
        data.append([_p(label, "TableCell"), _p(value, "TableCellBold")])
    col_widths = col_widths or [70 * mm, 92 * mm]
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(standard_table_style())
    return t


def create_generic_table(header, rows, col_widths):
    data = [[_p(h, "TableHead") for h in header]]
    for r in rows:
        data.append([_p(c, "TableCell") if not isinstance(c, Paragraph) else c for c in r])
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(standard_table_style())
    return t


def create_risk_table(rows):
    """rows: list of (hazard, L_before, S_before, controls, L_after, S_after)"""
    header = ["Hazard", "L", "S", "Score", "Controls", "L", "S", "Score"]
    data = [[_p(h, "TableHead") for h in header]]
    style_extra = []
    for i, (hz, lb, sb, controls, la, sa) in enumerate(rows, start=1):
        score_b = lb * sb
        score_a = la * sa
        row = [
            _p(hz, "TableCell"),
            _p(lb, "TableCell"),
            _p(sb, "TableCell"),
            _p(score_b, "TableCellBold"),
            _p(controls, "TableCell"),
            _p(la, "TableCell"),
            _p(sa, "TableCell"),
            _p(score_a, "TableCellBold"),
        ]
        data.append(row)
        # color code residual score
        color = HexColor("#437A22") if score_a <= 6 else (WARN if score_a <= 12 else HexColor("#A13544"))
        style_extra.append(("TEXTCOLOR", (7, i), (7, i), color))
    col_widths = [34 * mm, 7 * mm, 7 * mm, 11 * mm, 62 * mm, 7 * mm, 7 * mm, 11 * mm]
    t = Table(data, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    ts = standard_table_style()
    for e in style_extra:
        ts.add(*e)
    ts.add("FONTSIZE", (0, 0), (-1, -1), 7.6)
    t.setStyle(ts)
    return t


def section_heading(number, title):
    return Paragraph(f'<font color="#ff6a1a">{number:02d}</font> &nbsp; {title}', STYLES["H1"])


def sub_heading(text):
    return Paragraph(text, STYLES["H2"])


def kicker(text):
    return Paragraph(text.upper(), STYLES["H3"])


def bullets(items):
    flows = []
    for it in items:
        flows.append(Paragraph(f"\u2022 &nbsp; {it}", STYLES["Bullet"]))
    return flows


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceBefore=6, spaceAfter=10)

# ---------------------------------------------------------------------------
# Cover page (drawn directly on canvas, first page only)
# ---------------------------------------------------------------------------

def draw_cover_page(c, sc, plan_number_str):
    page_w, page_h = A4
    c.saveState()

    # background flash panel top
    c.setFillColor(DARK_NAVY)
    c.rect(0, page_h - 92 * mm, page_w, 92 * mm, fill=1, stroke=0)

    # watermark (on dark bg too, subtle)
    c.setFont("DMSans-Bold", 82)
    c.setFillColor(WHITE)
    c.setFillAlpha(0.04)
    c.saveState()
    c.translate(page_w / 2, page_h - 46 * mm)
    c.rotate(38)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()
    c.setFillAlpha(1)

    # logo
    draw_jmr_logo(c, MARGIN_LR, page_h - 26 * mm, size=11 * mm, mono=True)
    c.setFont("DMSans-Bold", 13)
    c.setFillColor(WHITE)
    c.drawString(MARGIN_LR + 16 * mm, page_h - 22 * mm, "JMR LIFTING SOLUTIONS")
    c.setFont("Inter", 8.5)
    c.setFillColor(HexColor("#c9cdd2"))
    c.drawString(MARGIN_LR + 16 * mm, page_h - 27 * mm, "Certified Heavy Lift Engineering")

    # Big title
    c.setFont("DMSans-Bold", 40)
    c.setFillColor(WHITE)
    c.drawString(MARGIN_LR, page_h - 55 * mm, "LIFT PLAN")
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2.4)
    c.line(MARGIN_LR, page_h - 59 * mm, MARGIN_LR + 32 * mm, page_h - 59 * mm)

    # Project title (wrap manually if long)
    c.setFont("DMSans-Medium", 15)
    c.setFillColor(ACCENT)
    title = sc["title"]
    max_chars = 46
    if len(title) > max_chars:
        # naive wrap on a space near midpoint
        words = title.split()
        line1, line2 = "", ""
        for wtxt in words:
            if len(line1) + len(wtxt) + 1 <= max_chars:
                line1 = (line1 + " " + wtxt).strip()
            else:
                line2 = (line2 + " " + wtxt).strip()
        c.drawString(MARGIN_LR, page_h - 70 * mm, line1)
        c.drawString(MARGIN_LR, page_h - 77 * mm, line2)
    else:
        c.drawString(MARGIN_LR, page_h - 70 * mm, title)

    c.setFont("Inter", 9)
    c.setFillColor(HexColor("#c9cdd2"))
    c.drawString(MARGIN_LR, page_h - 87 * mm, f"Plan number: {plan_number_str}")

    c.restoreState()

    # Cover illustration below dark panel
    illo_cy = page_h - 92 * mm - 26 * mm
    draw_cover_illustration(c, page_w / 2, illo_cy, width=70 * mm, height=42 * mm, icon=sc["icon"])

    # Info panel (below illustration)
    info_top = illo_cy - 30 * mm
    c.setFont("Inter", 9)
    rows = [
        ("Client", "[CLIENT CONFIDENTIAL]"),
        ("Location", "[LOCATION CONFIDENTIAL]"),
        ("Revision", "Rev 0 \u2014 SAMPLE"),
        ("Date", TODAY),
        ("Prepared by", PREPARED_BY),
        ("AP Certificate No.", CERT_NO),
        ("Reviewed by", REVIEWED_BY),
        ("Standards", STANDARDS_LINE),
    ]
    label_x = MARGIN_LR
    value_x = MARGIN_LR + 42 * mm
    y = info_top
    line_h = 6.6 * mm
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.6)
    c.line(MARGIN_LR, y + 4 * mm, page_w - MARGIN_LR, y + 4 * mm)
    for label, value in rows:
        c.setFont("Inter-Medium", 8.5)
        c.setFillColor(MUTED)
        c.drawString(label_x, y, label.upper())
        c.setFont("Inter", 9.5)
        c.setFillColor(BODY)
        # wrap long values
        max_w = page_w - MARGIN_LR - value_x
        if pdfmetrics.stringWidth(value, "Inter", 9.5) > max_w:
            c.setFont("Inter", 8)
        c.drawString(value_x, y, value)
        y -= line_h
    c.setStrokeColor(BORDER)
    c.line(MARGIN_LR, y + 3 * mm, page_w - MARGIN_LR, y + 3 * mm)

    # Footer disclaimer
    c.setFont("Inter-Italic", 7.8)
    c.setFillColor(MUTED)
    c.drawCentredString(
        page_w / 2, 14 * mm,
        "SAMPLE DOCUMENT \u2014 For demonstration purposes. Actual project plans include site-specific data."
    )
    c.setFont("Inter", 7.5)
    c.drawCentredString(page_w / 2, 10 * mm, CONTACT_EMAIL)


# ---------------------------------------------------------------------------
# Section builders (return list of flowables)
# ---------------------------------------------------------------------------

def section_exec_summary(sc):
    flows = [section_heading(1, "Executive Summary & Scope")]
    flows.append(Paragraph(sc["scope"], STYLES["Body"]))
    flows.append(Spacer(1, 4))
    flows.append(sub_heading("Key Parameters"))
    param_rows = [
        ("Load weight (t)", f"{sc['load_t']} t"),
        ("Dimensions (L \u00d7 W \u00d7 H)", sc["dims"]),
        ("Lift radius (m)", f"{sc['radius_m']} m" if sc["radius_m"] else "N/A \u2014 vertical raise"),
        ("Lift height (m)", f"{sc['lift_height_m']} m"),
        ("Duration (est.)", sc["duration"]),
        ("Location", sc["location"]),
    ]
    flows.append(create_parameter_table(param_rows))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Critical Risks"))
    crit_risks = [
        "Load overload beyond crane rated capacity at working radius",
        "Loss of control during dynamic/weather-sensitive lift phases",
        "Rigging failure due to incorrect sling angle or WLL selection",
        "Ground/foundation bearing failure under crane or outrigger loads",
    ]
    if "revision_note" in sc:
        crit_risks.insert(0, "Initial crane/radius selection required engineering revision \u2014 see Section 05")
    flows.extend(bullets(crit_risks))
    return flows


def section_load_data(sc):
    flows = [section_heading(2, "Load Data, Centre of Gravity & Dimensions")]
    flows.append(Paragraph(sc["load_desc"], STYLES["Body"]))
    flows.append(sub_heading("Weight Breakdown"))
    rows = [(label, val) for label, val in sc["weight_breakdown"]]
    flows.append(create_generic_table(
        ["Component", "Weight"], rows, col_widths=[120 * mm, 42 * mm]
    ))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Centre of Gravity"))
    cog_rows = [("X-axis", sc["cog"][0]), ("Y-axis", sc["cog"][1]), ("Z-axis", sc["cog"][2])]
    flows.append(create_parameter_table(cog_rows, col_widths=[50 * mm, 112 * mm]))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Lift Points"))
    flows.append(Paragraph(sc["lift_points"], STYLES["Body"]))
    flows.append(Spacer(1, 10))
    flows.append(sub_heading("Dimensional Sketch"))
    flows.append(Paragraph(
        "Simplified load outline with centre-of-gravity marker (not to scale):",
        STYLES["Muted"]
    ))

    def _sketch_drawer(dims_text, cog_labels):
        from reportlab.platypus import Flowable

        class SketchFlowable(Flowable):
            def __init__(self, w, h):
                Flowable.__init__(self)
                self.width = w
                self.height = h

            def draw(self):
                draw_load_sketch(self.canv, 0, 0, self.width, self.height, dims_text, cog_labels)

        return SketchFlowable(160 * mm, 34 * mm)

    flows.append(_sketch_drawer(sc["dims"], sc["cog"]))
    return flows


def section_crane_selection(sc):
    flows = [section_heading(3, "Crane Selection & Configuration")]
    for i, cr in enumerate(sc["cranes"], start=1):
        label = f"Crane {i}" if len(sc["cranes"]) > 1 else "Selected Crane"
        flows.append(sub_heading(f"{label}: {cr['model']}"))
        rows = [
            ("Rated capacity", f"{cr['capacity_t']} t" if cr["capacity_t"] else "N/A"),
            ("Boom length", f"{cr['boom_m']} m" if cr.get("boom_m") else "See configuration"),
            ("Configuration", cr["config"]),
            ("Working radius", f"{cr['radius_m']} m" if cr["radius_m"] else "N/A"),
            ("Capacity at working radius", f"{cr['capacity_at_radius_t']} t" if cr["capacity_at_radius_t"] else "See load chart notes"),
        ]
        flows.append(create_parameter_table(rows))
        flows.append(Spacer(1, 6))
    flows.append(sub_heading("Utilization Calculation"))
    flows.append(Paragraph(sc["util_calc"], STYLES["Body"]))
    if sc.get("util_pct") is not None:
        is_final_accepted = sc.get("revision_accepted", False)
        exceeds = sc["util_pct"] > 85 and not is_final_accepted
        util_color = "#A13544" if exceeds else "#437A22"
        if is_final_accepted:
            note = "(final revised value \u2014 ACCEPTED within safe working limit; see revision note below)"
        elif exceeds:
            note = "(exceeds 85% threshold \u2014 see revision note below)"
        else:
            note = "(within 85% safe working threshold)"
        flows.append(Paragraph(
            f'Utilization result: <font color="{util_color}"><b>{sc["util_pct"]}%</b></font> {note}',
            STYLES["Body"]
        ))
    if "revision_note" in sc:
        flows.append(Spacer(1, 6))
        flows.append(sub_heading("Engineering Revision Note"))
        for para in sc["revision_note"].split("\n\n"):
            style = "Warn" if para.strip().startswith(("WARNING", "INITIAL", "REVISION STEP 2")) else "BodyLeft"
            flows.append(Paragraph(para.replace("\n", "<br/>"), STYLES[style]))
    gb = sc["ground_bearing"]
    flows.append(Spacer(1, 6))
    flows.append(sub_heading("Ground Bearing Pressure"))
    flows.append(Paragraph(gb["calc_text"], STYLES["Body"]))
    flows.append(sub_heading("Standing / Pick Radius"))
    flows.append(Paragraph(
        f"Working radius maintained at {sc['radius_m']} m throughout the critical lift phase."
        if sc["radius_m"] else "Vertical lift/raise \u2014 no working radius applicable.",
        STYLES["Body"]
    ))
    return flows


def section_load_chart(sc):
    flows = [section_heading(4, "Load Chart & Utilization Calculation")]
    if sc["load_chart"]:
        flows.append(Paragraph(
            "Manufacturer load chart extract for the selected boom/jib configuration:",
            STYLES["Body"]
        ))
        rows = []
        for radius, cap in sc["load_chart"]:
            highlight = sc.get("working_radius_highlight") == radius
            r_txt = f"<b>{radius} m \u2192 WORKING POINT</b>" if highlight else f"{radius} m"
            c_txt = f"<b>{cap} t</b>" if highlight else f"{cap} t"
            rows.append([Paragraph(r_txt, STYLES["TableCell"]), Paragraph(c_txt, STYLES["TableCell"])])
        flows.append(create_generic_table(["Radius", "Capacity"], rows, col_widths=[81 * mm, 81 * mm]))
    else:
        flows.append(Paragraph(
            "Not applicable \u2014 this lift is executed by pneumatic air-raise method; "
            "no crane load chart governs the primary lift operation.",
            STYLES["Body"]
        ))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Dynamic Amplification Factor (DAF)"))
    daf_txt = f"DAF applied: <b>{sc['daf']}</b>" if sc["daf"] else "Not applicable to pneumatic air-raise method."
    flows.append(Paragraph(daf_txt, STYLES["Body"]))
    flows.append(sub_heading("Total Lifted Load Including DAF"))
    flows.append(Paragraph(sc["util_calc"], STYLES["Body"]))
    flows.append(Spacer(1, 8))
    gb = sc["ground_bearing"]
    flows.append(sub_heading("Ground Pressure Calculation"))
    flows.append(Paragraph(gb["calc_text"], STYLES["Body"]))
    if gb.get("pressure_kpa") is not None:
        rows = [
            ("Calculated ground pressure", f"{gb['pressure_kpa']} kPa"),
            ("Allowable bearing pressure", f"{gb['allowable_kpa']} kPa"),
            ("Crane pad / matting", gb["pad"]),
        ]
        flows.append(create_parameter_table(rows))
    return flows


def section_rigging_config(sc):
    flows = [section_heading(5, "Rigging Configuration")]
    rg = sc["rigging"]
    rows = [
        ("Sling type", rg["sling_type"]),
        ("Sling angle (min.)", f"{rg['angle_deg']}\u00b0" if rg["angle_deg"] else "N/A"),
        ("Number of slings", str(rg["n_slings"]) if rg["n_slings"] else "N/A"),
        ("WLL per sling", f"{rg['wll_each_t']} t" if rg["wll_each_t"] else "N/A"),
        ("Shackle grade", rg["shackle"]),
        ("Spreader / master link", rg["spreader"]),
    ]
    flows.append(create_parameter_table(rows))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Rigging Schematic (Summary)"))
    schem_rows = [
        ["Component", "Specification"],
        ["Hook / block", "Rated to crane main hoist capacity, latch-equipped"],
        ["Master link / spreader", rg["spreader"]],
        ["Sling legs", f"{rg['n_slings'] or 'N/A'} \u00d7 {rg['sling_type']}"],
        ["Shackles", rg["shackle"]],
        ["Sling angle from horizontal", f"{rg['angle_deg']}\u00b0 (minimum safe angle 60\u00b0 unless noted)" if rg["angle_deg"] else "N/A"],
    ]
    flows.append(create_generic_table(schem_rows[0], schem_rows[1:], col_widths=[55*mm, 107*mm]))
    if sc["radius_m"] and rg.get("angle_deg"):
        flows.append(Spacer(1, 8))
        flows.append(sub_heading("Sling Length Calculation"))
        flows.append(Paragraph(
            f"With a sling angle of {rg['angle_deg']}\u00b0 from horizontal, sling length is derived "
            f"from headroom and spread geometry per rigging arrangement drawing; angle maintained "
            f"\u2265 the minimum safe angle for the configuration.",
            STYLES["Body"]
        ))
    return flows


def section_rigging_calcs(sc):
    flows = [section_heading(6, "Rigging Load Calculations")]
    rg = sc["rigging"]
    flows.append(sub_heading("Individual Sling Load"))
    flows.append(Paragraph(
        "Formula: Sling load = (Load \u00d7 DAF) \u00f7 (n \u00d7 sin \u03b8)", STYLES["Body"]
    ))
    flows.append(Paragraph(rg["calc_text"], STYLES["Body"]))
    if rg.get("sling_load_t") is not None and rg.get("wll_each_t"):
        util = round(rg["sling_load_t"] / rg["wll_each_t"] * 100, 1)
        flows.append(Spacer(1, 6))
        rows = [
            ("Calculated sling load", f"{rg['sling_load_t']} t"),
            ("Selected sling WLL", f"{rg['wll_each_t']} t"),
            ("Sling utilization", f"{util}%"),
            ("Sling safety factor (design)", "5:1 minimum"),
            ("Shackle safety factor (design)", "4:1 minimum"),
        ]
        flows.append(create_parameter_table(rows))
    else:
        flows.append(Paragraph(
            "Not applicable \u2014 no crane rigging loads for this lift method.", STYLES["Body"]
        ))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Safety Factor Basis"))
    flows.append(Paragraph(
        "All wire rope slings are selected to a minimum design factor of 5:1 against "
        "minimum breaking load, in accordance with LEEA COPSULE guidance. All shackles "
        "are selected to a minimum design factor of 4:1. Working load limits (WLL) are "
        "marked and certificated per item.",
        STYLES["Body"]
    ))
    return flows


def section_ground_bearing(sc):
    flows = [section_heading(7, "Ground Bearing & Site Layout")]
    gb = sc["ground_bearing"]
    flows.append(sub_heading("Ground Bearing Pressure"))
    flows.append(Paragraph(gb["calc_text"], STYLES["Body"]))
    if gb.get("pressure_kpa") is not None:
        rows = [
            ("Ground bearing pressure (required)", f"{gb['pressure_kpa']} kPa"),
            ("Allowable bearing pressure (site)", f"{gb['allowable_kpa']} kPa"),
            ("Margin", f"{round((1 - gb['pressure_kpa']/gb['allowable_kpa'])*100,1)}% below allowable"),
        ]
        flows.append(create_parameter_table(rows))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Crane Pad / Matting"))
    flows.append(Paragraph(gb["pad"], STYLES["Body"]))
    flows.append(Spacer(1, 8))
    flows.append(sub_heading("Site Plan (Schematic)"))
    flows.append(Paragraph(
        "Simplified site layout showing crane standing position, load path, and exclusion zone (not to scale):",
        STYLES["Muted"]
    ))

    def _site_plan(w, h):
        from reportlab.platypus import Flowable

        class SitePlanFlowable(Flowable):
            def __init__(self, w, h, sc):
                Flowable.__init__(self)
                self.width = w
                self.height = h
                self.sc = sc

            def draw(self):
                c = self.canv
                c.saveState()
                c.setStrokeColor(BORDER)
                c.setLineWidth(0.6)
                c.rect(0, 0, self.width, self.height, fill=0, stroke=1)
                cx, cy = self.width * 0.28, self.height * 0.5
                c.setStrokeColor(ACCENT)
                c.setLineWidth(1.2)
                c.circle(cx, cy, 3 * mm, fill=0, stroke=1)
                c.setFont("Inter", 7)
                c.setFillColor(MUTED)
                c.drawCentredString(cx, cy - 6 * mm, "Crane standing position")
                lx, ly = self.width * 0.72, self.height * 0.5
                c.setStrokeColor(DARK_NAVY)
                c.rect(lx - 6*mm, ly - 4*mm, 12*mm, 8*mm, fill=0, stroke=1)
                c.drawCentredString(lx, ly - 8 * mm, "Load set position")
                c.setDash(2, 2)
                c.setStrokeColor(MUTED)
                c.line(cx, cy, lx, ly)
                c.setDash()
                # exclusion zone
                c.setStrokeColor(WARN)
                c.setLineWidth(0.6)
                c.circle(cx, cy, self.width * 0.30, fill=0, stroke=1)
                c.setFont("Inter-Italic", 6.5)
                c.setFillColor(WARN)
                c.drawString(2, self.height - 8, "Exclusion zone (dashed, radius per method statement)")
                c.restoreState()

        return SitePlanFlowable(w, h, sc)

    flows.append(_site_plan(160 * mm, 42 * mm))
    return flows


BASE_RISK_ROWS = [
    ("Overload beyond crane capacity", 3, 5, "Load chart verified; utilization capped below 85%; independent AP check", 1, 5),
    ("Crane mechanical/structural failure", 2, 5, "Pre-use inspection; current LOLER thorough examination certificate", 1, 5),
    ("Load drop during lift", 2, 5, "Certified rigging, redundant sling legs, trial lift at 25% load", 1, 5),
    ("Adverse weather conditions", 3, 3, "Weather forecast monitoring; defined go/no-go thresholds", 1, 3),
    ("Personnel struck by load/rigging", 3, 4, "Exclusion zone enforced; banksman control; no personnel under suspended load", 1, 4),
    ("Ground/foundation failure", 2, 5, "Ground bearing calculation verified; crane mats/pads sized to load", 1, 4),
    ("Sling/shackle failure", 2, 5, "Certified rigging to 5:1 (sling) / 4:1 (shackle) design factor; pre-use inspection", 1, 5),
    ("Overhead obstruction contact", 2, 4, "Route survey completed; spotter assigned; boom angle indicator monitored", 1, 3),
]


def section_risk_assessment(sc):
    flows = [section_heading(8, "Risk Assessment (BS 7121 Format)")]
    flows.append(Paragraph(
        "Risk scoring uses Likelihood (L) \u00d7 Severity (S), each rated 1\u20135. "
        "Residual score after controls is shown in the right-hand columns.",
        STYLES["Body"]
    ))
    flows.append(Spacer(1, 4))
    rows = list(BASE_RISK_ROWS)
    for extra in sc.get("risks_extra", []):
        rows.append(extra)
    flows.append(create_risk_table(rows))
    flows.append(Spacer(1, 6))
    flows.append(Paragraph(
        "Risk score key: <font color=\"#437A22\"><b>1\u20136 Low</b></font> \u00b7 "
        "<font color=\"#964219\"><b>7\u201312 Medium</b></font> \u00b7 "
        "<font color=\"#A13544\"><b>13\u201325 High</b></font> \u2014 all residual scores must be Low "
        "or Medium with documented additional controls before lift authorization.",
        STYLES["Small"]
    ))
    return flows


def section_method_statement(sc):
    flows = [section_heading(9, "Method Statement")]
    steps = [
        "Confirm current LOLER thorough examination certificates for crane(s), rigging, and lifting accessories.",
        "Conduct toolbox talk with all lift personnel; confirm roles per Section 11.",
        "Establish exclusion zone and barrier the lift area; brief banksman and signaller.",
        "Position crane(s) on verified ground bearing / matting per Section 07; set outriggers (if mobile) to full extension.",
        "Rig load per configuration in Section 05; attach taglines; conduct visual rigging inspection.",
        "Perform trial lift: raise load approximately 300 mm, hold at 25% of test criteria for a minimum dwell to verify rigging geometry, crane response, and brake holding.",
        "Confirm sling angles, load indicator readings, and COG behavior match plan before proceeding.",
        f"Execute main lift at working radius {sc['radius_m']} m" if sc["radius_m"] else "Execute main lift per pneumatic air-raise procedure",
        "Travel/luff/slew load along planned path, maintaining radius and load chart compliance throughout.",
        "Position load over set point; lower under controlled taglines to final bearing/foundation.",
        "Confirm secure landing, release rigging tension gradually, and inspect for damage.",
        "De-rig, remove accessories, and return crane to travel/stow configuration.",
        "Conduct post-lift debrief and close out permit-to-work documentation.",
    ]
    if "revision_note" in sc:
        steps.insert(3, "Verify revised crane selection and working radius per Section 03/04 engineering revision note before mobilization.")
    for i, s_txt in enumerate(steps, start=1):
        flows.append(Paragraph(f"<b>{i}.</b> &nbsp; {s_txt}", STYLES["Bullet"]))
    return flows


def section_roles(sc):
    flows = [section_heading(10, "Roles & Responsibilities")]
    rows = [
        ["Appointed Person", PREPARED_BY + f" (Cert. No. {CERT_NO}) \u2014 overall lift planning responsibility"],
        ["Lift Supervisor", "[TBD \u2014 assigned at mobilization, LEEA/CPCS certified]"],
        ["Crane Operator(s)", "[Certified operator(s), current CPCS/NPORS or equivalent license]"],
        ["Slinger / Signaller", "[Certified slinger/signaller per LEEA/CPCS standard]"],
        ["Banksman", "[Certified banksman \u2014 controls exclusion zone and ground personnel]"],
        ["Reviewed by", REVIEWED_BY],
    ]
    flows.append(create_generic_table(["Role", "Assignment"], rows, col_widths=[45*mm, 117*mm]))
    flows.append(Spacer(1, 10))
    flows.append(sub_heading("Contact"))
    flows.append(Paragraph(f"JMR Lifting Solutions \u2014 {CONTACT_EMAIL}", STYLES["Body"]))
    return flows


def section_approvals(sc):
    flows = [section_heading(11, "Approvals & References")]
    flows.append(sub_heading("Signature Block"))
    sig_rows = [
        ["Appointed Person", PREPARED_BY, ""],
        ["Client Representative", "[CLIENT CONFIDENTIAL]", ""],
        ["HSE Representative", "[TBD]", ""],
        ["Client Project Manager", "[CLIENT CONFIDENTIAL]", ""],
    ]
    flows.append(create_generic_table(["Role", "Name", "Signature / Date"], sig_rows, col_widths=[45*mm, 62*mm, 55*mm]))
    flows.append(Spacer(1, 10))
    flows.append(sub_heading("References"))
    refs = [
        "BS 7121-1:2016 \u2014 Code of practice for the safe use of cranes",
        "LOLER 1998 \u2014 Lifting Operations and Lifting Equipment Regulations (UK)",
        "ASME B30.5 \u2014 Mobile and Locomotive Cranes",
        "LEEA COPSULE \u2014 Code of Practice for the Safe Use of Lifting Equipment",
        "Crane manufacturer load chart (referenced Section 04/05)",
    ]
    flows.extend(bullets(refs))
    flows.append(Spacer(1, 10))
    flows.append(Paragraph(
        "This document is a SAMPLE lift plan produced for demonstration purposes only. "
        "It does not constitute an approved lift plan for any live lifting operation. "
        "Actual JMR Lifting Solutions project deliverables include site-specific surveys, "
        "certified equipment schedules, and a signed authorization prior to any lift.",
        STYLES["Small"]
    ))
    return flows


SECTION_BUILDERS = [
    section_exec_summary,
    section_load_data,
    section_crane_selection,
    section_load_chart,
    section_rigging_config,
    section_rigging_calcs,
    section_ground_bearing,
    section_risk_assessment,
    section_method_statement,
    section_roles,
    section_approvals,
]


def _make_numbered_canvas_factory(sc):
    from reportlab.pdfgen.canvas import Canvas

    class _Canvas(Canvas):
        def __init__(self, *args, **kwargs):
            Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_footer_page_count(total_pages)
                Canvas.showPage(self)
            Canvas.save(self)

        def _draw_footer_page_count(self, total_pages):
            if self._pageNumber == 1:
                return  # cover page has its own footer drawn in draw_cover_page
            page_w, page_h = A4
            footer_y = MARGIN_BOTTOM - 8 * mm
            self.saveState()
            self.setFont("Inter", 7.5)
            self.setFillColor(MUTED)
            self.drawString(
                MARGIN_LR, footer_y,
                f"Page {self._pageNumber} of {total_pages} \u00b7 SAMPLE DOCUMENT \u00b7 {CONTACT_EMAIL}"
            )
            self.restoreState()

    return _Canvas


def build_pdf(sc, plan_index):
    plan_number_str = f"LP-2026-{plan_index:03d}"
    out_path = OUT_DIR / sc["filename"]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        title=f"JMR Lift Plan \u2014 {sc['title']}",
        author="Perplexity Computer",
        topMargin=MARGIN_TOP + 6 * mm,
        bottomMargin=MARGIN_BOTTOM + 4 * mm,
        leftMargin=MARGIN_LR,
        rightMargin=MARGIN_LR,
    )

    story = []
    # Cover is drawn entirely on canvas via onFirstPage-like hook; we still need
    # a page in the story to trigger page 1. Use an invisible spacer + PageBreak.
    story.append(Spacer(1, 0))
    story.append(PageBreak())

    for builder in SECTION_BUILDERS:
        section_flows = builder(sc)
        story.append(KeepTogether(section_flows[:2]))
        story.extend(section_flows[2:])
        story.append(Spacer(1, 10))
        story.append(PageBreak())

    # remove trailing page break
    if isinstance(story[-1], PageBreak):
        story.pop()

    header_footer_cb = make_header_footer(sc["code"], sc["title"])

    def on_first_page(c, d):
        draw_cover_page(c, sc, plan_number_str)

    def on_later_pages(c, d):
        header_footer_cb(c, d)

    canvas_maker = _make_numbered_canvas_factory(sc)
    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages, canvasmaker=canvas_maker)

    return out_path


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def main():
    results = []
    for idx, sc in enumerate(SCENARIOS, start=1):
        print(f"Building {sc['code']} — {sc['title']} ...")
        try:
            path = build_pdf(sc, idx)
            size_kb = path.stat().st_size / 1024
            print(f"  -> {path.name} ({size_kb:.1f} KB)")
            results.append((sc["code"], path.name, size_kb))
        except Exception as e:
            print(f"  !! FAILED: {sc['code']}: {e}")
            raise
    print("\nDone. Summary:")
    for code, name, size_kb in results:
        print(f"  {code}: {name} — {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
