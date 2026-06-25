import textwrap
"""
AI India House Price Predictor — Landing Page
===============================================
Main entry point for the Streamlit application.
Displays hero section, KPI metrics, and feature cards.
"""

import streamlit as st
from utils import inject_css, load_model, load_data, format_price, format_number

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title='AI India House Price Predictor',
    page_icon='🏠',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ── Inject Premium CSS ──────────────────────────────────────────────
inject_css()

# ── Load Model & Metadata ──────────────────────────────────────────
try:
    model, preprocessor, metadata = load_model()
    stats = metadata.get('dataset_stats', {})
    model_loaded = True
except Exception as e:
    model_loaded = False
    stats = {}

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(textwrap.dedent("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">🏠</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-top: 0.3rem;">
            AI House Price Predictor
        </div>
        <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.2rem;">
            India Real Estate Intelligence
        </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown("---")

    if model_loaded:
        best_model = metadata.get('best_model_name', 'N/A')
        st.markdown(textwrap.dedent(f"""
        <div class="glass-card" style="padding: 1rem;">
            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;">
                Active Model
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #667eea; margin-top: 0.3rem;">
                {best_model}
            </div>
        </div>
        """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent("""
    <div style="padding: 0.5rem 0; color: #94a3b8; font-size: 0.85rem;">
        <div style="font-weight: 600; color: #f1f5f9; margin-bottom: 0.5rem;">📌 Quick Navigation</div>
        <div style="margin-bottom: 0.3rem;">🔮 <strong>Prediction</strong> — Get instant price estimates</div>
        <div style="margin-bottom: 0.3rem;">📊 <strong>Market Insights</strong> — Explore trends & analytics</div>
        <div style="margin-bottom: 0.3rem;">🤖 <strong>AI Insights</strong> — Intelligent data analysis</div>
    </div>
    """), unsafe_allow_html=True)


# ── Hero Section ────────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
<div class="hero-section">
    <div class="hero-title">AI India House Price Predictor</div>
    <div class="hero-subtitle">
        Predict property prices anywhere in India using machine learning
        and location intelligence. Powered by advanced AI models trained
        on comprehensive real estate data.
    </div>
</div>
"""), unsafe_allow_html=True)

# ── KPI Metric Cards ───────────────────────────────────────────────
total_properties = stats.get('total_properties', 0)
cities_covered = stats.get('cities_covered', 0)
avg_price = stats.get('avg_price', 0)
model_accuracy = stats.get('model_accuracy', 0)

kpi_data = [
    {
        'icon': '🏘️',
        'value': format_number(total_properties),
        'label': 'Total Properties',
        'delay': '0.1s',
    },
    {
        'icon': '🌆',
        'value': str(cities_covered),
        'label': 'Cities Covered',
        'delay': '0.2s',
    },
    {
        'icon': '💰',
        'value': format_price(avg_price),
        'label': 'Average Price',
        'delay': '0.3s',
    },
    {
        'icon': '🎯',
        'value': f'{model_accuracy * 100:.1f}%',
        'label': 'Model Accuracy (R²)',
        'delay': '0.4s',
    },
]

cols = st.columns(4)
for col, kpi in zip(cols, kpi_data):
    with col:
        st.markdown(textwrap.dedent(f"""
        <div class="kpi-card" style="animation-delay: {kpi['delay']};">
            <span class="kpi-icon">{kpi['icon']}</span>
            <div class="kpi-value">{kpi['value']}</div>
            <div class="kpi-label">{kpi['label']}</div>
        </div>
        """), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Cards ──────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
<div class="section-header">Explore the Platform</div>
<div class="section-subheader">Powerful tools for real estate intelligence</div>
"""), unsafe_allow_html=True)

features = [
    {
        'icon': '🔮',
        'title': 'Price Prediction',
        'desc': 'Get instant, AI-powered property price estimates based on location, area, and amenities. Our model analyzes multiple features for accurate valuations.',
    },
    {
        'icon': '📊',
        'title': 'Market Insights',
        'desc': 'Explore interactive dashboards with city-wise price trends, area distributions, and market comparisons across India\'s real estate landscape.',
    },
    {
        'icon': '🤖',
        'title': 'AI Insights',
        'desc': 'Discover intelligent, data-driven insights about pricing patterns, feature importance, location premiums, and model performance analytics.',
    },
]

feat_cols = st.columns(3)
for col, feat in zip(feat_cols, features):
    with col:
        st.markdown(textwrap.dedent(f"""
        <div class="feature-card">
            <span class="feature-icon">{feat['icon']}</span>
            <div class="feature-title">{feat['title']}</div>
            <div class="feature-desc">{feat['desc']}</div>
        </div>
        """), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Data Pipeline Overview ─────────────────────────────────────────
if model_loaded:
    cleaning_stats = metadata.get('cleaning_stats', {})
    if cleaning_stats:
        st.markdown(textwrap.dedent("""
        <div class="section-header">Data Pipeline Summary</div>
        <div class="section-subheader">How we cleaned and prepared the dataset</div>
        """), unsafe_allow_html=True)

        pipeline_cols = st.columns(4)
        pipeline_items = [
            ('📥', 'Original Records', format_number(cleaning_stats.get('original_rows', 0))),
            ('✅', 'Cleaned Records', format_number(cleaning_stats.get('cleaned_rows', 0))),
            ('🗑️', 'Duplicates Removed', format_number(cleaning_stats.get('duplicates_removed', 0))),
            ('📍', 'Invalid Coords Removed', format_number(cleaning_stats.get('invalid_coordinates_removed', 0))),
        ]

        for col, (icon, label, value) in zip(pipeline_cols, pipeline_items):
            with col:
                st.markdown(textwrap.dedent(f"""
                <div class="kpi-card">
                    <span class="kpi-icon">{icon}</span>
                    <div class="kpi-value" style="font-size: 1.4rem;">{value}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """), unsafe_allow_html=True)

        pipeline_cols2 = st.columns(4)
        pipeline_items2 = [
            ('📏', 'Invalid Area Removed', format_number(cleaning_stats.get('invalid_area_removed', 0))),
            ('💸', 'Price Outliers Removed', format_number(cleaning_stats.get('price_outliers_removed', 0))),
            ('🛏️', 'Extreme Bedrooms Removed', format_number(cleaning_stats.get('extreme_bedrooms_removed', 0))),
            ('📊', 'Locations Covered', format_number(stats.get('locations_covered', 0))),
        ]

        for col, (icon, label, value) in zip(pipeline_cols2, pipeline_items2):
            with col:
                st.markdown(textwrap.dedent(f"""
                <div class="kpi-card">
                    <span class="kpi-icon">{icon}</span>
                    <div class="kpi-value" style="font-size: 1.4rem;">{value}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """), unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
<div class="app-footer">
    <span class="powered-by">Powered by Machine Learning</span>
    <span style="margin: 0 0.5rem;">•</span>
    Built with Streamlit & Plotly
    <span style="margin: 0 0.5rem;">•</span>
    India Real Estate Intelligence Platform
</div>
"""), unsafe_allow_html=True)
