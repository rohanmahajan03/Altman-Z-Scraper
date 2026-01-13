"""Utility functions for CIK lookup and helper functions."""

import requests
from typing import Optional, Dict


def get_cik_from_ticker(ticker: str) -> Optional[str]:
    """
    Get CIK (Central Index Key) from ticker symbol.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        CIK as string (zero-padded to 10 digits) or None if not found
    """
    ticker = ticker.upper().strip()
    
    try:
        # SEC company tickers JSON endpoint
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Altman Z-Score API (contact@example.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Search for ticker in the data
        for entry in data.values():
            if entry.get('ticker', '').upper() == ticker:
                cik = str(entry.get('cik_str', ''))
                # Zero-pad CIK to 10 digits
                return cik.zfill(10)
        
        return None
    except Exception as e:
        print(f"Error fetching CIK for ticker {ticker}: {e}")
        return None


def get_cik_from_name(company_name: str) -> Optional[str]:
    """
    Get CIK from company name (approximate match).
    
    Args:
        company_name: Company name (e.g., 'Apple Inc.')
        
    Returns:
        CIK as string (zero-padded to 10 digits) or None if not found
    """
    company_name = company_name.strip()
    
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Altman Z-Score API (contact@example.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Normalize company name for comparison
        company_name_lower = company_name.lower()
        
        # Search for company name in the data
        for entry in data.values():
            title = entry.get('title', '').lower()
            # Check if company name is in title or vice versa
            if company_name_lower in title or title in company_name_lower:
                cik = str(entry.get('cik_str', ''))
                return cik.zfill(10)
        
        return None
    except Exception as e:
        print(f"Error fetching CIK for company name {company_name}: {e}")
        return None


def get_cik(company_identifier: str) -> Optional[str]:
    """
    Get CIK from either ticker or company name.
    
    Args:
        company_identifier: Ticker symbol or company name
        
    Returns:
        CIK as string (zero-padded to 10 digits) or None if not found
    """
    # First try as ticker (usually shorter, no spaces, uppercase)
    if len(company_identifier) <= 5 and company_identifier.replace('.', '').replace('-', '').isalnum():
        cik = get_cik_from_ticker(company_identifier)
        if cik:
            return cik
    
    # Try as company name
    cik = get_cik_from_name(company_identifier)
    if cik:
        return cik
    
    # Fallback: try as ticker even if it looks like a name
    return get_cik_from_ticker(company_identifier)


def get_cik_and_ticker(company_identifier: str) -> Optional[Dict[str, str]]:
    """
    Get both CIK and ticker from either ticker or company name.
    
    Args:
        company_identifier: Ticker symbol or company name
        
    Returns:
        Dictionary with 'cik' and 'ticker' keys, or None if not found
    """
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Altman Z-Score API (contact@example.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        company_identifier_upper = company_identifier.upper().strip()
        company_identifier_lower = company_identifier.lower().strip()
        
        # Search for ticker or company name
        for entry in data.values():
            ticker = entry.get('ticker', '').upper()
            title = entry.get('title', '').lower()
            
            # Check if it matches ticker
            if ticker == company_identifier_upper:
                return {
                    'cik': str(entry.get('cik_str', '')).zfill(10),
                    'ticker': ticker
                }
            
            # Check if it matches company name
            if (company_identifier_lower in title or title in company_identifier_lower):
                return {
                    'cik': str(entry.get('cik_str', '')).zfill(10),
                    'ticker': ticker
                }
        
        return None
    except Exception as e:
        print(f"Error fetching CIK and ticker for {company_identifier}: {e}")
        return None


def zero_pad_cik(cik: str) -> str:
    """
    Zero-pad CIK to 10 digits.
    
    Args:
        cik: CIK as string
        
    Returns:
        Zero-padded CIK string
    """
    return str(cik).zfill(10)

