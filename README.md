# Altman-Z-Scraper

API for calculating Altman Z-Score for public companies using 10-Q filings and current stock prices.

## Overview

This API calculates the Altman Z-Score for public companies by:
- Fetching the most recent 10-Q filing from SEC EDGAR
- Extracting financial statement data (Balance Sheet and Income Statement)
- Retrieving current stock price and shares outstanding from Yahoo Finance
- Calculating the Altman Z-Score using the standard formula

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Update the User-Agent in `app/sec_client.py` with your contact information (required by SEC API)

## Usage

### Start the API server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### GET `/zscore/{company}`
Calculate Z-Score for a company by ticker or name.

**Example:**
```bash
curl http://localhost:8000/zscore/AAPL
```

#### POST `/zscore`
Calculate Z-Score using JSON body.

**Example:**
```bash
curl -X POST http://localhost:8000/zscore \
  -H "Content-Type: application/json" \
  -d '{"company": "Apple Inc."}'
```

### Response Format

```json
{
  "company": "AAPL",
  "ticker": "AAPL",
  "z_score": 4.5234,
  "zone": "Safe Zone",
  "x1": 0.123456,
  "x2": 0.234567,
  "x3": 0.345678,
  "x4": 0.456789,
  "x5": 0.567890,
  "working_capital": 1234567890.0,
  "total_assets": 9876543210.0,
  "retained_earnings": 2345678901.0,
  "operating_income": 3456789012.0,
  "market_value_equity": 4567890123.0,
  "total_liabilities": 5678901234.0,
  "sales": 6789012345.0,
  "filing_date": "2024-01-15",
  "stock_price": 150.25,
  "shares_outstanding": 15728700000.0
}
```

### Z-Score Interpretation

- **Z > 2.99**: Safe Zone (low risk of bankruptcy)
- **1.81 < Z < 2.99**: Grey Zone (moderate risk)
- **Z < 1.81**: Distress Zone (high risk of bankruptcy)

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- The API uses the most recent 10-Q filing for financial data
- Stock prices are fetched in real-time from Yahoo Finance
- SEC API requires proper User-Agent headers (update in `app/sec_client.py`)
- Rate limiting: The SEC API has rate limits, so requests include delays
