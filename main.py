from typing import List, cast
from pprint import pprint

import requests
import os
import json
from dotenv import load_dotenv

from classes import Filter, NewsResponse, ScanResponse, StockReport, SummarizationGraphState, OverallGraphState
from prompts import SUMMARY_PROMPT
from utils import parse_stock_data_to_report, clean_state

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, MessagesState, START, StateGraph

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

def summarize_reports(state : OverallGraphState) -> OverallGraphState:
        
    structured_llm = analyst_llm.with_structured_output(SummarizationGraphState)

    system_message = SUMMARY_PROMPT.format(stock_report=state['stock_reports'][0])

    summary = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the summary and filtered report")])
    
    return {"stock_reports": state['stock_reports'], "stock_summaries" : [summary]}

if __name__ == "__main__":
    load_dotenv()

    analyst_llm = ChatOpenAI(model="gpt-5.6-luna", api_key=os.getenv("OPENAI_API_KEY"))
    orchestrator_llm = ChatAnthropic(model="claude-sonnet-5-5", api_key=os.getenv("ANTHROPIC_API_KEY"))
    allocator_llm = ChatOpenAI(model="gpt-5.6-sol", api_key=os.getenv("OPENAI_API_KEY"))
    api_key = os.getenv("TICKERBOT_API_KEY")
    
    ticker = "ORCL"

    with open('mock_data/stock_report.json', 'r', encoding='utf-8') as file:
        stock_report = json.load(file)

    builder = StateGraph(OverallGraphState)
    builder.add_node("summarize_reports", summarize_reports)
    builder.add_edge(START, "summarize_reports")
    builder.add_edge("summarize_reports", END)

    graph = builder.compile()

    thread = {"configurable": {"thread_id": "1"}}

    final_state: OverallGraphState = graph.invoke(
        {"stock_reports": [stock_report]},
        config=thread,
    )

    print(final_state)