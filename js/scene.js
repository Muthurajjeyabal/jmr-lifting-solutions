/* ============================================================
   MU Lifting Engineering — Scroll Animation Engine v3
   - Vessel STAYS ABOVE GROUND at all rotation angles
   - Realistic crawler crane: A-frame gantry, back stays, counterweight
   - Realistic mobile crane: telescopic boom, all-terrain carrier
   - Booms are FIXED, only wires/hooks move
   ============================================================ */

(function () {
  'use strict';

  /* ---- Geometry Constants ---- */
  var G = {
    viewBoxW: 1600,
    viewBoxH: 1200,
    groundY: 1080,

    /* Vessel dimensions */
    vesselR: 55,
    vesselLength: 620,      /* head to tail total length */
    mainLugOffset: 140,     /* main lug distance from head end */
    /* trunnionDist = distance between main lug and tail lug */
    trunnionDist: 300,

    /* Vessel position - dynamic:
       When flat (0°): main pivot Y = groundY - vesselR - 5 = 1020 (vessel rests on ground)
       When vertical (90°): main pivot Y must be at 540 so tail end (480 below) stays above ground
       We LERP the pivot Y from flatY to liftedY as vessel rotates.
    */
    mainPivot: { x: 720, y: 1020 },   /* base flat position */
    mainPivotFlat: 1020,
    mainPivotLifted: 540,

    /* Crane positions */
    crawlerBase: { x: 240, y: 1050 },        /* track center */
    crawlerBoomTip: { x: 720, y: 220 },      /* directly above main pivot, high up */

    mobileBase: { x: 1360, y: 1050 },        /* carrier center */
    mobileBoomTip: { x: 1020, y: 280 },      /* above tail lug when flat (720+300=1020) */

    hookRestOffsetY: 50    /* hook starts 50px below boom tip */
  };

  /* ---- Utility ---- */
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function easeInOutCubic(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  function easeInOutQuad(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
  function rad(d) { return d * Math.PI / 180; }
  function deg(r) { return r * 180 / Math.PI; }

  /* Compute main pivot Y based on rotation - vessel LIFTS as it rotates up.
     Need to lift FAST ENOUGH that tail end stays above ground.
     Tail end distance from pivot = trunnionDist + 120 = 420
     Tail end Y = pivotY + 420*sin(rot)
     Constraint: pivotY + 420*sin(rot) <= groundY - 20 (clearance)
     So: pivotY <= 1060 - 420*sin(rot)
     At rot=5°: pivotY <= 1060 - 37 = 1023 (safe at 1020)
     At rot=45°: pivotY <= 1060 - 297 = 763
     At rot=90°: pivotY <= 1060 - 420 = 640, but we use 540 for extra clearance
     So we track this ceiling: pivotY = min(mainPivotFlat, 1060 - 420*sin(rot))
  */
  function mainPivotYForRotation(vesselRot) {
    /* At 0°, vessel rests on ground */
    if (vesselRot < 0.5) return G.mainPivotFlat;
    var r = rad(vesselRot);
    var sinR = Math.sin(r);
    var cosR = Math.cos(r);
    /* Farthest-down point of vessel body relative to pivot: tail-end bottom corner */
    var farYOffset = (G.trunnionDist + 120) * sinR + G.vesselR * cosR;
    var maxPivotY = G.groundY - 25 - farYOffset;
    /* Never go higher than fully-lifted position */
    var minPivotY = G.mainPivotLifted;
    var y = Math.min(G.mainPivotFlat, maxPivotY);
    if (y < minPivotY) y = minPivotY;
    return y;
  }

  /* Compute vessel head/tail positions given rotation */
  function vesselPoints(vesselRot) {
    var r = rad(vesselRot);
    var cos = Math.cos(r), sin = Math.sin(r);
    var pivotY = mainPivotYForRotation(vesselRot);
    var main = { x: G.mainPivot.x, y: pivotY };
    /* Tail lug at trunnionDist along vessel axis */
    var tail = {
      x: main.x + G.trunnionDist * cos,
      y: main.y + G.trunnionDist * sin
    };
    /* Head end at -mainLugOffset along vessel axis */
    var head = {
      x: main.x - G.mainLugOffset * cos,
      y: main.y - G.mainLugOffset * sin
    };
    /* Tail end (extreme) at (trunnionDist + extra) */
    var tailEnd = {
      x: main.x + (G.trunnionDist + 120) * cos,
      y: main.y + (G.trunnionDist + 120) * sin
    };
    return { main: main, tail: tail, head: head, tailEnd: tailEnd };
  }

  /* DOM helpers */
  function setLine(id, x1, y1, x2, y2) {
    var el = document.getElementById(id);
    if (el) {
      el.setAttribute('x1', x1); el.setAttribute('y1', y1);
      el.setAttribute('x2', x2); el.setAttribute('y2', y2);
    }
  }
  function setOpacity(id, val) {
    var el = document.getElementById(id);
    if (el) el.style.opacity = val;
  }
  function setSvgTransform(id, x, y, angle) {
    var el = document.getElementById(id);
    if (el) el.setAttribute('transform', 'translate(' + x + ',' + y + ') rotate(' + angle + ')');
  }
  function setSvgTranslate(id, x, y) {
    var el = document.getElementById(id);
    if (el) el.setAttribute('transform', 'translate(' + x + ',' + (y || 0) + ')');
  }

  /* ============================================================
     SVG GENERATION - GROUND
     ============================================================ */

  function svgGround() {
    var s = '';
    s += '<line x1="0" y1="' + G.groundY + '" x2="' + G.viewBoxW + '" y2="' + G.groundY + '" stroke="#ff6a1a" stroke-width="1.4" stroke-opacity="0.7"/>';
    for (var x = 0; x < G.viewBoxW; x += 22) {
      s += '<line x1="' + x + '" y1="' + G.groundY + '" x2="' + (x + 16) + '" y2="' + (G.groundY + 20) + '" stroke="#555" stroke-width="0.7"/>';
    }
    for (var x2 = 10; x2 < G.viewBoxW; x2 += 55) {
      s += '<line x1="' + x2 + '" y1="' + (G.groundY + 2) + '" x2="' + (x2 + 18) + '" y2="' + (G.groundY + 2) + '" stroke="#666" stroke-width="0.5"/>';
    }
    return s;
  }

  /* ============================================================
     CRAWLER CRANE — Realistic with A-frame gantry, back stays, counterweight
     Base at G.crawlerBase, boom pivots up from cab, boom tip at G.crawlerBoomTip
     ============================================================ */

  function svgCrawlerCrane() {
    var cx = G.crawlerBase.x;
    var groundY = G.groundY;
    var boomTip = G.crawlerBoomTip;
    var s = '';

    /* --- TRACK ASSEMBLY (bottom) --- */
    var trackY = groundY - 30;
    var trackW = 380, trackH = 60;
    /* Track base */
    s += '<path d="M ' + (cx - trackW/2) + ' ' + trackY + ' L ' + (cx + trackW/2) + ' ' + trackY + ' L ' + (cx + trackW/2 + 15) + ' ' + (trackY + trackH) + ' L ' + (cx - trackW/2 - 15) + ' ' + (trackY + trackH) + ' Z" fill="#e8e8e8" stroke="#222" stroke-width="2.5"/>';
    /* Track shoes (top surface) */
    for (var tx = cx - trackW/2 + 8; tx < cx + trackW/2 - 6; tx += 14) {
      s += '<line x1="' + tx + '" y1="' + (trackY + 3) + '" x2="' + tx + '" y2="' + (trackY + trackH - 3) + '" stroke="#888" stroke-width="0.8"/>';
    }
    s += '<line x1="' + (cx - trackW/2) + '" y1="' + (trackY + 12) + '" x2="' + (cx + trackW/2) + '" y2="' + (trackY + 12) + '" stroke="#666" stroke-width="0.8"/>';
    /* Drive sprocket (rear/left) */
    s += '<circle cx="' + (cx - trackW/2 + 25) + '" cy="' + (trackY + trackH/2) + '" r="26" fill="#d8d8d8" stroke="#222" stroke-width="2"/>';
    s += '<circle cx="' + (cx - trackW/2 + 25) + '" cy="' + (trackY + trackH/2) + '" r="12" fill="#bbb" stroke="#444" stroke-width="1.2"/>';
    for (var a = 0; a < 360; a += 30) {
      var ar = rad(a);
      var sx1 = cx - trackW/2 + 25 + 15 * Math.cos(ar);
      var sy1 = trackY + trackH/2 + 15 * Math.sin(ar);
      var sx2 = cx - trackW/2 + 25 + 24 * Math.cos(ar);
      var sy2 = trackY + trackH/2 + 24 * Math.sin(ar);
      s += '<line x1="' + sx1 + '" y1="' + sy1 + '" x2="' + sx2 + '" y2="' + sy2 + '" stroke="#666" stroke-width="0.9"/>';
    }
    /* Idler wheel (front) */
    s += '<circle cx="' + (cx + trackW/2 - 25) + '" cy="' + (trackY + trackH/2) + '" r="24" fill="#d8d8d8" stroke="#222" stroke-width="2"/>';
    s += '<circle cx="' + (cx + trackW/2 - 25) + '" cy="' + (trackY + trackH/2) + '" r="10" fill="#bbb" stroke="#444" stroke-width="1.2"/>';
    /* Bottom rollers */
    var rollers = [80, 130, 180, 230, 280, 330];
    for (var i = 0; i < rollers.length; i++) {
      var rx = cx - trackW/2 + rollers[i];
      s += '<circle cx="' + rx + '" cy="' + (trackY + trackH - 6) + '" r="8" fill="#eee" stroke="#333" stroke-width="1.2"/>';
      s += '<circle cx="' + rx + '" cy="' + (trackY + trackH - 6) + '" r="3" fill="#999"/>';
    }
    /* Top rollers */
    for (var j = 0; j < 3; j++) {
      var trx = cx - 80 + j * 80;
      s += '<circle cx="' + trx + '" cy="' + (trackY + 6) + '" r="6" fill="#eee" stroke="#444" stroke-width="1"/>';
    }

    /* --- CARBODY / UPPER STRUCTURE BASE --- */
    var carY = trackY - 30;
    s += '<rect x="' + (cx - 140) + '" y="' + carY + '" width="280" height="30" fill="#e0e0e0" stroke="#222" stroke-width="2"/>';
    s += '<line x1="' + (cx - 140) + '" y1="' + (carY + 12) + '" x2="' + (cx + 140) + '" y2="' + (carY + 12) + '" stroke="#999" stroke-width="0.7"/>';
    /* Slew bearing */
    s += '<ellipse cx="' + cx + '" cy="' + carY + '" rx="90" ry="8" fill="#d0d0d0" stroke="#333" stroke-width="1.5"/>';

    /* --- UPPER STRUCTURE (revolving deck) --- */
    var deckY = carY - 80;
    /* Deck platform */
    s += '<path d="M ' + (cx - 130) + ' ' + deckY + ' L ' + (cx + 130) + ' ' + deckY + ' L ' + (cx + 140) + ' ' + carY + ' L ' + (cx - 140) + ' ' + carY + ' Z" fill="#f0f0f0" stroke="#222" stroke-width="2.2"/>';
    /* Platform detail lines */
    s += '<line x1="' + (cx - 125) + '" y1="' + (deckY + 20) + '" x2="' + (cx + 125) + '" y2="' + (deckY + 20) + '" stroke="#bbb" stroke-width="0.8"/>';
    s += '<line x1="' + (cx - 125) + '" y1="' + (deckY + 50) + '" x2="' + (cx + 125) + '" y2="' + (deckY + 50) + '" stroke="#bbb" stroke-width="0.8"/>';

    /* --- COUNTERWEIGHT (rear/left) --- */
    var cwX = cx - 105;
    var cwY = deckY - 60;
    s += '<rect x="' + (cwX - 55) + '" y="' + cwY + '" width="90" height="80" fill="#c8c8c8" stroke="#222" stroke-width="2.2"/>';
    /* Counterweight stacked blocks */
    for (var cb = 1; cb <= 3; cb++) {
      s += '<line x1="' + (cwX - 55) + '" y1="' + (cwY + cb * 20) + '" x2="' + (cwX + 35) + '" y2="' + (cwY + cb * 20) + '" stroke="#666" stroke-width="0.9"/>';
    }
    /* Counterweight label */
    s += '<text x="' + (cwX - 10) + '" y="' + (cwY + 45) + '" fill="#666" font-size="8" font-family="JetBrains Mono, monospace">CW</text>';
    /* Hoist drums behind cab */
    s += '<circle cx="' + (cx - 40) + '" cy="' + (deckY - 15) + '" r="22" fill="#d8d8d8" stroke="#222" stroke-width="1.8"/>';
    s += '<circle cx="' + (cx - 40) + '" cy="' + (deckY - 15) + '" r="6" fill="#888" stroke="#333" stroke-width="1"/>';
    for (var dr = 0; dr < 6; dr++) {
      s += '<line x1="' + (cx - 60) + '" y1="' + (deckY - 25 + dr * 4) + '" x2="' + (cx - 20) + '" y2="' + (deckY - 25 + dr * 4) + '" stroke="#aaa" stroke-width="0.5"/>';
    }

    /* --- OPERATOR CAB (right/front side) --- */
    var cabX = cx + 60;
    var cabY = deckY - 55;
    s += '<path d="M ' + cabX + ' ' + cabY + ' L ' + (cabX + 55) + ' ' + cabY + ' L ' + (cabX + 65) + ' ' + (cabY + 15) + ' L ' + (cabX + 65) + ' ' + deckY + ' L ' + cabX + ' ' + deckY + ' Z" fill="#f5f5f5" stroke="#222" stroke-width="2"/>';
    /* Cab windows */
    s += '<rect x="' + (cabX + 5) + '" y="' + (cabY + 5) + '" width="30" height="22" fill="#e8e8e8" stroke="#555" stroke-width="1"/>';
    s += '<path d="M ' + (cabX + 38) + ' ' + (cabY + 5) + ' L ' + (cabX + 58) + ' ' + (cabY + 5) + ' L ' + (cabX + 62) + ' ' + (cabY + 18) + ' L ' + (cabX + 38) + ' ' + (cabY + 18) + ' Z" fill="#e8e8e8" stroke="#555" stroke-width="1"/>';
    s += '<rect x="' + (cabX + 5) + '" y="' + (cabY + 32) + '" width="55" height="20" fill="none" stroke="#aaa" stroke-width="0.8"/>';

    /* --- A-FRAME GANTRY (behind operator cab, holds back stays) --- */
    var gantryBase = { x: cx - 20, y: deckY };
    var gantryTop = { x: cx - 10, y: deckY - 180 };
    var gantryFront = { x: cx + 40, y: deckY };
    /* A-frame legs */
    s += '<line x1="' + gantryBase.x + '" y1="' + gantryBase.y + '" x2="' + gantryTop.x + '" y2="' + gantryTop.y + '" stroke="#222" stroke-width="4"/>';
    s += '<line x1="' + gantryFront.x + '" y1="' + gantryFront.y + '" x2="' + gantryTop.x + '" y2="' + gantryTop.y + '" stroke="#222" stroke-width="4"/>';
    /* A-frame cross braces */
    s += '<line x1="' + lerp(gantryBase.x, gantryTop.x, 0.35) + '" y1="' + lerp(gantryBase.y, gantryTop.y, 0.35) + '" x2="' + lerp(gantryFront.x, gantryTop.x, 0.35) + '" y2="' + lerp(gantryFront.y, gantryTop.y, 0.35) + '" stroke="#555" stroke-width="1.5"/>';
    s += '<line x1="' + lerp(gantryBase.x, gantryTop.x, 0.65) + '" y1="' + lerp(gantryBase.y, gantryTop.y, 0.65) + '" x2="' + lerp(gantryFront.x, gantryTop.x, 0.65) + '" y2="' + lerp(gantryFront.y, gantryTop.y, 0.65) + '" stroke="#555" stroke-width="1.5"/>';
    /* Gantry top sheave */
    s += '<circle cx="' + gantryTop.x + '" cy="' + gantryTop.y + '" r="10" fill="#ddd" stroke="#222" stroke-width="1.8"/>';
    s += '<circle cx="' + gantryTop.x + '" cy="' + gantryTop.y + '" r="4" fill="#666"/>';

    /* --- BOOM (lattice, from foot to tip) --- */
    var boomFoot = { x: cx + 35, y: deckY - 5 };
    var boomLen = Math.sqrt(
      Math.pow(boomTip.x - boomFoot.x, 2) + Math.pow(boomTip.y - boomFoot.y, 2)
    );
    var boomAngle = deg(Math.atan2(boomTip.y - boomFoot.y, boomTip.x - boomFoot.x));

    /* Draw boom via a transformed group */
    var bw = 60, tw = 26;
    var slope = (tw - bw) / (2 * boomLen);
    var boom = '';
    boom += '<g transform="translate(' + boomFoot.x + ',' + boomFoot.y + ') rotate(' + boomAngle + ')">';
    /* Boom outline */
    boom += '<path d="M 0,' + (-bw/2) + ' L ' + boomLen + ',' + (-tw/2) + ' L ' + boomLen + ',' + (tw/2) + ' L 0,' + (bw/2) + ' Z" fill="#fafafa" stroke="#222" stroke-width="2.2"/>';
    /* Boom chord lines */
    boom += '<line x1="0" y1="' + (-bw/2 + 4) + '" x2="' + boomLen + '" y2="' + (-tw/2 + 4) + '" stroke="#333" stroke-width="1.5"/>';
    boom += '<line x1="0" y1="' + (bw/2 - 4) + '" x2="' + boomLen + '" y2="' + (tw/2 - 4) + '" stroke="#333" stroke-width="1.5"/>';
    /* Lattice diagonals */
    var sec = 36;
    var num = Math.floor(boomLen / sec);
    for (var m = 0; m <= num; m++) {
      var xm = m * sec;
      if (xm > boomLen) break;
      var hwm = bw/2 + slope * xm;
      boom += '<line x1="' + xm + '" y1="' + (-hwm + 2) + '" x2="' + xm + '" y2="' + (hwm - 2) + '" stroke="#555" stroke-width="0.9"/>';
      if (m < num) {
        var xn = Math.min((m + 1) * sec, boomLen);
        var hwn = bw/2 + slope * xn;
        if (m % 2 === 0) {
          boom += '<line x1="' + xm + '" y1="' + (-hwm + 2) + '" x2="' + xn + '" y2="' + (hwn - 2) + '" stroke="#777" stroke-width="0.7"/>';
        } else {
          boom += '<line x1="' + xm + '" y1="' + (hwm - 2) + '" x2="' + xn + '" y2="' + (-hwn + 2) + '" stroke="#777" stroke-width="0.7"/>';
        }
      }
    }
    /* Boom foot pivot */
    boom += '<circle cx="0" cy="0" r="10" fill="#ccc" stroke="#222" stroke-width="1.8"/>';
    boom += '<circle cx="0" cy="0" r="4" fill="#555"/>';
    /* Boom tip / point sheave */
    boom += '<rect x="' + (boomLen - 4) + '" y="' + (-tw/2 - 8) + '" width="14" height="' + (tw + 16) + '" rx="2" fill="#e8e8e8" stroke="#222" stroke-width="2"/>';
    boom += '<circle cx="' + (boomLen + 4) + '" cy="0" r="9" fill="#ddd" stroke="#222" stroke-width="1.5"/>';
    boom += '<circle cx="' + (boomLen + 4) + '" cy="0" r="4" fill="#666"/>';
    boom += '</g>';
    s += boom;

    /* --- BACK STAYS (cables from boom tip to gantry top) --- */
    s += '<line x1="' + boomTip.x + '" y1="' + boomTip.y + '" x2="' + gantryTop.x + '" y2="' + gantryTop.y + '" stroke="#222" stroke-width="1.8"/>';
    s += '<line x1="' + boomTip.x + '" y1="' + (boomTip.y + 5) + '" x2="' + gantryTop.x + '" y2="' + (gantryTop.y + 5) + '" stroke="#444" stroke-width="1"/>';
    /* Boom hoist cable from gantry top down to hoist drum */
    s += '<line x1="' + gantryTop.x + '" y1="' + gantryTop.y + '" x2="' + (cx - 40) + '" y2="' + (deckY - 15) + '" stroke="#666" stroke-width="1"/>';

    return s;
  }

  /* ============================================================
     MOBILE CRANE — All-terrain telescopic boom with wheeled carrier
     ============================================================ */

  function svgMobileCrane() {
    var cx = G.mobileBase.x;
    var groundY = G.groundY;
    var boomTip = G.mobileBoomTip;
    var s = '';

    /* --- WHEELS (8 wheels, 4 axles) --- */
    var wheelY = groundY - 22;
    var wheels = [-170, -110, -50, 10, 70, 130];
    for (var i = 0; i < wheels.length; i++) {
      var wx = cx + wheels[i];
      s += '<circle cx="' + wx + '" cy="' + wheelY + '" r="22" fill="#d8d8d8" stroke="#222" stroke-width="2"/>';
      s += '<circle cx="' + wx + '" cy="' + wheelY + '" r="10" fill="#bbb" stroke="#444" stroke-width="1.2"/>';
      s += '<circle cx="' + wx + '" cy="' + wheelY + '" r="3" fill="#666"/>';
      for (var a = 0; a < 360; a += 60) {
        var ar = rad(a);
        s += '<line x1="' + wx + '" y1="' + wheelY + '" x2="' + (wx + 8 * Math.cos(ar)) + '" y2="' + (wheelY + 8 * Math.sin(ar)) + '" stroke="#888" stroke-width="0.7"/>';
      }
    }
    /* Outrigger pads */
    s += '<rect x="' + (cx - 250) + '" y="' + (groundY - 8) + '" width="30" height="8" fill="#c8c8c8" stroke="#222" stroke-width="1.5"/>';
    s += '<line x1="' + (cx - 220) + '" y1="' + (groundY - 6) + '" x2="' + (cx - 180) + '" y2="' + (wheelY - 20) + '" stroke="#222" stroke-width="2.5"/>';
    s += '<rect x="' + (cx + 200) + '" y="' + (groundY - 8) + '" width="30" height="8" fill="#c8c8c8" stroke="#222" stroke-width="1.5"/>';
    s += '<line x1="' + (cx + 230) + '" y1="' + (groundY - 6) + '" x2="' + (cx + 175) + '" y2="' + (wheelY - 20) + '" stroke="#222" stroke-width="2.5"/>';

    /* --- CARRIER CHASSIS --- */
    var chassisY = wheelY - 25;
    s += '<path d="M ' + (cx - 195) + ' ' + chassisY + ' L ' + (cx + 165) + ' ' + chassisY + ' L ' + (cx + 175) + ' ' + (chassisY + 25) + ' L ' + (cx - 205) + ' ' + (chassisY + 25) + ' Z" fill="#e8e8e8" stroke="#222" stroke-width="2.2"/>';
    /* Chassis detail lines */
    s += '<line x1="' + (cx - 195) + '" y1="' + (chassisY + 12) + '" x2="' + (cx + 165) + '" y2="' + (chassisY + 12) + '" stroke="#999" stroke-width="0.8"/>';

    /* --- DRIVER CAB (front left) --- */
    var driverCabX = cx - 180;
    var driverCabY = chassisY - 55;
    s += '<path d="M ' + driverCabX + ' ' + driverCabY + ' L ' + (driverCabX + 60) + ' ' + driverCabY + ' L ' + (driverCabX + 70) + ' ' + (driverCabY + 20) + ' L ' + (driverCabX + 70) + ' ' + chassisY + ' L ' + driverCabX + ' ' + chassisY + ' Z" fill="#f5f5f5" stroke="#222" stroke-width="2"/>';
    /* Windshield */
    s += '<path d="M ' + (driverCabX + 5) + ' ' + (driverCabY + 5) + ' L ' + (driverCabX + 45) + ' ' + (driverCabY + 5) + ' L ' + (driverCabX + 62) + ' ' + (driverCabY + 22) + ' L ' + (driverCabX + 5) + ' ' + (driverCabY + 22) + ' Z" fill="#e0e0e0" stroke="#555" stroke-width="1"/>';
    /* Side window */
    s += '<rect x="' + (driverCabX + 5) + '" y="' + (driverCabY + 28) + '" width="55" height="15" fill="none" stroke="#aaa" stroke-width="0.8"/>';

    /* --- SLEW RING --- */
    var slewY = chassisY - 5;
    s += '<ellipse cx="' + (cx + 20) + '" cy="' + slewY + '" rx="80" ry="8" fill="#d0d0d0" stroke="#333" stroke-width="1.5"/>';

    /* --- UPPER STRUCTURE / CRANE CAB (revolving) --- */
    var craneCabX = cx - 50;
    var craneCabY = slewY - 65;
    s += '<rect x="' + craneCabX + '" y="' + craneCabY + '" width="70" height="65" fill="#f0f0f0" stroke="#222" stroke-width="2"/>';
    /* Crane cab window */
    s += '<rect x="' + (craneCabX + 8) + '" y="' + (craneCabY + 8) + '" width="28" height="22" fill="#e0e0e0" stroke="#555" stroke-width="1"/>';
    s += '<rect x="' + (craneCabX + 8) + '" y="' + (craneCabY + 36) + '" width="55" height="20" fill="none" stroke="#aaa" stroke-width="0.8"/>';

    /* --- COUNTERWEIGHT (rear/right of crane cab) --- */
    var cwX = cx + 70;
    var cwY = craneCabY - 5;
    s += '<rect x="' + cwX + '" y="' + cwY + '" width="70" height="70" fill="#c8c8c8" stroke="#222" stroke-width="2.2"/>';
    for (var cb = 1; cb <= 3; cb++) {
      s += '<line x1="' + cwX + '" y1="' + (cwY + cb * 17) + '" x2="' + (cwX + 70) + '" y2="' + (cwY + cb * 17) + '" stroke="#666" stroke-width="0.9"/>';
    }

    /* --- TELESCOPIC BOOM --- */
    var boomFoot = { x: cx + 20, y: craneCabY + 10 };
    var boomLen = Math.sqrt(
      Math.pow(boomTip.x - boomFoot.x, 2) + Math.pow(boomTip.y - boomFoot.y, 2)
    );
    var boomAngle = deg(Math.atan2(boomTip.y - boomFoot.y, boomTip.x - boomFoot.x));

    var boom = '';
    boom += '<g transform="translate(' + boomFoot.x + ',' + boomFoot.y + ') rotate(' + boomAngle + ')">';
    /* Boom is drawn as nested telescoping sections (widest at base, narrower toward tip) */
    var sections = [
      { start: 0,           end: boomLen * 0.40, halfW: 34 },
      { start: boomLen * 0.35, end: boomLen * 0.72, halfW: 26 },
      { start: boomLen * 0.68, end: boomLen,        halfW: 20 }
    ];
    /* Draw base section first, then progressively narrower on top */
    for (var si = 0; si < sections.length; si++) {
      var sec2 = sections[si];
      boom += '<rect x="' + sec2.start + '" y="' + (-sec2.halfW) + '" width="' + (sec2.end - sec2.start) + '" height="' + (sec2.halfW * 2) + '" fill="#fafafa" stroke="#222" stroke-width="2"/>';
      /* Detail lines */
      boom += '<line x1="' + sec2.start + '" y1="' + (-sec2.halfW + 4) + '" x2="' + sec2.end + '" y2="' + (-sec2.halfW + 4) + '" stroke="#888" stroke-width="0.6"/>';
      boom += '<line x1="' + sec2.start + '" y1="' + (sec2.halfW - 4) + '" x2="' + sec2.end + '" y2="' + (sec2.halfW - 4) + '" stroke="#888" stroke-width="0.6"/>';
      /* Center dashed line */
      boom += '<line x1="' + sec2.start + '" y1="0" x2="' + sec2.end + '" y2="0" stroke="#ccc" stroke-width="0.4" stroke-dasharray="4 4"/>';
    }
    /* Boom foot pivot */
    boom += '<circle cx="0" cy="0" r="9" fill="#ccc" stroke="#222" stroke-width="1.8"/>';
    boom += '<circle cx="0" cy="0" r="3" fill="#555"/>';
    /* Boom tip sheave */
    boom += '<rect x="' + (boomLen - 4) + '" y="-24" width="10" height="48" rx="2" fill="#e8e8e8" stroke="#222" stroke-width="1.8"/>';
    boom += '<circle cx="' + (boomLen + 2) + '" cy="0" r="8" fill="#ddd" stroke="#222" stroke-width="1.5"/>';
    boom += '<circle cx="' + (boomLen + 2) + '" cy="0" r="3" fill="#666"/>';
    boom += '</g>';
    s += boom;

    /* --- BOOM LIFT CYLINDER (hydraulic ram from cab base to boom underside) --- */
    var ramStart = { x: cx + 15, y: slewY - 5 };
    /* Ram end is 25% along boom bottom */
    var ramT = 0.28;
    var boomBotAngle = rad(boomAngle);
    var ramEnd = {
      x: boomFoot.x + Math.cos(boomBotAngle) * (boomLen * ramT) - Math.sin(boomBotAngle) * 30,
      y: boomFoot.y + Math.sin(boomBotAngle) * (boomLen * ramT) + Math.cos(boomBotAngle) * 30
    };
    s += '<line x1="' + ramStart.x + '" y1="' + ramStart.y + '" x2="' + ramEnd.x + '" y2="' + ramEnd.y + '" stroke="#222" stroke-width="5"/>';
    s += '<line x1="' + ramStart.x + '" y1="' + ramStart.y + '" x2="' + ramEnd.x + '" y2="' + ramEnd.y + '" stroke="#e0e0e0" stroke-width="2.5"/>';
    s += '<circle cx="' + ramStart.x + '" cy="' + ramStart.y + '" r="5" fill="#999" stroke="#222" stroke-width="1.5"/>';

    return s;
  }

  /* ============================================================
     HOOKS (drawn separately, translated per frame)
     ============================================================ */

  function svgCrawlerHook() {
    var s = '';
    /* Hook block - larger, sketch style */
    s += '<line x1="-14" y1="-6" x2="14" y2="-6" stroke="#333" stroke-width="1"/>';
    s += '<rect x="-18" y="-2" width="36" height="28" rx="2" fill="#f0f0f0" stroke="#222" stroke-width="2"/>';
    s += '<line x1="-12" y1="8" x2="12" y2="8" stroke="#888" stroke-width="0.8"/>';
    s += '<line x1="-12" y1="16" x2="12" y2="16" stroke="#888" stroke-width="0.8"/>';
    /* Twin sheaves inside block */
    s += '<circle cx="-6" cy="12" r="4" fill="#ddd" stroke="#555" stroke-width="0.8"/>';
    s += '<circle cx="6" cy="12" r="4" fill="#ddd" stroke="#555" stroke-width="0.8"/>';
    /* Hook proper */
    s += '<path d="M 0,26 L 0,36 Q 0,46 8,46 Q 16,46 16,38 L 16,32" fill="none" stroke="#222" stroke-width="2.2"/>';
    s += '<circle cx="0" cy="26" r="2.5" fill="#666"/>';
    return s;
  }

  function svgMobileHook() {
    var s = '';
    s += '<line x1="-10" y1="-4" x2="10" y2="-4" stroke="#333" stroke-width="0.8"/>';
    s += '<rect x="-13" y="0" width="26" height="22" rx="2" fill="#f0f0f0" stroke="#222" stroke-width="1.8"/>';
    s += '<line x1="-9" y1="7" x2="9" y2="7" stroke="#888" stroke-width="0.7"/>';
    s += '<line x1="-9" y1="13" x2="9" y2="13" stroke="#888" stroke-width="0.7"/>';
    s += '<circle cx="0" cy="10" r="3" fill="#ddd" stroke="#555" stroke-width="0.8"/>';
    s += '<path d="M 0,22 L 0,30 Q 0,38 6,38 Q 12,38 12,32 L 12,27" fill="none" stroke="#222" stroke-width="2"/>';
    return s;
  }

  /* ============================================================
     PRESSURE VESSEL - Realistic industrial vessel
     Vessel-group has origin at main lug, extends left (head) and right (tail)
     ============================================================ */

  function svgPressureVessel() {
    var r = G.vesselR;
    var headEnd = -G.mainLugOffset;
    var tailEnd = G.trunnionDist + 120;
    var s = '';

    s += '<defs><linearGradient id="vesselShade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbfbfb"/><stop offset="0.5" stop-color="#f0f0f0"/><stop offset="1" stop-color="#dcdcdc"/></linearGradient></defs>';
    /* Head cap (hemispherical/elliptical) */
    s += '<ellipse cx="' + headEnd + '" cy="0" rx="18" ry="' + r + '" fill="url(#vesselShade)" stroke="#222" stroke-width="2.2"/>';
    /* Body */
    s += '<rect x="' + headEnd + '" y="' + (-r) + '" width="' + (tailEnd - headEnd) + '" height="' + (r * 2) + '" fill="url(#vesselShade)" stroke="#222" stroke-width="2.2"/>';
    /* Tail cap */
    s += '<ellipse cx="' + tailEnd + '" cy="0" rx="18" ry="' + r + '" fill="url(#vesselShade)" stroke="#222" stroke-width="2.2"/>';
    /* Centerline */
    s += '<line x1="' + (headEnd - 25) + '" y1="0" x2="' + (tailEnd + 25) + '" y2="0" stroke="#bbb" stroke-width="0.5" stroke-dasharray="10 5 3 5"/>';

    /* Circumferential weld lines */
    for (var wx = headEnd + 60; wx < tailEnd - 40; wx += 70) {
      s += '<line x1="' + wx + '" y1="' + (-r + 2) + '" x2="' + wx + '" y2="' + (r - 2) + '" stroke="#bbb" stroke-width="0.6"/>';
    }

    /* Main lift lug (at origin) */
    s += '<rect x="-8" y="' + (-r - 18) + '" width="16" height="18" fill="#ddd" stroke="#222" stroke-width="1.8"/>';
    s += '<circle cx="0" cy="' + (-r - 9) + '" r="8" fill="#eee" stroke="#222" stroke-width="1.8"/>';
    s += '<circle cx="0" cy="' + (-r - 9) + '" r="3" fill="#666"/>';

    /* Tail lift lug */
    var tlx = G.trunnionDist;
    s += '<rect x="' + (tlx - 8) + '" y="' + (-r - 18) + '" width="16" height="18" fill="#ddd" stroke="#222" stroke-width="1.8"/>';
    s += '<circle cx="' + tlx + '" cy="' + (-r - 9) + '" r="8" fill="#eee" stroke="#222" stroke-width="1.8"/>';
    s += '<circle cx="' + tlx + '" cy="' + (-r - 9) + '" r="3" fill="#666"/>';

    /* Nozzles on top */
    var topNozzles = [40, 110, 200, 280];
    for (var i = 0; i < topNozzles.length; i++) {
      var nx = topNozzles[i];
      if (nx > tailEnd - 30) continue;
      s += '<rect x="' + (nx - 6) + '" y="' + (-r - 14) + '" width="12" height="14" fill="#eee" stroke="#333" stroke-width="1.2"/>';
      s += '<line x1="' + (nx - 6) + '" y1="' + (-r - 14) + '" x2="' + (nx + 6) + '" y2="' + (-r - 14) + '" stroke="#333" stroke-width="1"/>';
    }
    /* Nozzles on bottom */
    var botNozzles = [70, 180, 260];
    for (var bn = 0; bn < botNozzles.length; bn++) {
      var bnx = botNozzles[bn];
      if (bnx > tailEnd - 30) continue;
      s += '<line x1="' + bnx + '" y1="' + r + '" x2="' + bnx + '" y2="' + (r + 12) + '" stroke="#333" stroke-width="1.5"/>';
      s += '<rect x="' + (bnx - 5) + '" y="' + (r + 12) + '" width="10" height="7" fill="#eee" stroke="#333" stroke-width="1"/>';
    }
    /* Manway (large flange) at head end */
    s += '<rect x="' + (headEnd + 20) + '" y="-16" width="14" height="32" fill="#eee" stroke="#222" stroke-width="1.4"/>';
    /* Label */
    s += '<text x="' + (G.trunnionDist / 2) + '" y="4" text-anchor="middle" fill="#999" font-size="11" font-family="JetBrains Mono, monospace" letter-spacing="1.5">PRESSURE VESSEL</text>';
    return s;
  }

  function svgAnnotations() {
    var s = '';
    s += '<text x="' + G.crawlerBase.x + '" y="' + (G.groundY + 55) + '" text-anchor="middle" fill="#999" font-size="10" font-family="JetBrains Mono, monospace" letter-spacing="0.5">MAIN CRANE · CRAWLER</text>';
    s += '<text x="' + G.mobileBase.x + '" y="' + (G.groundY + 55) + '" text-anchor="middle" fill="#999" font-size="10" font-family="JetBrains Mono, monospace" letter-spacing="0.5">TAIL CRANE · MOBILE</text>';
    return s;
  }

  /* ============================================================
     SCENE INITIALIZATION
     ============================================================ */

  function initScene() {
    document.querySelector('#ground-group').innerHTML = svgGround();
    /* Combine crawler crane parts into single group */
    document.querySelector('#crawler-track').innerHTML = svgCrawlerCrane();
    document.querySelector('#crawler-body').innerHTML = '';
    document.querySelector('#crawler-boom').innerHTML = '';
    document.querySelector('#crawler-hook').innerHTML = svgCrawlerHook();

    document.querySelector('#mobile-body').innerHTML = svgMobileCrane();
    document.querySelector('#mobile-boom').innerHTML = '';
    document.querySelector('#mobile-hook').innerHTML = svgMobileHook();

    document.querySelector('#pressure-vessel').innerHTML = svgPressureVessel();
    document.querySelector('#annotations').innerHTML = svgAnnotations();

    updateScene(0);
  }

  /* ============================================================
     ANIMATION UPDATE
     ============================================================ */

  function updateScene(progress) {
    var vesselRot;
    var mainHookX = G.crawlerBoomTip.x;
    var mainHookY;
    var tailHookX = G.mobileBoomTip.x;
    var tailHookY;
    var mainSlingOpacity = 1;
    var tailSlingOpacity = 1;

    var mainHookRest = G.crawlerBoomTip.y + G.hookRestOffsetY;
    var tailHookRest = G.mobileBoomTip.y + G.hookRestOffsetY;

    var lugsFlat = vesselPoints(0);

    if (progress < 0.15) {
      /* Phase 1: Hooks descend from boom tips to vessel lugs */
      var p1 = progress / 0.15;
      var p1Eased = easeInOutQuad(p1);
      vesselRot = 0;
      mainHookY = lerp(mainHookRest, lugsFlat.main.y - 45, p1Eased);
      tailHookY = lerp(tailHookRest, lugsFlat.tail.y - 45, p1Eased);
      mainSlingOpacity = p1Eased;
      tailSlingOpacity = p1Eased;
    } else if (progress < 0.25) {
      /* Phase 2: Slings taut, vessel still on ground */
      vesselRot = 0;
      mainHookY = lugsFlat.main.y - 45;
      tailHookY = lugsFlat.tail.y - 45;
    } else if (progress < 0.90) {
      /* Phase 3: Upending — vessel rotates around main lug */
      var p3 = (progress - 0.25) / 0.65;
      var p3Eased = easeInOutCubic(p3);
      vesselRot = 90 * p3Eased;

      var lugsNow = vesselPoints(vesselRot);
      /* Main hook stays 45px above main lug (which is fixed) */
      mainHookY = lugsNow.main.y - 45;
      /* Tail hook stays 45px above tail lug (which moves in arc) */
      tailHookY = lugsNow.tail.y - 45;
      /* Prevent hook rising above boom tip */
      if (tailHookY < G.mobileBoomTip.y + 30) tailHookY = G.mobileBoomTip.y + 30;
    } else {
      /* Phase 4: Vessel vertical, tail crane releases and rises */
      var p4 = (progress - 0.90) / 0.10;
      var p4Eased = easeOutCubic(p4);
      vesselRot = 90;
      var lugsFinal = vesselPoints(90);
      mainHookY = lugsFinal.main.y - 45;
      var tailHookHold = lugsFinal.tail.y - 45;
      if (tailHookHold < G.mobileBoomTip.y + 30) tailHookHold = G.mobileBoomTip.y + 30;
      tailHookY = lerp(tailHookHold, G.mobileBoomTip.y + 30, p4Eased);
      tailSlingOpacity = 1 - p4Eased;
    }

    /* Apply vessel rotation and translation (pivot Y varies with rotation) */
    var pivotY = mainPivotYForRotation(vesselRot);
    var vesselEl = document.getElementById('vessel-group');
    if (vesselEl) {
      vesselEl.setAttribute('transform',
        'translate(' + G.mainPivot.x + ',' + pivotY + ') rotate(' + vesselRot + ')'
      );
    }

    /* Main wire: boom tip to hook (vertical) */
    setLine('crawler-wire-line', G.crawlerBoomTip.x, G.crawlerBoomTip.y, mainHookX, mainHookY);
    setSvgTranslate('crawler-hook', mainHookX, mainHookY);
    /* Main sling: hook to main lug */
    var lugsNow2 = vesselPoints(vesselRot);
    setLine('main-sling', mainHookX, mainHookY + 26, lugsNow2.main.x, lugsNow2.main.y - 15);
    setOpacity('main-sling', mainSlingOpacity);

    /* Tail wire */
    setLine('mobile-wire-line', G.mobileBoomTip.x, G.mobileBoomTip.y, tailHookX, tailHookY);
    setSvgTranslate('mobile-hook', tailHookX, tailHookY);
    setLine('tail-sling', tailHookX, tailHookY + 22, lugsNow2.tail.x, lugsNow2.tail.y - 15);
    setOpacity('tail-sling', tailSlingOpacity);
    setOpacity('mobile-hook', progress > 0.99 ? 0.3 : 1);

    /* Progress indicator */
    var progressPct = Math.round((vesselRot / 90) * 100);
    var degreeVal = Math.round(vesselRot);
    var fill = document.getElementById('progressFill');
    var degEl = document.getElementById('progressDegree');
    if (fill) fill.style.width = progressPct + '%';
    if (degEl) degEl.textContent = degreeVal + '\u00B0';
  }

  /* ============================================================
     PUBLIC API — used by main.js
     ============================================================ */
  window.SceneEngine = {
    init: function () { initScene(); updateScene(0); },
    update: function (p) { updateScene(p); }
  };

})();
