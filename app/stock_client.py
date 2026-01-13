"""Yahoo Finance client for fetching stock prices and market data."""

import yfinance as yf
from typing import Optional, Dict


def get_stock_data(ticker: str) -> Optional[Dict[str, float]]:
    """
    Get current stock price and shares outstanding for a ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        Dictionary with 'price', 'shares_outstanding', and 'market_value_equity'
        or None if data unavailable
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        # Get current price
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if price is None:
            # Try to get from recent data
            hist = ticker_obj.history(period="1d")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
        
        # Get shares outstanding
        shares_outstanding = info.get('sharesOutstanding') or info.get('impliedSharesOutstanding')
        
        if price is None or shares_outstanding is None:
            return None
        
        market_value_equity = float(price) * float(shares_outstanding)
        
        return {
            'price': float(price),
            'shares_outstanding': float(shares_outstanding),
            'market_value_equity': market_value_equity
        }
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None

