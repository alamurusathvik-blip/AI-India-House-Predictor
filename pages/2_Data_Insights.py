"""

Data Insights Page
===================
Data-driven insights computed from the dataset and model metadata.
Covers city pricing, area analysis, feature importance, bedroom trends,
location premiums, and model performance analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    inject_css, load_data, load_model, format_price,
    format_price_per_sqft, format_number, get_chart_layout,
    CHART_COLORS, GRADIENT_COLORS,
)

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title='Data Insights | India House Price Predictor',
    page_icon='📈',
    layout='wide',
    initial_sidebar_state='collapsed',
)

# ── Inject Premium CSS ──────────────────────────────────────────────
inject_css()

# ── Horizontal Nav Bar ──────────────────────────────────────────────
st.html("""
<nav class="top-nav">
    <div class="top-nav-inner">
        <div class="top-nav-brand">🏠 India House Predictor</div>
        <div class="top-nav-links">
            <a class="top-nav-link" href="/">🔮 Predict</a>
            <a class="top-nav-link" href="/Market_Insights">📊 Market Insights</a>
            <a class="top-nav-link active" href="/Data_Insights">📈 Data Insights</a>
        </div>
    </div>
</nav>
<div style="height: 4rem;"></div>
""")

# ── Load Data & Metadata ───────────────────────────────────────────
try:
    df = load_data()
    model, preprocessor, metadata = load_model()
    data_loaded = True
except Exception as e:
    st.error(f"⚠️ Failed to load data: {e}")
    data_loaded = False
    st.stop()

# ── Page Header ─────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<div class="page-title">🤖 AI-Generated Insights</div>
<div class="page-subtitle">Intelligent analysis powered by data science and machine learning</div>
"""))

st.html("---")

# ── Extract metadata values ─────────────────────────────────────────
national_avg = metadata.get('national_avg_price', 0)
national_avg_pps = metadata.get('national_avg_price_per_sqft', 0)
city_avg_prices = metadata.get('city_avg_prices', {})
city_avg_pps = metadata.get('city_avg_price_per_sqft', {})
feature_importance = metadata.get('feature_importance', [])
premium_score_map = metadata.get('premium_score_map', {})
metrics_dict = metadata.get('metrics', {})
best_model_name = metadata.get('best_model_name', 'N/A')
cleaning_stats = metadata.get('cleaning_stats', {})


# ═══════════════════════════════════════════════════════════════════
# SECTION 1: City Price Insights
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">🏙️ City Price Insights</div>
<div class="section-subheader">How major cities compare to the national average</div>
""")

# Top 10 cities by property count
top_10_cities = df['city'].value_counts().head(10).index.tolist()

city_insight_cols = st.columns(2)
for i, city in enumerate(top_10_cities):
    city_avg = city_avg_prices.get(city, 0)
    if national_avg > 0 and city_avg > 0:
        pct_diff = ((city_avg - national_avg) / national_avg) * 100
        direction = 'more' if pct_diff > 0 else 'less'
        emoji = '📈' if pct_diff > 0 else '📉'

        with city_insight_cols[i % 2]:
            st.html(textwrap.dedent(f"""
            <div class="insight-card">
                <div class="insight-text">
                    {emoji} Properties in <strong>{city}</strong> are
                    <strong>{abs(pct_diff):.1f}%</strong> {direction} expensive
                    than the national average ({format_price(national_avg)}).
                    City average: <strong>{format_price(city_avg)}</strong>
                </div>
            </div>
            """))

st.html(textwrap.dedent("<br>"))


# ═══════════════════════════════════════════════════════════════════
# SECTION 2: Area Size Insights
# ═══════════════════════════════════════════════════════════════════
st.html(textwrap.dedent("""
<div class="section-header">📐 Area Size Insights</div>
<div class="section-subheader">How property size impacts pricing</div>
"""))

# Large/Luxury vs Small comparison
large_luxury = df[df['area_sqft'] > 2500]['price_value'].mean()
small = df[df['area_sqft'] <= 800]['price_value'].mean()

if small > 0 and large_luxury > 0:
    premium_pct = ((large_luxury - small) / small) * 100

    st.html(textwrap.dedent(f"""
    <div class="insight-card">
        <div class="insight-text">
            📐 Large and luxury properties above <strong>2,500 sq.ft</strong> command a premium of
            <strong>{premium_pct:.0f}%</strong> over smaller properties (under 800 sq.ft).
            Large/Luxury avg: <strong>{format_price(large_luxury)}</strong> vs
            Small avg: <strong>{format_price(small)}</strong>
        </div>
    </div>
    """))

# Area category breakdown
area_categories = ['Small', 'Medium', 'Large', 'Luxury']
area_desc = {'Small': '≤ 800 sq.ft', 'Medium': '801–1500 sq.ft', 'Large': '1501–2500 sq.ft', 'Luxury': '> 2500 sq.ft'}

area_cols = st.columns(4)
for col, cat in zip(area_cols, area_categories):
    cat_data = df[df['area_category'] == cat]
    if len(cat_data) > 0:
        avg_price = cat_data['price_value'].mean()
        count = len(cat_data)
        with col:
            st.html(textwrap.dedent(f"""
            <div class="kpi-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;">
                    {cat} ({area_desc.get(cat, '')})
                </div>
                <div class="kpi-value" style="font-size: 1.2rem;">{format_price(avg_price)}</div>
                <div class="kpi-label" style="font-size: 0.75rem;">{format_number(count)} properties</div>
            </div>
            """))

st.html(textwrap.dedent("<br>"))


# ═══════════════════════════════════════════════════════════════════
# SECTION 3: Feature Importance Insights
# ═══════════════════════════════════════════════════════════════════
st.html(textwrap.dedent("""
<div class="section-header">🎯 Feature Importance Insights</div>
<div class="section-subheader">What drives property prices according to our AI model</div>
"""))

if feature_importance:
    # Total importance for percentage calculation
    total_importance = sum(imp for _, imp in feature_importance)

    # Top feature insight
    top_feat_name, top_feat_imp = feature_importance[0]
    top_feat_pct = (top_feat_imp / total_importance * 100) if total_importance > 0 else 0

    st.html(textwrap.dedent(f"""
    <div class="insight-card">
        <div class="insight-text">
            🎯 <strong>{top_feat_name}</strong> is the strongest predictor of property prices,
            contributing <strong>{top_feat_pct:.1f}%</strong> to the model's price predictions.
        </div>
    </div>
    """))

    # Location vs Bedroom importance
    location_imp = 0
    bedroom_imp = 0
    for feat, imp in feature_importance:
        feat_lower = feat.lower()
        if 'location' in feat_lower or 'city' in feat_lower or 'latitude' in feat_lower or 'longitude' in feat_lower:
            location_imp += imp
        if 'bedroom' in feat_lower or 'bhk' in feat_lower:
            bedroom_imp += imp

    loc_pct = (location_imp / total_importance * 100) if total_importance > 0 else 0
    bed_pct = (bedroom_imp / total_importance * 100) if total_importance > 0 else 0
    loc_vs_bed = 'more' if loc_pct > bed_pct else 'less'

    st.html(textwrap.dedent(f"""
    <div class="insight-card">
        <div class="insight-text">
            📍 Location-related features contribute <strong>{loc_pct:.1f}%</strong> to predictions —
            that's {loc_vs_bed} than bedroom-related features (<strong>{bed_pct:.1f}%</strong>).
            This shows that <strong>{"where you buy matters most" if loc_pct > bed_pct else "property size matters as much as location"}</strong>.
        </div>
    </div>
    """))

    # Feature Importance Bar Chart
    fi_cols = st.columns([2, 1])
    with fi_cols[0]:
        top_n = min(15, len(feature_importance))
        fi_names = [fi[0] for fi in feature_importance[:top_n]][::-1]
        fi_values = [fi[1] for fi in feature_importance[:top_n]][::-1]
        fi_pcts = [(v / total_importance * 100) for v in fi_values] if total_importance > 0 else fi_values

        fig_fi = go.Figure()
        fig_fi.add_trace(go.Bar(
            y=fi_names,
            x=fi_pcts,
            orientation='h',
            marker=dict(
                color=fi_pcts,
                colorscale=[[0, '#667eea'], [0.5, '#764ba2'], [1, '#f093fb']],
                line=dict(width=0),
            ),
            text=[f'{v:.1f}%' for v in fi_pcts],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=10),
            hovertemplate='<b>%{y}</b><br>Importance: %{x:.2f}%<extra></extra>',
        ))

        layout_fi = get_chart_layout(f'Top {top_n} Feature Importance', height=500)
        layout_fi['xaxis']['title'] = 'Relative Importance (%)'
        layout_fi['margin']['l'] = 200
        fig_fi.update_layout(**layout_fi)

        st.plotly_chart(fig_fi, use_container_width=True)

    with fi_cols[1]:
        st.html(textwrap.dedent("""
        <div class="glass-card" style="padding: 1.2rem;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.8rem;">
                📋 Top Features Breakdown
            </div>
        """))

        for feat_name, feat_imp in feature_importance[:10]:
            feat_pct = (feat_imp / total_importance * 100) if total_importance > 0 else 0
            bar_width = min(feat_pct * 3, 100)
            st.html(textwrap.dedent(f"""
            <div style="margin-bottom: 0.6rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.2rem;">
                    <span>{feat_name}</span>
                    <span style="color: #667eea; font-weight: 600;">{feat_pct:.1f}%</span>
                </div>
                <div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; overflow: hidden;">
                    <div style="width: {bar_width}%; height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px;"></div>
                </div>
            </div>
            """))

        st.html(textwrap.dedent("</div>"))

st.html(textwrap.dedent("<br>"))


# ═══════════════════════════════════════════════════════════════════
# SECTION 4: Bedroom Insights
# ═══════════════════════════════════════════════════════════════════
st.html(textwrap.dedent("""
<div class="section-header">🛏️ Bedroom Insights</div>
<div class="section-subheader">How bedroom count affects property pricing</div>
"""))

bedroom_avg = df.groupby('bedrooms')['price_value'].mean().sort_index()

# Generate insights for consecutive bedroom jumps
bed_insight_cols = st.columns(2)
insight_idx = 0
for n in range(1, min(int(bedroom_avg.index.max()), 6)):
    if n in bedroom_avg.index and (n + 1) in bedroom_avg.index:
        price_n = bedroom_avg[n]
        price_n1 = bedroom_avg[n + 1]
        if price_n > 0:
            jump_pct = ((price_n1 - price_n) / price_n) * 100
            direction = 'increases' if jump_pct > 0 else 'decreases'
            emoji = '📈' if jump_pct > 0 else '📉'

            with bed_insight_cols[insight_idx % 2]:
                st.html(textwrap.dedent(f"""
                <div class="insight-card">
                    <div class="insight-text">
                        {emoji} Adding a bedroom from <strong>{n} BHK</strong> to
                        <strong>{n + 1} BHK</strong> {direction} the average price by
                        <strong>{abs(jump_pct):.1f}%</strong>
                        ({format_price(price_n)} → {format_price(price_n1)})
                    </div>
                </div>
                """))
            insight_idx += 1

st.html(textwrap.dedent("<br>"))

# Bedroom Price Chart
bedroom_chart_data = bedroom_avg.reset_index()
bedroom_chart_data.columns = ['Bedrooms', 'Avg_Price']

fig_bed = go.Figure()
fig_bed.add_trace(go.Bar(
    x=[f'{int(b)} BHK' for b in bedroom_chart_data['Bedrooms']],
    y=bedroom_chart_data['Avg_Price'],
    marker=dict(
        color=bedroom_chart_data['Avg_Price'],
        colorscale=[[0, '#00d2ff'], [0.5, '#667eea'], [1, '#f093fb']],
        line=dict(width=0),
        cornerradius=6,
    ),
    text=[format_price(v) for v in bedroom_chart_data['Avg_Price']],
    textposition='outside',
    textfont=dict(color='#94a3b8', size=10),
    hovertemplate='<b>%{x}</b><br>Avg Price: %{text}<extra></extra>',
))

layout_bed = get_chart_layout('Average Price by Bedroom Count', height=400)
layout_bed['yaxis']['title'] = 'Average Price (Lakhs)'
fig_bed.update_layout(**layout_bed)

st.plotly_chart(fig_bed, use_container_width=True)

st.html(textwrap.dedent("<br>"))


# ═══════════════════════════════════════════════════════════════════
# SECTION 5: Location Premium Insights
# ═══════════════════════════════════════════════════════════════════
st.html(textwrap.dedent("""
<div class="section-header">💎 Location Premium Insights</div>
<div class="section-subheader">Locations commanding the highest price premiums</div>
"""))

# Top 5 premium locations
if premium_score_map:
    sorted_premiums = sorted(premium_score_map.items(), key=lambda x: x[1], reverse=True)[:10]

    # Try to get city for each location from the data
    loc_city_map = {}
    for _, row in df.drop_duplicates(subset='location_name').iterrows():
        loc_city_map[row['location_name']] = row['city']

    # Get avg price_per_sqft for these locations
    loc_avg_pps = df.groupby('location_name')['price_per_sqft'].mean()

    premium_cols = st.columns(2)
    for i, (loc_name, score) in enumerate(sorted_premiums[:10]):
        city_name = loc_city_map.get(loc_name, 'India')
        pps = loc_avg_pps.get(loc_name, 0)
        pps_rupees = pps * 100000

        with premium_cols[i % 2]:
            rank_emoji = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'][i]
            st.html(textwrap.dedent(f"""
            <div class="insight-card">
                <div class="insight-text">
                    {rank_emoji} <strong>{loc_name}</strong> in {city_name} commands a
                    high price premium (score: <strong>{score:.2f}</strong>) at
                    <strong>₹{pps_rupees:,.0f}/sq.ft</strong> average.
                </div>
            </div>
            """))

st.html(textwrap.dedent("<br>"))


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: Model Performance
# ═══════════════════════════════════════════════════════════════════
st.html(textwrap.dedent("""
<div class="section-header">🧠 Model Performance</div>
<div class="section-subheader">Comparison of trained machine learning models</div>
"""))

# ── Model Comparison Table ──────────────────────────────────────────
if metrics_dict:
    table_html = """
    <div class="glass-card" style="overflow-x: auto;">
        <table class="model-table">
            <thead>
                <tr>
                    <th>Model</th>
                    <th>MAE (Lakhs)</th>
                    <th>RMSE (Lakhs)</th>
                    <th>R² Score</th>
                    <th>CV R² Mean</th>
                    <th>CV R² Std</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """

    for model_name, model_metrics in metrics_dict.items():
        is_best = model_name == best_model_name
        row_class = ' class="best-model"' if is_best else ''
        status = '⭐ Best' if is_best else '—'

        mae = model_metrics.get('mae', 0)
        rmse = model_metrics.get('rmse', 0)
        r2 = model_metrics.get('r2', 0)
        cv_r2_mean = model_metrics.get('cv_r2_mean', 0)
        cv_r2_std = model_metrics.get('cv_r2_std', 0)

        table_html += f"""
                <tr{row_class}>
                    <td style="font-weight: {'700' if is_best else '400'}; color: {'#667eea' if is_best else '#94a3b8'};">
                        {model_name}
                    </td>
                    <td>{mae:.2f}</td>
                    <td>{rmse:.2f}</td>
                    <td style="color: {'#4ade80' if r2 > 0.8 else '#fbbf24' if r2 > 0.6 else '#f87171'};">
                        {r2:.4f}
                    </td>
                    <td>{cv_r2_mean:.4f}</td>
                    <td>±{cv_r2_std:.4f}</td>
                    <td>{status}</td>
                </tr>
        """

    table_html += """
            </tbody>
        </table>
    </div>
    """

    st.html(textwrap.dedent(table_html))

st.html(textwrap.dedent("<br>"))

# ── Model Performance Visual ────────────────────────────────────────
if metrics_dict:
    perf_cols = st.columns(2)

    # R² comparison chart
    with perf_cols[0]:
        model_names = list(metrics_dict.keys())
        r2_scores = [metrics_dict[m].get('r2', 0) for m in model_names]

        fig_r2 = go.Figure()
        fig_r2.add_trace(go.Bar(
            x=model_names,
            y=r2_scores,
            marker=dict(
                color=r2_scores,
                colorscale=[[0, '#f5576c'], [0.5, '#fbbf24'], [1, '#4ade80']],
                line=dict(width=0),
                cornerradius=6,
            ),
            text=[f'{v:.4f}' for v in r2_scores],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=11),
            hovertemplate='<b>%{x}</b><br>R²: %{y:.4f}<extra></extra>',
        ))

        layout_r2 = get_chart_layout('R² Score Comparison', height=400)
        layout_r2['yaxis']['title'] = 'R² Score'
        layout_r2['yaxis']['range'] = [0, max(r2_scores) * 1.15] if r2_scores else [0, 1]
        fig_r2.update_layout(**layout_r2)

        st.plotly_chart(fig_r2, use_container_width=True)

    # MAE & RMSE comparison
    with perf_cols[1]:
        mae_scores = [metrics_dict[m].get('mae', 0) for m in model_names]
        rmse_scores = [metrics_dict[m].get('rmse', 0) for m in model_names]

        fig_err = go.Figure()
        fig_err.add_trace(go.Bar(
            x=model_names,
            y=mae_scores,
            name='MAE',
            marker=dict(color='rgba(0, 210, 255, 0.7)', cornerradius=4),
            text=[f'{v:.1f}' for v in mae_scores],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=10),
        ))
        fig_err.add_trace(go.Bar(
            x=model_names,
            y=rmse_scores,
            name='RMSE',
            marker=dict(color='rgba(118, 75, 162, 0.7)', cornerradius=4),
            text=[f'{v:.1f}' for v in rmse_scores],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=10),
        ))

        layout_err = get_chart_layout('Error Metrics Comparison', height=400)
        layout_err['yaxis']['title'] = 'Error (Lakhs)'
        layout_err['barmode'] = 'group'
        fig_err.update_layout(**layout_err)

        st.plotly_chart(fig_err, use_container_width=True)

st.html(textwrap.dedent("<br>"))

# ── Cross-Validation Scores ─────────────────────────────────────────
if metrics_dict:
    st.html(textwrap.dedent("""
    <div class="section-header">📊 Cross-Validation Analysis</div>
    <div class="section-subheader">Model stability and generalization scores</div>
    """))

    cv_cols = st.columns(len(metrics_dict))
    for col, (model_name, model_metrics) in zip(cv_cols, metrics_dict.items()):
        cv_mean = model_metrics.get('cv_r2_mean', 0)
        cv_std = model_metrics.get('cv_r2_std', 0)
        is_best = model_name == best_model_name

        border_color = 'rgba(102, 126, 234, 0.4)' if is_best else 'rgba(255, 255, 255, 0.08)'
        badge = '<span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 600;">BEST</span>' if is_best else ''

        with col:
            st.html(textwrap.dedent(f"""
            <div class="kpi-card" style="border-color: {border_color};">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                    {model_name} {badge}
                </div>
                <div class="kpi-value" style="font-size: 1.5rem;">{cv_mean:.4f}</div>
                <div class="kpi-label">CV R² Mean ± {cv_std:.4f}</div>
                <div style="margin-top: 0.5rem;">
                    <div style="background: rgba(255,255,255,0.05); border-radius: 4px; height: 8px; overflow: hidden;">
                        <div style="width: {cv_mean * 100}%; height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """))

st.html(textwrap.dedent("<br>"))

# ── Hyperparameters Section ─────────────────────────────────────────
hyperparams = metadata.get('hyperparameters', {})
if hyperparams:
    st.html(textwrap.dedent("""
    <div class="section-header">⚙️ Optimized Hyperparameters</div>
    <div class="section-subheader">Best parameters found during hyperparameter tuning</div>
    """))

    hp_cols = st.columns(min(len(hyperparams), 3))
    for i, (model_name, params) in enumerate(hyperparams.items()):
        with hp_cols[i % len(hp_cols)]:
            params_html = ""
            for param_name, param_val in params.items():
                params_html += f"""
                <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);">
                    <span style="color: #94a3b8; font-size: 0.8rem;">{param_name}</span>
                    <span style="color: #667eea; font-weight: 600; font-size: 0.8rem;">{param_val}</span>
                </div>
                """

            st.html(textwrap.dedent(f"""
            <div class="glass-card">
                <div style="font-weight: 600; color: #f1f5f9; margin-bottom: 0.8rem; font-size: 0.95rem;">
                    {'⭐ ' if model_name == best_model_name else ''}{model_name}
                </div>
                {params_html}
            </div>
            """))

# ── Footer ──────────────────────────────────────────────────────────
st.html(textwrap.dedent("""
<div class="app-footer">
    <span class="powered-by">AI Insights</span>
    <span style="margin: 0 0.5rem;">•</span>
    All insights are dynamically generated from the trained model and dataset
</div>
"""))
