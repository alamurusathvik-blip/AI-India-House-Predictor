import textwrap
"""
Price Prediction Page
======================
Interactive property price prediction using trained ML models.
Users select city, location, bedrooms, and area to get instant
AI-powered price estimates with confidence ranges.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils import (
    inject_css, load_model, load_data, format_price,
    format_price_per_sqft, format_number, predict_price,
)

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title='Price Prediction',
    page_icon='🔮',
    layout='wide',
)

# ── Inject Premium CSS ──────────────────────────────────────────────
inject_css()

# ── Load Model & Metadata ──────────────────────────────────────────
try:
    model, preprocessor, metadata = load_model()
    city_location_map = metadata.get('city_location_map', {})
    location_coords = metadata.get('location_coords', {})
    city_avg_price_per_sqft = metadata.get('city_avg_price_per_sqft', {})
    city_avg_prices = metadata.get('city_avg_prices', {})
    model_loaded = True
except Exception as e:
    st.error(f"⚠️ Failed to load model: {e}")
    model_loaded = False
    st.stop()

# ── Page Header ─────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<div class="page-title">🔮 Property Price Prediction</div>
<div class="page-subtitle">Get instant AI-powered property valuations across India</div>
"""))

st.html("---")

# ── Sidebar Inputs ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(textwrap.dedent("""
    <div style="text-align: center; padding: 0.8rem 0 0.5rem 0;">
        <div style="font-size: 1.8rem;">🔮</div>
        <div style="font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-top: 0.2rem;">
            Property Details
        </div>
        <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.1rem;">
            Fill in the details below
        </div>
    </div>
    """))

    st.html("---")

    # City Selection
    cities = sorted(city_location_map.keys())
    selected_city = st.selectbox(
        '🌆 Select City',
        options=cities,
        index=0,
        help='Choose the city where the property is located.',
    )

    # Location Selection (filtered by city)
    locations = sorted(city_location_map.get(selected_city, []))
    selected_location = st.selectbox(
        '📍 Select Location',
        options=locations,
        index=0,
        help='Choose the specific area or locality.',
    )

    st.markdown("<br>")

    # Bedrooms
    bedrooms = st.slider(
        '🛏️ Number of Bedrooms',
        min_value=1,
        max_value=10,
        value=2,
        step=1,
        help='Select the number of bedrooms (1-10 BHK).',
    )

    # Area
    area_sqft = st.slider(
        '📐 Area (sq.ft)',
        min_value=100,
        max_value=10000,
        value=1200,
        step=50,
        help='Enter the property area in square feet.',
    )

    st.html(textwrap.dedent("<br>"))

    # Auto-fill coordinates
    coord_key = f"{selected_city}||{selected_location}"
    default_lat, default_lon = location_coords.get(coord_key, (20.5937, 78.9629))

    st.html(textwrap.dedent("""
    <div style="font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 0.5rem;">
        📌 Auto-Detected Coordinates
    </div>
    """))

    lat = st.number_input(
        'Latitude',
        value=float(default_lat),
        format='%.6f',
        disabled=True,
    )

    lon = st.number_input(
        'Longitude',
        value=float(default_lon),
        format='%.6f',
        disabled=True,
    )

    st.html(textwrap.dedent("<br>"))

    # Predict Button
    predict_clicked = st.button('🚀 Predict Price', use_container_width=True)


# ── Main Area ───────────────────────────────────────────────────────

if not predict_clicked:
    # Placeholder message
    st.html(textwrap.dedent("""
    <div class="placeholder-card">
        <span class="placeholder-icon">🏡</span>
        <div class="placeholder-text">
            Select a <strong>city</strong>, <strong>location</strong>, <strong>bedrooms</strong>,
            and <strong>area</strong> from the sidebar, then click
            <strong>Predict Price</strong> to get an instant AI-powered valuation.
        </div>
    </div>
    """))

    st.html(textwrap.dedent("<br>"))

    # Quick stats cards
    st.html(textwrap.dedent("""
    <div class="section-header">How It Works</div>
    <div class="section-subheader">Our AI model considers multiple factors for accurate predictions</div>
    """))

    how_cols = st.columns(4)
    steps = [
        ('1️⃣', 'Select Location', 'Choose from hundreds of cities and localities across India'),
        ('2️⃣', 'Set Parameters', 'Specify bedrooms, area size, and let GPS auto-detect'),
        ('3️⃣', 'AI Analysis', 'Our ML model processes location data, market trends & features'),
        ('4️⃣', 'Get Results', 'Receive instant price prediction with confidence range'),
    ]
    for col, (icon, title, desc) in zip(how_cols, steps):
        with col:
            st.html(textwrap.dedent(f"""
            <div class="feature-card" style="min-height: 180px;">
                <span style="font-size: 2rem; display: block; margin-bottom: 0.5rem;">{icon}</span>
                <div class="feature-title" style="font-size: 1rem;">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """))

else:
    # ── Prediction Logic ────────────────────────────────────────────
    with st.spinner('🔮 Analyzing property data and generating prediction...'):
        predicted_price = predict_price(
            city=selected_city,
            location=selected_location,
            bedrooms=bedrooms,
            area_sqft=area_sqft,
            lat=lat,
            lon=lon,
            model=model,
            preprocessor=preprocessor,
            metadata=metadata,
        )

    # ── Main Prediction Card ────────────────────────────────────────
    formatted_price = format_price(predicted_price)

    st.html(textwrap.dedent(f"""
    <div class="prediction-card">
        <div class="prediction-label">Estimated Property Value</div>
        <div class="prediction-price">{formatted_price}</div>
        <div class="prediction-subtitle">
            AI-powered valuation for {selected_location}, {selected_city}
        </div>
    </div>
    """))

    st.html(textwrap.dedent("<br>"))

    # ── Confidence Range ────────────────────────────────────────────
    low_price = predicted_price * 0.90
    high_price = predicted_price * 1.10

    conf_cols = st.columns([1, 2, 1])
    with conf_cols[1]:
        st.html(textwrap.dedent(f"""
        <div class="confidence-card">
            <div class="confidence-label">📊 Confidence Range (±10%)</div>
            <div class="confidence-range">
                {format_price(low_price)} — {format_price(high_price)}
            </div>
        </div>
        """))

    st.html(textwrap.dedent("<br>"))

    # ── Property Summary Card ───────────────────────────────────────
    st.html(textwrap.dedent("""
    <div class="section-header">Property Summary</div>
    """))

    st.html(textwrap.dedent(f"""
    <div class="summary-card">
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-item-label">City</div>
                <div class="summary-item-value">🌆 {selected_city}</div>
            </div>
            <div class="summary-item">
                <div class="summary-item-label">Location</div>
                <div class="summary-item-value">📍 {selected_location}</div>
            </div>
            <div class="summary-item">
                <div class="summary-item-label">Bedrooms</div>
                <div class="summary-item-value">🛏️ {bedrooms} BHK</div>
            </div>
            <div class="summary-item">
                <div class="summary-item-label">Area</div>
                <div class="summary-item-value">📐 {format_number(area_sqft)} sq.ft</div>
            </div>
            <div class="summary-item">
                <div class="summary-item-label">Latitude</div>
                <div class="summary-item-value">🧭 {lat:.4f}°</div>
            </div>
            <div class="summary-item">
                <div class="summary-item-label">Longitude</div>
                <div class="summary-item-value">🧭 {lon:.4f}°</div>
            </div>
        </div>
    </div>
    """))

    st.html(textwrap.dedent("<br>"))

    # ── Price Breakdown Section ─────────────────────────────────────
    st.html(textwrap.dedent("""
    <div class="section-header">Price Breakdown</div>
    <div class="section-subheader">How your property compares to market averages</div>
    """))

    # Predicted Price Per Sq.Ft
    predicted_pps_lakhs = predicted_price / area_sqft  # in lakhs per sqft
    predicted_pps_rupees = predicted_pps_lakhs * 100000

    # Market Average Per Sq.Ft for city
    market_pps_lakhs = city_avg_price_per_sqft.get(selected_city, 0)
    market_pps_rupees = market_pps_lakhs * 100000

    # Comparison
    if market_pps_rupees > 0:
        pps_diff_pct = ((predicted_pps_rupees - market_pps_rupees) / market_pps_rupees) * 100
        is_above = pps_diff_pct > 0
    else:
        pps_diff_pct = 0
        is_above = False

    breakdown_cols = st.columns(3)

    with breakdown_cols[0]:
        st.html(textwrap.dedent(f"""
        <div class="breakdown-card">
            <div class="breakdown-label">Predicted Price/Sq.Ft</div>
            <div class="breakdown-value" style="color: #00d2ff;">₹{predicted_pps_rupees:,.0f}</div>
            <div class="breakdown-label">Per Square Foot</div>
        </div>
        """))

    with breakdown_cols[1]:
        st.html(textwrap.dedent(f"""
        <div class="breakdown-card">
            <div class="breakdown-label">Market Average ({selected_city})</div>
            <div class="breakdown-value" style="color: #667eea;">₹{market_pps_rupees:,.0f}</div>
            <div class="breakdown-label">City Avg Per Sq.Ft</div>
        </div>
        """))

    with breakdown_cols[2]:
        badge_class = 'badge-above' if is_above else 'badge-below'
        badge_text = f"{'↑' if is_above else '↓'} {abs(pps_diff_pct):.1f}% {'above' if is_above else 'below'} average"
        st.html(textwrap.dedent(f"""
        <div class="breakdown-card">
            <div class="breakdown-label">Comparison</div>
            <div style="margin: 0.5rem 0;">
                <span class="{badge_class}">{badge_text}</span>
            </div>
            <div class="breakdown-label">vs {selected_city} Average</div>
        </div>
        """))

    st.html(textwrap.dedent("<br>"))

    # ── City Average Price Card ─────────────────────────────────────
    city_avg = city_avg_prices.get(selected_city, 0)
    if city_avg > 0:
        city_diff_pct = ((predicted_price - city_avg) / city_avg) * 100
        city_is_above = city_diff_pct > 0
        city_badge_class = 'badge-above' if city_is_above else 'badge-below'
        city_badge_text = f"{'↑' if city_is_above else '↓'} {abs(city_diff_pct):.1f}% {'above' if city_is_above else 'below'} city average"

        avg_cols = st.columns([1, 2, 1])
        with avg_cols[1]:
            st.html(textwrap.dedent(f"""
            <div class="confidence-card" style="background: rgba(102, 126, 234, 0.04); border-color: rgba(102, 126, 234, 0.15);">
                <div class="confidence-label">💰 City Average Property Price</div>
                <div class="confidence-range" style="color: #667eea;">
                    {format_price(city_avg)}
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="{city_badge_class}">{city_badge_text}</span>
                </div>
            </div>
            """))
