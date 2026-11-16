from getpass import getpass
import os

from pydantic import Field

from classes import StockReport, CompanyProfile, Fundamentals, FinancialHealth, Valuation, TechnicalAnalysis, EarningsAndAnalysts, OwnershipAndDividends, BusinessExposure, NewsResult
from pydantic import Field
from typing import Any

def set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

def parse_stock_data_to_report(
    stock_data_result: dict[str, Any],
    stock_news_result: list[NewsResult] = Field(default_factory=list),
    ticker: str | None = None,
) -> StockReport:
    """
    Parse Tickerbot API response into a StockReport object.

    Args:
        stock_data_result (dict[str, Any]): The raw response from Tickerbot.
        stock_news_result (list[NewsResult]): The list of news results for the stock.
        ticker (str | None): The ticker symbol to extract from the response.

    Returns:
        StockReport: The parsed stock report.

    Raises:
        ValueError: If the response is invalid or contains multiple tickers without specifying one.
        KeyError: If the specified ticker is not found in the response.
    """

    if not isinstance(stock_data_result, dict) or not stock_data_result:
        raise ValueError("Invalid Tickerbot response")
    

    if not isinstance(stock_data_result, dict):
        raise ValueError("Invalid ticker data")

    if not isinstance(stock_news_result, list):
        raise ValueError("Invalid stock news result")

    return StockReport(
        ticker=ticker,
        company_profile=CompanyProfile.model_validate(stock_data_result),
        fundamentals=Fundamentals.model_validate(stock_data_result),
        financial_health=FinancialHealth.model_validate(stock_data_result),
        valuation=Valuation.model_validate(stock_data_result),
        technical_analysis=TechnicalAnalysis.model_validate(stock_data_result),
        earnings_and_analysts=EarningsAndAnalysts.model_validate(stock_data_result),
        ownership_and_dividends=OwnershipAndDividends.model_validate(stock_data_result),
        business_exposure=BusinessExposure.model_validate(stock_data_result),
        news=stock_news_result,

        price_asof=stock_data_result.get("price_asof"),
        ratios_asof=stock_data_result.get("ratios_asof"),
        reporting_currency=stock_data_result.get("reporting_currency"),
        fundamentals_basis=stock_data_result.get("fundamentals_basis"),
    )