"""
AdSellix Audit Tool - PPC Analysis Module
Version: 1.0.0
Status: PROTECTED - Do not modify without backup

This module handles:
- Campaign performance analysis (SP, SB, SD)
- Search term mining and optimization
- Waste detection and opportunity identification
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CampaignSummary:
    """Summary of campaign performance."""
    campaign_id: str
    campaign_name: str
    campaign_type: str  # SP, SB, SD
    targeting_type: str  # Auto, Manual
    state: str
    impressions: int
    clicks: int
    spend: float
    sales: float
    orders: int
    acos: float
    roas: float
    cvr: float
    cpc: float


@dataclass
class SearchTermAnalysis:
    """Analysis of a search term."""
    search_term: str
    campaign_name: str
    ad_group_name: str
    keyword: str
    match_type: str
    impressions: int
    clicks: int
    spend: float
    sales: float
    orders: int
    acos: float
    cvr: float
    recommendation: str  # 'Scale', 'Maintain', 'Optimize', 'Negate'


# =============================================================================
# CAMPAIGN PARSING
# =============================================================================

def parse_campaign_name(campaign_name: str) -> Dict[str, str]:
    """
    Parse campaign naming convention to extract components.
    
    Common patterns:
    - "SP-Exact-keyword" -> {type: SP, match: Exact, target: keyword}
    - "OG | Goal | Auto" -> {brand: OG, objective: Goal, targeting: Auto}
    - "BS | Ball | Dribble" -> {brand: BS, product: Ball, target: Dribble}
    """
    result = {
        'ad_type': '',
        'match_type': '',
        'targeting': '',
        'brand_code': '',
        'objective': ''
    }
    
    name_lower = campaign_name.lower() if campaign_name else ''
    
    # Detect ad type
    if name_lower.startswith('sp-') or 'sponsored products' in name_lower:
        result['ad_type'] = 'SP'
    elif name_lower.startswith('sb-') or 'sponsored brands' in name_lower:
        result['ad_type'] = 'SB'
    elif name_lower.startswith('sd-') or 'sponsored display' in name_lower:
        result['ad_type'] = 'SD'
    
    # Detect match type
    if 'exact' in name_lower:
        result['match_type'] = 'Exact'
    elif 'phrase' in name_lower:
        result['match_type'] = 'Phrase'
    elif 'broad' in name_lower:
        result['match_type'] = 'Broad'
    elif 'auto' in name_lower:
        result['targeting'] = 'Auto'
    elif 'asin' in name_lower or 'product' in name_lower:
        result['targeting'] = 'Product'
    
    # Parse pipe-separated format
    if '|' in campaign_name:
        parts = [p.strip() for p in campaign_name.split('|')]
        if len(parts) >= 2:
            result['brand_code'] = parts[0]
            result['objective'] = parts[1]
    
    return result


def get_campaign_type(entity: str) -> str:
    """Map entity type to campaign type."""
    mapping = {
        'Campaign': 'Campaign',
        'Ad Group': 'Ad Group',
        'Keyword': 'Keyword',
        'Product Targeting': 'Product Target',
        'Bidding Adjustment': 'Bid Adjustment',
        'Negative Keyword': 'Negative KW',
        'Negative Product Targeting': 'Negative PT'
    }
    return mapping.get(entity, entity)


# =============================================================================
# CAMPAIGN ANALYSIS
# =============================================================================

def analyze_sp_campaigns(sp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze Sponsored Products campaigns.
    
    Returns DataFrame with campaign-level metrics.
    """
    # Filter to campaign-level rows
    campaigns = sp_df[sp_df['Entity'] == 'Campaign'].copy()
    
    if campaigns.empty:
        return pd.DataFrame()
    
    # Calculate metrics
    analysis = pd.DataFrame({
        'Campaign ID': campaigns['Campaign ID'],
        'Campaign Name': campaigns['Campaign Name'],
        'State': campaigns['State'],
        'Daily Budget': campaigns['Daily Budget'],
        'Targeting Type': campaigns['Targeting Type'],
        'Bidding Strategy': campaigns['Bidding Strategy'],
        'Impressions': campaigns['Impressions'],
        'Clicks': campaigns['Clicks'],
        'CTR': campaigns['Click-through Rate'],
        'Spend': campaigns['Spend'],
        'Sales': campaigns['Sales'],
        'Orders': campaigns['Orders'],
        'CVR': campaigns['Conversion Rate'],
        'ACoS': campaigns['ACOS'],
        'ROAS': campaigns['ROAS'],
        'CPC': campaigns['CPC']
    })
    
    # Parse campaign names
    parsed = analysis['Campaign Name'].apply(parse_campaign_name)
    analysis['Ad Type'] = parsed.apply(lambda x: x.get('ad_type', 'SP'))
    analysis['Match Type'] = parsed.apply(lambda x: x.get('match_type', ''))
    analysis['Auto/Manual'] = parsed.apply(lambda x: 'Auto' if x.get('targeting') == 'Auto' else 'Manual')
    
    return analysis.sort_values('Spend', ascending=False)


def analyze_ad_groups(sp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze ad group performance within campaigns.
    """
    ad_groups = sp_df[sp_df['Entity'] == 'Ad Group'].copy()
    
    if ad_groups.empty:
        return pd.DataFrame()
    
    analysis = pd.DataFrame({
        'Campaign Name': ad_groups['Campaign Name (Informational only)'],
        'Ad Group Name': ad_groups['Ad Group Name'],
        'State': ad_groups['State'],
        'Default Bid': ad_groups['Ad Group Default Bid'],
        'Impressions': ad_groups['Impressions'],
        'Clicks': ad_groups['Clicks'],
        'Spend': ad_groups['Spend'],
        'Sales': ad_groups['Sales'],
        'Orders': ad_groups['Orders'],
        'CVR': ad_groups['Conversion Rate'],
        'ACoS': ad_groups['ACOS'],
        'ROAS': ad_groups['ROAS']
    })
    
    return analysis.sort_values('Spend', ascending=False)


def analyze_keywords(sp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze keyword performance.
    """
    keywords = sp_df[sp_df['Entity'] == 'Keyword'].copy()
    
    if keywords.empty:
        return pd.DataFrame()
    
    analysis = pd.DataFrame({
        'Campaign Name': keywords['Campaign Name (Informational only)'],
        'Ad Group Name': keywords['Ad Group Name (Informational only)'],
        'Keyword': keywords['Keyword Text'],
        'Match Type': keywords['Match Type'],
        'Bid': keywords['Bid'],
        'State': keywords['State'],
        'Impressions': keywords['Impressions'],
        'Clicks': keywords['Clicks'],
        'CTR': keywords['Click-through Rate'],
        'Spend': keywords['Spend'],
        'Sales': keywords['Sales'],
        'Orders': keywords['Orders'],
        'CVR': keywords['Conversion Rate'],
        'ACoS': keywords['ACOS'],
        'ROAS': keywords['ROAS'],
        'CPC': keywords['CPC']
    })
    
    return analysis.sort_values('Spend', ascending=False)


def analyze_product_targeting(sp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze product targeting performance.
    """
    pt = sp_df[sp_df['Entity'] == 'Product Targeting'].copy()
    
    if pt.empty:
        return pd.DataFrame()
    
    analysis = pd.DataFrame({
        'Campaign Name': pt['Campaign Name (Informational only)'],
        'Ad Group Name': pt['Ad Group Name (Informational only)'],
        'Target Expression': pt['Product Targeting Expression'],
        'Bid': pt['Bid'],
        'State': pt['State'],
        'Impressions': pt['Impressions'],
        'Clicks': pt['Clicks'],
        'Spend': pt['Spend'],
        'Sales': pt['Sales'],
        'Orders': pt['Orders'],
        'CVR': pt['Conversion Rate'],
        'ACoS': pt['ACOS'],
        'ROAS': pt['ROAS']
    })
    
    return analysis.sort_values('Spend', ascending=False)


# =============================================================================
# SEARCH TERM ANALYSIS
# =============================================================================

def analyze_search_terms(str_df: pd.DataFrame, breakeven_acos: float = 30.0) -> pd.DataFrame:
    """
    Analyze search term performance and generate recommendations.
    
    Args:
        str_df: Search Term Report DataFrame
        breakeven_acos: Target ACoS for profitability
    
    Returns:
        DataFrame with search terms and recommendations
    """
    analysis = pd.DataFrame({
        'Search Term': str_df['Customer Search Term'],
        'Campaign': str_df['Campaign Name (Informational only)'],
        'Ad Group': str_df['Ad Group Name (Informational only)'],
        'Keyword': str_df['Keyword Text'],
        'Match Type': str_df['Match Type'],
        'Impressions': str_df['Impressions'],
        'Clicks': str_df['Clicks'],
        'CTR': str_df['Click-through Rate'],
        'Spend': str_df['Spend'],
        'Sales': str_df['Sales'],
        'Orders': str_df['Orders'],
        'CVR': str_df['Conversion Rate'],
        'ACoS': str_df['ACOS'],
        'ROAS': str_df['ROAS'],
        'CPC': str_df['CPC']
    })
    
    # Generate recommendations
    def get_recommendation(row):
        spend = row['Spend']
        sales = row['Sales']
        cvr = row['CVR']
        acos = row['ACoS']
        clicks = row['Clicks']
        
        if spend == 0:
            return 'No Data'
        
        # High performer - Scale
        if acos > 0 and acos <= breakeven_acos * 0.7 and cvr >= 5:
            return '🚀 Scale'
        
        # Good performer - Maintain
        if acos > 0 and acos <= breakeven_acos and cvr >= 2:
            return '✅ Maintain'
        
        # Needs optimization
        if acos > breakeven_acos and acos <= breakeven_acos * 1.5 and sales > 0:
            return '⚠️ Optimize'
        
        # High spend, no sales - Negate
        if spend >= 10 and clicks >= 10 and (sales == 0 or acos > breakeven_acos * 2):
            return '🛑 Negate'
        
        # Not enough data
        if clicks < 5:
            return '📊 More Data'
        
        return '👀 Monitor'
    
    analysis['Recommendation'] = analysis.apply(get_recommendation, axis=1)
    
    # Sort by potential impact
    analysis['Impact Score'] = analysis['Spend'] * (1 + (analysis['CVR'] / 10))
    analysis = analysis.sort_values('Impact Score', ascending=False)
    
    return analysis


def find_search_term_opportunities(
    str_df: pd.DataFrame,
    sqp_df: pd.DataFrame = None
) -> Dict[str, pd.DataFrame]:
    """
    Find search term optimization opportunities.
    
    Returns dict with:
    - 'to_scale': High performers to increase bids
    - 'to_negate': Wasted spend to add as negatives
    - 'new_keywords': Search terms to add as keywords
    - 'to_exact': Broad/Phrase matches to promote to Exact
    """
    opportunities = {}
    
    # Scale opportunities: Low ACoS, Good CVR
    scale = str_df[
        (str_df['ACOS'] > 0) &
        (str_df['ACOS'] <= 20) &
        (str_df['Conversion Rate'] >= 5) &
        (str_df['Impressions'] >= 500)
    ].copy()
    scale['Potential'] = scale['Sales'] * (1 - scale['ACOS'] / 100)
    opportunities['to_scale'] = scale.sort_values('Potential', ascending=False)
    
    # Negate: High spend, no conversions
    negate = str_df[
        (str_df['Spend'] >= 15) &
        (str_df['Clicks'] >= 15) &
        ((str_df['Sales'] == 0) | (str_df['ACOS'] > 100))
    ].copy()
    negate['Wasted Spend'] = negate['Spend'] - negate['Sales']
    opportunities['to_negate'] = negate.sort_values('Wasted Spend', ascending=False)
    
    # New keyword opportunities: Good performance, might not be targeted
    new_kw = str_df[
        (str_df['ACOS'] > 0) &
        (str_df['ACOS'] <= 30) &
        (str_df['Orders'] >= 2) &
        (str_df['Customer Search Term'] != str_df['Keyword Text'])
    ].copy()
    opportunities['new_keywords'] = new_kw.sort_values('Orders', ascending=False)
    
    # Promote to Exact: Good Broad/Phrase performers
    to_exact = str_df[
        (str_df['Match Type'].isin(['Broad', 'Phrase'])) &
        (str_df['ACOS'] > 0) &
        (str_df['ACOS'] <= 25) &
        (str_df['Orders'] >= 3)
    ].copy()
    opportunities['to_exact'] = to_exact.sort_values('Orders', ascending=False)
    
    return opportunities


# =============================================================================
# WASTE DETECTION
# =============================================================================

def detect_ppc_waste(
    ppc_data: Dict[str, pd.DataFrame],
    breakeven_acos: float = 30.0
) -> Dict[str, pd.DataFrame]:
    """
    Detect wasted PPC spend across all campaign types.
    
    Returns dict with waste categories:
    - 'high_acos_campaigns': Campaigns with ACoS > 2x breakeven
    - 'zero_sales_spend': Spend with no sales
    - 'low_ctr_high_spend': High spend but poor CTR
    - 'cannibalization': Potential self-competition
    """
    waste = {}
    
    # Combine all campaign data
    sp_campaigns = ppc_data.get('Sponsored Products Campaigns', pd.DataFrame())
    
    if not sp_campaigns.empty:
        campaigns = sp_campaigns[sp_campaigns['Entity'] == 'Campaign'].copy()
        
        # High ACoS campaigns
        high_acos = campaigns[
            (campaigns['ACOS'] > breakeven_acos * 2) &
            (campaigns['Spend'] >= 50)
        ].copy()
        high_acos['Excess Spend'] = high_acos['Spend'] - (high_acos['Sales'] * breakeven_acos / 100)
        waste['high_acos_campaigns'] = high_acos.sort_values('Excess Spend', ascending=False)
        
        # Zero sales spend (keywords/targets)
        keywords = sp_campaigns[sp_campaigns['Entity'].isin(['Keyword', 'Product Targeting'])].copy()
        zero_sales = keywords[
            (keywords['Spend'] >= 20) &
            (keywords['Sales'] == 0) &
            (keywords['Clicks'] >= 10)
        ].copy()
        waste['zero_sales_spend'] = zero_sales.sort_values('Spend', ascending=False)
        
        # Low CTR high spend (visibility but no engagement)
        low_ctr = keywords[
            (keywords['Impressions'] >= 5000) &
            (keywords['Spend'] >= 20) &
            (keywords['Click-through Rate'] < 0.2)
        ].copy()
        waste['low_ctr_high_spend'] = low_ctr.sort_values('Impressions', ascending=False)
    
    # Calculate total waste
    total_waste = 0
    for category, df in waste.items():
        if not df.empty and 'Spend' in df.columns:
            if category == 'high_acos_campaigns':
                total_waste += df['Excess Spend'].sum() if 'Excess Spend' in df.columns else 0
            else:
                total_waste += df['Spend'].sum()
    
    waste['total_estimated_waste'] = total_waste
    
    return waste


# =============================================================================
# PPC SUMMARY METRICS
# =============================================================================

def calculate_ppc_summary(ppc_data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
    """
    Calculate overall PPC performance summary.
    """
    summary = {
        'total_spend': 0,
        'total_sales': 0,
        'total_orders': 0,
        'total_impressions': 0,
        'total_clicks': 0,
        'overall_acos': 0,
        'overall_roas': 0,
        'overall_ctr': 0,
        'overall_cvr': 0,
        'sp_spend': 0,
        'sb_spend': 0,
        'sd_spend': 0,
        'campaign_count': 0,
        'active_campaigns': 0
    }
    
    for sheet_name, df in ppc_data.items():
        if df.empty:
            continue
        
        if 'Campaigns' in sheet_name:
            campaigns = df[df['Entity'] == 'Campaign'].copy()
            
            spend = campaigns['Spend'].sum()
            sales = campaigns['Sales'].sum()
            
            summary['total_spend'] += spend
            summary['total_sales'] += sales
            summary['total_orders'] += campaigns['Orders'].sum()
            summary['total_impressions'] += campaigns['Impressions'].sum()
            summary['total_clicks'] += campaigns['Clicks'].sum()
            summary['campaign_count'] += len(campaigns)
            summary['active_campaigns'] += len(campaigns[campaigns['State'] == 'enabled'])
            
            if 'Sponsored Products' in sheet_name:
                summary['sp_spend'] = spend
            elif 'Sponsored Brands' in sheet_name:
                summary['sb_spend'] = spend
            elif 'Sponsored Display' in sheet_name:
                summary['sd_spend'] = spend
    
    # Calculate rates
    if summary['total_sales'] > 0:
        summary['overall_acos'] = (summary['total_spend'] / summary['total_sales']) * 100
        
    if summary['total_spend'] > 0:
        summary['overall_roas'] = summary['total_sales'] / summary['total_spend']
    
    if summary['total_impressions'] > 0:
        summary['overall_ctr'] = (summary['total_clicks'] / summary['total_impressions']) * 100
    
    if summary['total_clicks'] > 0:
        summary['overall_cvr'] = (summary['total_orders'] / summary['total_clicks']) * 100
    
    return summary


def get_top_performers(
    ppc_data: Dict[str, pd.DataFrame],
    metric: str = 'Sales',
    top_n: int = 10
) -> pd.DataFrame:
    """
    Get top performing keywords/targets by specified metric.
    """
    all_keywords = []
    
    for sheet_name, df in ppc_data.items():
        if 'Campaigns' in sheet_name and not df.empty:
            keywords = df[df['Entity'].isin(['Keyword', 'Product Targeting'])].copy()
            keywords['Source'] = sheet_name.replace(' Campaigns', '')
            all_keywords.append(keywords)
    
    if not all_keywords:
        return pd.DataFrame()
    
    combined = pd.concat(all_keywords, ignore_index=True)
    
    # Filter to performers with sales
    performers = combined[combined['Sales'] > 0].copy()
    
    return performers.nlargest(top_n, metric)


def get_worst_performers(
    ppc_data: Dict[str, pd.DataFrame],
    min_spend: float = 20,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Get worst performing keywords/targets (high spend, low returns).
    """
    all_keywords = []
    
    for sheet_name, df in ppc_data.items():
        if 'Campaigns' in sheet_name and not df.empty:
            keywords = df[df['Entity'].isin(['Keyword', 'Product Targeting'])].copy()
            keywords['Source'] = sheet_name.replace(' Campaigns', '')
            all_keywords.append(keywords)
    
    if not all_keywords:
        return pd.DataFrame()
    
    combined = pd.concat(all_keywords, ignore_index=True)
    
    # Filter to high spend, poor performance
    poor = combined[
        (combined['Spend'] >= min_spend) &
        ((combined['Sales'] == 0) | (combined['ACOS'] > 50))
    ].copy()
    
    poor['Waste Score'] = poor['Spend'] - poor['Sales']
    
    return poor.nlargest(top_n, 'Waste Score')
