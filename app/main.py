"""FastAPI application for Altman Z-Score API."""

from fastapi import FastAPI, HTTPException, Path
import traceback

from app.models import ZScoreRequest, ZScoreResponse, ErrorResponse
from app.utils import get_cik, get_cik_and_ticker
from app.sec_client import get_financial_data_from_10q
from app.stock_client import get_stock_data
from app.calculator import calculate_altman_z_score

app = FastAPI(
    title="Altman Z-Score API",
    description="Calculate Altman Z-Score for public companies using 10-Q filings and current stock prices",
    version="1.0.0"
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {"message": "Altman Z-Score API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get(
    "/zscore/{company}",
    response_model=ZScoreResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Z-Score"]
)
async def get_zscore(
    company: str = Path(..., description="Company name or ticker symbol")
):
    """
    Calculate Altman Z-Score for a public company.
    
    Args:
        company: Company name or ticker symbol (e.g., 'AAPL' or 'Apple Inc.')
        
    Returns:
        Z-Score calculation results with financial metrics
    """
    try:
        # Step 1: Get CIK and ticker from company identifier
        cik_ticker_info = get_cik_and_ticker(company)
        if not cik_ticker_info:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company}' not found. Please provide a valid ticker symbol or company name."
            )
        
        cik = cik_ticker_info['cik']
        ticker = cik_ticker_info['ticker']
        
        # Step 2: Get financial data from most recent 10-Q
        financial_data = get_financial_data_from_10q(cik)
        if not financial_data:
            raise HTTPException(
                status_code=404,
                detail=f"Could not retrieve 10-Q filing data for '{company}'. The company may not have filed a 10-Q recently."
            )
        
        # Validate required financial data
        required_fields = ['working_capital', 'total_assets', 'retained_earnings', 
                          'operating_income', 'total_liabilities', 'sales']
        missing_fields = [field for field in required_fields if field not in financial_data]
        if missing_fields:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required financial data fields: {', '.join(missing_fields)}"
            )
        
        # Step 3: Get stock data using ticker
        stock_data = get_stock_data(ticker)
        
        if not stock_data:
            raise HTTPException(
                status_code=404,
                detail=f"Could not retrieve stock price data for ticker '{ticker}'. Please verify the ticker symbol is correct."
            )
        
        # Step 4: Calculate Z-Score
        try:
            zscore_result = calculate_altman_z_score(
                working_capital=financial_data['working_capital'],
                total_assets=financial_data['total_assets'],
                retained_earnings=financial_data['retained_earnings'],
                operating_income=financial_data['operating_income'],
                market_value_equity=stock_data['market_value_equity'],
                total_liabilities=financial_data['total_liabilities'],
                sales=financial_data['sales']
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating Z-Score: {str(e)}"
            )
        
        # Step 5: Build response
        response = ZScoreResponse(
            company=company,
            ticker=ticker,
            z_score=zscore_result['z_score'],
            zone=zscore_result['zone'],
            x1=zscore_result['x1'],
            x2=zscore_result['x2'],
            x3=zscore_result['x3'],
            x4=zscore_result['x4'],
            x5=zscore_result['x5'],
            working_capital=zscore_result['working_capital'],
            total_assets=zscore_result['total_assets'],
            retained_earnings=zscore_result['retained_earnings'],
            operating_income=zscore_result['operating_income'],
            market_value_equity=zscore_result['market_value_equity'],
            total_liabilities=zscore_result['total_liabilities'],
            sales=zscore_result['sales'],
            filing_date=financial_data.get('filing_date'),
            stock_price=stock_data.get('price'),
            shares_outstanding=stock_data.get('shares_outstanding')
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post(
    "/zscore",
    response_model=ZScoreResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Z-Score"]
)
async def post_zscore(request: ZScoreRequest):
    """
    Calculate Altman Z-Score for a public company (POST endpoint).
    
    Args:
        request: ZScoreRequest with company name or ticker
        
    Returns:
        Z-Score calculation results with financial metrics
    """
    return await get_zscore(request.company)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

