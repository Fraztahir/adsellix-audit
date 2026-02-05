"""
AdSellix AI Audit Tool - Main Application
Version: 1.0.0 (Phase 1 MVP)
Status: ACTIVE

Multi-tab Streamlit application for Amazon brand audits.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# Import core modules
from core.data_loaders import (
    MARKETPLACES, AuditDataLoader,
    load_sqp_brand_view, load_sqp_asin_view,
    load_business_report, load_ppc_bulk_sheet,
    load_inventory_report, load_cogs, load_fba_fees,
    load_category_listing_report
)
from core.hierarchy import (
    parse_clr_hierarchy, detect_hero_asins,
    build_hierarchy_from_business_report,
    get_hierarchy_summary, get_children_summary,
    get_all_hero_asins
)
from core.calculations import (
    calculate_tacos, calculate_true_acos, calculate_roas,
    calculate_brand_growth, calculate_market_growth,
    compare_sqp_periods, calculate_brand_health_score, get_health_grade
)
from ppc.analysis import (
    analyze_sp_campaigns, analyze_ad_groups, analyze_keywords,
    analyze_search_terms, find_search_term_opportunities,
    detect_ppc_waste, calculate_ppc_summary,
    get_top_performers, get_worst_performers
)
from modules.keep_kill import (
    build_keep_kill_matrix, matrix_to_dataframe, get_action_summary
)


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="AdSellix AI Audit Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .score-excellent { color: #10B981; font-weight: bold; }
    .score-good { color: #3B82F6; font-weight: bold; }
    .score-average { color: #F59E0B; font-weight: bold; }
    .score-poor { color: #EF4444; font-weight: bold; }
    .action-invest { background-color: #10B981; color: white; padding: 3px 8px; border-radius: 4px; }
    .action-maintain { background-color: #3B82F6; color: white; padding: 3px 8px; border-radius: 4px; }
    .action-optimize { background-color: #F59E0B; color: white; padding: 3px 8px; border-radius: 4px; }
    .action-harvest { background-color: #8B5CF6; color: white; padding: 3px 8px; border-radius: 4px; }
    .action-exit { background-color: #EF4444; color: white; padding: 3px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'marketplace' not in st.session_state:
    st.session_state.marketplace = None
if 'loader' not in st.session_state:
    st.session_state.loader = None
if 'audit_data' not in st.session_state:
    st.session_state.audit_data = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'hierarchy' not in st.session_state:
    st.session_state.hierarchy = None


# =============================================================================
# SIDEBAR - MARKETPLACE & SETUP
# =============================================================================

with st.sidebar:
    st.markdown("## 🌍 Marketplace Selection")
    
    marketplace_options = {f"{v['name']} ({k})": k for k, v in MARKETPLACES.items()}
    selected_marketplace = st.selectbox(
        "Select Marketplace",
        options=list(marketplace_options.keys()),
        index=0 if st.session_state.marketplace is None else list(marketplace_options.values()).index(st.session_state.marketplace)
    )
    
    if selected_marketplace:
        marketplace_code = marketplace_options[selected_marketplace]
        if st.session_state.marketplace != marketplace_code:
            st.session_state.marketplace = marketplace_code
            st.session_state.loader = AuditDataLoader(marketplace_code)
            st.session_state.audit_data = {}
            st.session_state.analysis_results = {}
    
    st.markdown("---")
    
    # Show loaded data status
    st.markdown("## 📂 Data Status")
    
    data_status = {
        'SQP Brand (Current)': 'sqp_brand_current' in st.session_state.audit_data,
        'SQP Brand (Previous)': 'sqp_brand_previous' in st.session_state.audit_data,
        'Business Report': 'business_report' in st.session_state.audit_data,
        'PPC Data': 'ppc' in st.session_state.audit_data,
        'Inventory': 'inventory' in st.session_state.audit_data,
        'COGS': 'cogs' in st.session_state.audit_data,
        'FBA Fees': 'fba_fees' in st.session_state.audit_data,
    }
    
    for name, loaded in data_status.items():
        status = "✅" if loaded else "⬜"
        st.write(f"{status} {name}")
    
    st.markdown("---")
    st.markdown(f"**Version:** 1.0.0 (Phase 1 MVP)")
    st.markdown(f"**Marketplace:** {st.session_state.marketplace or 'Not Selected'}")


# =============================================================================
# MAIN CONTENT - TABS
# =============================================================================

st.markdown('<p class="main-header">📊 AdSellix AI Audit Tool</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Enterprise Amazon Brand Analytics | {MARKETPLACES.get(st.session_state.marketplace, {}).get("name", "Select Marketplace")}</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📁 Data Upload",
    "📈 Market Position",
    "💰 PPC Analysis",
    "📦 Inventory",
    "🎯 Keep/Kill Matrix",
    "🏆 Brand Health",
    "📄 Executive Summary"
])


# =============================================================================
# TAB 1: DATA UPLOAD
# =============================================================================

with tab1:
    st.header("📁 Data Upload")
    
    if not st.session_state.marketplace:
        st.warning("⚠️ Please select a marketplace from the sidebar first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Period Data")
            
            # SQP Brand View Current
            sqp_current = st.file_uploader(
                "SQP Brand View (Current Period)",
                type=['csv'],
                key='sqp_brand_current_upload'
            )
            if sqp_current:
                try:
                    df, meta = load_sqp_brand_view(sqp_current)
                    st.session_state.audit_data['sqp_brand_current'] = df
                    st.session_state.audit_data['sqp_brand_current_meta'] = meta
                    st.success(f"✅ Loaded {len(df)} search queries | {meta.get('brand', 'Unknown')} | Q{meta.get('select_quarter', '?')} {meta.get('select_year', '?')}")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            
            # Business Report
            br_file = st.file_uploader(
                "Business Report (Detail Page Sales)",
                type=['csv'],
                key='br_upload'
            )
            if br_file:
                try:
                    df = load_business_report(br_file)
                    st.session_state.audit_data['business_report'] = df
                    st.success(f"✅ Loaded {len(df)} ASINs")
                    
                    # Auto-build hierarchy from BR
                    hierarchy = build_hierarchy_from_business_report(df)
                    hierarchy = detect_hero_asins(hierarchy, df, top_n=3)
                    st.session_state.hierarchy = hierarchy
                    st.info(f"📊 Auto-detected {len(hierarchy)} parent groups with hero ASINs")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            
            # PPC Bulk Sheet
            ppc_file = st.file_uploader(
                "PPC Bulk Sheet (Excel)",
                type=['xlsx', 'xls'],
                key='ppc_upload'
            )
            if ppc_file:
                try:
                    sheets = load_ppc_bulk_sheet(ppc_file)
                    st.session_state.audit_data['ppc'] = sheets
                    total_rows = sum(len(df) for df in sheets.values())
                    st.success(f"✅ Loaded {len(sheets)} sheets ({total_rows:,} total rows)")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            
            # Inventory
            inv_file = st.file_uploader(
                "Inventory Report",
                type=['csv'],
                key='inv_upload'
            )
            if inv_file:
                try:
                    df = load_inventory_report(inv_file)
                    st.session_state.audit_data['inventory'] = df
                    st.success(f"✅ Loaded {len(df)} SKUs")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
        
        with col2:
            st.subheader("Comparison & Reference Data")
            
            # SQP Brand View Previous
            sqp_previous = st.file_uploader(
                "SQP Brand View (Previous Period)",
                type=['csv'],
                key='sqp_brand_previous_upload'
            )
            if sqp_previous:
                try:
                    df, meta = load_sqp_brand_view(sqp_previous)
                    st.session_state.audit_data['sqp_brand_previous'] = df
                    st.session_state.audit_data['sqp_brand_previous_meta'] = meta
                    st.success(f"✅ Loaded {len(df)} search queries | Q{meta.get('select_quarter', '?')} {meta.get('select_year', '?')}")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            
            # COGS
            cogs_file = st.file_uploader(
                "COGS Data",
                type=['csv'],
                key='cogs_upload'
            )
            if cogs_file:
                try:
                    df = load_cogs(cogs_file)
                    st.session_state.audit_data['cogs'] = df
                    st.success(f"✅ Loaded COGS for {len(df)} SKUs")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            
            # FBA Fees
            fees_file = st.file_uploader(
                "FBA & Referral Fees Report",
                type=['csv'],
                key='fees_upload'
            )
            if fees_file:
                try:
                    df = load_fba_fees(fees_file)
                    st.session_state.audit_data['fba_fees'] = df
                    st.success(f"✅ Loaded fees for {len(df)} ASINs")
                except Exception as e:
                    st.error(f"Error loading file: {e}")
            
            # SQP ASIN Views (multiple)
            st.markdown("---")
            st.subheader("ASIN-Level SQP (Optional)")
            sqp_asin_files = st.file_uploader(
                "SQP ASIN Views (select multiple)",
                type=['csv'],
                key='sqp_asin_upload',
                accept_multiple_files=True
            )
            if sqp_asin_files:
                st.session_state.audit_data['sqp_asin'] = {}
                for f in sqp_asin_files:
                    try:
                        df, meta = load_sqp_asin_view(f)
                        asin = meta.get('asin', f.name)
                        st.session_state.audit_data['sqp_asin'][asin] = df
                        st.success(f"✅ {asin}: {len(df)} queries")
                    except Exception as e:
                        st.error(f"Error with {f.name}: {e}")


# =============================================================================
# TAB 2: MARKET POSITION
# =============================================================================

with tab2:
    st.header("📈 Market Position Analysis")
    
    if 'sqp_brand_current' not in st.session_state.audit_data:
        st.warning("⚠️ Please upload SQP Brand View (Current Period) in the Data Upload tab.")
    else:
        sqp_current = st.session_state.audit_data['sqp_brand_current']
        sqp_previous = st.session_state.audit_data.get('sqp_brand_previous')
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_queries = len(sqp_current)
        total_impressions = sqp_current['Impressions: Brand Count'].sum()
        total_clicks = sqp_current['Clicks: Brand Count'].sum()
        total_purchases = sqp_current['Purchases: Brand Count'].sum()
        
        with col1:
            st.metric("Search Queries", f"{total_queries:,}")
        with col2:
            st.metric("Brand Impressions", f"{total_impressions:,}")
        with col3:
            st.metric("Brand Clicks", f"{total_clicks:,}")
        with col4:
            st.metric("Brand Purchases", f"{total_purchases:,}")
        
        # Top performing queries
        st.subheader("🔝 Top Performing Search Queries")
        
        top_queries = sqp_current.nlargest(20, 'Purchases: Brand Count')[
            ['Search Query', 'Search Query Volume', 'Impressions: Brand Share %',
             'Clicks: Brand Count', 'Purchases: Brand Count']
        ]
        st.dataframe(top_queries, use_container_width=True)
        
        # Period comparison
        if sqp_previous is not None:
            st.subheader("📊 Period-over-Period Comparison")
            
            comparison = compare_sqp_periods(sqp_current, sqp_previous, 'brand')
            
            # Show top gainers
            gainers = comparison.nlargest(10, 'Share Change (pp)')[
                ['Search Query', 'Brand Share % (Current)', 'Brand Share % (Previous)', 
                 'Share Change (pp)', 'Purchases Change']
            ]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 Top Gainers (Share)**")
                st.dataframe(gainers, use_container_width=True)
            
            with col2:
                losers = comparison.nsmallest(10, 'Share Change (pp)')[
                    ['Search Query', 'Brand Share % (Current)', 'Brand Share % (Previous)',
                     'Share Change (pp)', 'Purchases Change']
                ]
                st.markdown("**📉 Top Losers (Share)**")
                st.dataframe(losers, use_container_width=True)


# =============================================================================
# TAB 3: PPC ANALYSIS
# =============================================================================

with tab3:
    st.header("💰 PPC Analysis")
    
    if 'ppc' not in st.session_state.audit_data:
        st.warning("⚠️ Please upload PPC Bulk Sheet in the Data Upload tab.")
    else:
        ppc_data = st.session_state.audit_data['ppc']
        
        # Calculate summary
        summary = calculate_ppc_summary(ppc_data)
        
        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Spend", f"${summary['total_spend']:,.2f}")
        with col2:
            st.metric("Total Sales", f"${summary['total_sales']:,.2f}")
        with col3:
            st.metric("ACoS", f"{summary['overall_acos']:.1f}%")
        with col4:
            st.metric("ROAS", f"{summary['overall_roas']:.2f}x")
        with col5:
            st.metric("Active Campaigns", summary['active_campaigns'])
        
        # Spend breakdown
        st.subheader("💵 Spend by Ad Type")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sponsored Products", f"${summary['sp_spend']:,.2f}")
        with col2:
            st.metric("Sponsored Brands", f"${summary['sb_spend']:,.2f}")
        with col3:
            st.metric("Sponsored Display", f"${summary['sd_spend']:,.2f}")
        
        # Campaign analysis tabs
        ppc_tab1, ppc_tab2, ppc_tab3, ppc_tab4 = st.tabs([
            "Campaigns", "Keywords", "Search Terms", "Waste Detection"
        ])
        
        with ppc_tab1:
            if 'Sponsored Products Campaigns' in ppc_data:
                campaigns = analyze_sp_campaigns(ppc_data['Sponsored Products Campaigns'])
                if not campaigns.empty:
                    st.dataframe(
                        campaigns[['Campaign Name', 'State', 'Impressions', 'Clicks', 
                                   'Spend', 'Sales', 'ACoS', 'ROAS']].head(20),
                        use_container_width=True
                    )
        
        with ppc_tab2:
            if 'Sponsored Products Campaigns' in ppc_data:
                keywords = analyze_keywords(ppc_data['Sponsored Products Campaigns'])
                if not keywords.empty:
                    st.dataframe(
                        keywords[['Campaign Name', 'Keyword', 'Match Type', 
                                  'Spend', 'Sales', 'Orders', 'ACoS']].head(30),
                        use_container_width=True
                    )
        
        with ppc_tab3:
            if 'SP Search Term Report' in ppc_data:
                # Breakeven ACoS input
                breakeven = st.slider("Break-even ACoS %", 10, 50, 30)
                
                str_analysis = analyze_search_terms(ppc_data['SP Search Term Report'], breakeven)
                
                # Show by recommendation
                rec_filter = st.multiselect(
                    "Filter by Recommendation",
                    ['🚀 Scale', '✅ Maintain', '⚠️ Optimize', '🛑 Negate', '👀 Monitor'],
                    default=['🚀 Scale', '🛑 Negate']
                )
                
                filtered = str_analysis[str_analysis['Recommendation'].isin(rec_filter)]
                st.dataframe(
                    filtered[['Search Term', 'Campaign', 'Spend', 'Sales', 
                              'CVR', 'ACoS', 'Recommendation']].head(50),
                    use_container_width=True
                )
        
        with ppc_tab4:
            waste = detect_ppc_waste(ppc_data)
            
            st.metric("Estimated Total Waste", f"${waste.get('total_estimated_waste', 0):,.2f}")
            
            if 'high_acos_campaigns' in waste and not waste['high_acos_campaigns'].empty:
                st.markdown("**🔴 High ACoS Campaigns**")
                st.dataframe(waste['high_acos_campaigns'][['Campaign Name', 'Spend', 'Sales', 'ACOS']].head(10))
            
            if 'zero_sales_spend' in waste and not waste['zero_sales_spend'].empty:
                st.markdown("**🔴 Zero Sales Spend**")
                st.dataframe(waste['zero_sales_spend'][['Campaign Name (Informational only)', 'Keyword Text', 'Spend', 'Clicks']].head(10))


# =============================================================================
# TAB 4: INVENTORY
# =============================================================================

with tab4:
    st.header("📦 Inventory Analysis")
    
    if 'inventory' not in st.session_state.audit_data:
        st.warning("⚠️ Please upload Inventory Report in the Data Upload tab.")
    else:
        inv_df = st.session_state.audit_data['inventory']
        
        # Summary metrics
        total_units = inv_df['available'].sum()
        low_stock = len(inv_df[inv_df['fba-inventory-level-health-status'] == 'Low stock'])
        healthy = len(inv_df[inv_df['fba-inventory-level-health-status'] == 'Healthy'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total SKUs", len(inv_df))
        with col2:
            st.metric("Total Units", f"{total_units:,}")
        with col3:
            st.metric("Low Stock", low_stock)
        with col4:
            st.metric("Healthy", healthy)
        
        # Inventory table
        st.subheader("📋 Inventory Details")
        display_cols = ['asin', 'sku', 'product-name', 'available', 'days-of-supply',
                        'units-shipped-t30', 'fba-inventory-level-health-status']
        available_cols = [c for c in display_cols if c in inv_df.columns]
        st.dataframe(inv_df[available_cols], use_container_width=True)


# =============================================================================
# TAB 5: KEEP/KILL MATRIX
# =============================================================================

with tab5:
    st.header("🎯 Keep/Kill Matrix")
    
    required = ['business_report']
    missing = [r for r in required if r not in st.session_state.audit_data]
    
    if missing:
        st.warning(f"⚠️ Please upload: {', '.join(missing)}")
    else:
        # Build matrix
        scores = build_keep_kill_matrix(
            st.session_state.audit_data['business_report'],
            st.session_state.audit_data.get('sqp_brand_current', pd.DataFrame()),
            st.session_state.audit_data.get('sqp_brand_previous', pd.DataFrame()),
            {},
            st.session_state.audit_data.get('inventory', pd.DataFrame()),
            st.session_state.audit_data.get('cogs', pd.DataFrame()),
            st.session_state.audit_data.get('fba_fees', pd.DataFrame())
        )
        
        if scores:
            # Action summary
            action_summary = get_action_summary(scores)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🚀 INVEST", action_summary['INVEST'])
            with col2:
                st.metric("✅ MAINTAIN", action_summary['MAINTAIN'])
            with col3:
                st.metric("⚠️ OPTIMIZE", action_summary['OPTIMIZE'])
            with col4:
                st.metric("💰 HARVEST", action_summary['HARVEST'])
            with col5:
                st.metric("🛑 EXIT", action_summary['EXIT'])
            
            # Matrix table
            matrix_df = matrix_to_dataframe(scores)
            
            # Filter by action
            action_filter = st.multiselect(
                "Filter by Action",
                ['INVEST', 'MAINTAIN', 'OPTIMIZE', 'HARVEST', 'EXIT'],
                default=['INVEST', 'MAINTAIN', 'OPTIMIZE', 'HARVEST', 'EXIT']
            )
            
            filtered_matrix = matrix_df[matrix_df['Action'].isin(action_filter)]
            st.dataframe(filtered_matrix, use_container_width=True)


# =============================================================================
# TAB 6: BRAND HEALTH
# =============================================================================

with tab6:
    st.header("🏆 Brand Health Score")
    
    # Calculate overall health score
    market_share = 5  # Placeholder
    share_change = 0
    brand_growth = 0
    market_growth = 0
    avg_cvr = 10
    inv_health = 80
    ppc_eff = 60
    
    if 'sqp_brand_current' in st.session_state.audit_data:
        sqp = st.session_state.audit_data['sqp_brand_current']
        market_share = sqp['Impressions: Brand Share %'].mean()
        avg_cvr = (sqp['Purchases: Brand Count'].sum() / max(1, sqp['Clicks: Brand Count'].sum())) * 100
    
    if 'ppc' in st.session_state.audit_data:
        summary = calculate_ppc_summary(st.session_state.audit_data['ppc'])
        ppc_eff = min(100, (1 / max(0.01, summary['overall_acos'] / 30)) * 60)
    
    total_score, components = calculate_brand_health_score(
        market_share, share_change, brand_growth, market_growth,
        avg_cvr, inv_health, ppc_eff
    )
    
    grade = get_health_grade(total_score)
    
    # Display score
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px;">
            <h1 style="font-size: 5rem; margin: 0; color: white;">{grade}</h1>
            <h2 style="font-size: 2rem; margin: 0; color: white;">{total_score:.0f}/100</h2>
            <p style="color: rgba(255,255,255,0.8);">Brand Health Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Score Components")
        for component, score in components.items():
            max_score = 25 if component != 'Inventory Health' else 20
            if component == 'PPC Efficiency':
                max_score = 30
            pct = (score / max_score) * 100
            st.progress(pct / 100, text=f"{component}: {score:.1f}/{max_score}")


# =============================================================================
# TAB 7: EXECUTIVE SUMMARY
# =============================================================================

with tab7:
    st.header("📄 Executive Summary")
    
    st.markdown("""
    ### Brand Performance Overview
    
    *This section will be enhanced with AI-generated insights in a future update.*
    """)
    
    # Summary cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Key Strengths")
        st.markdown("""
        - Strong market presence in core search terms
        - Efficient PPC campaigns with positive ROAS
        - Healthy inventory levels
        """)
    
    with col2:
        st.subheader("⚠️ Areas for Improvement")
        st.markdown("""
        - Optimize high-ACoS campaigns
        - Address low-stock alerts
        - Expand into growth search terms
        """)
    
    # Export options
    st.markdown("---")
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to Excel"):
            st.info("Excel export coming in Phase 2")
    
    with col2:
        if st.button("📄 Generate PDF Report"):
            st.info("PDF export coming in Phase 2")
    
    with col3:
        if st.button("📋 Copy Summary"):
            st.info("Copy function coming in Phase 2")


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>AdSellix AI Audit Tool v1.0.0 | Phase 1 MVP</p>
    <p>© 2026 AdSellix. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
