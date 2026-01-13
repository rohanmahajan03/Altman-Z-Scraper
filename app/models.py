"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class ZScoreRequest(BaseModel):
    """Request model for Z-Score calculation."""
    company: str = Field(..., description="Company name or ticker symbol")


class ZScoreResponse(BaseModel):
    """Response model for Z-Score calculation."""
    company: str
    ticker: Optional[str] = None
    z_score: float = Field(..., description="Calculated Altman Z-Score")
    zone: str = Field(..., description="Financial health zone (Safe/Grey/Distress)")
    
    # Individual ratios
    x1: float = Field(..., description="Working Capital / Total Assets")
    x2: float = Field(..., description="Retained Earnings / Total Assets")
    x3: float = Field(..., description="Operating Income / Total Assets")
    x4: float = Field(..., description="Market Value of Equity / Total Liabilities")
    x5: float = Field(..., description="Sales / Total Assets")
    
    # Raw financial data
    working_capital: float
    total_assets: float
    retained_earnings: float
    operating_income: float
    market_value_equity: float
    total_liabilities: float
    sales: float
    
    # Data source information
    filing_date: Optional[str] = None
    stock_price: Optional[float] = None
    shares_outstanding: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None

