import textwrap
"""
Shared Utilities for AI India House Price Predictor
====================================================
Provides common functions for data loading, model loading,
price formatting, prediction logic, and premium CSS theming.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# =============================================================================
# PRICE FORMATTING
# =============================================================================

def format_price(price_lakhs: float) -> str:
    """Format price in Lakhs/Crore with ₹ symbol.

    Args:
        price_lakhs: Price value in Lakhs.

    Returns:
        Formatted string like '₹1.75 Crore' or '₹82.50 Lakhs'.
    """
    if price_lakhs >= 100:
        crore = price_lakhs / 100
        return f'₹{crore:.2f} Crore'
    else:
        return f'₹{price_lakhs:.2f} Lakhs'


def format_price_per_sqft(pps_lakhs: float) -> str:
    """Format price_per_sqft (which is in lakhs) to ₹X,XXX per sq.ft.

    Args:
        pps_lakhs: Price per square foot in Lakhs.

    Returns:
        Formatted string like '₹8,500/sq.ft'.
    """
    rupees = pps_lakhs * 100000  # convert lakhs to rupees
    return f'₹{rupees:,.0f}/sq.ft'


def format_number(num: float) -> str:
    """Format a number with commas for thousands separators.

    Args:
        num: Number to format.

    Returns:
        Formatted string like '1,23,456'.
    """
    return f'{num:,.0f}'


# =============================================================================
# MODEL & DATA LOADING
# =============================================================================

@st.cache_resource
def load_model():
    """Load the trained model, preprocessor, and training metadata.

    Returns:
        Tuple of (model, preprocessor, metadata dict).
    """
    model = joblib.load('models/model.pkl')
    preprocessor = joblib.load('models/preprocessor.pkl')
    metadata = joblib.load('models/training_metadata.pkl')
    return model, preprocessor, metadata


@st.cache_data
def load_data():
    """Load the cleaned dataset used for analytics.

    Returns:
        pandas DataFrame with cleaned property data.
    """
    return joblib.load('models/cleaned_data.pkl')


# =============================================================================
# PREDICTION LOGIC
# =============================================================================

def predict_price(city, location, bedrooms, area_sqft, lat, lon, model, preprocessor, metadata):
    """Predict property price from user inputs.

    Args:
        city: City name.
        location: Location name within the city.
        bedrooms: Number of bedrooms.
        area_sqft: Property area in square feet.
        lat: Latitude coordinate.
        lon: Longitude coordinate.
        model: Trained ML model.
        preprocessor: Fitted sklearn ColumnTransformer.
        metadata: Training metadata dict.

    Returns:
        Predicted price in Lakhs (minimum ₹1 Lakh).
    """
    bedroom_density = area_sqft / max(bedrooms, 1)
    geo_cluster = str(metadata['geo_clusterer'].predict([[lat, lon]])[0])

    if area_sqft <= 800:
        area_cat = 'Small'
    elif area_sqft <= 1500:
        area_cat = 'Medium'
    elif area_sqft <= 2500:
        area_cat = 'Large'
    else:
        area_cat = 'Luxury'

    premium_score = metadata['premium_score_map'].get(location, 0.5)

    input_df = pd.DataFrame([{
        'city': city,
        'location_name': location,
        'latitude': lat,
        'longitude': lon,
        'bedrooms': bedrooms,
        'area_sqft': float(area_sqft),
        'bedroom_density': bedroom_density,
        'geo_cluster': geo_cluster,
        'area_category': area_cat,
        'premium_location_score': premium_score,
    }])

    X = preprocessor.transform(input_df)
    prediction = model.predict(X)[0]
    return max(prediction, 1.0)  # minimum ₹1 Lakh


# =============================================================================
# PLOTLY THEME HELPERS
# =============================================================================

CHART_COLORS = [
    '#00d2ff', '#3a7bd5', '#667eea', '#764ba2', '#f093fb',
    '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
    '#fa709a', '#fee140', '#a18cd1', '#fbc2eb', '#8fd3f4',
]

GRADIENT_COLORS = [
    '#0ea5e9', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
    '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e',
]


def get_chart_layout(title: str = '', height: int = 450) -> dict:
    """Get standard Plotly chart layout with dark theme.

    Args:
        title: Chart title.
        height: Chart height in pixels.

    Returns:
        Dict of Plotly layout properties.
    """
    return dict(
        title=dict(
            text=title,
            font=dict(family='Inter, sans-serif', size=18, color='#e2e8f0'),
            x=0.5,
            xanchor='center',
        ),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        font=dict(family='Inter, sans-serif', color='#94a3b8'),
        margin=dict(l=60, r=30, t=60, b=50),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)',
            font=dict(color='#94a3b8'),
        ),
    )


# =============================================================================
# CSS INJECTION
# =============================================================================

CSS = """
<style>
/* ================================================================
   GOOGLE FONT — Inter
   ================================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ================================================================
   ROOT & GLOBAL RESET
   ================================================================ */
:root {
    --bg-primary: #0a0a1a;
    --bg-secondary: #1a1a2e;
    --bg-tertiary: #16213e;
    --card-bg: rgba(255, 255, 255, 0.03);
    --card-border: rgba(255, 255, 255, 0.08);
    --card-hover-border: rgba(255, 255, 255, 0.15);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-blue: #00d2ff;
    --accent-purple: #764ba2;
    --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --kpi-gradient: linear-gradient(90deg, #00d2ff, #3a7bd5);
    --sidebar-bg: rgba(15, 15, 35, 0.95);
    --border-radius: 16px;
    --transition-speed: 0.3s;
    --glow-blue: 0 0 20px rgba(0, 210, 255, 0.15);
    --glow-purple: 0 0 20px rgba(118, 75, 162, 0.15);
}

*, *::before, *::after {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
}

/* ================================================================
   MAIN APP BACKGROUND
   ================================================================ */
.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%) !important;
    color: var(--text-primary) !important;
}

.stApp > header {
    background: transparent !important;
}

[data-testid="stHeader"] {
    background: rgba(10, 10, 26, 0.8) !important;
    backdrop-filter: blur(10px) !important;
}

/* ================================================================
   HIDE DEFAULT STREAMLIT ELEMENTS
   ================================================================ */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header[data-testid="stHeader"] .stDeployButton {display: none !important;}

/* ================================================================
   SIDEBAR STYLING
   ================================================================ */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(20px) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--text-secondary) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    padding-top: 1rem !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    color: var(--text-secondary) !important;
    padding: 0.6rem 1rem !important;
    border-radius: 10px !important;
    transition: all var(--transition-speed) ease !important;
    margin: 2px 8px !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: rgba(102, 126, 234, 0.15) !important;
    color: #667eea !important;
    border-left: 3px solid #667eea !important;
}

/* ================================================================
   GLASSMORPHIC CARD CLASSES
   ================================================================ */
.glass-card {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: var(--border-radius) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    transition: all var(--transition-speed) ease !important;
    animation: fadeInUp 0.6s ease-out !important;
}

.glass-card:hover {
    border-color: var(--card-hover-border) !important;
    box-shadow: var(--glow-blue) !important;
    transform: translateY(-2px) !important;
}

/* ================================================================
   KPI / METRIC CARDS
   ================================================================ */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--border-radius);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all var(--transition-speed) ease;
    animation: fadeInUp 0.6s ease-out;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--kpi-gradient);
    border-radius: var(--border-radius) var(--border-radius) 0 0;
}

.kpi-card:hover {
    border-color: var(--card-hover-border);
    box-shadow: var(--glow-blue);
    transform: translateY(-4px);
}

.kpi-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    display: block;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: var(--kpi-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0.3rem 0;
    line-height: 1.2;
}

.kpi-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

/* ================================================================
   PREDICTION RESULT CARD
   ================================================================ */
.prediction-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    padding: 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    animation: fadeInScale 0.8s ease-out;
}

.prediction-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
}

.prediction-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 60%);
    pointer-events: none;
}

.prediction-label {
    font-size: 1rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.prediction-price {
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin: 0.5rem 0;
}

.prediction-subtitle {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
}

/* ================================================================
   CONFIDENCE RANGE CARD
   ================================================================ */
.confidence-card {
    background: rgba(0, 210, 255, 0.04);
    border: 1px solid rgba(0, 210, 255, 0.15);
    border-radius: var(--border-radius);
    padding: 1.2rem 1.5rem;
    text-align: center;
    animation: fadeInUp 0.7s ease-out;
}

.confidence-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

.confidence-range {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--accent-blue);
    margin-top: 0.3rem;
}

/* ================================================================
   PROPERTY SUMMARY CARD
   ================================================================ */
.summary-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--border-radius);
    backdrop-filter: blur(20px);
    padding: 1.5rem;
    animation: fadeInUp 0.8s ease-out;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 0.5rem;
}

.summary-item {
    text-align: center;
    padding: 0.8rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.04);
}

.summary-item-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

.summary-item-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 0.3rem;
}

/* ================================================================
   COMPARISON BADGE
   ================================================================ */
.badge-above {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-below {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

/* ================================================================
   FEATURE CARDS (Landing page)
   ================================================================ */
.feature-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--border-radius);
    backdrop-filter: blur(20px);
    padding: 2rem;
    text-align: center;
    transition: all var(--transition-speed) ease;
    animation: fadeInUp 0.6s ease-out;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.feature-card:hover {
    border-color: var(--card-hover-border);
    box-shadow: var(--glow-purple);
    transform: translateY(-6px);
}

.feature-icon {
    font-size: 2.8rem;
    margin-bottom: 1rem;
    display: block;
}

.feature-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.feature-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* ================================================================
   HERO SECTION
   ================================================================ */
.hero-section {
    text-align: center;
    padding: 2rem 0 1.5rem 0;
    animation: fadeInDown 0.8s ease-out;
}

.hero-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    font-weight: 400;
    max-width: 650px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ================================================================
   SECTION HEADERS
   ================================================================ */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid transparent;
    border-image: linear-gradient(90deg, #667eea, #764ba2, transparent) 1;
    display: inline-block;
}

.section-subheader {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
    font-weight: 400;
}

/* ================================================================
   INSIGHT CARDS (AI Insights Page)
   ================================================================ */
.insight-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    backdrop-filter: blur(20px);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    transition: all var(--transition-speed) ease;
    animation: fadeInUp 0.5s ease-out;
}

.insight-card:hover {
    border-color: rgba(102, 126, 234, 0.3);
    box-shadow: 0 0 15px rgba(102, 126, 234, 0.08);
    transform: translateX(4px);
}

.insight-text {
    font-size: 0.95rem;
    color: var(--text-primary);
    line-height: 1.6;
    font-weight: 400;
}

.insight-text strong {
    color: #00d2ff;
    font-weight: 600;
}

/* ================================================================
   MODEL COMPARISON TABLE
   ================================================================ */
.model-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: var(--border-radius);
    overflow: hidden;
    animation: fadeInUp 0.6s ease-out;
}

.model-table thead th {
    background: rgba(102, 126, 234, 0.15);
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.8rem 1rem;
    text-align: left;
    border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.model-table tbody td {
    padding: 0.7rem 1rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    background: rgba(255, 255, 255, 0.01);
}

.model-table tbody tr:hover td {
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-primary);
}

.model-table tbody tr.best-model td {
    background: rgba(102, 126, 234, 0.08);
    color: var(--text-primary);
    font-weight: 500;
}

/* ================================================================
   BUTTONS
   ================================================================ */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.03em !important;
    transition: all var(--transition-speed) ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4) !important;
}

.stButton > button:active {
    transform: scale(0.98) !important;
}

/* ================================================================
   SELECTBOX, SLIDER, NUMBER INPUT
   ================================================================ */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stSlider > div > div > div {
    background: rgba(102, 126, 234, 0.3) !important;
}

.stSlider [data-testid="stThumbValue"] {
    color: var(--text-primary) !important;
}

/* ================================================================
   TABS
   ================================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 0;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: none !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 500 !important;
    transition: all var(--transition-speed) ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.04) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    background: rgba(102, 126, 234, 0.1) !important;
    border-bottom: 3px solid transparent !important;
    border-image: linear-gradient(90deg, #667eea, #764ba2) 1 !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem;
}

/* ================================================================
   STREAMLIT NATIVE METRIC OVERRIDE
   ================================================================ */
[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: var(--border-radius) !important;
    padding: 1rem !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
}

/* ================================================================
   EXPANDER
   ================================================================ */
.streamlit-expanderHeader {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* ================================================================
   PLOTLY CHART CONTAINERS
   ================================================================ */
[data-testid="stPlotlyChart"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: var(--border-radius) !important;
    padding: 0.5rem !important;
    transition: all var(--transition-speed) ease !important;
}

[data-testid="stPlotlyChart"]:hover {
    border-color: rgba(255, 255, 255, 0.12) !important;
}

/* ================================================================
   DATAFRAME
   ================================================================ */
[data-testid="stDataFrame"] {
    border-radius: var(--border-radius) !important;
    overflow: hidden !important;
}

/* ================================================================
   DIVIDER
   ================================================================ */
hr {
    border: none !important;
    border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
    margin: 1.5rem 0 !important;
}

/* ================================================================
   FOOTER SECTION
   ================================================================ */
.app-footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    color: var(--text-muted);
    font-size: 0.85rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    margin-top: 3rem;
}

.app-footer .powered-by {
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
}

/* ================================================================
   PLACEHOLDER CARD
   ================================================================ */
.placeholder-card {
    background: var(--card-bg);
    border: 2px dashed rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius);
    padding: 3rem 2rem;
    text-align: center;
    animation: fadeInUp 0.6s ease-out;
}

.placeholder-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    display: block;
    opacity: 0.7;
}

.placeholder-text {
    font-size: 1.1rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* ================================================================
   KEYFRAME ANIMATIONS
   ================================================================ */
@keyframes fadeInUp {
    0% {
        opacity: 0;
        transform: translateY(20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    0% {
        opacity: 0;
        transform: translateY(-20px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInScale {
    0% {
        opacity: 0;
        transform: scale(0.95);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* ================================================================
   PAGE TITLE OVERRIDE
   ================================================================ */
.page-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #667eea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}

.page-subtitle {
    font-size: 1rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
    font-weight: 400;
}

/* ================================================================
   SCROLLBAR
   ================================================================ */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* ================================================================
   RESPONSIVE
   ================================================================ */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }
    .hero-subtitle {
        font-size: 1rem;
    }
    .kpi-value {
        font-size: 1.4rem;
    }
    .prediction-price {
        font-size: 2.2rem;
    }
}

/* ================================================================
   PRICE BREAKDOWN CARD
   ================================================================ */
.breakdown-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    animation: fadeInUp 0.7s ease-out;
}

.breakdown-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0.3rem 0;
}

.breakdown-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}

/* ================================================================
   CHART CARD WRAPPER
   ================================================================ */
.chart-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--border-radius);
    padding: 1rem;
    margin-bottom: 1.5rem;
    transition: all var(--transition-speed) ease;
}

.chart-card:hover {
    border-color: rgba(255, 255, 255, 0.12);
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}

.chart-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.8rem;
    padding-left: 0.5rem;
    border-left: 3px solid #667eea;
}
</style>
"""


def inject_css():
    """Inject the premium dark theme CSS into the Streamlit app."""
    st.markdown(CSS, unsafe_allow_html=True)
