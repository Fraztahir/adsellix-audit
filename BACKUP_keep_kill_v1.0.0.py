"""
AdSellix Audit Tool - Keep/Kill Matrix Module
Version: 1.0.0
Status: PROTECTED - Do not modify without backup

This module implements the ASIN portfolio classification:
- INVEST: High growth, high potential
- MAINTAIN: Stable performers
- OPTIMIZE: Needs improvement
- HARVEST: Milk for cash, reduce investment
- EXIT: Consider discontinuing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PortfolioAction(Enum):
    INVEST = "INVEST"
    MAINTAIN = "MAINTAIN"
    OPTIMIZE = "OPTIMIZE"
    HARVEST = "HARVEST"
    EXIT = "EXIT"


@dataclass
class ASINScore:
    """Scoring components for an ASIN."""
    asin: str
    title: str
    
    # Sales & Revenue
    sales_revenue: float
    sales_trend: float  # % change
    units_sold: int
    
    # Profitability
    gross_margin: float
    contribution_margin: float
    acos: float
    breakeven_acos: float
    
    # Market Position
    market_share: float
    market_share_change: float
    search_visibility: float
    
    # Conversion
    conversion_rate: float
    buy_box_percentage: float
    
    # Inventory
    days_of_supply: float
    inventory_health: str
    
    # Scores
    profitability_score: float
    growth_score: float
    market_score: float
    efficiency_score: float
    total_score: float
    
    # Classification
    action: PortfolioAction
    rationale: str


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

def calculate_profitability_score(
    gross_margin: float,
    acos: float,
    breakeven_acos: float,
    contribution_margin: float
) -> float:
    """
    Calculate profitability score (0-25).
    
    Components:
    - Gross margin strength
    - ACoS vs breakeven
    - Contribution margin
    """
    score = 0
    
    # Gross margin component (0-10)
    if gross_margin >= 50:
        score += 10
    elif gross_margin >= 40:
        score += 8
    elif gross_margin >= 30:
        score += 6
    elif gross_margin >= 20:
        score += 4
    elif gross_margin >= 10:
        score += 2
    
    # ACoS component (0-10)
    if breakeven_acos > 0:
        acos_ratio = acos / breakeven_acos if acos > 0 else 0
        if acos_ratio == 0:  # No ad spend
            score += 5
        elif acos_ratio <= 0.5:
            score += 10
        elif acos_ratio <= 0.75:
            score += 8
        elif acos_ratio <= 1.0:
            score += 6
        elif acos_ratio <= 1.25:
            score += 3
        else:
            score += 0
    
    # Contribution margin component (0-5)
    if contribution_margin >= 20:
        score += 5
    elif contribution_margin >= 10:
        score += 4
    elif contribution_margin >= 5:
        score += 3
    elif contribution_margin >= 0:
        score += 2
    else:
        score += 0
    
    return min(25, score)


def calculate_growth_score(
    sales_trend: float,
    units_trend: float,
    market_growth: float
) -> float:
    """
    Calculate growth score (0-25).
    
    Components:
    - Absolute growth rate
    - Growth vs market
    """
    score = 0
    
    # Absolute growth (0-15)
    if sales_trend >= 100:
        score += 15
    elif sales_trend >= 50:
        score += 12
    elif sales_trend >= 25:
        score += 10
    elif sales_trend >= 10:
        score += 8
    elif sales_trend >= 0:
        score += 5
    elif sales_trend >= -10:
        score += 3
    else:
        score += 0
    
    # Growth vs market (0-10)
    relative_growth = sales_trend - market_growth
    if relative_growth >= 50:
        score += 10
    elif relative_growth >= 25:
        score += 8
    elif relative_growth >= 10:
        score += 6
    elif relative_growth >= 0:
        score += 4
    elif relative_growth >= -10:
        score += 2
    else:
        score += 0
    
    return min(25, score)


def calculate_market_score(
    market_share: float,
    market_share_change: float,
    search_visibility: float
) -> float:
    """
    Calculate market position score (0-25).
    
    Components:
    - Current market share
    - Share change trend
    - Search visibility
    """
    score = 0
    
    # Market share (0-12)
    if market_share >= 20:
        score += 12
    elif market_share >= 10:
        score += 10
    elif market_share >= 5:
        score += 8
    elif market_share >= 2:
        score += 5
    elif market_share >= 1:
        score += 3
    else:
        score += 1
    
    # Share change (0-8)
    if market_share_change >= 5:
        score += 8
    elif market_share_change >= 2:
        score += 6
    elif market_share_change >= 0:
        score += 4
    elif market_share_change >= -2:
        score += 2
    else:
        score += 0
    
    # Search visibility (0-5)
    if search_visibility >= 10:
        score += 5
    elif search_visibility >= 5:
        score += 4
    elif search_visibility >= 2:
        score += 3
    elif search_visibility >= 1:
        score += 2
    else:
        score += 1
    
    return min(25, score)


def calculate_efficiency_score(
    conversion_rate: float,
    buy_box_percentage: float,
    days_of_supply: float,
    inventory_health: str
) -> float:
    """
    Calculate operational efficiency score (0-25).
    
    Components:
    - Conversion rate
    - Buy box ownership
    - Inventory efficiency
    """
    score = 0
    
    # Conversion rate (0-10)
    if conversion_rate >= 20:
        score += 10
    elif conversion_rate >= 15:
        score += 8
    elif conversion_rate >= 10:
        score += 6
    elif conversion_rate >= 5:
        score += 4
    elif conversion_rate >= 2:
        score += 2
    else:
        score += 1
    
    # Buy box (0-8)
    if buy_box_percentage >= 95:
        score += 8
    elif buy_box_percentage >= 90:
        score += 7
    elif buy_box_percentage >= 80:
        score += 5
    elif buy_box_percentage >= 70:
        score += 3
    else:
        score += 1
    
    # Inventory (0-7)
    if inventory_health == 'Healthy':
        score += 7
    elif inventory_health == 'Low Stock':
        score += 3  # Risk but not bad
    elif inventory_health == 'Excess':
        score += 2
    elif inventory_health == 'Aging':
        score += 1
    else:
        score += 4  # Unknown
    
    return min(25, score)


# =============================================================================
# CLASSIFICATION
# =============================================================================

def classify_asin(total_score: float, growth_score: float, profitability_score: float) -> Tuple[PortfolioAction, str]:
    """
    Classify ASIN into portfolio action based on scores.
    
    Returns (action, rationale)
    """
    # High performers
    if total_score >= 80:
        return PortfolioAction.INVEST, "Top performer - maximize investment"
    
    if total_score >= 65:
        if growth_score >= 18:
            return PortfolioAction.INVEST, "Strong growth trajectory - increase investment"
        else:
            return PortfolioAction.MAINTAIN, "Solid performer - maintain current strategy"
    
    if total_score >= 50:
        if profitability_score >= 18:
            return PortfolioAction.HARVEST, "Profitable but limited growth - optimize for cash"
        elif growth_score >= 15:
            return PortfolioAction.OPTIMIZE, "Growth potential but needs optimization"
        else:
            return PortfolioAction.OPTIMIZE, "Needs improvement across metrics"
    
    if total_score >= 35:
        if profitability_score >= 12:
            return PortfolioAction.HARVEST, "Marginally profitable - reduce investment, harvest"
        else:
            return PortfolioAction.EXIT, "Underperforming - consider discontinuation"
    
    return PortfolioAction.EXIT, "Poor performance - recommend exit"


# =============================================================================
# MATRIX BUILDER
# =============================================================================

def build_keep_kill_matrix(
    business_report_df: pd.DataFrame,
    sqp_brand_current: pd.DataFrame,
    sqp_brand_previous: pd.DataFrame,
    ppc_summary: Dict,
    inventory_df: pd.DataFrame,
    cogs_df: pd.DataFrame,
    fba_fees_df: pd.DataFrame,
    market_growth: float = 0
) -> List[ASINScore]:
    """
    Build the complete Keep/Kill Matrix for all ASINs.
    
    Returns list of ASINScore objects for each ASIN.
    """
    results = []
    
    # Build lookup tables
    cogs_lookup = {}
    if cogs_df is not None and not cogs_df.empty:
        for _, row in cogs_df.iterrows():
            asin = row.get('ASIN')
            if asin:
                cogs_lookup[asin] = row.get('Cost', 0)
    
    fees_lookup = {}
    if fba_fees_df is not None and not fba_fees_df.empty:
        for _, row in fba_fees_df.iterrows():
            asin = row.get('asin')
            if asin:
                fees_lookup[asin] = {
                    'referral': row.get('estimated-referral-fee-per-unit', 0),
                    'fba': row.get('expected-domestic-fulfilment-fee-per-unit', 0),
                    'price': row.get('your-price', 0)
                }
    
    inventory_lookup = {}
    if inventory_df is not None and not inventory_df.empty:
        for _, row in inventory_df.iterrows():
            asin = row.get('asin')
            if asin:
                inventory_lookup[asin] = {
                    'available': row.get('available', 0),
                    'days_of_supply': row.get('days-of-supply', 0),
                    'health': row.get('fba-inventory-level-health-status', 'Unknown')
                }
    
    # Calculate SQP metrics by aggregating at ASIN level
    # (Note: Brand View gives brand-level, we'll use Business Report for ASIN level)
    
    # Process each ASIN from Business Report
    for _, row in business_report_df.iterrows():
        asin = row.get('(Child) ASIN')
        if not asin:
            continue
        
        title = row.get('Title', '')[:50] + '...' if row.get('Title') and len(row.get('Title', '')) > 50 else row.get('Title', '')
        
        # Sales metrics
        sales_revenue = row.get('Ordered Product Sales', 0)
        units_sold = int(row.get('Units Ordered', 0))
        
        # Conversion
        conversion_rate = row.get('Unit Session Percentage', 0)
        buy_box_pct = row.get('Featured Offer (Buy Box) Percentage', 0)
        
        # Get costs and fees
        cogs = cogs_lookup.get(asin, 0)
        fees = fees_lookup.get(asin, {'referral': 0, 'fba': 0, 'price': 0})
        price = fees.get('price', 0) or (sales_revenue / units_sold if units_sold > 0 else 0)
        
        # Calculate margins
        referral_fee = fees.get('referral', 0)
        fba_fee = fees.get('fba', 0)
        gross_margin_pct = 0
        if price > 0:
            gross_margin = price - cogs - referral_fee - fba_fee
            gross_margin_pct = (gross_margin / price) * 100
        
        breakeven_acos = gross_margin_pct  # ACoS that would eat all margin
        
        # Get inventory
        inv = inventory_lookup.get(asin, {'available': 0, 'days_of_supply': 0, 'health': 'Unknown'})
        
        # Calculate scores
        profitability_score = calculate_profitability_score(
            gross_margin_pct,
            0,  # ACoS - would need to link to PPC data
            breakeven_acos,
            gross_margin_pct - 10  # Rough CM estimate
        )
        
        growth_score = calculate_growth_score(
            0,  # Would need previous period data
            0,
            market_growth
        )
        
        market_score = calculate_market_score(
            0,  # Would need SQP data linked
            0,
            0
        )
        
        efficiency_score = calculate_efficiency_score(
            conversion_rate,
            buy_box_pct,
            inv['days_of_supply'],
            inv['health']
        )
        
        total_score = profitability_score + growth_score + market_score + efficiency_score
        
        # Classify
        action, rationale = classify_asin(total_score, growth_score, profitability_score)
        
        asin_score = ASINScore(
            asin=asin,
            title=title,
            sales_revenue=sales_revenue,
            sales_trend=0,  # Need previous period
            units_sold=units_sold,
            gross_margin=gross_margin_pct,
            contribution_margin=gross_margin_pct - 10,  # Estimate
            acos=0,
            breakeven_acos=breakeven_acos,
            market_share=0,
            market_share_change=0,
            search_visibility=0,
            conversion_rate=conversion_rate,
            buy_box_percentage=buy_box_pct,
            days_of_supply=inv['days_of_supply'],
            inventory_health=inv['health'],
            profitability_score=profitability_score,
            growth_score=growth_score,
            market_score=market_score,
            efficiency_score=efficiency_score,
            total_score=total_score,
            action=action,
            rationale=rationale
        )
        
        results.append(asin_score)
    
    # Sort by total score descending
    results.sort(key=lambda x: x.total_score, reverse=True)
    
    return results


def matrix_to_dataframe(scores: List[ASINScore]) -> pd.DataFrame:
    """Convert list of ASINScore to DataFrame for display."""
    data = []
    for s in scores:
        data.append({
            'ASIN': s.asin,
            'Title': s.title,
            'Revenue': s.sales_revenue,
            'Units': s.units_sold,
            'Gross Margin %': round(s.gross_margin, 1),
            'CVR %': round(s.conversion_rate, 1),
            'Buy Box %': round(s.buy_box_percentage, 1),
            'Days of Supply': round(s.days_of_supply, 0),
            'Inv. Health': s.inventory_health,
            'Profit Score': round(s.profitability_score, 1),
            'Growth Score': round(s.growth_score, 1),
            'Market Score': round(s.market_score, 1),
            'Efficiency Score': round(s.efficiency_score, 1),
            'Total Score': round(s.total_score, 1),
            'Action': s.action.value,
            'Rationale': s.rationale
        })
    
    return pd.DataFrame(data)


def get_action_summary(scores: List[ASINScore]) -> Dict[str, int]:
    """Get count of ASINs by action category."""
    summary = {
        'INVEST': 0,
        'MAINTAIN': 0,
        'OPTIMIZE': 0,
        'HARVEST': 0,
        'EXIT': 0
    }
    
    for s in scores:
        summary[s.action.value] += 1
    
    return summary
