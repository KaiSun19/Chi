from typing import List, Literal
from langgraph.prebuilt import ToolNode
import pandas as pd

import requests
import os
import json
from dotenv import load_dotenv

from classes import Filter, FredIndicatorWithData, FredMetadataResponse, FredSeriesResponse, NewsResponse, OrchestratorGraphState, MacroReportOutput , ScanResponse, SummarizationGraphState, OverallGraphState
from constants import ALL_FRED_INDICATORS_SERIES_IDS, FRED_INDICATORS, IS_TESTING
from prompts import SUMMARY_PROMPT, MACROECONOMIC_REPORT_PROMPT

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

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

DATE_3_YEARS_AGO = (pd.Timestamp.now() - pd.DateOffset(years=3)).strftime('%Y-%m-%d')

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

def summarize_reports(llm : ChatOpenAI, state : OverallGraphState) -> OverallGraphState:
        
    structured_llm = llm.with_structured_output(SummarizationGraphState)

    system_message = SUMMARY_PROMPT.format(stock_report=state['stock_reports'][0])

    summary = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the summary and filtered report")])
    
    return {"stock_reports": state['stock_reports'], "stock_summaries" : [summary]}

def create_macro_report_and_constraints(state: OrchestratorGraphState) -> OrchestratorGraphState:

    structured_llm = orchestrator_llm.with_structured_output(MacroReportOutput, method="json_schema")

    system_message = MACROECONOMIC_REPORT_PROMPT.format(macro_data=state['fred_series_data'])

    tool_messages = [ToolNode(content=msg) for msg in state['messages']]

    output = structured_llm.invoke([SystemMessage(content=system_message)]+ tool_messages)

    return {"macro_report": output.macro_report, "portfolio_constraints": output.portfolio_constraints}

def fetch_fred_metadata(series_id: str) -> FredMetadataResponse:
    """
    Fetch metadata for a given FRED series ID.

    Parameters:
    - series_id (str): The FRED series ID to fetch metadata for.

    Returns:
    - FredMetadataResponse: The metadata response for the specified series.
    """

    print(f'Fetching metadata for series ID: {series_id}')

    api_key = os.getenv("FRED_API_KEY")

    response = requests.get(
        url=f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={api_key}&file_type=json",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )

    return response.json()

def fetch_fred_series(series_id: str, api_key: str) -> FredSeriesResponse:

    api_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&observation_start={DATE_3_YEARS_AGO}&api_key={api_key}&file_type=json"

    if FRED_INDICATORS[series_id]["frequency"] != "quarterly":
        api_url += "&frequency=m"

    response = requests.get(
        url=api_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )

    return response.json()

def fetch_all_fred_series_data(api_key: str) -> dict[str, list[dict[str, str]]]:

    if IS_TESTING:
        with open('mock_data/all_fred_series_data_3y.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    all_fred_series_data = {}

    for id in ALL_FRED_INDICATORS_SERIES_IDS:
        print(f'Fetching data for series ID: {id}')
        series_data = fetch_fred_series(id, api_key)['observations']
        all_fred_series_data[id] = list(map(lambda x : {"date": x["date"], "value": x["value"]}, series_data))

    return all_fred_series_data

def call_orchestrator_model(state: OrchestratorGraphState):
    """Invoke LLM with the current state messages."""
    response = orchestrator_llm.invoke(state["messages"])

    if getattr(response, "tool_calls", None):
        return {"messages": [response], "route": "tools"}

    return {"messages": [response], "route": "create_macro_report_and_constraints"}

def should_continue_to_tools(state: OrchestratorGraphState) -> Literal["tools", "create_macro_report_and_constraints"]:
    """Route to tools if the LLM made a tool call, otherwise go to next node"""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "create_macro_report_and_constraints"

if __name__ == "__main__":
    load_dotenv()

    orchestrator_tools = [fetch_fred_metadata]

    analyst_llm = ChatOpenAI(model="gpt-5.6-luna", api_key=os.getenv("OPENAI_API_KEY"))
    orchestrator_llm = ChatAnthropic(model="claude-sonnet-5-5", api_key=os.getenv("ANTHROPIC_API_KEY")).bind_tools(orchestrator_tools)
    allocator_llm = ChatOpenAI(model="gpt-5.6-sol", api_key=os.getenv("OPENAI_API_KEY"))
    api_key = os.getenv("TICKERBOT_API_KEY")

    fred_api_key = os.getenv("FRED_API_KEY")
    
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

    all_fred_series_data = fetch_all_fred_series_data(fred_api_key)

    fred_indicators_with_data: FredIndicatorWithData = {}

    for series_id, series_data in FRED_INDICATORS.items():
        fred_indicators_with_data[series_id] = {
            "indicator": series_data,
            "data": all_fred_series_data.get(series_id, [])
        }

    builder = StateGraph(OrchestratorGraphState)

    builder.add_node("call_model", call_orchestrator_model)
    builder.add_node("create_macro_report_and_constraints", create_macro_report_and_constraints)
    builder.add_node("tools", ToolNode(orchestrator_tools))

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue_to_tools, {"tools": "tools", "create_macro_report_and_constraints": "create_macro_report_and_constraints"})
    builder.add_edge("tools", "create_macro_report_and_constraints")
    builder.add_edge("create_macro_report_and_constraints", END)

    graph = builder.compile()

    thread = {"configurable": {"thread_id": "1"}}

    final_state: OrchestratorGraphState = graph.invoke(
        {"fred_series_data": fred_indicators_with_data, "messages": [HumanMessage(content="Generate the macro report and constraints")]},
        config=thread,
    )