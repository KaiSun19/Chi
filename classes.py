from typing import Any, Literal, NotRequired, TypedDict
from langgraph.graph import add_messages
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Annotated

class ScanResult(TypedDict):
    ticker: str
    name: str
    asset_class: str
    asset_type: str
    price: float | None
    change_1d_pct: float | None
    gap_pct: float | None
    relative_volume: float | None
    market_cap: int | None

class ScanQuery(TypedDict):
    q: str
    limit: int
    order: str
    dir: str
    fields: list[str]
    full: bool
    universe: str | None
    asset_class: str | list[str] | None

class NewsQuery(TypedDict):
    q: str | None
    tickers: list[str]
    min_relevance: float
    from_: str
    select: list[str]
    group_by: str | None
    having: str | None
    order: str
    dir: str
    limit: int
    surface: str

class ScanCoverageColumn(TypedDict):
    null_rows: int
    evaluable_rows: int

class ScanNullCoverage(TypedDict):
    measured_at: str
    in_scope_rows: int
    columns: dict[str, ScanCoverageColumn]
    note: str

class ScanMeta(TypedDict):
    null_coverage: ScanNullCoverage

class ScanResponse(TypedDict):
    as_of: str
    query: ScanQuery
    _meta: NotRequired[ScanMeta]
    count: int
    next_cursor: NotRequired[str | None]
    results: list[ScanResult]

class NewsTopic(TypedDict):
    topic: str
    relevance_score: float | None

class NewsResult(TypedDict):
    id: int
    time_published: str
    title: str
    summary: str
    source: str
    source_domain: str
    category: str | None
    topics: list[NewsTopic]
    url: str
    overall_sentiment_score: float | None
    overall_sentiment_label: str | None
    relevance: float | None

class NewsResponse(TypedDict):
    results: list[NewsResult]
    as_of: str
    next_cursor: NotRequired[str | None]
    query: NewsQuery
    count: int

class Filter(TypedDict):
    field: str
    operator: Literal['<', '<=', '>', '>=', 'EQ', 'NEQ', 'IN', 'NOT_IN']
    value: str | int | float | bool | tuple[str | int | float | bool]

class TickerbotModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",          # Ignore fields we haven't added to the report yet
        populate_by_name=True,
    )

class CompanyProfile(TickerbotModel):
    ticker: str
    name: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    exchange: str | None = None
    asset_type: str | None = None
    market_cap: float | None = None

class Fundamentals(TickerbotModel):
    revenue_ttm: float | None = None
    revenue_growth_yoy_pct: float | None = None
    eps: float | None = None
    diluted_eps_ttm: float | None = None
    earnings_growth_yoy_pct: float | None = None

    gross_profit_ttm: float | None = None
    gross_margin: float | None = None
    operating_income_loss: float | None = None
    operating_margin_ttm: float | None = None
    net_income_loss: float | None = None
    profit_margin_ttm: float | None = None
    free_cash_flow: float | None = None

class FinancialHealth(TickerbotModel):
    total_debt: float | None = None
    cash_and_short_term_investments: float | None = None
    assets: float | None = None
    liabilities: float | None = None
    equity: float | None = None
    current_ratio: float | None = None
    debt_to_equity: float | None = None

class Valuation(TickerbotModel):
    price: float | None = None
    price_source: str | None = None
    enterprise_value: float | None = None

    pe_ratio: float | None = None
    forward_pe: float | None = None
    peg_ratio: float | None = None
    price_to_sales: float | None = None
    ev_to_ebitda: float | None = None

class TechnicalAnalysis(TickerbotModel):
    # Price performance
    change_1d_pct: float | None = None
    change_1w_pct: float | None = None
    change_1m_pct: float | None = None
    change_3m_pct: float | None = None
    change_6m_pct: float | None = None
    change_1y_pct: float | None = None

    # Moving averages
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    from_sma_50_pct: float | None = None
    from_sma_200_pct: float | None = None

    # Momentum
    rsi_14: float | None = None
    macd_histogram: float | None = None
    adx_14: float | None = None

    # Volatility
    atr_pct: float | None = None
    bollinger_width: float | None = None

    # Trading activity
    relative_volume: float | None = None
    avg_volume_30d: float | None = None

    # Price range
    high_52w: float | None = None
    low_52w: float | None = None
    from_52w_high_pct: float | None = None
    position_in_52w_range_pct: float | None = None

class EarningsAndAnalysts(TickerbotModel):
    earnings_date: str | None = None
    last_earnings_date: str | None = None

    last_reported_eps: float | None = None
    last_eps_estimate: float | None = None
    last_earnings_surprise_pct: float | None = None

    next_eps_estimate: float | None = None
    next_revenue_estimate: float | None = None
    eps_estimate_revision_up_30d: int | None = None
    eps_estimate_revision_down_30d: int | None = None

    analyst_consensus_rating: str | None = None
    analyst_consensus_target_price: float | None = None
    analyst_target_upside_pct: float | None = None

class OwnershipAndDividends(TickerbotModel):
    shares_outstanding: float | None = None
    float_shares: float | None = None

    short_interest: float | None = None
    short_float_pct: float | None = None
    days_to_cover: float | None = None

    insiders_pct: float | None = None
    institutions_pct: float | None = None
    dividend_yield: float | None = None

class BusinessExposure(TickerbotModel):
    revenue_by_product: list[dict[str, Any]] = Field(default_factory=list)
    revenue_by_geography: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("revenue_by_product", "revenue_by_geography", mode="before")
    @classmethod
    def _none_to_empty_list(cls, v: Any) -> Any:
        return [] if v is None else v


class StockReport(TickerbotModel):
    company_profile: CompanyProfile
    fundamentals: Fundamentals = Field(default_factory=Fundamentals)
    financial_health: FinancialHealth = Field(default_factory=FinancialHealth)
    valuation: Valuation = Field(default_factory=Valuation)
    technical_analysis: TechnicalAnalysis = Field(
        default_factory=TechnicalAnalysis
    )
    earnings_and_analysts: EarningsAndAnalysts = Field(
        default_factory=EarningsAndAnalysts
    )
    ownership_and_dividends: OwnershipAndDividends = Field(
        default_factory=OwnershipAndDividends
    )
    business_exposure: BusinessExposure = Field(
        default_factory=BusinessExposure
    )
    news: list[NewsResult] = Field(default_factory=list)

    # Data timestamps and context
    price_asof: str | None = None
    ratios_asof: str | None = None
    reporting_currency: str | None = None
    fundamentals_basis: str | None = None

class FilteredStockReport(TypedDict, total=False):
    company_profile: dict[str, Any]
    fundamentals: dict[str, Any]
    financial_health: dict[str, Any]
    valuation: dict[str, Any]
    technical_analysis: dict[str, Any]
    earnings_and_analysts: dict[str, Any]
    ownership_and_dividends: dict[str, Any]
    business_exposure: dict[str, Any]
    news: list[NewsResult]
    price_asof: str | None
    ratios_asof: str | None
    reporting_currency: str | None
    fundamentals_basis: str | None

class SummarizationGraphState(TypedDict):
    summary : str
    filtered_report: FilteredStockReport

class OverallGraphState(TypedDict):
    stock_reports: list[StockReport] = Field(default_factory=list)
    stock_summaries: list[SummarizationGraphState] = Field(default_factory=list)

class FredIndicator(TypedDict):
    name: str
    category: str
    frequency: Literal["daily", "weekly", "monthly", "quarterly"]
    description: str
    importance: Literal["critical", "high", "medium"]

class FredSeriesMetadata(TypedDict):
    id: str
    realtime_start: str
    realtime_end: str
    title: str
    observation_start: str
    observation_end: str
    frequency: str
    frequency_short: str
    units: str
    units_short: str
    seasonal_adjustment: str
    seasonal_adjustment_short: str
    last_updated: str
    popularity: int
    notes: str

class FredMetadataResponse(TypedDict):
    realtime_start: str
    realtime_end: str
    seriess: list[FredSeriesMetadata]

class FredSeriesObservation(TypedDict):
    realtime_start: str
    realtime_end: str
    date: str
    value: str

class FredSeriesObservationFiltered(TypedDict):
    date: str
    value: str

class FredIndicatorWithData(FredIndicator):
    series_data: list[FredSeriesObservationFiltered]

class FredSeriesResponse(TypedDict):
    realtime_start: str
    realtime_end: str
    observation_start: str
    observation_end: str
    units: str
    output_type: int
    file_type: str
    order_by: str
    sort_order: str
    count: int
    offset: int
    limit: int
    observations: list[FredSeriesObservation]

ConstraintOperator = Literal[
    "<=",
    ">=",
    "==",
    "in",
    "not_in",
]

ConstraintValue = float | int | str | list[str]

class PortfolioConstraint(TypedDict):
    constraint: str
    description: str
    operator: ConstraintOperator
    value: ConstraintValue
    applied_to: list[Literal["stocks", "etfs"]]

class MacroReportOutput(BaseModel):
    macro_report: str = Field(default_factory=str, description="The macroeconomic report text")
    portfolio_constraints: list[PortfolioConstraint] = Field(default_factory=list , description="The list of portfolio constraints")

class OrchestratorGraphState(TypedDict):
    #messages is needed to enable deferring to a tool node 
    messages: Annotated[list, add_messages]
    fred_series_data: dict[str , FredIndicatorWithData] = Field(default_factory=dict)
    portfolio_constraints: list[PortfolioConstraint] = Field(default_factory=list)
    macro_report: str = Field(default_factory=str)
