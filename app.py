"""
AdSellix Premium AI Audit Tool
Version 1.0

A comprehensive Amazon brand audit system powered by AI.
Analyzes SQP, PPC, Business Reports, and Inventory data
to provide actionable insights and strategic recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import io
import os

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="AdSellix Premium AI Audit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Score cards */
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .score-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .score-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .score-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .score-value {
        font-size: 3rem;
        font-weight: 700;
    }
    .score-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    /* Status badges */
    .badge-green { 
        background: #d4edda; 
        color: #155724; 
        padding: 0.25rem 0.75rem; 
        border-radius: 20px; 
        font-size: 0.85rem;
    }
    .badge-yellow { 
        background: #fff3cd; 
        color: #856404; 
        padding: 0.25rem 0.75rem; 
        border-radius: 20px; 
        font-size: 0.85rem;
    }
    .badge-red { 
        background: #f8d7da; 
        color: #721c24; 
        padding: 0.25rem 0.75rem; 
        border-radius: 20px; 
        font-size: 0.85rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A5F;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Insight boxes */
    .insight-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .insight-box.positive { border-left-color: #28a745; }
    .insight-box.negative { border-left-color: #dc3545; }
    .insight-box.warning { border-left-color: #ffc107; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'audit_data' not in st.session_state:
    st.session_state.audit_data = {
        'sqp_brand': None,
        'sqp_asin': None,
        'ppc_bulk': None,
        'business_report': None,
        'inventory': None,
        'cogs': None,
        'brand_name': None,
        'audit_complete': False
    }

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_currency(value):
    """Convert currency strings to float."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace('$', '').replace(',', '').replace('%', ''))

def format_currency(value):
    """Format number as currency."""
    if value >= 1000000:
        return f"${value/1000000:.1f}M"
    elif value >= 1000:
        return f"${value/1000:.1f}K"
    else:
        return f"${value:.2f}"

def format_percent(value):
    """Format number as percentage."""
    return f"{value:.1f}%"

def get_trend_icon(current, previous):
    """Get trend icon based on comparison."""
    if previous == 0:
        return "→"
    change = (current - previous) / previous * 100
    if change > 5:
        return "↑"
    elif change < -5:
        return "↓"
    else:
        return "→"

def get_health_color(score):
    """Get color based on health score."""
    if score >= 80:
        return "#28a745"
    elif score >= 60:
        return "#17a2b8"
    elif score >= 40:
        return "#ffc107"
    else:
        return "#dc3545"

def get_health_label(score):
    """Get label based on health score."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Average"
    elif score >= 20:
        return "Below Average"
    else:
        return "Critical"

# =============================================================================
# DATA PROCESSING FUNCTIONS
# =============================================================================

def process_sqp_data(df):
    """Process SQP (Search Query Performance) data."""
    processed = df.copy()
    
    # Standardize column names
    column_mapping = {
        'Search Query': 'query',
        'Search Query Score': 'query_score',
        'Search Query Volume': 'search_volume',
        'Impressions: Total Count': 'total_impressions',
        'Impressions: Brand Count': 'brand_impressions',
        'Impressions: Brand Share': 'impression_share',
        'Clicks: Total Count': 'total_clicks',
        'Clicks: Brand Count': 'brand_clicks',
        'Clicks: Brand Share': 'click_share',
        'Cart Adds: Total Count': 'total_cart_adds',
        'Cart Adds: Brand Count': 'brand_cart_adds',
        'Cart Adds: Brand Share': 'cart_add_share',
        'Purchases: Total Count': 'total_purchases',
        'Purchases: Brand Count': 'brand_purchases',
        'Purchases: Brand Share': 'purchase_share'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in processed.columns:
            processed = processed.rename(columns={old_col: new_col})
    
    # Convert share columns to percentages
    share_cols = ['impression_share', 'click_share', 'cart_add_share', 'purchase_share']
    for col in share_cols:
        if col in processed.columns:
            processed[col] = processed[col].apply(lambda x: parse_currency(x) if pd.notna(x) else 0)
    
    # Calculate derived metrics
    if 'click_share' in processed.columns and 'impression_share' in processed.columns:
        processed['ctr_index'] = processed.apply(
            lambda row: row['click_share'] / row['impression_share'] if row['impression_share'] > 0 else 0, 
            axis=1
        )
    
    if 'purchase_share' in processed.columns and 'click_share' in processed.columns:
        processed['cvr_index'] = processed.apply(
            lambda row: row['purchase_share'] / row['click_share'] if row['click_share'] > 0 else 0, 
            axis=1
        )
    
    return processed

def process_ppc_data(df):
    """Process PPC Bulk Sheet data."""
    processed = df.copy()
    
    # Identify numeric columns
    numeric_cols = ['Impressions', 'Clicks', 'Spend', 'Sales', 'Orders', 'Units']
    
    for col in numeric_cols:
        matching_cols = [c for c in processed.columns if col.lower() in c.lower()]
        for mc in matching_cols:
            processed[mc] = processed[mc].apply(parse_currency)
    
    # Calculate key metrics
    if 'Spend' in processed.columns and 'Sales' in processed.columns:
        processed['ACoS'] = processed.apply(
            lambda row: (row['Spend'] / row['Sales'] * 100) if row['Sales'] > 0 else 0, 
            axis=1
        )
        processed['ROAS'] = processed.apply(
            lambda row: (row['Sales'] / row['Spend']) if row['Spend'] > 0 else 0, 
            axis=1
        )
    
    if 'Clicks' in processed.columns and 'Impressions' in processed.columns:
        processed['CTR'] = processed.apply(
            lambda row: (row['Clicks'] / row['Impressions'] * 100) if row['Impressions'] > 0 else 0, 
            axis=1
        )
    
    if 'Spend' in processed.columns and 'Clicks' in processed.columns:
        processed['CPC'] = processed.apply(
            lambda row: (row['Spend'] / row['Clicks']) if row['Clicks'] > 0 else 0, 
            axis=1
        )
    
    return processed

def process_business_report(df):
    """Process Business Report data."""
    processed = df.copy()
    
    # Standardize column names
    column_mapping = {
        '(Parent) ASIN': 'parent_asin',
        '(Child) ASIN': 'asin',
        'Title': 'title',
        'Sessions': 'sessions',
        'Session Percentage': 'session_pct',
        'Page Views': 'page_views',
        'Page Views Percentage': 'page_views_pct',
        'Buy Box Percentage': 'buy_box_pct',
        'Units Ordered': 'units',
        'Unit Session Percentage': 'conversion_rate',
        'Ordered Product Sales': 'revenue',
        'Total Order Items': 'orders'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in processed.columns:
            processed = processed.rename(columns={old_col: new_col})
    
    # Convert numeric columns
    for col in ['sessions', 'page_views', 'units', 'orders']:
        if col in processed.columns:
            processed[col] = processed[col].apply(parse_currency)
    
    for col in ['revenue']:
        if col in processed.columns:
            processed[col] = processed[col].apply(parse_currency)
    
    for col in ['session_pct', 'page_views_pct', 'buy_box_pct', 'conversion_rate']:
        if col in processed.columns:
            processed[col] = processed[col].apply(lambda x: parse_currency(x))
    
    return processed

def process_inventory_data(df):
    """Process FBA Inventory data."""
    processed = df.copy()
    
    # Key columns we're looking for
    inventory_cols = {
        'sku': ['sku', 'seller-sku', 'seller sku'],
        'asin': ['asin'],
        'fnsku': ['fnsku'],
        'product_name': ['product-name', 'product name', 'title'],
        'available': ['afn-fulfillable-quantity', 'available', 'fulfillable'],
        'inbound': ['afn-inbound-working-quantity', 'inbound'],
        'reserved': ['afn-reserved-quantity', 'reserved'],
        'total_units': ['afn-total-quantity', 'total'],
        'days_of_supply': ['days-of-supply', 'days of supply'],
        'inv_age_0_90': ['inv-age-0-to-90-days', '0-90 days'],
        'inv_age_91_180': ['inv-age-91-to-180-days', '91-180 days'],
        'inv_age_181_270': ['inv-age-181-to-270-days', '181-270 days'],
        'inv_age_271_365': ['inv-age-271-to-365-days', '271-365 days'],
        'inv_age_365plus': ['inv-age-365-plus-days', '365+ days'],
        'estimated_storage_fee': ['estimated-storage-cost', 'storage fee'],
        'estimated_aged_surcharge': ['estimated-aged-inventory-surcharge', 'aged surcharge']
    }
    
    # Map columns
    for new_col, possible_names in inventory_cols.items():
        for possible_name in possible_names:
            matching = [c for c in processed.columns if possible_name.lower() in c.lower()]
            if matching:
                processed = processed.rename(columns={matching[0]: new_col})
                break
    
    # Calculate inventory health metrics
    if 'days_of_supply' in processed.columns:
        processed['stock_status'] = processed['days_of_supply'].apply(
            lambda x: 'Low' if x < 30 else ('Healthy' if x <= 90 else ('Excess' if x <= 180 else 'Aged'))
        )
    
    return processed

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_brand_health_score(data):
    """Calculate overall brand health score (0-100)."""
    scores = {}
    weights = {
        'market_position': 0.20,
        'financial_health': 0.25,
        'portfolio_health': 0.15,
        'advertising_efficiency': 0.15,
        'listing_quality': 0.10,
        'inventory_health': 0.10,
        'operational': 0.05
    }
    
    # Market Position Score (from SQP)
    if data.get('sqp_brand') is not None:
        sqp = data['sqp_brand']
        if 'purchase_share' in sqp.columns:
            avg_purchase_share = sqp['purchase_share'].mean()
            scores['market_position'] = min(100, avg_purchase_share * 5)  # Scale to 100
        else:
            scores['market_position'] = 50
    else:
        scores['market_position'] = 50
    
    # Financial Health Score (from Business Report)
    if data.get('business_report') is not None:
        br = data['business_report']
        if 'conversion_rate' in br.columns:
            avg_cvr = br['conversion_rate'].mean()
            scores['financial_health'] = min(100, avg_cvr * 5)  # Scale to 100
        else:
            scores['financial_health'] = 50
    else:
        scores['financial_health'] = 50
    
    # Advertising Efficiency Score (from PPC)
    if data.get('ppc_bulk') is not None:
        ppc = data['ppc_bulk']
        if 'ACoS' in ppc.columns:
            avg_acos = ppc[ppc['ACoS'] > 0]['ACoS'].mean()
            if avg_acos > 0:
                scores['advertising_efficiency'] = max(0, min(100, 100 - (avg_acos - 20) * 2))
            else:
                scores['advertising_efficiency'] = 50
        else:
            scores['advertising_efficiency'] = 50
    else:
        scores['advertising_efficiency'] = 50
    
    # Inventory Health Score
    if data.get('inventory') is not None:
        inv = data['inventory']
        if 'stock_status' in inv.columns:
            healthy_pct = (inv['stock_status'] == 'Healthy').sum() / len(inv) * 100
            scores['inventory_health'] = healthy_pct
        else:
            scores['inventory_health'] = 50
    else:
        scores['inventory_health'] = 50
    
    # Default scores for missing data
    scores['portfolio_health'] = scores.get('portfolio_health', 60)
    scores['listing_quality'] = scores.get('listing_quality', 60)
    scores['operational'] = scores.get('operational', 60)
    
    # Calculate weighted average
    total_score = sum(scores[key] * weights[key] for key in weights.keys())
    
    return {
        'total': round(total_score, 1),
        'components': scores
    }

def analyze_sqp(df):
    """Analyze SQP data and generate insights."""
    insights = []
    
    if df is None or df.empty:
        return {'insights': [], 'top_queries': [], 'opportunities': []}
    
    # Top performing queries
    if 'purchase_share' in df.columns:
        top_queries = df.nlargest(10, 'purchase_share')[['query', 'search_volume', 'impression_share', 'click_share', 'purchase_share']].to_dict('records')
    else:
        top_queries = []
    
    # Identify opportunities (high click share, low purchase share = listing issue)
    opportunities = []
    if 'click_share' in df.columns and 'purchase_share' in df.columns:
        df['conversion_gap'] = df['click_share'] - df['purchase_share']
        conversion_issues = df[df['conversion_gap'] > 2].nlargest(5, 'conversion_gap')
        for _, row in conversion_issues.iterrows():
            opportunities.append({
                'query': row.get('query', 'Unknown'),
                'type': 'Conversion Issue',
                'detail': f"Click share ({row['click_share']:.1f}%) > Purchase share ({row['purchase_share']:.1f}%)",
                'action': 'Review listing content, price, or reviews'
            })
    
    # Identify visibility opportunities (low impression share on high volume queries)
    if 'search_volume' in df.columns and 'impression_share' in df.columns:
        high_volume_low_share = df[(df['search_volume'] > df['search_volume'].median()) & (df['impression_share'] < 5)]
        for _, row in high_volume_low_share.head(5).iterrows():
            opportunities.append({
                'query': row.get('query', 'Unknown'),
                'type': 'Visibility Opportunity',
                'detail': f"High volume query with only {row['impression_share']:.1f}% impression share",
                'action': 'Increase PPC bids or improve organic ranking'
            })
    
    return {
        'insights': insights,
        'top_queries': top_queries,
        'opportunities': opportunities,
        'summary': {
            'total_queries': len(df),
            'avg_impression_share': df['impression_share'].mean() if 'impression_share' in df.columns else 0,
            'avg_click_share': df['click_share'].mean() if 'click_share' in df.columns else 0,
            'avg_purchase_share': df['purchase_share'].mean() if 'purchase_share' in df.columns else 0
        }
    }

def analyze_ppc(df):
    """Analyze PPC data and generate insights."""
    if df is None or df.empty:
        return {'insights': [], 'summary': {}, 'waste': {}}
    
    insights = []
    
    # Calculate summary metrics
    total_spend = df['Spend'].sum() if 'Spend' in df.columns else 0
    total_sales = df['Sales'].sum() if 'Sales' in df.columns else 0
    overall_acos = (total_spend / total_sales * 100) if total_sales > 0 else 0
    overall_roas = (total_sales / total_spend) if total_spend > 0 else 0
    
    # Waste analysis
    if 'ACoS' in df.columns and 'Spend' in df.columns:
        # Assuming 30% is target ACoS
        target_acos = 30
        wasteful = df[df['ACoS'] > target_acos]
        waste_spend = wasteful['Spend'].sum()
        waste_pct = (waste_spend / total_spend * 100) if total_spend > 0 else 0
        
        # Profitable spend
        profitable = df[df['ACoS'] <= target_acos]
        profitable_spend = profitable['Spend'].sum()
        profitable_pct = (profitable_spend / total_spend * 100) if total_spend > 0 else 0
    else:
        waste_spend = 0
        waste_pct = 0
        profitable_spend = 0
        profitable_pct = 0
    
    # Generate insights
    if overall_acos > 35:
        insights.append({
            'type': 'warning',
            'title': 'High Overall ACoS',
            'detail': f'Your ACoS of {overall_acos:.1f}% is above the healthy range. Consider restructuring campaigns.'
        })
    
    if waste_pct > 30:
        insights.append({
            'type': 'negative',
            'title': 'Significant Ad Waste',
            'detail': f'{waste_pct:.1f}% of spend ({format_currency(waste_spend)}) is going to unprofitable keywords.'
        })
    
    return {
        'insights': insights,
        'summary': {
            'total_spend': total_spend,
            'total_sales': total_sales,
            'overall_acos': overall_acos,
            'overall_roas': overall_roas,
            'total_impressions': df['Impressions'].sum() if 'Impressions' in df.columns else 0,
            'total_clicks': df['Clicks'].sum() if 'Clicks' in df.columns else 0
        },
        'waste': {
            'waste_spend': waste_spend,
            'waste_pct': waste_pct,
            'profitable_spend': profitable_spend,
            'profitable_pct': profitable_pct
        }
    }

def analyze_inventory(df):
    """Analyze inventory data and generate insights."""
    if df is None or df.empty:
        return {'insights': [], 'summary': {}, 'at_risk': []}
    
    insights = []
    
    # Summary metrics
    total_units = df['available'].sum() if 'available' in df.columns else 0
    
    # Stock status distribution
    status_dist = {}
    if 'stock_status' in df.columns:
        status_dist = df['stock_status'].value_counts().to_dict()
    
    # Fee exposure
    storage_fees = df['estimated_storage_fee'].sum() if 'estimated_storage_fee' in df.columns else 0
    aged_surcharge = df['estimated_aged_surcharge'].sum() if 'estimated_aged_surcharge' in df.columns else 0
    
    # At-risk inventory (aged)
    at_risk = []
    if 'inv_age_181_270' in df.columns:
        aged = df[df.get('inv_age_181_270', pd.Series([0]*len(df))) > 0]
        for _, row in aged.head(5).iterrows():
            at_risk.append({
                'sku': row.get('sku', 'Unknown'),
                'asin': row.get('asin', 'Unknown'),
                'aged_units': row.get('inv_age_181_270', 0),
                'action': 'Consider liquidation or promotion'
            })
    
    # Generate insights
    if aged_surcharge > 100:
        insights.append({
            'type': 'negative',
            'title': 'Aged Inventory Surcharge Alert',
            'detail': f'You are paying ${aged_surcharge:.2f}/month in aged inventory fees. Consider liquidation.'
        })
    
    excess_pct = status_dist.get('Excess', 0) / len(df) * 100 if len(df) > 0 else 0
    if excess_pct > 20:
        insights.append({
            'type': 'warning',
            'title': 'High Excess Inventory',
            'detail': f'{excess_pct:.1f}% of SKUs have excess inventory. Review restock strategy.'
        })
    
    return {
        'insights': insights,
        'summary': {
            'total_units': total_units,
            'status_distribution': status_dist,
            'storage_fees': storage_fees,
            'aged_surcharge': aged_surcharge
        },
        'at_risk': at_risk
    }

def generate_keep_kill_matrix(business_report, inventory, cogs=None):
    """Generate Keep/Kill matrix for ASINs."""
    if business_report is None or business_report.empty:
        return []
    
    matrix = []
    
    for _, row in business_report.iterrows():
        asin = row.get('asin', row.get('parent_asin', 'Unknown'))
        
        # Calculate score components
        revenue = row.get('revenue', 0)
        cvr = row.get('conversion_rate', 0)
        sessions = row.get('sessions', 0)
        
        # Score calculation (simplified)
        revenue_score = min(5, revenue / 10000 + 1) if revenue > 0 else 1
        cvr_score = min(5, cvr / 4 + 1) if cvr > 0 else 1
        traffic_score = min(5, sessions / 500 + 1) if sessions > 0 else 1
        
        total_score = (revenue_score * 0.4 + cvr_score * 0.35 + traffic_score * 0.25)
        
        # Recommendation
        if total_score >= 4:
            recommendation = 'INVEST'
            color = '#28a745'
        elif total_score >= 3:
            recommendation = 'MAINTAIN'
            color = '#17a2b8'
        elif total_score >= 2:
            recommendation = 'OPTIMIZE'
            color = '#ffc107'
        else:
            recommendation = 'EXIT'
            color = '#dc3545'
        
        matrix.append({
            'asin': asin,
            'title': row.get('title', 'Unknown')[:50] + '...' if len(str(row.get('title', ''))) > 50 else row.get('title', 'Unknown'),
            'revenue': revenue,
            'cvr': cvr,
            'sessions': sessions,
            'score': round(total_score, 2),
            'recommendation': recommendation,
            'color': color
        })
    
    return sorted(matrix, key=lambda x: x['score'], reverse=True)

# =============================================================================
# AI INTEGRATION (Claude API)
# =============================================================================

def call_claude_api(prompt, system_prompt=None):
    """Call Claude API for AI-powered insights."""
    api_key = os.environ.get('ANTHROPIC_API_KEY', st.secrets.get('ANTHROPIC_API_KEY', None))
    
    if not api_key:
        return "AI insights require API key configuration."
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt or "You are an expert Amazon business analyst providing actionable insights.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

def generate_ai_executive_summary(data, health_score):
    """Generate AI-powered executive summary."""
    # Prepare context
    context = f"""
Brand Health Score: {health_score['total']}/100

Key Metrics:
"""
    
    if data.get('ppc_bulk') is not None:
        ppc_analysis = analyze_ppc(data['ppc_bulk'])
        context += f"""
- Total Ad Spend: {format_currency(ppc_analysis['summary']['total_spend'])}
- Total Ad Sales: {format_currency(ppc_analysis['summary']['total_sales'])}
- Overall ACoS: {ppc_analysis['summary']['overall_acos']:.1f}%
- Ad Waste: {ppc_analysis['waste']['waste_pct']:.1f}%
"""
    
    if data.get('sqp_brand') is not None:
        sqp_analysis = analyze_sqp(data['sqp_brand'])
        context += f"""
- Avg Impression Share: {sqp_analysis['summary']['avg_impression_share']:.1f}%
- Avg Click Share: {sqp_analysis['summary']['avg_click_share']:.1f}%
- Avg Purchase Share: {sqp_analysis['summary']['avg_purchase_share']:.1f}%
"""
    
    prompt = f"""Based on this Amazon brand audit data, write a brief executive summary (3-4 paragraphs) covering:
1. Overall brand health assessment
2. Top 3 strengths
3. Top 3 areas needing improvement
4. Key recommended actions

Data:
{context}

Write in a professional but accessible tone. Be specific with numbers where available."""
    
    return call_claude_api(prompt)

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_score_card(title, value, subtitle="", card_class=""):
    """Render a styled score card."""
    st.markdown(f"""
    <div class="score-card {card_class}">
        <div class="score-label">{title}</div>
        <div class="score-value">{value}</div>
        <div class="score-label">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def render_insight_box(insight):
    """Render an insight box."""
    icon = "✅" if insight['type'] == 'positive' else ("⚠️" if insight['type'] == 'warning' else "❌")
    st.markdown(f"""
    <div class="insight-box {insight['type']}">
        <strong>{icon} {insight['title']}</strong><br>
        {insight['detail']}
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 AdSellix Premium AI Audit</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Comprehensive Amazon brand analysis powered by AI</p>', unsafe_allow_html=True)
    
    # Sidebar - Data Upload
    with st.sidebar:
        st.markdown("### 📁 Data Upload")
        st.markdown("Upload your Amazon reports to begin the audit.")
        
        brand_name = st.text_input("Brand Name", placeholder="Enter your brand name")
        if brand_name:
            st.session_state.audit_data['brand_name'] = brand_name
        
        st.markdown("---")
        st.markdown("**Required Reports:**")
        
        # SQP Brand View
        sqp_file = st.file_uploader("SQP Brand View (CSV)", type=['csv'], key='sqp')
        if sqp_file:
            df = pd.read_csv(sqp_file)
            st.session_state.audit_data['sqp_brand'] = process_sqp_data(df)
            st.success(f"✓ SQP: {len(df)} queries loaded")
        
        # PPC Bulk Sheet
        ppc_file = st.file_uploader("PPC Bulk Sheet (CSV/Excel)", type=['csv', 'xlsx'], key='ppc')
        if ppc_file:
            if ppc_file.name.endswith('.csv'):
                df = pd.read_csv(ppc_file)
            else:
                df = pd.read_excel(ppc_file)
            st.session_state.audit_data['ppc_bulk'] = process_ppc_data(df)
            st.success(f"✓ PPC: {len(df)} rows loaded")
        
        # Business Report
        br_file = st.file_uploader("Business Report (CSV)", type=['csv'], key='br')
        if br_file:
            df = pd.read_csv(br_file)
            st.session_state.audit_data['business_report'] = process_business_report(df)
            st.success(f"✓ Business Report: {len(df)} ASINs loaded")
        
        # Inventory Report
        inv_file = st.file_uploader("FBA Inventory (CSV)", type=['csv'], key='inv')
        if inv_file:
            df = pd.read_csv(inv_file)
            st.session_state.audit_data['inventory'] = process_inventory_data(df)
            st.success(f"✓ Inventory: {len(df)} SKUs loaded")
        
        st.markdown("---")
        
        # Run Analysis Button
        if st.button("🚀 Run Full Audit", type="primary", use_container_width=True):
            with st.spinner("Analyzing your data..."):
                # Calculate health score
                health_score = calculate_brand_health_score(st.session_state.audit_data)
                st.session_state.analysis_results['health_score'] = health_score
                
                # Run individual analyses
                if st.session_state.audit_data['sqp_brand'] is not None:
                    st.session_state.analysis_results['sqp'] = analyze_sqp(st.session_state.audit_data['sqp_brand'])
                
                if st.session_state.audit_data['ppc_bulk'] is not None:
                    st.session_state.analysis_results['ppc'] = analyze_ppc(st.session_state.audit_data['ppc_bulk'])
                
                if st.session_state.audit_data['inventory'] is not None:
                    st.session_state.analysis_results['inventory'] = analyze_inventory(st.session_state.audit_data['inventory'])
                
                if st.session_state.audit_data['business_report'] is not None:
                    st.session_state.analysis_results['keep_kill'] = generate_keep_kill_matrix(
                        st.session_state.audit_data['business_report'],
                        st.session_state.audit_data['inventory']
                    )
                
                st.session_state.audit_data['audit_complete'] = True
            
            st.success("✅ Audit complete!")
            st.rerun()
    
    # Main Content Area
    if not st.session_state.audit_data['audit_complete']:
        # Welcome screen
        st.markdown("""
        ### Welcome to the Premium AI Audit
        
        Upload your Amazon data files using the sidebar to begin your comprehensive brand analysis.
        
        **This audit will analyze:**
        - 🎯 Market Position (from SQP data)
        - 💰 Advertising Efficiency (from PPC data)
        - 📈 Product Performance (from Business Reports)
        - 📦 Inventory Health (from FBA data)
        
        **You'll receive:**
        - Brand Health Score (0-100)
        - Keep/Kill Matrix for every ASIN
        - AI-powered insights and recommendations
        - 90-day action plan
        """)
        
        # Sample data option
        if st.button("📊 Load Sample Data (Demo)"):
            st.info("Sample data loading is coming soon!")
    
    else:
        # Display Audit Results
        results = st.session_state.analysis_results
        
        # Tabs for different sections
        tabs = st.tabs(["📋 Executive Summary", "🎯 Market Position", "💰 PPC Analysis", "📦 Inventory", "⚖️ Keep/Kill Matrix", "📊 Full Report"])
        
        # TAB 1: Executive Summary
        with tabs[0]:
            health_score = results.get('health_score', {'total': 0, 'components': {}})
            
            # Score cards row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                color = get_health_color(health_score['total'])
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color} 0%, {color}88 100%); 
                            border-radius: 15px; padding: 1.5rem; text-align: center; color: white;">
                    <div style="font-size: 0.9rem; opacity: 0.9;">Brand Health Score</div>
                    <div style="font-size: 3rem; font-weight: 700;">{health_score['total']}</div>
                    <div style="font-size: 0.9rem;">{get_health_label(health_score['total'])}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                ppc = results.get('ppc', {}).get('summary', {})
                st.metric(
                    "Total Ad Spend",
                    format_currency(ppc.get('total_spend', 0)),
                    f"ACoS: {ppc.get('overall_acos', 0):.1f}%"
                )
            
            with col3:
                st.metric(
                    "Total Ad Sales",
                    format_currency(ppc.get('total_sales', 0)),
                    f"ROAS: {ppc.get('overall_roas', 0):.2f}x"
                )
            
            with col4:
                sqp = results.get('sqp', {}).get('summary', {})
                st.metric(
                    "Avg Purchase Share",
                    f"{sqp.get('avg_purchase_share', 0):.1f}%",
                    "Market Position"
                )
            
            st.markdown("---")
            
            # Component scores
            st.markdown("### Health Score Breakdown")
            components = health_score.get('components', {})
            
            fig = go.Figure(go.Bar(
                x=list(components.values()),
                y=[k.replace('_', ' ').title() for k in components.keys()],
                orientation='h',
                marker_color=[get_health_color(v) for v in components.values()]
            ))
            fig.update_layout(
                xaxis_title="Score (0-100)",
                yaxis_title="",
                height=300,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Key Insights
            st.markdown("### 🔍 Key Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Opportunities**")
                for opp in results.get('sqp', {}).get('opportunities', [])[:3]:
                    st.markdown(f"""
                    <div class="insight-box positive">
                        <strong>🎯 {opp['type']}</strong>: {opp['query']}<br>
                        <small>{opp['detail']}</small><br>
                        <em>Action: {opp['action']}</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Risks**")
                for insight in results.get('ppc', {}).get('insights', [])[:3]:
                    render_insight_box(insight)
                for insight in results.get('inventory', {}).get('insights', [])[:3]:
                    render_insight_box(insight)
        
        # TAB 2: Market Position
        with tabs[1]:
            st.markdown("### 🎯 Market Position Analysis")
            
            sqp_data = st.session_state.audit_data.get('sqp_brand')
            if sqp_data is not None and not sqp_data.empty:
                # Top queries table
                st.markdown("#### Top Performing Queries")
                
                if 'purchase_share' in sqp_data.columns:
                    top_queries = sqp_data.nlargest(20, 'purchase_share')
                    
                    # Visualization
                    fig = px.bar(
                        top_queries.head(10),
                        x='query',
                        y=['impression_share', 'click_share', 'purchase_share'],
                        title="Share of Voice: Top 10 Queries",
                        barmode='group'
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Data table
                    display_cols = ['query', 'search_volume', 'impression_share', 'click_share', 'purchase_share']
                    display_cols = [c for c in display_cols if c in top_queries.columns]
                    st.dataframe(
                        top_queries[display_cols].style.format({
                            'impression_share': '{:.2f}%',
                            'click_share': '{:.2f}%',
                            'purchase_share': '{:.2f}%'
                        }),
                        use_container_width=True
                    )
            else:
                st.info("Upload SQP data to see market position analysis.")
        
        # TAB 3: PPC Analysis
        with tabs[2]:
            st.markdown("### 💰 PPC Performance Analysis")
            
            ppc_data = st.session_state.audit_data.get('ppc_bulk')
            ppc_results = results.get('ppc', {})
            
            if ppc_data is not None and not ppc_data.empty:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                summary = ppc_results.get('summary', {})
                waste = ppc_results.get('waste', {})
                
                with col1:
                    st.metric("Total Spend", format_currency(summary.get('total_spend', 0)))
                with col2:
                    st.metric("Total Sales", format_currency(summary.get('total_sales', 0)))
                with col3:
                    st.metric("Overall ACoS", f"{summary.get('overall_acos', 0):.1f}%")
                with col4:
                    st.metric("ROAS", f"{summary.get('overall_roas', 0):.2f}x")
                
                st.markdown("---")
                
                # Waste analysis
                st.markdown("#### 💸 Spend Efficiency Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart
                    fig = go.Figure(data=[go.Pie(
                        labels=['Profitable', 'Wasteful'],
                        values=[waste.get('profitable_spend', 0), waste.get('waste_spend', 0)],
                        hole=.4,
                        marker_colors=['#28a745', '#dc3545']
                    )])
                    fig.update_layout(title="Spend Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                    **Profitable Spend:** {format_currency(waste.get('profitable_spend', 0))} ({waste.get('profitable_pct', 0):.1f}%)
                    
                    **Wasteful Spend:** {format_currency(waste.get('waste_spend', 0))} ({waste.get('waste_pct', 0):.1f}%)
                    
                    **Potential Savings:** {format_currency(waste.get('waste_spend', 0) * 0.5)}
                    
                    *By optimizing underperforming keywords, you could redirect up to 50% of wasteful spend.*
                    """)
                
                # Campaign performance table
                st.markdown("#### Campaign Performance")
                if 'Campaign Name' in ppc_data.columns:
                    campaign_summary = ppc_data.groupby('Campaign Name').agg({
                        'Spend': 'sum',
                        'Sales': 'sum',
                        'Impressions': 'sum',
                        'Clicks': 'sum'
                    }).reset_index()
                    campaign_summary['ACoS'] = campaign_summary['Spend'] / campaign_summary['Sales'] * 100
                    campaign_summary = campaign_summary.replace([np.inf, -np.inf], 0)
                    
                    st.dataframe(
                        campaign_summary.sort_values('Spend', ascending=False).head(20),
                        use_container_width=True
                    )
            else:
                st.info("Upload PPC bulk sheet to see advertising analysis.")
        
        # TAB 4: Inventory
        with tabs[3]:
            st.markdown("### 📦 Inventory Health Analysis")
            
            inv_data = st.session_state.audit_data.get('inventory')
            inv_results = results.get('inventory', {})
            
            if inv_data is not None and not inv_data.empty:
                summary = inv_results.get('summary', {})
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Units", f"{summary.get('total_units', 0):,.0f}")
                with col2:
                    st.metric("Storage Fees", format_currency(summary.get('storage_fees', 0)) + "/mo")
                with col3:
                    st.metric("Aged Surcharge", format_currency(summary.get('aged_surcharge', 0)) + "/mo")
                
                st.markdown("---")
                
                # Stock status distribution
                status_dist = summary.get('status_distribution', {})
                if status_dist:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = go.Figure(data=[go.Pie(
                            labels=list(status_dist.keys()),
                            values=list(status_dist.values()),
                            hole=.4,
                            marker_colors=['#28a745', '#17a2b8', '#ffc107', '#dc3545']
                        )])
                        fig.update_layout(title="Inventory by Stock Status")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### Stock Status Legend")
                        st.markdown("""
                        - 🟢 **Healthy** (30-90 days): Optimal level
                        - 🔵 **Low** (<30 days): Risk of stockout
                        - 🟡 **Excess** (90-180 days): Consider promotions
                        - 🔴 **Aged** (>180 days): Incurring surcharges
                        """)
                
                # At-risk inventory
                at_risk = inv_results.get('at_risk', [])
                if at_risk:
                    st.markdown("#### ⚠️ At-Risk Inventory (Aged)")
                    st.dataframe(pd.DataFrame(at_risk), use_container_width=True)
            else:
                st.info("Upload inventory report to see inventory analysis.")
        
        # TAB 5: Keep/Kill Matrix
        with tabs[4]:
            st.markdown("### ⚖️ Product Keep/Kill Matrix")
            
            matrix = results.get('keep_kill', [])
            
            if matrix:
                # Summary counts
                recommendations = pd.DataFrame(matrix)['recommendation'].value_counts().to_dict()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("INVEST", recommendations.get('INVEST', 0), "High performers")
                with col2:
                    st.metric("MAINTAIN", recommendations.get('MAINTAIN', 0), "Stable")
                with col3:
                    st.metric("OPTIMIZE", recommendations.get('OPTIMIZE', 0), "Need work")
                with col4:
                    st.metric("EXIT", recommendations.get('EXIT', 0), "Consider removing")
                
                st.markdown("---")
                
                # Matrix visualization
                df_matrix = pd.DataFrame(matrix)
                
                fig = px.scatter(
                    df_matrix,
                    x='cvr',
                    y='revenue',
                    size='sessions',
                    color='recommendation',
                    hover_data=['asin', 'title', 'score'],
                    color_discrete_map={
                        'INVEST': '#28a745',
                        'MAINTAIN': '#17a2b8',
                        'OPTIMIZE': '#ffc107',
                        'EXIT': '#dc3545'
                    },
                    title="Product Portfolio Matrix"
                )
                fig.update_layout(
                    xaxis_title="Conversion Rate (%)",
                    yaxis_title="Revenue ($)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed table
                st.markdown("#### Detailed ASIN Analysis")
                st.dataframe(
                    df_matrix.style.apply(
                        lambda x: ['background-color: ' + x['color']] * len(x) if x.name >= 0 else [''] * len(x),
                        axis=1
                    ),
                    use_container_width=True
                )
            else:
                st.info("Upload Business Report to see Keep/Kill matrix.")
        
        # TAB 6: Full Report
        with tabs[5]:
            st.markdown("### 📊 Export Full Report")
            
            st.markdown("""
            Download your complete audit report including:
            - Executive Summary
            - Market Position Analysis
            - PPC Performance Review
            - Inventory Health Assessment
            - Product Portfolio Recommendations
            - 90-Day Action Plan
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate PDF Report", use_container_width=True):
                    st.info("PDF generation is coming soon!")
            
            with col2:
                if st.button("📊 Export to Excel", use_container_width=True):
                    # Create Excel file
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        if st.session_state.audit_data['sqp_brand'] is not None:
                            st.session_state.audit_data['sqp_brand'].to_excel(writer, sheet_name='SQP Analysis', index=False)
                        if st.session_state.audit_data['ppc_bulk'] is not None:
                            st.session_state.audit_data['ppc_bulk'].to_excel(writer, sheet_name='PPC Analysis', index=False)
                        if results.get('keep_kill'):
                            pd.DataFrame(results['keep_kill']).to_excel(writer, sheet_name='Keep-Kill Matrix', index=False)
                    
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=output.getvalue(),
                        file_name=f"audit_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

# =============================================================================
# RUN APPLICATION
# =============================================================================

if __name__ == "__main__":
    main()
