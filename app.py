import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
import time

st.set_page_config(
    page_title="MatchLog Misty Optimizer",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Constants ────────────────────────────────────────────────────────────────
MILEAGE         = 2.5   # km per litre (fixed)
CIRCUITY_FACTOR = 1.25  # great-circle → road distance multiplier

# ── Hardcoded yard coordinates ────────────────────────────────────────────────
YARD_COORDS = {
    "Bharuch":     (21.7051, 72.9959),   # Misty Yard – Bharuch, Gujarat
    "Vapi":        (20.3720, 72.9010),   # Misty Yard – Vapi, Gujarat
    "Chakan":      (18.7600, 73.8600),   # Misty Yard – Chakan, Pune
    "Nhava Sheva": (18.9500, 72.9500),   # Default empty yard (JNPT)
}

# Pre-resolved coords for common ICDs/ports (avoids geocoding well-known names)
KNOWN_EMPTY_YARDS = {
    "nhava sheva":      (18.9500, 72.9500),
    "jnpt":             (18.9500, 72.9500),
    "icd tumb":         (19.2183, 72.9781),
    "mundra port":      (22.8461, 69.7020),
    "hazira port":      (21.0847, 72.6479),
    "pipavav":          (20.9167, 71.5333),
    "icd sabarmati":    (23.0669, 72.6030),
    "icd khodiyar":     (23.1000, 72.6500),
    "icd pune":         (18.5204, 73.8567),
    "icd nagpur":       (21.1458, 79.0882),
    "icd patparganj":   (28.6270, 77.2980),
    "icd loni":         (28.7500, 77.4000),
    "concor icd":       (28.6139, 77.2090),
}

# ── Geocoder (one instance, cached across reruns) ─────────────────────────────
@st.cache_resource
def get_geocoder():
    return Nominatim(user_agent="matchlog_misty_optimizer_v2", timeout=10)

def geocode_location(place: str):
    """Return (lat, lon) or None. Biases search to India."""
    if not place or len(place.strip()) < 3:
        return None
    geolocator = get_geocoder()
    try:
        result = geolocator.geocode(place.strip() + ", India")
        if result:
            return (result.latitude, result.longitude)
        result = geolocator.geocode(place.strip())
        if result:
            return (result.latitude, result.longitude)
    except Exception:
        pass
    return None

def road_distance_km(coord_a, coord_b) -> float:
    """Great-circle distance multiplied by circuity factor, rounded to 1 dp."""
    gc = great_circle(coord_a, coord_b).km
    return round(gc * CIRCUITY_FACTOR, 1)

def resolve_empty_yard_coords(yard_text: str):
    """Check known-dict first, then fall back to Nominatim."""
    key = yard_text.strip().lower()
    for k, coords in KNOWN_EMPTY_YARDS.items():
        if k in key or key in k:
            return coords
    return geocode_location(yard_text)

# ── Session-state defaults ────────────────────────────────────────────────────
_defaults = {
    "dist_bharuch":        0.0,
    "dist_vapi":           0.0,
    "dist_chakan":         0.0,
    "dist_empty":          0.0,
    "geo_status":          "",      # "ok" | "error" | ""
    "last_geocoded_drop":  "",      # debounce: skip re-geocode if unchanged
    "last_geocoded_empty": "",
    "drop_coords":         None,
    "auto_fetched":        False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d1117; }

.ml-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b27 100%);
    border-bottom: 1px solid #21293a;
    padding: 1.5rem 2rem 1.25rem;
    margin: -1rem -1rem 2rem;
    display: flex; align-items: center; gap: 1rem;
}
.ml-logo { width:38px;height:38px;background:#1d6fa4;border-radius:8px;
           display:flex;align-items:center;justify-content:center;font-size:18px; }
.ml-brand { line-height: 1.2; }
.ml-brand-name { font-size:16px;font-weight:600;color:#e8edf5;letter-spacing:-0.02em; }
.ml-brand-sub  { font-size:11px;color:#5a7090;letter-spacing:0.06em;text-transform:uppercase; }

.section-header {
    font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
    color:#3e5a78;margin-bottom:0.75rem;
    border-bottom:1px solid #161f2c;padding-bottom:0.5rem;
}

.geo-badge { display:inline-flex;align-items:center;gap:5px;
             font-size:11px;padding:3px 10px;border-radius:20px;margin-bottom:0.5rem; }
.geo-ok   { background:#0a1f15;color:#34c97e;border:1px solid #0e3a22; }
.geo-warn { background:#1a1200;color:#f0a500;border:1px solid #3a2c00; }
.geo-err  { background:#1a0f0f;color:#e74c3c;border:1px solid #3d1f1f; }
.geo-info { background:#0d1e30;color:#4a9fd4;border:1px solid #1a3a5c; }

.reco-banner {
    background:linear-gradient(135deg,#0a1f35 0%,#0d2a45 100%);
    border:1px solid #1a3a5c;border-left:4px solid #1d6fa4;
    border-radius:10px;padding:1.25rem 1.75rem;margin-bottom:1.5rem;
}
.reco-label  { font-size:10px;font-weight:600;letter-spacing:0.12em;
               text-transform:uppercase;color:#1d6fa4;margin-bottom:0.25rem; }
.reco-title  { font-size:26px;font-weight:600;color:#e8edf5;letter-spacing:-0.03em; }
.reco-subtitle { font-size:13px;color:#5a7090;margin-top:0.25rem; }

.route-card { background:#111822;border:1px solid #1c2636;border-radius:10px;padding:1.25rem 1.5rem;height:100%; }
.route-card.winner { border-color:#1d6fa4;background:linear-gradient(160deg,#0d1e30 0%,#111822 100%); }
.card-badge { display:inline-block;font-size:10px;font-weight:600;letter-spacing:0.08em;
              text-transform:uppercase;padding:3px 10px;border-radius:20px;margin-bottom:0.75rem; }
.badge-blue { background:#0d2a45;color:#4a9fd4;border:1px solid #1a3a5c; }
.badge-gray { background:#161f2c;color:#4a5568;border:1px solid #1c2636; }
.card-title { font-size:15px;font-weight:500;color:#c9d8e8;margin-bottom:1rem; }
.card-row   { display:flex;justify-content:space-between;align-items:baseline;
              padding:7px 0;border-bottom:1px solid #161f2c;font-size:13px; }
.card-row:last-child { border-bottom:none; }
.card-key        { color:#4a5568; }
.card-val        { color:#c9d8e8;font-family:'DM Mono',monospace;font-size:13px; }
.card-val-accent { color:#4a9fd4;font-family:'DM Mono',monospace;font-size:13px; }

.metric-block { flex:1;background:#111822;border:1px solid #1c2636;border-radius:10px;padding:1.25rem 1.5rem; }
.metric-block.positive { border-top:3px solid #1d6fa4; }
.metric-block.negative { border-top:3px solid #c0392b; }
.metric-label { font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#3e5a78;margin-bottom:0.5rem; }
.metric-value { font-size:28px;font-weight:600;font-family:'DM Mono',monospace;letter-spacing:-0.03em; }
.metric-value.positive { color:#4a9fd4; }
.metric-value.negative { color:#e74c3c; }
.metric-unit { font-size:14px;font-weight:400;color:#3e5a78;margin-left:4px; }

.yard-pills { display:flex;gap:8px;margin-bottom:1rem; }
.yard-pill  { padding:4px 14px;border-radius:20px;font-size:12px;font-weight:500;border:1px solid #1c2636; }
.yard-pill.selected     { background:#0d2a45;color:#4a9fd4;border-color:#1a3a5c; }
.yard-pill.not-selected { background:#0d1117;color:#3e5a78; }

div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background:#0d1117 !important; border:1px solid #1c2636 !important;
    color:#c9d8e8 !important; border-radius:6px !important;
    font-family:'DM Sans',sans-serif !important; font-size:13px !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color:#1d6fa4 !important;
    box-shadow:0 0 0 2px rgba(29,111,164,0.2) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size:12px !important; color:#5a7090 !important; font-weight:400 !important;
}
div[data-testid="stButton"] button {
    background:#0d2a45 !important; color:#4a9fd4 !important;
    border:1px solid #1a3a5c !important; border-radius:6px !important;
    font-size:12px !important; font-weight:500 !important;
    letter-spacing:0.03em !important; padding:0.35rem 1rem !important;
}
div[data-testid="stButton"] button:hover {
    background:#0f3356 !important; border-color:#1d6fa4 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ml-header">
  <div class="ml-logo">🚛</div>
  <div class="ml-brand">
    <div class="ml-brand-name">MatchLog</div>
    <div class="ml-brand-sub">Misty Yard Route Optimizer</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Two-column layout ─────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.6], gap="large")

# ════════════════════════════════════════════
# LEFT PANEL — Inputs
# ════════════════════════════════════════════
with left_col:
    st.markdown('<div class="section-header">Shipment Details</div>', unsafe_allow_html=True)

    drop_location = st.text_input(
        "Shipment Drop Location",
        placeholder="e.g. Surat, Gujarat",
        key="drop_loc",
        help="Type any city, port, or address in India. Distances auto-fill via geocoding."
    )
    empty_yard = st.text_input(
        "Preferred Empty Yard / ICD",
        placeholder="e.g. Nhava Sheva, CONCOR ICD Surat",
        value="Nhava Sheva",
        key="empty_yard_name",
        help="Default is Nhava Sheva (JNPT). Type any ICD/CFS/port name."
    )

    # ── Auto-geocode: only fires when text actually changes ───────────────────
    drop_changed  = drop_location.strip()  != st.session_state["last_geocoded_drop"]
    empty_changed = empty_yard.strip()     != st.session_state["last_geocoded_empty"]

    if drop_changed and len(drop_location.strip()) >= 3:
        with st.spinner("📡 Locating drop point via OpenStreetMap…"):
            time.sleep(1)          # Nominatim: max 1 request/second
            coords = geocode_location(drop_location.strip())

        st.session_state["last_geocoded_drop"] = drop_location.strip()

        if coords:
            st.session_state["drop_coords"]  = coords
            st.session_state["geo_status"]   = "ok"
            st.session_state["auto_fetched"] = True

            # Resolve empty-yard coords
            ey_text   = empty_yard.strip() or "Nhava Sheva"
            ey_coords = resolve_empty_yard_coords(ey_text)
            if not ey_coords:
                ey_coords = YARD_COORDS["Nhava Sheva"]

            # Populate all four distance fields
            st.session_state["dist_bharuch"] = road_distance_km(coords, YARD_COORDS["Bharuch"])
            st.session_state["dist_vapi"]    = road_distance_km(coords, YARD_COORDS["Vapi"])
            st.session_state["dist_chakan"]  = road_distance_km(coords, YARD_COORDS["Chakan"])
            st.session_state["dist_empty"]   = road_distance_km(coords, ey_coords)
            st.session_state["last_geocoded_empty"] = ey_text
        else:
            st.session_state["geo_status"]  = "error"
            st.session_state["drop_coords"] = None

    # Re-compute empty-yard distance when that field changes independently
    if (empty_changed and len(empty_yard.strip()) >= 3
            and st.session_state.get("drop_coords")):
        ey_coords = resolve_empty_yard_coords(empty_yard.strip())
        if ey_coords:
            st.session_state["dist_empty"]          = road_distance_km(
                st.session_state["drop_coords"], ey_coords
            )
            st.session_state["last_geocoded_empty"] = empty_yard.strip()

    # ── Status badge ─────────────────────────────────────────────────────────
    geo_s = st.session_state["geo_status"]
    if geo_s == "ok" and st.session_state["drop_coords"]:
        lat, lon = st.session_state["drop_coords"]
        st.markdown(
            f'<span class="geo-badge geo-ok">'
            f'✓ Located ({lat:.4f}, {lon:.4f}) · circuity ×{CIRCUITY_FACTOR} applied'
            f'</span>',
            unsafe_allow_html=True
        )
    elif geo_s == "error":
        st.markdown(
            '<span class="geo-badge geo-err">'
            '⚠ Location not found — please enter distances manually'
            '</span>',
            unsafe_allow_html=True
        )
    elif drop_location.strip():
        st.markdown(
            '<span class="geo-badge geo-info">⟳ Geocoding…</span>',
            unsafe_allow_html=True
        )

    # ── Distance inputs ───────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header" style="margin-top:1.1rem">'
        'Distance Inputs (one-way km) '
        '<span style="font-weight:400;text-transform:none;letter-spacing:0;'
        'font-size:10px;color:#2a3a4a;">— auto-filled · editable</span></div>',
        unsafe_allow_html=True
    )

    dist_empty = st.number_input(
        "Drop → Empty Yard / ICD (km)",
        min_value=0.0, step=1.0,
        value=float(st.session_state["dist_empty"]),
        key="input_empty"
    )

    st.markdown(
        '<div style="font-size:11px;color:#3e5a78;margin:0.75rem 0 0.4rem;">'
        'Misty Yard Distances</div>',
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        dist_bharuch = st.number_input(
            "Bharuch", min_value=0.0, step=1.0,
            value=float(st.session_state["dist_bharuch"]),
            key="input_bharuch"
        )
    with c2:
        dist_vapi = st.number_input(
            "Vapi", min_value=0.0, step=1.0,
            value=float(st.session_state["dist_vapi"]),
            key="input_vapi"
        )
    with c3:
        dist_chakan = st.number_input(
            "Chakan", min_value=0.0, step=1.0,
            value=float(st.session_state["dist_chakan"]),
            key="input_chakan"
        )

    if st.session_state["auto_fetched"]:
        st.markdown(
            '<div style="font-size:10px;color:#2a3a4a;margin-top:0.4rem;">'
            '✎ Edit any box to override the estimate.</div>',
            unsafe_allow_html=True
        )

    # ── Fuel parameters ───────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header" style="margin-top:1.25rem">Fuel Parameters</div>',
        unsafe_allow_html=True
    )
    fr_col, ml_col = st.columns(2)
    with fr_col:
        fuel_rate = st.number_input(
            "Fuel Rate (₹/litre)", min_value=0.0, step=0.5, value=95.0
        )
    with ml_col:
        st.markdown('<div style="padding-top:1.75rem"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:12px;color:#5a7090;">Mileage (fixed)</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="font-size:20px;font-weight:600;color:#4a9fd4;'
            "font-family:'DM Mono',monospace;\">"
            '2.5 <span style="font-size:13px;color:#3e5a78;">km/L</span></div>',
            unsafe_allow_html=True
        )

    # Methodology note
    st.markdown(f"""
    <div style="margin-top:1.25rem;background:#0d1421;border:1px solid #161f2c;
                border-radius:8px;padding:0.75rem 1rem;font-size:11px;
                color:#3e5a78;line-height:1.8">
      <b style="color:#4a5568;">How distances are estimated</b><br>
      Uses <b>Nominatim / OpenStreetMap</b> — free, no API key needed.<br>
      Formula: <b style="color:#4a9fd4;">Great-Circle × {CIRCUITY_FACTOR}</b> (circuity factor) = estimated road km.<br>
      Yard coordinates are hardcoded. All fields remain manually editable.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════
# CALCULATIONS
# ════════════════════════════════════════════
yards       = {"Bharuch": dist_bharuch, "Vapi": dist_vapi, "Chakan": dist_chakan}
valid_yards = {k: v for k, v in yards.items() if v > 0}
has_data    = dist_empty > 0 and len(valid_yards) > 0 and fuel_rate > 0

if has_data:
    closest_name = min(valid_yards, key=valid_yards.get)
    dist_misty   = valid_yards[closest_name]

    rt_empty  = dist_empty * 2
    rt_misty  = dist_misty * 2

    fuel_empty = rt_empty  / MILEAGE
    fuel_misty = rt_misty  / MILEAGE

    cost_empty  = fuel_empty * fuel_rate
    cost_misty  = fuel_misty * fuel_rate

    km_saved    = rt_empty - rt_misty
    fuel_saved  = km_saved / MILEAGE
    money_saved = fuel_saved * fuel_rate
    saving      = km_saved >= 0

# ════════════════════════════════════════════
# RIGHT PANEL — Outputs
# ════════════════════════════════════════════
with right_col:
    if not has_data:
        hint = (
            "Type a drop location on the left — distances auto-fill via geocoding."
            if not drop_location.strip()
            else "Geocoding in progress, or distances not yet available."
        )
        st.markdown(f"""
        <div style="background:#111822;border:1px dashed #1c2636;border-radius:10px;
                    padding:3rem 2rem;text-align:center;margin-top:2rem">
          <div style="font-size:32px;margin-bottom:0.75rem">🗺️</div>
          <div style="font-size:14px;color:#3e5a78;">{hint}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Yard selection pills
        pills_html = '<div class="yard-pills">'
        for y in ["Bharuch", "Vapi", "Chakan"]:
            cls  = "selected" if y == closest_name else "not-selected"
            icon = "✓ " if y == closest_name else ""
            dlbl = f" · {yards[y]:.0f} km" if yards[y] > 0 else " · —"
            pills_html += f'<span class="yard-pill {cls}">{icon}{y}{dlbl}</span>'
        pills_html += '</div>'
        st.markdown(pills_html, unsafe_allow_html=True)

        # Recommendation banner
        reco_sub = (
            f"{dist_misty:.0f} km away · {rt_misty:.0f} km round trip "
            f"· ₹{cost_misty:,.0f} fuel cost"
        )
        st.markdown(f"""
        <div class="reco-banner">
          <div class="reco-label">Recommended Route</div>
          <div class="reco-title">Suggested: Misty {closest_name}</div>
          <div class="reco-subtitle">{reco_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        # Comparison cards
        empty_label  = empty_yard.strip() if empty_yard.strip() else "Empty Yard / ICD"
        c_left, c_right = st.columns(2, gap="medium")

        with c_left:
            wc = "winner" if not saving else ""
            st.markdown(f"""
            <div class="route-card {wc}">
              <span class="card-badge badge-gray">Traditional Route</span>
              <div class="card-title">{empty_label}</div>
              <div class="card-row"><span class="card-key">One-way</span>
                <span class="card-val">{dist_empty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Round trip</span>
                <span class="card-val">{rt_empty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Fuel consumed</span>
                <span class="card-val">{fuel_empty:.1f} L</span></div>
              <div class="card-row"><span class="card-key">Fuel cost</span>
                <span class="card-val">₹{cost_empty:,.0f}</span></div>
            </div>""", unsafe_allow_html=True)

        with c_right:
            wc = "winner" if saving else ""
            st.markdown(f"""
            <div class="route-card {wc}">
              <span class="card-badge badge-blue">Misty Route</span>
              <div class="card-title">Misty {closest_name}</div>
              <div class="card-row"><span class="card-key">One-way</span>
                <span class="card-val-accent">{dist_misty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Round trip</span>
                <span class="card-val-accent">{rt_misty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Fuel consumed</span>
                <span class="card-val-accent">{fuel_misty:.1f} L</span></div>
              <div class="card-row"><span class="card-key">Fuel cost</span>
                <span class="card-val-accent">₹{cost_misty:,.0f}</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)

        # Savings dashboard
        st.markdown(
            '<div class="section-header">Savings Dashboard</div>',
            unsafe_allow_html=True
        )
        polarity = "positive" if saving else "negative"

        s1, s2, s3 = st.columns(3, gap="small")
        with s1:
            st.markdown(f"""
            <div class="metric-block {polarity}">
              <div class="metric-label">KM Saved</div>
              <div class="metric-value {polarity}">{abs(km_saved):.0f}
                <span class="metric-unit">km</span></div>
              <div style="font-size:11px;color:#3e5a78;margin-top:4px;">round trip delta</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="metric-block {polarity}">
              <div class="metric-label">Fuel Saved</div>
              <div class="metric-value {polarity}">{abs(fuel_saved):.1f}
                <span class="metric-unit">L</span></div>
              <div style="font-size:11px;color:#3e5a78;margin-top:4px;">at 2.5 km/L</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="metric-block {polarity}">
              <div class="metric-label">Cash Saved</div>
              <div class="metric-value {polarity}">₹{abs(money_saved):,.0f}</div>
              <div style="font-size:11px;color:#3e5a78;margin-top:4px;">at ₹{fuel_rate:.0f}/L</div>
            </div>""", unsafe_allow_html=True)

        if not saving:
            st.markdown(f"""
            <div style="background:#1a0f0f;border:1px solid #3d1f1f;border-radius:8px;
                        padding:0.75rem 1.25rem;margin-top:0.75rem;font-size:12px;color:#c0392b;">
              ⚠ Misty {closest_name} adds {abs(km_saved):.0f} km for this origin.
              The Empty Yard / ICD is more efficient here.
            </div>""", unsafe_allow_html=True)

        # Coordinate transparency strip
        if st.session_state.get("drop_coords"):
            lat, lon = st.session_state["drop_coords"]
            st.markdown(f"""
            <div style="margin-top:1.25rem;background:#0a0f1a;border:1px solid #161f2c;
                        border-radius:8px;padding:0.65rem 1rem;
                        display:flex;gap:1.5rem;flex-wrap:wrap;font-size:11px;color:#3e5a78;">
              <span>📍 Drop: <b style="color:#4a5568;">{lat:.5f}, {lon:.5f}</b></span>
              <span>📦 Bharuch: <b style="color:#4a5568;">{YARD_COORDS['Bharuch']}</b></span>
              <span>📦 Vapi: <b style="color:#4a5568;">{YARD_COORDS['Vapi']}</b></span>
              <span>📦 Chakan: <b style="color:#4a5568;">{YARD_COORDS['Chakan']}</b></span>
              <span>✕ Circuity: <b style="color:#4a9fd4;">×{CIRCUITY_FACTOR}</b></span>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #161f2c;margin-top:2.5rem;padding-top:1rem;
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem">
  <span style="font-size:11px;color:#2a3a4a;">MatchLog · Misty Optimizer v2.0</span>
  <span style="font-size:11px;color:#2a3a4a;">
    Nominatim / OSM · Great-circle × 1.25 · 2.5 km/L · distances × 2 round trip
  </span>
</div>
""", unsafe_allow_html=True)
