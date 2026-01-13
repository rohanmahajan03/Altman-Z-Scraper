"""SEC EDGAR API client for fetching 10-Q filings and extracting financial data."""

import requests
import re
from typing import Optional, Dict
from bs4 import BeautifulSoup
import time


SEC_BASE_URL = "https://data.sec.gov"
USER_AGENT = "Altman Z-Score API contact@example.com"


def get_sec_headers() -> Dict[str, str]:
    """Get headers required for SEC API requests."""
    return {
        'User-Agent': USER_AGENT,
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'data.sec.gov'
    }


def get_latest_10q_filing(cik: str) -> Optional[Dict]:
    """
    Get the most recent 10-Q filing for a company.
    
    Args:
        cik: Company CIK (zero-padded to 10 digits)
        
    Returns:
        Dictionary with filing information or None if not found
    """
    try:
        cik = cik.zfill(10)
        url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
        
        response = requests.get(url, headers=get_sec_headers(), timeout=10)
        response.raise_for_status()
        
        data = response.json()
        filings = data.get('filings', {}).get('recent', {})
        
        # Find most recent 10-Q
        forms = filings.get('form', [])
        filing_dates = filings.get('filingDate', [])
        accession_numbers = filings.get('accessionNumber', [])
        
        # Search backwards from most recent filings
        for i in range(len(forms) - 1, -1, -1):
            if forms[i] == '10-Q':
                return {
                    'form': forms[i],
                    'filingDate': filing_dates[i],
                    'accessionNumber': accession_numbers[i].replace('-', ''),
                    'cik': cik
                }
        
        return None
    except Exception as e:
        print(f"Error fetching 10-Q filing for CIK {cik}: {e}")
        return None


def get_filing_document_url(cik: str, accession_number: str) -> Optional[str]:
    """
    Get the URL for the main filing document (usually the HTML or XBRL instance).
    
    Args:
        cik: Company CIK
        accession_number: Filing accession number
        
    Returns:
        URL to the filing document or None
    """
    try:
        cik = cik.zfill(10)
        # Try to get the XBRL instance document first
        url = f"{SEC_BASE_URL}/files/company-tickers.json"
        # Actually, we need to construct the filing URL
        # Format: https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/
        
        # Remove dashes from accession number for URL
        acc_no_clean = accession_number.replace('-', '')
        
        # Try XBRL instance document
        xbrl_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_clean}/{accession_number}-xbrl.zip"
        
        # For now, we'll use the HTML filing
        # The actual filing HTML is usually at: {accession_number}.txt or {accession_number}.htm
        html_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no_clean}/{accession_number}.txt"
        
        return html_url
    except Exception as e:
        print(f"Error constructing filing URL: {e}")
        return None


def parse_number(value_str: str) -> Optional[float]:
    """
    Parse a number string that may contain commas, parentheses (for negatives), or be in millions.
    
    Args:
        value_str: String representation of number
        
    Returns:
        Parsed float value or None
    """
    try:
        # Remove commas and dollar signs
        cleaned = value_str.replace(',', '').replace('$', '').strip()
        
        # Check for parentheses (negative numbers)
        is_negative = cleaned.startswith('(') and cleaned.endswith(')')
        if is_negative:
            cleaned = cleaned[1:-1]
        
        # Parse the number
        value = float(cleaned)
        if is_negative:
            value = -value
        
        return value
    except (ValueError, AttributeError):
        return None


def extract_financial_data_from_html(html_content: str) -> Optional[Dict[str, float]]:
    """
    Extract financial data from HTML 10-Q filing.
    
    This parser looks for financial statement tables and extracts values.
    
    Args:
        html_content: HTML content of the 10-Q filing
        
    Returns:
        Dictionary with financial metrics or None if extraction fails
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        text_lower = text.lower()
        
        financial_data = {}
        
        # Enhanced patterns with better matching
        # Look for patterns in tables and text
        patterns = {
            'current_assets': [
                r'total\s+current\s+assets[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'current\s+assets[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
            'current_liabilities': [
                r'total\s+current\s+liabilities[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'current\s+liabilities[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
            'total_assets': [
                r'total\s+assets[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
            'retained_earnings': [
                r'retained\s+earnings[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'accumulated\s+retained\s+earnings[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
            'operating_income': [
                r'operating\s+income[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'income\s+from\s+operations[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
            'total_liabilities': [
                r'total\s+liabilities[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
            'sales': [
                r'net\s+sales[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'total\s+revenue[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'net\s+revenue[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
                r'total\s+net\s+revenue[^\d]*[\$]?\s*([\d,\(\)]+\.?\d*)\s*(?:million|thousand|billion)?',
            ],
        }
        
        # Extract values using patterns
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                values_found = []
                for match in matches:
                    value_str = match.group(1)
                    parsed_value = parse_number(value_str)
                    if parsed_value is not None:
                        # Check for scale indicators
                        match_text = match.group(0).lower()
                        if 'million' in match_text:
                            parsed_value *= 1_000_000
                        elif 'thousand' in match_text:
                            parsed_value *= 1_000
                        elif 'billion' in match_text:
                            parsed_value *= 1_000_000_000
                        values_found.append(abs(parsed_value))  # Use absolute value
                
                if values_found:
                    # Take the largest value (usually the most recent period)
                    financial_data[key] = max(values_found)
                    break
        
        # Validate we have all required fields
        required_fields = ['current_assets', 'current_liabilities', 'total_assets', 
                          'retained_earnings', 'operating_income', 'total_liabilities', 'sales']
        
        if all(field in financial_data for field in required_fields):
            # Calculate working capital
            financial_data['working_capital'] = (
                financial_data['current_assets'] - financial_data['current_liabilities']
            )
            return financial_data
        
        return None
    except Exception as e:
        print(f"Error extracting financial data from HTML: {e}")
        return None


def get_financial_data_from_10q(cik: str) -> Optional[Dict[str, float]]:
    """
    Get financial data from the most recent 10-Q filing.
    
    Args:
        cik: Company CIK
        
    Returns:
        Dictionary with financial metrics or None if extraction fails
    """
    try:
        # Get latest 10-Q filing
        filing = get_latest_10q_filing(cik)
        if not filing:
            return None
        
        # Get filing document URL
        doc_url = get_filing_document_url(cik, filing['accessionNumber'])
        if not doc_url:
            return None
        
        # Fetch the filing document
        headers = {
            'User-Agent': USER_AGENT,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        # Add delay to respect rate limits
        time.sleep(0.1)
        
        response = requests.get(doc_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Try to extract from HTML
        financial_data = extract_financial_data_from_html(response.text)
        
        if financial_data:
            financial_data['filing_date'] = filing['filingDate']
            financial_data['accession_number'] = filing['accessionNumber']
        
        return financial_data
    except Exception as e:
        print(f"Error getting financial data from 10-Q for CIK {cik}: {e}")
        return None

