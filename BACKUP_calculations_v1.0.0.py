"""
AdSellix Audit Tool - Calculations & Metrics
Version: 1.0.0
Status: PROTECTED - Do not modify without backup

This module handles:
- Financial calculations (margins, break-even ACoS)
- Market metrics (share, growth, RMS)
- Performance scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# =============================================================================
# FINANCIAL CALCULATIONS
# =============================================================================

def calculate_gross_margin(
    selling_price: float,
    cogs: float,
    fba_fee: float,
    referral_fee: float
) -> float:
    """
    Calculate gross margin after Amazon fees.
    
    Gross Margin = Selling Price - COGS - FBA Fee - Referral Fee
    """
    return selling_price - cogs - fba_fee - referral_fee


def calculate_gross_margin_percentage(
    selling_price: float,
    cogs: float,
    fba_fee: float,
    referral_fee: float
) -> float:
    """
    Calculate gross margin percentage.
    
    Gross Margin % = (Gross Margin / Selling Price) × 100
    """
    if selling_price == 0:
        return 0.0
    
    gross_margin = calculate_gross_margin(selling_price, cogs, fba_fee, referral_fee)
    return (gross_margin / selling_price) * 100


def calculate_breakeven_acos(
    selling_price: float,
    cogs: float,
    fba_fee: float,
    referral_fee: float
) -> float:
    """
    Calculate break-even ACoS.
    
    Break-even ACoS = Gross Margin %
    Any ACoS below this is profitable.
    """
    return calculate_gross_margin_percentage(selling_price, cogs, fba_fee, referral_fee)


def calculate_contribution_margin(
    selling_price: float,
    cogs: float,
    fba_fee: float,
    referral_fee: float,
    ad_spend: float,
    units_sold: int
) -> float:
    """
    Calculate contribution margin per unit after ad spend.
    
    CM = Gross Margin - (Ad Spend / Units Sold)
    """
    if units_sold == 0:
        return 0.0
    
    gross_margin = calculate_gross_margin(selling_price, cogs, fba_fee, referral_fee)
    ad_cost_per_unit = ad_spend / units_sold
    
    return gross_margin - ad_cost_per_unit


def calculate_true_acos(
    ad_spend: float,
    total_sales: float
) -> float:
    """
    Calculate true ACoS (Advertising Cost of Sales).
    
    ACoS = (Ad Spend / Ad-Attributed Sales) × 100
    """
    if total_sales == 0:
        return 0.0
    return (ad_spend / total_sales) * 100


def calculate_tacos(
    ad_spend: float,
    total_sales: float
) -> float:
    """
    Calculate TACoS (Total Advertising Cost of Sales).
    
    TACoS = (Ad Spend / Total Sales) × 100
    """
    if total_sales == 0:
        return 0.0
    return (ad_spend / total_sales) * 100


def calculate_roas(ad_spend: float, sales: float) -> float:
    """
    Calculate ROAS (Return on Ad Spend).
    
    ROAS = Sales / Ad Spend
    """
    if ad_spend == 0:
        return 0.0
    return sales / ad_spend


# =============================================================================
# MARKET METRICS
# =============================================================================

def calculate_brand_share_change(
    current_share: float,
    previous_share: float
) -> float:
    """
    Calculate absolute change in brand share.
    
    Change = Current Share - Previous Share
    """
    return current_share - previous_share


def calculate_relative_market_share(
    brand_share: float,
    market_growth: float,
    brand_growth: float
) -> str:
    """
    Calculate Relative Market Share position.
    
    Returns quadrant: 'Star', 'Question Mark', 'Cash Cow', or 'Dog'
    """
    # BCG Matrix logic
    high_share_threshold = 10  # 10% market share
    high_growth_threshold = 20  # 20% growth
    
    high_share = brand_share >= high_share_threshold
    high_growth = market_growth >= high_growth_threshold
    
    if high_share and high_growth:
        return 'Star'
    elif not high_share and high_growth:
        return 'Question Mark'
    elif high_share and not high_growth:
        return 'Cash Cow'
    else:
        return 'Dog'


def calculate_market_growth(
    current_total_purchases: float,
    previous_total_purchases: float
) -> float:
    """
    Calculate market growth percentage.
    
    Growth = ((Current - Previous) / Previous) × 100
    """
    if previous_total_purchases == 0:
        return 0.0
    return ((current_total_purchases - previous_total_purchases) / previous_total_purchases) * 100


def calculate_brand_growth(
    current_brand_purchases: float,
    previous_brand_purchases: float
) -> float:
    """
    Calculate brand growth percentage.
    """
    if previous_brand_purchases == 0:
        return 0.0 if current_brand_purchases == 0 else 100.0
    return ((current_brand_purchases - previous_brand_purchases) / previous_brand_purchases) * 100


# =============================================================================
# FUNNEL METRICS
# =============================================================================

def calculate_funnel_metrics(
    impressions: float,
    clicks: float,
    cart_adds: float,
    purchases: float
) -> Dict[str, float]:
    """
    Calculate full funnel conversion metrics.
    
    Returns dict with:
    - ctr: Click-through rate
    - cart_rate: Cart add rate
    - purchase_rate: Purchase rate from cart
    - overall_cvr: Overall conversion rate
    """
    return {
        'ctr': (clicks / impressions * 100) if impressions > 0 else 0,
        'cart_rate': (cart_adds / clicks * 100) if clicks > 0 else 0,
        'purchase_rate': (purchases / cart_adds * 100) if cart_adds > 0 else 0,
        'overall_cvr': (purchases / impressions * 100) if impressions > 0 else 0
    }


# =============================================================================
# SQP COMPARISON METRICS
# =============================================================================

def compare_sqp_periods(
    current_df: pd.DataFrame,
    previous_df: pd.DataFrame,
    view_type: str = 'brand'  # 'brand' or 'asin'
) -> pd.DataFrame:
    """
    Compare two SQP periods and calculate changes.
    
    Args:
        current_df: Current period SQP data
        previous_df: Previous period SQP data
        view_type: 'brand' for Brand View, 'asin' for ASIN View
    
    Returns:
        DataFrame with comparison metrics
    """
    # Determine column prefix
    prefix = 'Brand' if view_type == 'brand' else 'ASIN'
    
    # Merge on Search Query
    merged = current_df.merge(
        previous_df,
        on='Search Query',
        how='outer',
        suffixes=('_current', '_previous')
    )
    
    # Fill NaN with 0 for calculations
    merged = merged.fillna(0)
    
    # Calculate changes
    result = pd.DataFrame({
        'Search Query': merged['Search Query'],
        'Search Query Volume (Current)': merged.get(f'Search Query Volume_current', 0),
        'Search Query Volume (Previous)': merged.get(f'Search Query Volume_previous', 0),
        f'{prefix} Impressions (Current)': merged.get(f'Impressions: {prefix} Count_current', 0),
        f'{prefix} Impressions (Previous)': merged.get(f'Impressions: {prefix} Count_previous', 0),
        f'{prefix} Share % (Current)': merged.get(f'Impressions: {prefix} Share %_current', 0),
        f'{prefix} Share % (Previous)': merged.get(f'Impressions: {prefix} Share %_previous', 0),
        f'{prefix} Clicks (Current)': merged.get(f'Clicks: {prefix} Count_current', 0),
        f'{prefix} Clicks (Previous)': merged.get(f'Clicks: {prefix} Count_previous', 0),
        f'{prefix} Purchases (Current)': merged.get(f'Purchases: {prefix} Count_current', 0),
        f'{prefix} Purchases (Previous)': merged.get(f'Purchases: {prefix} Count_previous', 0),
    })
    
    # Calculate changes
    result['Volume Change %'] = result.apply(
        lambda r: calculate_brand_growth(
            r['Search Query Volume (Current)'],
            r['Search Query Volume (Previous)']
        ), axis=1
    )
    
    result['Share Change (pp)'] = (
        result[f'{prefix} Share % (Current)'] - result[f'{prefix} Share % (Previous)']
    )
    
    result['Purchases Change'] = (
        result[f'{prefix} Purchases (Current)'] - result[f'{prefix} Purchases (Previous)']
    )
    
    return result


# =============================================================================
# INVENTORY METRICS
# =============================================================================

def calculate_days_of_supply(
    available_units: int,
    units_sold_30_days: int
) -> float:
    """
    Calculate days of supply.
    
    DOS = (Available Units / Daily Sales Rate)
    """
    if units_sold_30_days == 0:
        return float('inf')
    
    daily_sales = units_sold_30_days / 30
    return available_units / daily_sales


def calculate_sell_through_rate(
    units_sold: int,
    units_available: int
) -> float:
    """
    Calculate sell-through rate.
    
    STR = (Units Sold / (Units Sold + Units Available)) × 100
    """
    total = units_sold + units_available
    if total == 0:
        return 0.0
    return (units_sold / total) * 100


def categorize_inventory_health(
    days_of_supply: float,
    age_0_90: int,
    age_90_plus: int
) -> str:
    """
    Categorize inventory health status.
    
    Returns: 'Healthy', 'Low Stock', 'Excess', 'Aging'
    """
    total = age_0_90 + age_90_plus
    
    if days_of_supply < 14:
        return 'Low Stock'
    elif days_of_supply > 180:
        return 'Excess'
    elif total > 0 and age_90_plus / total > 0.3:
        return 'Aging'
    else:
        return 'Healthy'


# =============================================================================
# PPC EFFICIENCY METRICS
# =============================================================================

def calculate_ppc_efficiency_score(
    acos: float,
    breakeven_acos: float,
    cvr: float,
    cpc: float,
    impressions: int
) -> float:
    """
    Calculate PPC efficiency score (0-100).
    
    Components:
    - ACoS vs Break-even (40%)
    - Conversion Rate (30%)
    - CPC efficiency (20%)
    - Impression volume (10%)
    """
    score = 0
    
    # ACoS component (40%)
    if breakeven_acos > 0:
        acos_ratio = acos / breakeven_acos
        if acos_ratio <= 0.5:
            score += 40
        elif acos_ratio <= 0.75:
            score += 35
        elif acos_ratio <= 1.0:
            score += 25
        elif acos_ratio <= 1.25:
            score += 15
        else:
            score += 5
    
    # CVR component (30%)
    if cvr >= 15:
        score += 30
    elif cvr >= 10:
        score += 25
    elif cvr >= 5:
        score += 15
    elif cvr >= 2:
        score += 10
    else:
        score += 5
    
    # CPC component (20%)
    if cpc <= 0.5:
        score += 20
    elif cpc <= 1.0:
        score += 15
    elif cpc <= 2.0:
        score += 10
    else:
        score += 5
    
    # Impressions component (10%)
    if impressions >= 10000:
        score += 10
    elif impressions >= 5000:
        score += 8
    elif impressions >= 1000:
        score += 5
    else:
        score += 2
    
    return score


def identify_wasted_spend(
    ppc_df: pd.DataFrame,
    min_spend: float = 10.0,
    min_clicks: int = 10,
    max_cvr: float = 0.5
) -> pd.DataFrame:
    """
    Identify wasted PPC spend (high spend, low conversions).
    
    Criteria:
    - Spend > min_spend
    - Clicks > min_clicks
    - Conversion Rate < max_cvr%
    """
    wasted = ppc_df[
        (ppc_df['Spend'] >= min_spend) &
        (ppc_df['Clicks'] >= min_clicks) &
        (ppc_df['Conversion Rate'] < max_cvr)
    ].copy()
    
    wasted = wasted.sort_values('Spend', ascending=False)
    
    return wasted


def identify_scaling_opportunities(
    ppc_df: pd.DataFrame,
    min_cvr: float = 5.0,
    max_acos: float = 30.0,
    min_impressions: int = 1000
) -> pd.DataFrame:
    """
    Identify PPC scaling opportunities (efficient performers).
    
    Criteria:
    - Conversion Rate >= min_cvr%
    - ACoS <= max_acos%
    - Impressions >= min_impressions
    """
    opportunities = ppc_df[
        (ppc_df['Conversion Rate'] >= min_cvr) &
        (ppc_df['ACOS'] <= max_acos) &
        (ppc_df['ACOS'] > 0) &
        (ppc_df['Impressions'] >= min_impressions)
    ].copy()
    
    # Sort by potential (high CVR, low ACoS)
    opportunities['Potential Score'] = opportunities['Conversion Rate'] / (opportunities['ACOS'] + 1)
    opportunities = opportunities.sort_values('Potential Score', ascending=False)
    
    return opportunities


# =============================================================================
# SCORING AGGREGATIONS
# =============================================================================

def calculate_brand_health_score(
    market_share: float,
    market_share_change: float,
    brand_growth: float,
    market_growth: float,
    avg_conversion_rate: float,
    inventory_health_pct: float,
    ppc_efficiency: float
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate overall Brand Health Score (0-100).
    
    Components:
    - Market Position (25%): Share and growth vs market
    - Conversion Health (25%): CVR performance
    - Inventory Health (20%): Stock levels
    - PPC Efficiency (30%): Ad performance
    
    Returns:
        Tuple of (total_score, component_scores)
    """
    components = {}
    
    # Market Position (25%)
    market_score = 0
    if market_share >= 10:
        market_score += 15
    elif market_share >= 5:
        market_score += 10
    elif market_share >= 1:
        market_score += 5
    
    if market_share_change > 0:
        market_score += min(5, market_share_change)
    
    if brand_growth > market_growth:
        market_score += 5
    
    components['Market Position'] = min(25, market_score)
    
    # Conversion Health (25%)
    cvr_score = 0
    if avg_conversion_rate >= 15:
        cvr_score = 25
    elif avg_conversion_rate >= 10:
        cvr_score = 20
    elif avg_conversion_rate >= 5:
        cvr_score = 15
    elif avg_conversion_rate >= 2:
        cvr_score = 10
    else:
        cvr_score = 5
    
    components['Conversion Health'] = cvr_score
    
    # Inventory Health (20%)
    inv_score = inventory_health_pct * 0.2
    components['Inventory Health'] = inv_score
    
    # PPC Efficiency (30%)
    ppc_score = ppc_efficiency * 0.3
    components['PPC Efficiency'] = ppc_score
    
    total_score = sum(components.values())
    
    return total_score, components


def get_health_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B+'
    elif score >= 60:
        return 'B'
    elif score >= 50:
        return 'C'
    elif score >= 40:
        return 'D'
    else:
        return 'F'
