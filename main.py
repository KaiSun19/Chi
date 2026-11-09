from typing import List

import requests
import os
import json
from dotenv import load_dotenv

from classes import Filter, NewsResponse, ScanResponse, StockReport
from utils import parse_stock_data_to_report

SCREENER_FILTERS: List[Filter] = [
    {"field": "market_cap", "operator": ">", "value": 1e10},
    {"field": "analyst_consensus_rating", "operator": "IN", "value": ("buy", "strong buy")},
    {"field": "revenue_growth_yoy_pct", "operator": ">", "value": 20},
    {"field": "from_sma_200_pct", "operator": "<", "value": 0},
    {"field": "earnings_growth_yoy_pct", "operator": ">", "value": 20},
    {"field": "gross_profit_ttm", "operator": ">", "value": 1e9},
    {"field": "return_on_equity_ttm", "operator": ">", "value": 0.15},
    {"field": "free_cash_flow", "operator": ">", "value": 0},
    {"field": "exchange", "operator": "IN", "value": ("NASDAQ", "NYSE" , "NYSE Arca" , "FSE" , "LSE")}
]

NEWS_SELECT = "id,time_published,title,summary,source,source_domain,category,topics,url,overall_sentiment_score,overall_sentiment_label"

def serialize_screener_filters(filters: List[Filter]) -> dict:

    serialized_filters = []
    for f in filters:
        if isinstance(f['value'], bool):
            serialized_filters.append(f"{f['field']}")
        else:
            serialized_filters.append(f"{f['field']} {f['operator']} {f['value']}")

    return {
        "q": " AND ".join(serialized_filters)
    }

def fetch_scan_results(filters: List[Filter], api_key: str) -> ScanResponse:
    response = requests.post(
        url="https://api.tickerbot.io/v2/scan",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=serialize_screener_filters(filters)
    )
    return response.json()

def fetch_asset_news(ticker: str, api_key: str) -> NewsResponse:

    params = {
        "ticker": ticker,
        "min_relevance": "0.8",
        "from": "2026-10-23",
        "select": f"{NEWS_SELECT}, ticker_data -> '{ticker}' ->> 'rel' AS relevance",
        "limit": "10"
   }
    
    response = requests.get(
        url=f"https://api.tickerbot.io/v2/sandbox/news",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        params=params,
    )

    return response.json()

def fetch_asset_info(tickers: str |List[str], api_key: str) -> dict:

    if isinstance(tickers, str):
        tickers = [tickers]
    
    response = requests.get(
        url=f"https://api.tickerbot.io/v2/sandbox/tickers/{','.join(tickers)}",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        params={"tickers": ",".join(tickers)},
    )
    return response.json()

if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("TICKERBOT_API_KEY")
    ticker = "ORCL"

    stock_news = fetch_asset_news(ticker, api_key)
    stock_data = fetch_asset_info(ticker, api_key)

    stock_report = parse_stock_data_to_report(
        stock_data.get('data', {}), 
        stock_news.get('results', []), ticker
    )

    print(json.dumps(stock_report.model_dump(), indent=4))