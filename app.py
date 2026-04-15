import streamlit as st

st.set_page_config(
    page_title="MatchLog Misty Optimizer",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MILEAGE = 2.5

SUGGESTED_DISTANCES = {
    "Surat":       {"Bharuch": 60,  "Vapi": 45,  "Chakan": 310, "empty": 85},
    "Ahmedabad":   {"Bharuch": 95,  "Vapi": 175, "Chakan": 370, "empty": 120},
    "Mumbai":      {"Bharuch": 250, "Vapi": 135, "Chakan": 95,  "empty": 60},
    "Pune":        {"Bharuch": 320, "Vapi": 200, "Chakan": 40,  "empty": 55},
    "Vadodara":    {"Bharuch": 35,  "Vapi": 115, "Chakan": 290, "empty": 70},
    "Rajkot":      {"Bharuch": 210, "Vapi": 290, "Chakan": 470, "empty": 240},
    "Nashik":      {"Bharuch": 340, "Vapi": 215, "Chakan": 175, "empty": 195},
    "Ankleshwar":  {"Bharuch": 10,  "Vapi": 90,  "Chakan": 265, "empty": 50},
    "Hazira":      {"Bharuch": 55,  "Vapi": 50,  "Chakan": 315, "empty": 90},
    "Mundra":      {"Bharuch": 295, "Vapi": 380, "Chakan": 555, "empty": 320},
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0d1117;
}

/* Header */
.ml-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b27 100%);
    border-bottom: 1px solid #21293a;
    padding: 1.5rem 2rem 1.25rem;
    margin: -1rem -1rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.ml-logo {
    width: 38px; height: 38px;
    background: #1d6fa4;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}

.ml-brand { line-height: 1.2; }
.ml-brand-name {
    font-size: 16px; font-weight: 600;
    color: #e8edf5; letter-spacing: -0.02em;
}
.ml-brand-sub {
    font-size: 11px; color: #5a7090;
    letter-spacing: 0.06em; text-transform: uppercase;
}

/* Section headers */
.section-header {
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #3e5a78; margin-bottom: 0.75rem;
    border-bottom: 1px solid #161f2c;
    padding-bottom: 0.5rem;
}

/* Panel / card */
.panel {
    background: #111822;
    border: 1px solid #1c2636;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

/* Recommendation banner */
.reco-banner {
    background: linear-gradient(135deg, #0a1f35 0%, #0d2a45 100%);
    border: 1px solid #1a3a5c;
    border-left: 4px solid #1d6fa4;
    border-radius: 10px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.5rem;
}
.reco-label {
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: #1d6fa4; margin-bottom: 0.25rem;
}
.reco-title {
    font-size: 26px; font-weight: 600;
    color: #e8edf5; letter-spacing: -0.03em;
}
.reco-subtitle { font-size: 13px; color: #5a7090; margin-top: 0.25rem; }

/* Comparison cards */
.route-card {
    background: #111822;
    border: 1px solid #1c2636;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    height: 100%;
}
.route-card.winner {
    border-color: #1d6fa4;
    background: linear-gradient(160deg, #0d1e30 0%, #111822 100%);
}
.card-badge {
    display: inline-block;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 3px 10px; border-radius: 20px; margin-bottom: 0.75rem;
}
.badge-blue { background: #0d2a45; color: #4a9fd4; border: 1px solid #1a3a5c; }
.badge-gray { background: #161f2c; color: #4a5568; border: 1px solid #1c2636; }
.card-title {
    font-size: 15px; font-weight: 500;
    color: #c9d8e8; margin-bottom: 1rem;
}
.card-row {
    display: flex; justify-content: space-between;
    align-items: baseline; padding: 7px 0;
    border-bottom: 1px solid #161f2c; font-size: 13px;
}
.card-row:last-child { border-bottom: none; }
.card-key { color: #4a5568; }
.card-val { color: #c9d8e8; font-family: 'DM Mono', monospace; font-size: 13px; }
.card-val-accent { color: #4a9fd4; font-family: 'DM Mono', monospace; font-size: 13px; }

/* Savings metrics */
.metric-row {
    display: flex; gap: 1rem; margin-bottom: 1rem;
}
.metric-block {
    flex: 1;
    background: #111822;
    border: 1px solid #1c2636;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
}
.metric-block.positive { border-top: 3px solid #1d6fa4; }
.metric-block.negative { border-top: 3px solid #c0392b; }
.metric-label {
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #3e5a78; margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 28px; font-weight: 600;
    font-family: 'DM Mono', monospace;
    letter-spacing: -0.03em;
}
.metric-value.positive { color: #4a9fd4; }
.metric-value.negative { color: #e74c3c; }
.metric-unit { font-size: 14px; font-weight: 400; color: #3e5a78; margin-left: 4px; }

/* Misty yard pills */
.yard-pills { display: flex; gap: 8px; margin-bottom: 1rem; }
.yard-pill {
    padding: 4px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 500;
    border: 1px solid #1c2636;
}
.yard-pill.selected { background: #0d2a45; color: #4a9fd4; border-color: #1a3a5c; }
.yard-pill.not-selected { background: #0d1117; color: #3e5a78; }

/* Input styling overrides */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #0d1117 !important;
    border: 1px solid #1c2636 !important;
    color: #c9d8e8 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #1d6fa4 !important;
    box-shadow: 0 0 0 2px rgba(29,111,164,0.2) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 12px !important;
    color: #5a7090 !important;
    font-weight: 400 !important;
}
div[data-testid="stButton"] button {
    background: #0d2a45 !important;
    color: #4a9fd4 !important;
    border: 1px solid #1a3a5c !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    padding: 0.35rem 1rem !important;
}
div[data-testid="stButton"] button:hover {
    background: #0f3356 !important;
    border-color: #1d6fa4 !important;
}
div[data-testid="stSelectbox"] select {
    background: #0d1117 !important;
    border: 1px solid #1c2636 !important;
    color: #c9d8e8 !important;
}

/* Streamlit element overrides */
.stMarkdown h3 { color: #e8edf5 !important; }
div.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ml-header">
  <div class="ml-logo">🚛</div>
  <div class="ml-brand">
    <div class="ml-brand-name">MatchLog</div>
    <div class="ml-brand-sub">Misty Yard Route Optimizer</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Session state init ───────────────────────────────────────────────────────
for k, v in [("dist_bharuch", 0.0), ("dist_vapi", 0.0),
              ("dist_chakan", 0.0), ("dist_empty", 0.0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Layout ───────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.6], gap="large")

# ════════════════════════════════════════════
# LEFT PANEL — Inputs
# ════════════════════════════════════════════
with left_col:
    st.markdown('<div class="section-header">Shipment Details</div>', unsafe_allow_html=True)

    drop_location = st.text_input("Shipment Drop Location", placeholder="e.g. Surat, Gujarat", key="drop_loc")
    empty_yard    = st.text_input("Preferred Empty Yard / ICD", placeholder="e.g. CONCOR ICD Surat", key="empty_yard_name")

    # Fetch suggestions
    matched_key = None
    if drop_location:
        for k in SUGGESTED_DISTANCES:
            if k.lower() in drop_location.lower() or drop_location.lower() in k.lower():
                matched_key = k
                break

    fetch_col, hint_col = st.columns([1, 2])
    with fetch_col:
        fetch_clicked = st.button("⟳  Suggest Distances")
    with hint_col:
        if matched_key:
            st.markdown(f'<span style="font-size:11px;color:#3e5a78;">Match found: <b style="color:#4a9fd4">{matched_key}</b></span>', unsafe_allow_html=True)
        elif drop_location:
            st.markdown('<span style="font-size:11px;color:#3e5a78;">No preset — enter manually</span>', unsafe_allow_html=True)

    if fetch_clicked and matched_key:
        d = SUGGESTED_DISTANCES[matched_key]
        st.session_state["dist_bharuch"] = float(d["Bharuch"])
        st.session_state["dist_vapi"]    = float(d["Vapi"])
        st.session_state["dist_chakan"]  = float(d["Chakan"])
        st.session_state["dist_empty"]   = float(d["empty"])

    st.markdown('<div class="section-header" style="margin-top:1.25rem">Distance Inputs (one-way km)</div>', unsafe_allow_html=True)

    dist_empty = st.number_input(
        "Drop → Empty Yard / ICD (km)", min_value=0.0, step=1.0,
        value=st.session_state["dist_empty"], key="input_empty"
    )

    st.markdown('<div style="font-size:11px;color:#3e5a78;margin:0.75rem 0 0.4rem;">Misty Yard Distances</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        dist_bharuch = st.number_input("Bharuch", min_value=0.0, step=1.0,
                                        value=st.session_state["dist_bharuch"], key="input_bharuch")
    with c2:
        dist_vapi = st.number_input("Vapi", min_value=0.0, step=1.0,
                                     value=st.session_state["dist_vapi"], key="input_vapi")
    with c3:
        dist_chakan = st.number_input("Chakan", min_value=0.0, step=1.0,
                                       value=st.session_state["dist_chakan"], key="input_chakan")

    st.markdown('<div class="section-header" style="margin-top:1.25rem">Fuel Parameters</div>', unsafe_allow_html=True)
    fr_col, ml_col = st.columns(2)
    with fr_col:
        fuel_rate = st.number_input("Fuel Rate (₹/litre)", min_value=0.0, step=0.5, value=95.0)
    with ml_col:
        st.markdown('<div style="padding-top:1.75rem"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#5a7090;">Mileage (fixed)</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:20px;font-weight:600;color:#4a9fd4;font-family:\'DM Mono\',monospace;">2.5 <span style="font-size:13px;color:#3e5a78;">km/L</span></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# CALCULATIONS
# ════════════════════════════════════════════
yards = {"Bharuch": dist_bharuch, "Vapi": dist_vapi, "Chakan": dist_chakan}
valid_yards = {k: v for k, v in yards.items() if v > 0}
has_data = dist_empty > 0 and len(valid_yards) > 0 and fuel_rate > 0

if has_data:
    closest_name = min(valid_yards, key=valid_yards.get)
    dist_misty   = valid_yards[closest_name]

    rt_empty = dist_empty * 2
    rt_misty = dist_misty * 2

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
        st.markdown("""
        <div style="background:#111822;border:1px dashed #1c2636;border-radius:10px;
                    padding:3rem 2rem;text-align:center;margin-top:2rem">
          <div style="font-size:32px;margin-bottom:0.75rem">🗺️</div>
          <div style="font-size:14px;color:#3e5a78;">Enter shipment details and distances on the left<br>to generate your route comparison.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Yard pills ──
        pills_html = '<div class="yard-pills">'
        for y in ["Bharuch", "Vapi", "Chakan"]:
            cls = "selected" if y == closest_name else "not-selected"
            icon = "✓ " if y == closest_name else ""
            dist_label = f" · {yards[y]:.0f} km" if yards[y] > 0 else " · —"
            pills_html += f'<span class="yard-pill {cls}">{icon}{y}{dist_label}</span>'
        pills_html += '</div>'
        st.markdown(pills_html, unsafe_allow_html=True)

        # ── Recommendation banner ──
        reco_sub = f"{dist_misty:.0f} km away · {rt_misty:.0f} km round trip · ₹{cost_misty:,.0f} fuel cost"
        st.markdown(f"""
        <div class="reco-banner">
          <div class="reco-label">Recommended Route</div>
          <div class="reco-title">Suggested: Misty {closest_name}</div>
          <div class="reco-subtitle">{reco_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Comparison cards ──
        empty_label = empty_yard if empty_yard.strip() else "Empty Yard / ICD"
        c_left, c_right = st.columns(2, gap="medium")

        with c_left:
            st.markdown(f"""
            <div class="route-card {'winner' if not saving else ''}">
              <span class="card-badge badge-gray">Traditional Route</span>
              <div class="card-title">{empty_label}</div>
              <div class="card-row"><span class="card-key">One-way</span><span class="card-val">{dist_empty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Round trip</span><span class="card-val">{rt_empty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Fuel consumed</span><span class="card-val">{fuel_empty:.1f} L</span></div>
              <div class="card-row"><span class="card-key">Fuel cost</span><span class="card-val">₹{cost_empty:,.0f}</span></div>
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            st.markdown(f"""
            <div class="route-card {'winner' if saving else ''}">
              <span class="card-badge badge-blue">Misty Route</span>
              <div class="card-title">Misty {closest_name}</div>
              <div class="card-row"><span class="card-key">One-way</span><span class="card-val-accent">{dist_misty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Round trip</span><span class="card-val-accent">{rt_misty:.0f} km</span></div>
              <div class="card-row"><span class="card-key">Fuel consumed</span><span class="card-val-accent">{fuel_misty:.1f} L</span></div>
              <div class="card-row"><span class="card-key">Fuel cost</span><span class="card-val-accent">₹{cost_misty:,.0f}</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)

        # ── Savings dashboard ──
        st.markdown('<div class="section-header">Savings Dashboard</div>', unsafe_allow_html=True)

        polarity = "positive" if saving else "negative"
        prefix   = "" if saving else "+"   # positive = savings, negative = extra spend

        s1, s2, s3 = st.columns(3, gap="small")
        with s1:
            st.markdown(f"""
            <div class="metric-block {polarity}">
              <div class="metric-label">KM Saved</div>
              <div class="metric-value {polarity}">{abs(km_saved):.0f}<span class="metric-unit">km</span></div>
              <div style="font-size:11px;color:#3e5a78;margin-top:4px;">round trip delta</div>
            </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="metric-block {polarity}">
              <div class="metric-label">Fuel Saved</div>
              <div class="metric-value {polarity}">{abs(fuel_saved):.1f}<span class="metric-unit">L</span></div>
              <div style="font-size:11px;color:#3e5a78;margin-top:4px;">at 2.5 km/L</div>
            </div>
            """, unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
            <div class="metric-block {polarity}">
              <div class="metric-label">Cash Saved</div>
              <div class="metric-value {polarity}">₹{abs(money_saved):,.0f}</div>
              <div style="font-size:11px;color:#3e5a78;margin-top:4px;">at ₹{fuel_rate:.0f}/L</div>
            </div>
            """, unsafe_allow_html=True)

        if not saving:
            st.markdown(f"""
            <div style="background:#1a0f0f;border:1px solid #3d1f1f;border-radius:8px;
                        padding:0.75rem 1.25rem;margin-top:0.75rem;font-size:12px;color:#c0392b;">
              ⚠ Misty {closest_name} adds {abs(km_saved):.0f} km over the traditional route for this origin.
              The Empty Yard is the more efficient option here.
            </div>
            """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #161f2c;margin-top:2.5rem;padding-top:1rem;
            display:flex;justify-content:space-between;align-items:center">
  <span style="font-size:11px;color:#2a3a4a;">MatchLog · Misty Optimizer v1.0</span>
  <span style="font-size:11px;color:#2a3a4a;">Mileage: 2.5 km/L · All distances ×2 for round trip</span>
</div>
""", unsafe_allow_html=True)
