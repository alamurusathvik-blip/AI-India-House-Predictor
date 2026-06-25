import textwrap
"""
AI India House Price Predictor — Home & Prediction Page
=========================================================
Main entry point. Shows hero header, horizontal nav, prediction
form inline, and results. KPI stats shown below.
"""

import streamlit as st
import pandas as pd
from utils import (
    inject_css, load_model, load_data, format_price,
    format_number, format_price_per_sqft, predict_price,
)

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title='AI India House Price Predictor',
    page_icon='🏠',
    layout='wide',
    initial_sidebar_state='collapsed',
)

# ── Inject CSS ──────────────────────────────────────────────────────
inject_css()

# ── Horizontal Nav Bar ──────────────────────────────────────────────
st.html("""
<nav class="top-nav">
    <div class="top-nav-inner">
        <div class="top-nav-brand">🏠 India House Predictor</div>
        <div class="top-nav-links">
            <a class="top-nav-link active" href="/">🔮 Predict</a>
            <a class="top-nav-link" href="/Market_Insights">📊 Market Insights</a>
            <a class="top-nav-link" href="/Data_Insights">📈 Data Insights</a>
        </div>
    </div>
</nav>
<div style="height: 4rem;"></div>
""")

# ── Load Model ──────────────────────────────────────────────────────
try:
    model, preprocessor, metadata = load_model()
    stats = metadata.get('dataset_stats', {})
    city_location_map = metadata.get('city_location_map', {})
    location_coords = metadata.get('location_coords', {})
    city_avg_price_per_sqft = metadata.get('city_avg_price_per_sqft', {})
    city_avg_prices = metadata.get('city_avg_prices', {})
    model_loaded = True
except Exception as e:
    st.error(f"⚠️ Failed to load model: {e}")
    model_loaded = False
    st.stop()

# ── Hero Header ─────────────────────────────────────────────────────
st.html("""
<div class="hero-section" style="padding: 1.5rem 0 1rem 0; text-align: center;">
    <div class="hero-title" style="font-size: 2.2rem;">AI India House Price Predictor</div>
    <div class="hero-subtitle" style="font-size: 1rem; max-width: 580px; margin: 0.5rem auto 0;">
        Enter property details below and get an instant ML-powered valuation.
    </div>
</div>
""")

# ── KPI Row ─────────────────────────────────────────────────────────
total_properties = stats.get('total_properties', 0)
cities_covered = stats.get('cities_covered', 0)
avg_price = stats.get('avg_price', 0)
model_accuracy = stats.get('model_accuracy', 0)
national_pps = metadata.get('national_avg_price_per_sqft', 0)

kpi_cols = st.columns(4)
kpis = [
    ('🏘️', format_number(total_properties), 'Properties Analyzed'),
    ('🌆', str(cities_covered), 'Cities'),
    ('💰', format_price(avg_price), 'National Avg Price'),
    ('📐', format_price_per_sqft(national_pps), 'National Avg/Sq.Ft'),
]
for col, (icon, val, lbl) in zip(kpi_cols, kpis):
    with col:
        st.html(f"""
        <div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{lbl}</div>
        </div>
        """)

st.html("<br>")

# ── Prediction Form ─────────────────────────────────────────────────
cities = sorted(city_location_map.keys())

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.html("""<div class="glass-card" style="padding: 1.5rem;">
    <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 1.2rem;">
        🏡 Property Details
    </div>""")

    selected_city = st.selectbox(
        '🌆 City',
        options=cities,
        index=0,
        help='Choose the city where the property is located.',
    )
    locations = sorted(city_location_map.get(selected_city, []))
    selected_location = st.selectbox(
        '📍 Location',
        options=locations,
        index=0,
        help='Choose the specific locality.',
    )

    bedrooms = st.slider(
        '🛏️ Bedrooms',
        min_value=1, max_value=10, value=2,
        help='Number of bedrooms (BHK).',
    )
    area_sqft = st.slider(
        '📐 Area (sq.ft)',
        min_value=100, max_value=10000, value=1200, step=50,
        help='Built-up area in square feet.',
    )

    # ── Coordinate lookup ───────────────────────────────────────────
    coord_key = f"{selected_city}||{selected_location}"
    is_fallback = coord_key not in location_coords
    default_lat, default_lon = location_coords.get(coord_key, (20.5937, 78.9629))

    coord_c1, coord_c2 = st.columns(2)
    with coord_c1:
        st.number_input('Latitude', value=float(default_lat), format='%.6f', disabled=True)
    with coord_c2:
        st.number_input('Longitude', value=float(default_lon), format='%.6f', disabled=True)

    if is_fallback:
        st.html("""
        <div style="background: rgba(251,191,36,0.12); border: 1px solid rgba(251,191,36,0.35);
             border-radius: 8px; padding: 0.6rem 0.9rem; margin: 0.5rem 0;
             color: #fbbf24; font-size: 0.82rem; line-height: 1.5;">
            ⚠️ <strong>Approximate location:</strong> Exact coordinates for this locality
            aren't in our dataset. Using regional centre — prediction may be less precise.
        </div>
        """)

    # ── Sanity check ────────────────────────────────────────────────
    sqft_per_bed = area_sqft / max(bedrooms, 1)
    if sqft_per_bed < 150:
        st.html(f"""
        <div style="background: rgba(248,113,113,0.10); border: 1px solid rgba(248,113,113,0.35);
             border-radius: 8px; padding: 0.6rem 0.9rem; margin: 0.5rem 0;
             color: #f87171; font-size: 0.82rem; line-height: 1.5;">
            ⚠️ <strong>Unusual ratio:</strong> {area_sqft:,} sq.ft for {bedrooms} bedroom(s)
            is less than 150 sq.ft/bedroom — the model may extrapolate unreliably.
        </div>
        """)

    st.html("</div>")  # close glass-card

    predict_clicked = st.button('🚀 Predict Price', use_container_width=True)

# ── Run prediction on click, persist in session_state ───────────────
if predict_clicked:
    with st.spinner('Analysing property data…'):
        predicted_price = predict_price(
            city=selected_city,
            location=selected_location,
            bedrooms=bedrooms,
            area_sqft=area_sqft,
            lat=default_lat,
            lon=default_lon,
            model=model,
            preprocessor=preprocessor,
            metadata=metadata,
        )
    st.session_state['last_prediction'] = {
        'price': predicted_price,
        'city': selected_city,
        'location': selected_location,
        'bedrooms': bedrooms,
        'area_sqft': area_sqft,
        'lat': default_lat,
        'lon': default_lon,
        'is_fallback': is_fallback,
    }

# ── Results Panel ───────────────────────────────────────────────────
with right_col:
    pred = st.session_state.get('last_prediction')

    if pred is None:
        st.html("""
        <div class="placeholder-card" style="min-height: 340px; display: flex;
             flex-direction: column; align-items: center; justify-content: center;">
            <span class="placeholder-icon">🏡</span>
            <div class="placeholder-text">
                Fill in the property details on the left and click
                <strong>Predict Price</strong> to get an instant valuation.
            </div>
        </div>
        """)
    else:
        p = pred['price']
        formatted_price = format_price(p)
        low = p * 0.90
        high = p * 1.10

        st.html(f"""
        <div class="prediction-card">
            <div class="prediction-label">Estimated Property Value</div>
            <div class="prediction-price">{formatted_price}</div>
            <div class="prediction-subtitle">
                {pred['location']}, {pred['city']} &nbsp;·&nbsp;
                {pred['bedrooms']} BHK &nbsp;·&nbsp; {format_number(pred['area_sqft'])} sq.ft
            </div>
        </div>
        """)

        st.html("<br>")

        # Typical range (honestly labelled)
        st.html(f"""
        <div class="confidence-card">
            <div class="confidence-label">📊 Typical Price Range (±10%)</div>
            <div class="confidence-range">{format_price(low)} — {format_price(high)}</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.4rem;">
                Based on typical market variance, not a statistical model interval.
            </div>
        </div>
        """)

        st.html("<br>")

        # Price breakdown
        predicted_pps_rupees = (p / pred['area_sqft']) * 100_000
        market_pps_rupees = city_avg_price_per_sqft.get(pred['city'], 0) * 100_000
        if market_pps_rupees > 0:
            diff_pct = ((predicted_pps_rupees - market_pps_rupees) / market_pps_rupees) * 100
            is_above = diff_pct > 0
            badge_class = 'badge-above' if is_above else 'badge-below'
            badge_text = f"{'↑' if is_above else '↓'} {abs(diff_pct):.1f}% {'above' if is_above else 'below'} avg"
        else:
            badge_text, badge_class = '—', ''

        b1, b2, b3 = st.columns(3)
        with b1:
            st.html(f"""<div class="breakdown-card">
                <div class="breakdown-label">Your Price/Sq.Ft</div>
                <div class="breakdown-value" style="color:#00d2ff;">₹{predicted_pps_rupees:,.0f}</div>
            </div>""")
        with b2:
            st.html(f"""<div class="breakdown-card">
                <div class="breakdown-label">{pred['city']} Avg/Sq.Ft</div>
                <div class="breakdown-value" style="color:#667eea;">₹{market_pps_rupees:,.0f}</div>
            </div>""")
        with b3:
            st.html(f"""<div class="breakdown-card">
                <div class="breakdown-label">Comparison</div>
                <div style="margin-top:0.5rem;"><span class="{badge_class}">{badge_text}</span></div>
            </div>""")

        if pred.get('is_fallback'):
            st.html("""
            <div style="margin-top:1rem; background: rgba(251,191,36,0.10);
                 border:1px solid rgba(251,191,36,0.3); border-radius:8px;
                 padding:0.5rem 0.9rem; color:#fbbf24; font-size:0.78rem;">
                📍 Approximate location used — coordinates inferred from city centre.
            </div>
            """)

# ── Data Pipeline Stats ─────────────────────────────────────────────
if model_loaded:
    cleaning_stats = metadata.get('cleaning_stats', {})
    if cleaning_stats:
        st.html("<br>")
        st.html("""
        <div class="section-header">Data Pipeline Summary</div>
        <div class="section-subheader">How we cleaned and prepared the dataset</div>
        """)
        pipe_cols = st.columns(4)
        pipeline_items = [
            ('📥', 'Original Records', format_number(cleaning_stats.get('original_rows', 0))),
            ('✅', 'Cleaned Records', format_number(cleaning_stats.get('cleaned_rows', 0))),
            ('🗑️', 'Duplicates Removed', format_number(cleaning_stats.get('duplicates_removed', 0))),
            ('📍', 'Invalid Coords Removed', format_number(cleaning_stats.get('invalid_coordinates_removed', 0))),
        ]
        for col, (icon, label, value) in zip(pipe_cols, pipeline_items):
            with col:
                st.html(f"""<div class="kpi-card">
                    <span class="kpi-icon">{icon}</span>
                    <div class="kpi-value" style="font-size:1.4rem;">{value}</div>
                    <div class="kpi-label">{label}</div>
                </div>""")

# ── Footer ──────────────────────────────────────────────────────────
st.html("""
<div class="app-footer">
    <span class="powered-by">Powered by Machine Learning</span>
    <span style="margin: 0 0.5rem;">•</span>
    Built with Streamlit &amp; Plotly
    <span style="margin: 0 0.5rem;">•</span>
    India Real Estate Intelligence Platform
</div>
""")
