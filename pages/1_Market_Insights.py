"""

Market Insights Page
=====================
Interactive analytics dashboard with Plotly charts showing
city-wise price trends, distributions, and market comparisons.
"""

import streamlit as st
import textwrap
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    inject_css, render_html, load_data, load_model, format_price,
    format_price_per_sqft, format_number, get_chart_layout,
    CHART_COLORS, GRADIENT_COLORS,
)

# â”€â”€ Page Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.set_page_config(
    page_title='Market Insights | India House Price Predictor',
    page_icon='ðŸ“Š',
    layout='wide',
    initial_sidebar_state='collapsed',
)

# â”€â”€ Inject Premium CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
inject_css()

# â”€â”€ Horizontal Nav Bar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
render_html("""
<nav class="top-nav">
    <div class="top-nav-inner">
        <div class="top-nav-brand">ðŸ  India House Predictor</div>
        <div class="top-nav-links">
            <a class="top-nav-link" href="/">ðŸ”® Predict</a>
            <a class="top-nav-link active" href="/Market_Insights">ðŸ“Š Market Insights</a>
            <a class="top-nav-link" href="/Data_Insights">ðŸ“ˆ Data Insights</a>
        </div>
    </div>
</nav>
<div style="height: 4rem;"></div>
""")

# â”€â”€ Load Data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    df = load_data()
    model, preprocessor, metadata = load_model()
    data_loaded = True
except Exception as e:
    st.error(f"âš ï¸ Failed to load data: {e}")
    data_loaded = False
    st.stop()

# â”€â”€ Page Header â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
render_html(textwrap.dedent("""
<div class="page-title">ðŸ“Š Market Insights</div>
<div class="page-subtitle">Comprehensive real estate analytics across Indian cities</div>
"""))

render_html("---")

# â”€â”€ Quick Stats Row â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
stats = metadata.get('dataset_stats', {})
national_avg = metadata.get('national_avg_price', 0)
national_avg_pps = metadata.get('national_avg_price_per_sqft', 0)
median_price = stats.get('median_price', 0)

quick_cols = st.columns(4)
quick_items = [
    ('ðŸ˜ï¸', format_number(len(df)), 'Properties Analyzed'),
    ('ðŸŒ†', str(df['city'].nunique()), 'Cities'),
    ('ðŸ’°', format_price(national_avg), 'National Avg Price'),
    ('ðŸ“', format_price_per_sqft(national_avg_pps), 'National Avg/Sq.Ft'),
]

for col, (icon, value, label) in zip(quick_cols, quick_items):
    with col:
        st.markdown(textwrap.dedent(f"""
        <div class="kpi-card">
            <span class="kpi-icon">{icon}</span>
            <div class="kpi-value" style="font-size: 1.4rem;">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """))

render_html(textwrap.dedent("<br>"))

# â”€â”€ Tabs for Chart Organization â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
tab1, tab2, tab3 = st.tabs(['ðŸ™ï¸ City Analysis', 'ðŸ“ Property Analysis', 'ðŸ“ˆ Distributions'])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 1: City Analysis
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab1:
    # â”€â”€ Chart 1: Average Price by City (Top 20) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    render_html(textwrap.dedent("""
    <div class="section-header">Average Price by City</div>
    <div class="section-subheader">Top 20 cities ranked by average property price</div>
    """))

    city_avg = df.groupby('city')['price_value'].mean().sort_values(ascending=False).head(20)

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=city_avg.index[::-1],
        x=city_avg.values[::-1],
        orientation='h',
        marker=dict(
            color=city_avg.values[::-1],
            colorscale='Tealgrn',
            line=dict(width=0),
        ),
        text=[format_price(v) for v in city_avg.values[::-1]],
        textposition='outside',
        textfont=dict(color='#94a3b8', size=10),
        hovertemplate='<b>%{y}</b><br>Avg Price: %{text}<extra></extra>',
    ))
    layout1 = get_chart_layout('Average Property Price by City (Top 20)', height=600)
    layout1['xaxis']['title'] = 'Average Price (Lakhs)'
    layout1['margin']['l'] = 150
    fig1.update_layout(**layout1)

    st.plotly_chart(fig1, use_container_width=True)

    render_html(textwrap.dedent("<br>"))

    # â”€â”€ Charts 2 & 3: Most Expensive & Affordable â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    exp_col, aff_col = st.columns(2)

    with exp_col:
        render_html(textwrap.dedent("""
        <div class="section-header">Top 10 Most Expensive Cities</div>
        """))

        top_expensive = df.groupby('city')['price_value'].mean().sort_values(ascending=False).head(10)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=top_expensive.index,
            y=top_expensive.values,
            marker=dict(
                color=top_expensive.values,
                colorscale=[[0, '#f5576c'], [0.5, '#764ba2'], [1, '#667eea']],
                line=dict(width=0),
            ),
            text=[format_price(v) for v in top_expensive.values],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=9),
            hovertemplate='<b>%{x}</b><br>Avg Price: %{text}<extra></extra>',
        ))
        layout2 = get_chart_layout('', height=400)
        layout2['yaxis']['title'] = 'Average Price (Lakhs)'
        layout2['xaxis']['tickangle'] = -45
        fig2.update_layout(**layout2)

        st.plotly_chart(fig2, use_container_width=True)

    with aff_col:
        render_html(textwrap.dedent("""
        <div class="section-header">Top 10 Most Affordable Cities</div>
        """))

        # Filter cities with at least 20 properties for statistical reliability
        city_counts = df['city'].value_counts()
        valid_cities = city_counts[city_counts >= 20].index
        affordable_df = df[df['city'].isin(valid_cities)]
        top_affordable = affordable_df.groupby('city')['price_value'].mean().sort_values().head(10)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=top_affordable.index,
            y=top_affordable.values,
            marker=dict(
                color=top_affordable.values,
                colorscale=[[0, '#43e97b'], [0.5, '#38f9d7'], [1, '#00d2ff']],
                line=dict(width=0),
            ),
            text=[format_price(v) for v in top_affordable.values],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=9),
            hovertemplate='<b>%{x}</b><br>Avg Price: %{text}<extra></extra>',
        ))
        layout3 = get_chart_layout('', height=400)
        layout3['yaxis']['title'] = 'Average Price (Lakhs)'
        layout3['xaxis']['tickangle'] = -45
        fig3.update_layout(**layout3)

        st.plotly_chart(fig3, use_container_width=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 2: Property Analysis
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab2:
    # â”€â”€ Chart 4: Area vs Price Scatter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    render_html(textwrap.dedent("""
    <div class="section-header">Area vs Price</div>
    <div class="section-subheader">Relationship between property size and price (sampled for performance)</div>
    """))

    # Sample for performance
    top_10_cities = df['city'].value_counts().head(10).index.tolist()
    scatter_df = df[df['city'].isin(top_10_cities)]
    if len(scatter_df) > 5000:
        scatter_df = scatter_df.sample(n=5000, random_state=42)

    fig4 = px.scatter(
        scatter_df,
        x='area_sqft',
        y='price_value',
        color='city',
        color_discrete_sequence=CHART_COLORS,
        opacity=0.6,
        trendline='ols',
        labels={
            'area_sqft': 'Area (sq.ft)',
            'price_value': 'Price (Lakhs)',
            'city': 'City',
        },
        hover_data={'area_sqft': ':,.0f', 'price_value': ':.2f'},
    )

    layout4 = get_chart_layout('Area (sq.ft) vs Price (Lakhs)', height=550)
    fig4.update_layout(**layout4)
    fig4.update_traces(marker=dict(size=5))

    st.plotly_chart(fig4, use_container_width=True)

    render_html(textwrap.dedent("<br>"))

    # â”€â”€ Chart 6: Price Per Sq.Ft Box Plot â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    render_html(textwrap.dedent("""
    <div class="section-header">Price Per Sq.Ft Analysis</div>
    <div class="section-subheader">Distribution of price per square foot across top 15 cities</div>
    """))

    top_15_cities = df['city'].value_counts().head(15).index.tolist()
    box_df = df[df['city'].isin(top_15_cities)].copy()

    # Convert price_per_sqft from lakhs to rupees for display
    box_df['price_per_sqft_rupees'] = box_df['price_per_sqft'] * 100000

    fig6 = px.box(
        box_df,
        x='city',
        y='price_per_sqft_rupees',
        color='city',
        color_discrete_sequence=CHART_COLORS,
        labels={
            'city': 'City',
            'price_per_sqft_rupees': 'Price per Sq.Ft (â‚¹)',
        },
    )

    layout6 = get_chart_layout('Price Per Sq.Ft Distribution (â‚¹)', height=500)
    layout6['xaxis']['tickangle'] = -45
    layout6['showlegend'] = False
    fig6.update_layout(**layout6)

    st.plotly_chart(fig6, use_container_width=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 3: Distributions
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab3:
    dist_col1, dist_col2 = st.columns(2)

    # â”€â”€ Chart 5: Property Distribution by City (Donut) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with dist_col1:
        render_html(textwrap.dedent("""
        <div class="section-header">Property Distribution</div>
        <div class="section-subheader">Properties by city (top 15)</div>
        """))

        city_dist = df['city'].value_counts().head(15)

        fig5 = go.Figure()
        fig5.add_trace(go.Pie(
            labels=city_dist.index,
            values=city_dist.values,
            hole=0.45,
            marker=dict(
                colors=CHART_COLORS[:len(city_dist)],
                line=dict(color='rgba(0,0,0,0.3)', width=1),
            ),
            textinfo='label+percent',
            textfont=dict(color='#e2e8f0', size=11),
            hovertemplate='<b>%{label}</b><br>Properties: %{value:,}<br>Share: %{percent}<extra></extra>',
            pull=[0.03] + [0] * (len(city_dist) - 1),
        ))

        layout5 = get_chart_layout('Property Distribution by City', height=500)
        layout5['showlegend'] = False
        fig5.update_layout(**layout5)

        st.plotly_chart(fig5, use_container_width=True)

    # â”€â”€ Chart 7: Bedroom Distribution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with dist_col2:
        render_html(textwrap.dedent("""
        <div class="section-header">Bedroom Distribution</div>
        <div class="section-subheader">Properties by bedroom count</div>
        """))

        bedroom_dist = df['bedrooms'].value_counts().sort_index()

        fig7 = go.Figure()
        fig7.add_trace(go.Bar(
            x=[f'{int(b)} BHK' for b in bedroom_dist.index],
            y=bedroom_dist.values,
            marker=dict(
                color=bedroom_dist.values,
                colorscale=[[0, '#667eea'], [0.5, '#764ba2'], [1, '#f093fb']],
                line=dict(width=0),
                cornerradius=6,
            ),
            text=[format_number(v) for v in bedroom_dist.values],
            textposition='outside',
            textfont=dict(color='#94a3b8', size=10),
            hovertemplate='<b>%{x}</b><br>Count: %{text}<extra></extra>',
        ))

        layout7 = get_chart_layout('Properties by Bedroom Count', height=500)
        layout7['yaxis']['title'] = 'Number of Properties'
        fig7.update_layout(**layout7)

        st.plotly_chart(fig7, use_container_width=True)

    render_html(textwrap.dedent("<br>"))

    # â”€â”€ Additional: Price Histogram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    render_html(textwrap.dedent("""
    <div class="section-header">Price Distribution</div>
    <div class="section-subheader">Overall distribution of property prices across India</div>
    """))

    # Cap at 99th percentile for better visualization
    price_cap = df['price_value'].quantile(0.99)
    hist_df = df[df['price_value'] <= price_cap]

    fig8 = go.Figure()
    fig8.add_trace(go.Histogram(
        x=hist_df['price_value'],
        nbinsx=60,
        marker=dict(
            color='rgba(102, 126, 234, 0.6)',
            line=dict(color='rgba(102, 126, 234, 0.8)', width=1),
        ),
        hovertemplate='Price: â‚¹%{x:.1f} Lakhs<br>Count: %{y}<extra></extra>',
    ))

    # Add median line
    median_val = df['price_value'].median()
    fig8.add_vline(
        x=median_val,
        line_dash='dash',
        line_color='#f093fb',
        annotation_text=f'Median: {format_price(median_val)}',
        annotation_font=dict(color='#f093fb', size=12),
        annotation_position='top',
    )

    # Add mean line
    mean_val = df['price_value'].mean()
    fig8.add_vline(
        x=mean_val,
        line_dash='dash',
        line_color='#00d2ff',
        annotation_text=f'Mean: {format_price(mean_val)}',
        annotation_font=dict(color='#00d2ff', size=12),
        annotation_position='top left',
    )

    layout8 = get_chart_layout('Property Price Distribution (capped at 99th percentile)', height=450)
    layout8['xaxis']['title'] = 'Price (Lakhs)'
    layout8['yaxis']['title'] = 'Number of Properties'
    fig8.update_layout(**layout8)

    st.plotly_chart(fig8, use_container_width=True)

    render_html(textwrap.dedent("<br>"))

    # â”€â”€ Area Distribution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    render_html(textwrap.dedent("""
    <div class="section-header">Area Size Distribution</div>
    <div class="section-subheader">Breakdown of properties by size category</div>
    """))

    area_cats = df['area_category'].value_counts()
    cat_order = ['Small', 'Medium', 'Large', 'Luxury']
    area_cats = area_cats.reindex([c for c in cat_order if c in area_cats.index])

    cat_colors = {'Small': '#43e97b', 'Medium': '#00d2ff', 'Large': '#667eea', 'Luxury': '#f093fb'}

    fig9 = go.Figure()
    fig9.add_trace(go.Bar(
        x=area_cats.index,
        y=area_cats.values,
        marker=dict(
            color=[cat_colors.get(c, '#667eea') for c in area_cats.index],
            line=dict(width=0),
            cornerradius=8,
        ),
        text=[format_number(v) for v in area_cats.values],
        textposition='outside',
        textfont=dict(color='#94a3b8', size=11),
        hovertemplate='<b>%{x}</b><br>Count: %{text}<extra></extra>',
    ))

    layout9 = get_chart_layout('Properties by Area Category', height=400)
    layout9['yaxis']['title'] = 'Number of Properties'
    fig9.update_layout(**layout9)

    st.plotly_chart(fig9, use_container_width=True)
