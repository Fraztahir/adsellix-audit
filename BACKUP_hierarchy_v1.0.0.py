"""
AdSellix Audit Tool - Hierarchy & ASIN Management
Version: 1.0.0
Status: PROTECTED - Do not modify without backup

This module handles:
- Parent-Child ASIN hierarchy from CLR
- Hero ASIN auto-detection from Business Report
- ASIN grouping and mapping
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ASINInfo:
    """Data class for ASIN information."""
    asin: str
    sku: str
    title: str
    brand: str
    parentage_level: str  # 'Parent' or 'Child'
    parent_sku: Optional[str]
    variation_theme: Optional[str]
    colour: Optional[str]
    size: Optional[str]
    is_hero: bool = False


@dataclass
class ParentGroup:
    """Data class for Parent ASIN group."""
    parent_sku: str
    parent_asin: Optional[str]
    parent_title: str
    variation_theme: str
    children: List[ASINInfo]
    hero_asins: List[str]
    total_sessions: float = 0
    total_sales: float = 0
    total_units: int = 0


# =============================================================================
# HIERARCHY PARSER
# =============================================================================

def parse_clr_hierarchy(clr_df: pd.DataFrame) -> Dict[str, ParentGroup]:
    """
    Parse Category Listing Report to extract parent-child hierarchy.
    
    Args:
        clr_df: DataFrame from load_category_listing_report()
    
    Returns:
        Dict mapping parent SKU to ParentGroup objects
    """
    hierarchy = {}
    
    # First pass: identify all parents
    parents = clr_df[clr_df['Parentage Level'] == 'Parent'].copy()
    
    for _, parent_row in parents.iterrows():
        parent_sku = parent_row['SKU']
        
        parent_group = ParentGroup(
            parent_sku=parent_sku,
            parent_asin=parent_row.get('Product Id'),
            parent_title=parent_row.get('Item Name', ''),
            variation_theme=parent_row.get('Variation Theme', ''),
            children=[],
            hero_asins=[]
        )
        
        hierarchy[parent_sku] = parent_group
    
    # Second pass: assign children to parents
    children = clr_df[clr_df['Parentage Level'] == 'Child'].copy()
    
    for _, child_row in children.iterrows():
        parent_sku = child_row.get('Parent SKU')
        
        if parent_sku and parent_sku in hierarchy:
            child_info = ASINInfo(
                asin=child_row.get('Product Id', ''),
                sku=child_row.get('SKU', ''),
                title=child_row.get('Item Name', ''),
                brand=child_row.get('Brand Name', ''),
                parentage_level='Child',
                parent_sku=parent_sku,
                variation_theme=child_row.get('Variation Theme'),
                colour=child_row.get('Colour'),
                size=child_row.get('Size')
            )
            
            hierarchy[parent_sku].children.append(child_info)
    
    # Handle standalone ASINs (no parent)
    standalone = clr_df[
        (clr_df['Parentage Level'].isna() | (clr_df['Parentage Level'] == '')) &
        (clr_df['Parent SKU'].isna() | (clr_df['Parent SKU'] == ''))
    ].copy()
    
    for _, row in standalone.iterrows():
        sku = row['SKU']
        if sku and sku not in hierarchy:
            # Create as its own parent
            standalone_info = ASINInfo(
                asin=row.get('Product Id', ''),
                sku=sku,
                title=row.get('Item Name', ''),
                brand=row.get('Brand Name', ''),
                parentage_level='Standalone',
                parent_sku=None,
                variation_theme=None,
                colour=row.get('Colour'),
                size=row.get('Size')
            )
            
            hierarchy[sku] = ParentGroup(
                parent_sku=sku,
                parent_asin=row.get('Product Id'),
                parent_title=row.get('Item Name', ''),
                variation_theme='Standalone',
                children=[standalone_info],
                hero_asins=[]
            )
    
    return hierarchy


# =============================================================================
# HERO ASIN DETECTION
# =============================================================================

def detect_hero_asins(
    hierarchy: Dict[str, ParentGroup],
    business_report_df: pd.DataFrame,
    top_n: int = 3
) -> Dict[str, ParentGroup]:
    """
    Auto-detect Hero ASINs based on Business Report sales data.
    
    Hero ASINs are the top N children by Ordered Product Sales within each parent.
    
    Args:
        hierarchy: Dict from parse_clr_hierarchy()
        business_report_df: DataFrame from load_business_report()
        top_n: Number of hero ASINs to select per parent (default 3)
    
    Returns:
        Updated hierarchy with hero_asins populated
    """
    # Create ASIN to sales mapping from business report
    asin_sales = {}
    asin_sessions = {}
    asin_units = {}
    
    for _, row in business_report_df.iterrows():
        child_asin = row.get('(Child) ASIN')
        if child_asin:
            asin_sales[child_asin] = row.get('Ordered Product Sales', 0)
            asin_sessions[child_asin] = row.get('Sessions - Total', 0)
            asin_units[child_asin] = row.get('Units Ordered', 0)
    
    # For each parent, find top N children by sales
    for parent_sku, parent_group in hierarchy.items():
        children_with_sales = []
        
        for child in parent_group.children:
            sales = asin_sales.get(child.asin, 0)
            sessions = asin_sessions.get(child.asin, 0)
            units = asin_units.get(child.asin, 0)
            
            children_with_sales.append({
                'asin': child.asin,
                'sales': sales,
                'sessions': sessions,
                'units': units
            })
            
            # Update parent totals
            parent_group.total_sales += sales
            parent_group.total_sessions += sessions
            parent_group.total_units += units
        
        # Sort by sales descending
        children_with_sales.sort(key=lambda x: x['sales'], reverse=True)
        
        # Select top N as heroes
        hero_asins = [c['asin'] for c in children_with_sales[:top_n] if c['asin']]
        parent_group.hero_asins = hero_asins
        
        # Update is_hero flag on children
        for child in parent_group.children:
            if child.asin in hero_asins:
                child.is_hero = True
    
    return hierarchy


# =============================================================================
# ASIN LOOKUP UTILITIES
# =============================================================================

def get_all_asins(hierarchy: Dict[str, ParentGroup]) -> List[str]:
    """Get flat list of all child ASINs."""
    asins = []
    for parent_group in hierarchy.values():
        for child in parent_group.children:
            if child.asin:
                asins.append(child.asin)
    return asins


def get_all_hero_asins(hierarchy: Dict[str, ParentGroup]) -> List[str]:
    """Get flat list of all hero ASINs."""
    hero_asins = []
    for parent_group in hierarchy.values():
        hero_asins.extend(parent_group.hero_asins)
    return hero_asins


def get_asin_parent(asin: str, hierarchy: Dict[str, ParentGroup]) -> Optional[str]:
    """Get parent SKU for a given ASIN."""
    for parent_sku, parent_group in hierarchy.items():
        for child in parent_group.children:
            if child.asin == asin:
                return parent_sku
    return None


def get_parent_asins(hierarchy: Dict[str, ParentGroup]) -> List[str]:
    """Get list of parent ASINs."""
    return [pg.parent_asin for pg in hierarchy.values() if pg.parent_asin]


def build_asin_to_sku_map(hierarchy: Dict[str, ParentGroup]) -> Dict[str, str]:
    """Build mapping from ASIN to SKU."""
    mapping = {}
    for parent_group in hierarchy.values():
        for child in parent_group.children:
            if child.asin and child.sku:
                mapping[child.asin] = child.sku
    return mapping


def build_sku_to_asin_map(hierarchy: Dict[str, ParentGroup]) -> Dict[str, str]:
    """Build mapping from SKU to ASIN."""
    mapping = {}
    for parent_group in hierarchy.values():
        for child in parent_group.children:
            if child.sku and child.asin:
                mapping[child.sku] = child.asin
    return mapping


# =============================================================================
# HIERARCHY SUMMARY
# =============================================================================

def get_hierarchy_summary(hierarchy: Dict[str, ParentGroup]) -> pd.DataFrame:
    """
    Generate summary DataFrame of hierarchy.
    
    Returns:
        DataFrame with parent-level summary
    """
    summary_data = []
    
    for parent_sku, parent_group in hierarchy.items():
        summary_data.append({
            'Parent SKU': parent_sku,
            'Parent ASIN': parent_group.parent_asin,
            'Parent Title': parent_group.parent_title[:50] + '...' if len(parent_group.parent_title) > 50 else parent_group.parent_title,
            'Variation Theme': parent_group.variation_theme,
            'Child Count': len(parent_group.children),
            'Hero ASINs': ', '.join(parent_group.hero_asins),
            'Total Sessions': parent_group.total_sessions,
            'Total Sales': parent_group.total_sales,
            'Total Units': parent_group.total_units
        })
    
    df = pd.DataFrame(summary_data)
    df = df.sort_values('Total Sales', ascending=False)
    
    return df


def get_children_summary(hierarchy: Dict[str, ParentGroup]) -> pd.DataFrame:
    """
    Generate detailed DataFrame of all children.
    
    Returns:
        DataFrame with child-level details
    """
    children_data = []
    
    for parent_sku, parent_group in hierarchy.items():
        for child in parent_group.children:
            children_data.append({
                'Parent SKU': parent_sku,
                'Child ASIN': child.asin,
                'Child SKU': child.sku,
                'Title': child.title[:50] + '...' if child.title and len(child.title) > 50 else child.title,
                'Colour': child.colour,
                'Size': child.size,
                'Is Hero': child.is_hero
            })
    
    return pd.DataFrame(children_data)


# =============================================================================
# SIMPLE HIERARCHY BUILDER (Without CLR)
# =============================================================================

def build_hierarchy_from_business_report(business_report_df: pd.DataFrame) -> Dict[str, ParentGroup]:
    """
    Build hierarchy directly from Business Report when CLR is not available.
    Uses (Parent) ASIN and (Child) ASIN columns.
    
    Args:
        business_report_df: DataFrame from load_business_report()
    
    Returns:
        Dict mapping parent ASIN to ParentGroup objects
    """
    hierarchy = {}
    
    for _, row in business_report_df.iterrows():
        parent_asin = row.get('(Parent) ASIN', '')
        child_asin = row.get('(Child) ASIN', '')
        
        if not parent_asin:
            continue
        
        # Create or update parent group
        if parent_asin not in hierarchy:
            hierarchy[parent_asin] = ParentGroup(
                parent_sku=parent_asin,  # Use ASIN as SKU when CLR not available
                parent_asin=parent_asin,
                parent_title=row.get('Title', '')[:50] if row.get('Title') else '',
                variation_theme='Unknown',
                children=[],
                hero_asins=[]
            )
        
        # Add child
        child_info = ASINInfo(
            asin=child_asin,
            sku=row.get('SKU', ''),
            title=row.get('Title', ''),
            brand='',
            parentage_level='Child',
            parent_sku=parent_asin,
            variation_theme=None,
            colour=None,
            size=None
        )
        
        # Check if child already exists
        existing_asins = [c.asin for c in hierarchy[parent_asin].children]
        if child_asin not in existing_asins:
            hierarchy[parent_asin].children.append(child_info)
        
        # Update totals
        hierarchy[parent_asin].total_sales += row.get('Ordered Product Sales', 0)
        hierarchy[parent_asin].total_sessions += row.get('Sessions - Total', 0)
        hierarchy[parent_asin].total_units += row.get('Units Ordered', 0)
    
    return hierarchy
