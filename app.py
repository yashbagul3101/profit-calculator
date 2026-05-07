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

# Pre-resolved coords for common ICDs/ports
KNOWN_EMPTY_YARDS = {
    "nhava sheva":      (18.9500, 72.9500),
    "jnpt":              (18.9500, 72.9500),
    "icd tumb":          (19.2183, 72.9781),
    "mundra port":       (22.8461, 69.7020),
    "hazira port":       (21.0847, 72.6479),
    "pipavav":           (20.9167, 71.5333),
    "icd sabarmati":     (23.0669, 72.6030),
    "icd khodiyar":      (23.1000, 72.6500),
    "icd pune":          (18.5204, 73.8567),
    "icd nagpur":        (21.1458, 79.0882),
    "icd patparganj":    (28.6270, 77.2980),
    "icd loni":          (28.7500, 77.4000),
    "concor icd":        (28.6139, 77.2090),
}

# ── Geocoding Logic ──────────────────────────────────────────────────────────
@st.cache_resource
def get_geocoder():
    return Nominatim(user_agent="matchlog_misty_optimizer_v2", timeout=10)

def geocode_location(place: str):
    if not place or len(place.strip()) < 3:
        return None
    geolocator = get_geocoder()
    try:
        result = geolocator.geocode(place.strip() + ", India")
        if result: return (result.latitude, result.longitude)
        result = geolocator.geocode(place.strip())
        if result: return (result.latitude, result.longitude)
    except Exception:
        pass
    return None

def road_distance_km(coord_a, coord_b) -> float:
    gc = great_circle(coord_a, coord_b).km
    return round(gc * CIRCUITY_FACTOR, 1)

def resolve_empty_yard_coords(yard_text: str):
    key = yard_text.strip().lower()
    for k, coords in KNOWN_EMPTY_YARDS.items():
        if k in key or key in k:
            return coords
    return geocode_location(yard_text)

# ── Session State ─────────────────────────────────────────────────────────────
_defaults = {
    "dist_bharuch":        0.0,
    "dist_vapi":           0.0,
    "dist_chakan":         0.0,
    "dist_empty":          0.0,
    "geo_status":          "",
    "last_geocoded_drop":  "",
    "last_geocoded_empty": "",
    "drop_coords":         None,
    "auto_fetched":        False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d1117; }
.ml-header { background: linear-gradient(135deg, #0d1117 0%, #161b27 100%); border-bottom: 1px solid #21293a; padding: 1.5rem 2rem 1.25rem; margin: -1rem -1rem 2rem; display: flex; align-items: center; gap: 1rem; }
.ml-logo { width:38px;height:38px;background:#1d6fa4;border-radius:8px; display:flex;align-items:center;justify-content:center;font-size:18px; }
.ml-brand { line-height: 1.2; }
.ml-brand-name { font-size:16px;font-weight:600;color:#e8edf5;letter-spacing:-0.02em; }
.ml-brand-sub  { font-size:11px;color:#5a7090;letter-spacing:0.06em;text-transform:uppercase; }
.section-header { font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase; color:#3e5a78;margin-bottom:0.75rem; border-bottom:1px solid #161f2c;padding-bottom:0.5rem; }
.geo-badge { display:inline-flex;align-items:center;gap:5px; font-size:11px;padding:3px 10px;border-radius:20px;margin-bottom:0.5rem; }
.geo-ok   { background:#0a1f15;color:#34c97e;border:1px solid #0e3a22; }
.geo-err  { background:#1a0f0f;color:#e74c3c;border:1px solid #3d1f1f; }
.geo-info { background:#0d1e30;color:#4a9fd4;border:1px solid #1a3a5c; }
.reco-banner { background:linear-gradient(135deg,#0a1f35 0%,#0d2a45 100%); border:1px solid #1a3a5c;border-left:4px solid #1d6fa4; border-radius:10px;padding:1.25rem 1.75rem;margin-bottom:1.5rem; }
.reco-label  { font-size:10px;font-weight:600;letter-spacing:0.12em; text-transform:uppercase;color:#1d6fa4;margin-bottom:0.25rem; }
.reco-title  { font-size:26px;font-weight:600;color:#e8edf5;letter-spacing:-0.03em; }
.reco-subtitle { font-size:13px;color:#5a7090;margin-top:0.25rem; }
.route-card { background:#111822;border:1px solid #1c2636;border-radius:10px;padding:1.25rem 1.5rem;height:100%; }
.route-card.winner { border-color:#1d6fa4;background:linear-gradient(160deg,#0d1e30 0%,#111822 100%); }
.card-badge { display:inline-block;font-size:10px;font-weight:600;letter-spacing:0.08em; text-transform:uppercase;padding:3px 10px;border-radius:20px;margin-bottom:0.75rem; }
.badge-blue { background:#0d2a45;color:#4a9fd4;border:1px solid #1a3a5c; }
.badge-gray { background:#161f2c;color:#4a5568;border:1px solid #1c2636; }
.card-title { font-size:15px;font-weight:500;color:#c9d8e8;margin-bottom:1rem; }
.card-row   { display:flex;justify-content:space-between;align-items:baseline; padding:7px 0;border-bottom:1px solid #161f2c;font-size:13px; }
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
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input { background:#0d1117 !important; border:1px solid #1c2636 !important; color:#c9d8e8 !important; border-radius:6px !important; font-family:'DM Sans',sans-serif !important; font-size:13px !important; }
div[data-testid="stButton"] button { background:#0d2a45 !important; color:#4a9fd4 !important; border:1px solid #1a3a5c !important; border-radius:6px !important; font-size:12px !important; font-weight:500 !important; }
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

left_col, right_col = st.columns([1, 1.6], gap="large")

# ════════════════════════════════════════════
# LEFT PANEL — Inputs
# ════════════════════════════════════════════
with left_col:
    st.markdown('<div class="section-header">Shipment Details</div>', unsafe_allow_html=True)
    drop_location = st.text_input("Shipment Drop Location", placeholder="e.g. Surat, Gujarat", key="drop_loc")
    empty_yard = st.text_input("Preferred Empty Yard / ICD", value="Nhava Sheva", key="empty_yard_name")

    # Geocoding Triggers
    drop_changed  = drop_location.strip() != st.session_state["last_geocoded_drop"]
    empty_changed = empty_yard.strip() != st.session_state["last_geocoded_empty"]

    if drop_changed and len(drop_location.strip()) >= 3:
        with st.spinner("📡 Geocoding..."):
            time.sleep(1)
            coords = geocode_location(drop_location.strip())
            st.session_state["last_geocoded_drop"] = drop_location.strip()
            if coords:
                st.session_state["drop_coords"] = coords
                st.session_state["geo_status"] = "ok"
                st.session_state["auto_fetched"] = True
                ey_coords = resolve_empty_yard_coords(empty_yard.strip() or "Nhava Sheva") or YARD_COORDS["Nhava Sheva"]
                st.session_state["dist_bharuch"] = road_distance_km(coords, YARD_COORDS["Bharuch"])
                st.session_state["dist_vapi"]    = road_distance_km(coords, YARD_COORDS["Vapi"])
                st.session_state["dist_chakan"]  = road_distance_km(coords, YARD_COORDS["Chakan"])
                st.session_state["dist_empty"]   = road_distance_km(coords, ey_coords)
            else:
                st.session_state["geo_status"] = "error"

    # Status badge
    if st.session_state["geo_status"] == "ok" and st.session_state["drop_coords"]:
        lat, lon = st.session_state["drop_coords"]
        st.markdown(f'<span class="geo-badge geo-ok">✓ Located ({lat:.4f}, {lon:.4f})</span>', unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:1.1rem">Distance Inputs (one-way km)</div>', unsafe_allow_html=True)
    dist_empty = st.number_input("Drop → Empty Yard / ICD (km)", value=float(st.session_state["dist_empty"]), key="input_empty")
    
    c1, c2, c3 = st.columns(3)
    with c1: dist_bharuch = st.number_input("Bharuch", value=float(st.session_state["dist_bharuch"]), key="input_bharuch")
    with c2: dist_vapi = st.number_input("Vapi", value=float(st.session_state["dist_vapi"]), key="input_vapi")
    with c3: dist_chakan = st.number_input("Chakan", value=float(st.session_state["dist_chakan"]), key="input_chakan")

    fuel_rate = st.number_input("Fuel Rate (₹/litre)", value=95.0)

# ════════════════════════════════════════════
# CALCULATIONS (LOGIC FIX APPLIED HERE)
# ════════════════════════════════════════════
yards       = {"Bharuch": dist_bharuch, "Vapi": dist_vapi, "Chakan": dist_chakan}
valid_yards = {k: v for k, v in yards.items() if v > 0}
has_data    = dist_empty > 0 and len(valid_yards) > 0 and fuel_rate > 0

if has_data:
    closest_name = min(valid_yards, key=valid_yards.get)
    dist_misty   = valid_yards[closest_name]

    # TRADITIONAL: Delivery (e.g. 136km) + Full Empty Return (136km)
    rt_empty  = dist_empty * 2 
    
    # MISTY: Delivery (e.g. 136km) + Small Satellite Return (e.g. 1km)
    # FIX: We add the 'dist_empty' as the delivery leg to the 'dist_misty' as the return leg.
    rt_misty  = dist_empty + dist_misty 

    fuel_empty = rt_empty / MILEAGE
    fuel_misty = rt_misty / MILEAGE
    cost_empty = fuel_empty * fuel_rate
    cost_misty = fuel_misty * fuel_rate
    km_saved    = rt_empty - rt_misty
    fuel_saved  = km_saved / MILEAGE
    money_saved = fuel_saved * fuel_rate
    saving      = km_saved >= 0

# ════════════════════════════════════════════
# RIGHT PANEL — Outputs
# ════════════════════════════════════════════
with right_col:
    if not has_data:
        st.markdown('<div style="background:#111822;border:1px dashed #1c2636;border-radius:10px;padding:3rem 2rem;text-align:center;margin-top:2rem">🗺️ Enter location to begin analysis</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="reco-banner"><div class="reco-label">Recommended Route</div><div class="reco-title">Misty {closest_name}</div><div class="reco-subtitle">₹{cost_misty:,.0f} Total Mission Fuel Cost</div></div>', unsafe_allow_html=True)

        c_left, c_right = st.columns(2, gap="medium")
        with c_left:
            st.markdown(f'<div class="route-card"><span class="card-badge badge-gray">Traditional Route</span><div class="card-title">Empty Yard / ICD</div><div class="card-row"><span class="card-key">Delivery</span><span class="card-val">{dist_empty:.0f} km</span></div><div class="card-row"><span class="card-key">Empty Return</span><span class="card-val">{dist_empty:.0f} km</span></div><div class="card-row"><span class="card-key">Mission Total</span><span class="card-val">{rt_empty:.0f} km</span></div><div class="card-row"><span class="card-key">Fuel Cost</span><span class="card-val">₹{cost_empty:,.0f}</span></div></div>', unsafe_allow_html=True)
        with c_right:
            st.markdown(f'<div class="route-card winner"><span class="card-badge badge-blue">Misty Route</span><div class="card-title">Misty {closest_name}</div><div class="card-row"><span class="card-key">Delivery</span><span class="card-val-accent">{dist_empty:.0f} km</span></div><div class="card-row"><span class="card-key">Misty Return</span><span class="card-val-accent">{dist_misty:.0f} km</span></div><div class="card-row"><span class="card-key">Mission Total</span><span class="card-val-accent">{rt_misty:.0f} km</span></div><div class="card-row"><span class="card-key">Fuel Cost</span><span class="card-val-accent">₹{cost_misty:,.0f}</span></div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:1.5rem">Savings Dashboard</div>', unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        with s1: st.markdown(f'<div class="metric-block positive"><div class="metric-label">KM Saved</div><div class="metric-value positive">{abs(km_saved):.0f} <span class="metric-unit">km</span></div></div>', unsafe_allow_html=True)
        with s2: st.markdown(f'<div class="metric-block positive"><div class="metric-label">Fuel Saved</div><div class="metric-value positive">{abs(fuel_saved):.1f} <span class="metric-unit">L</span></div></div>', unsafe_allow_html=True)
        with s3: st.markdown(f'<div class="metric-block positive"><div class="metric-label">Cash Saved</div><div class="metric-value positive">₹{abs(money_saved):,.0f}</div></div>', unsafe_allow_html=True)
