"""Altman Z-Score calculation logic."""

from typing import Dict, Optional
from enum import Enum


class ZoneType(str, Enum):
    """Z-Score interpretation zones."""
    SAFE = "Safe Zone"
    GREY = "Grey Zone"
    DISTRESS = "Distress Zone"


def calculate_altman_z_score(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    operating_income: float,
    market_value_equity: float,
    total_liabilities: float,
    sales: float
) -> Dict[str, float]:
    """
    Calculate Altman Z-Score for manufacturing companies.
    
    Formula: Z = 1.2×X₁ + 1.4×X₂ + 3.3×X₃ + 0.6×X₄ + 1.0×X₅
    
    Where:
    - X₁ = Working Capital / Total Assets
    - X₂ = Retained Earnings / Total Assets
    - X₃ = Operating Income / Total Assets
    - X₄ = Market Value of Equity / Total Liabilities
    - X₅ = Sales / Total Assets
    
    Args:
        working_capital: Current Assets - Current Liabilities
        total_assets: Total assets
        retained_earnings: Retained earnings
        operating_income: Operating income (used as EBIT)
        market_value_equity: Market value of equity (price × shares outstanding)
        total_liabilities: Total liabilities
        sales: Total sales/revenue
        
    Returns:
        Dictionary with Z-Score, individual ratios, and interpretation
    """
    # Calculate individual ratios
    x1 = working_capital / total_assets if total_assets != 0 else 0.0
    x2 = retained_earnings / total_assets if total_assets != 0 else 0.0
    x3 = operating_income / total_assets if total_assets != 0 else 0.0
    x4 = market_value_equity / total_liabilities if total_liabilities != 0 else 0.0
    x5 = sales / total_assets if total_assets != 0 else 0.0
    
    # Calculate Z-Score
    z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)
    
    # Determine zone
    if z_score > 2.99:
        zone = ZoneType.SAFE
    elif z_score > 1.81:
        zone = ZoneType.GREY
    else:
        zone = ZoneType.DISTRESS
    
    return {
        'z_score': round(z_score, 4),
        'x1': round(x1, 6),
        'x2': round(x2, 6),
        'x3': round(x3, 6),
        'x4': round(x4, 6),
        'x5': round(x5, 6),
        'zone': zone.value,
        'working_capital': working_capital,
        'total_assets': total_assets,
        'retained_earnings': retained_earnings,
        'operating_income': operating_income,
        'market_value_equity': market_value_equity,
        'total_liabilities': total_liabilities,
        'sales': sales
    }

