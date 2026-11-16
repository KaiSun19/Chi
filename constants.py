from classes import FredIndicator

IS_TESTING = True

FRED_INDICATORS: dict[str, FredIndicator] = {

    # Inflation (3)
    "CPIAUCSL": {
        "name": "headline_cpi",
        "category": "inflation",
        "frequency": "monthly",
        "description": "Consumer Price Index for All Urban Consumers. Measures changes in the prices paid by consumers for a broad basket of goods and services. Primary measure of headline US inflation.",
        "importance": "critical",
    },
    "CPILFESL": {
        "name": "core_cpi",
        "category": "inflation",
        "frequency": "monthly",
        "description": "Consumer Price Index excluding food and energy. Measures underlying consumer inflation while filtering out more volatile price components.",
        "importance": "high",
    },
    "PCEPILFE": {
        "name": "core_pce",
        "category": "inflation",
        "frequency": "monthly",
        "description": "Personal Consumption Expenditures Price Index excluding food and energy. The Federal Reserve's preferred underlying inflation measure.",
        "importance": "critical",
    },

    # Economic growth (3)
    "GDPC1": {
        "name": "real_gdp",
        "category": "economic_growth",
        "frequency": "quarterly",
        "description": "Real Gross Domestic Product, adjusted for inflation. Measures the overall size and growth of the US economy.",
        "importance": "critical",
    },
    "INDPRO": {
        "name": "industrial_production",
        "category": "economic_growth",
        "frequency": "monthly",
        "description": "Measures real output from US manufacturing, mining, and utilities. Provides insight into industrial and manufacturing activity.",
        "importance": "high",
    },
    "RSAFS": {
        "name": "retail_sales",
        "category": "economic_growth",
        "frequency": "monthly",
        "description": "Advance Retail Sales: Retail and Food Services. Measures consumer spending at retail businesses and provides insight into consumer demand.",
        "importance": "high",
    },

    # Employment (3)
    "UNRATE": {
        "name": "unemployment_rate",
        "category": "employment",
        "frequency": "monthly",
        "description": "Civilian Unemployment Rate. Measures the percentage of the labour force that is unemployed and actively seeking work.",
        "importance": "critical",
    },
    "PAYEMS": {
        "name": "nonfarm_payrolls",
        "category": "employment",
        "frequency": "monthly",
        "description": "Total nonfarm payroll employment. Measures the number of employees across US nonfarm businesses and government, providing insight into job creation.",
        "importance": "critical",
    },
    "ICSA": {
        "name": "initial_jobless_claims",
        "category": "employment",
        "frequency": "weekly",
        "description": "Initial Claims for Unemployment Insurance. Measures new applications for unemployment benefits and provides a more timely indication of labour-market deterioration.",
        "importance": "high",
    },

    # Monetary policy (2)
    "DFF": {
        "name": "effective_federal_funds_rate",
        "category": "monetary_policy",
        "frequency": "daily",
        "description": "Effective Federal Funds Rate. Represents the overnight interbank lending rate and reflects the prevailing level of US monetary policy.",
        "importance": "critical",
    },
    "DFEDTARU": {
        "name": "fed_target_upper_bound",
        "category": "monetary_policy",
        "frequency": "daily",
        "description": "Upper limit of the Federal Reserve's federal funds target range. Indicates the Fed's stated policy-rate setting.",
        "importance": "high",
    },

    # Interest rates (3)
    "DGS2": {
        "name": "treasury_2y",
        "category": "interest_rates",
        "frequency": "daily",
        "description": "2-Year US Treasury Constant Maturity Rate. Reflects market expectations for short-to-medium-term interest rates and monetary policy.",
        "importance": "high",
    },
    "DGS10": {
        "name": "treasury_10y",
        "category": "interest_rates",
        "frequency": "daily",
        "description": "10-Year US Treasury Constant Maturity Rate. Represents longer-term borrowing costs and market expectations for economic growth and inflation.",
        "importance": "critical",
    },
    "DFII10": {
        "name": "real_treasury_10y",
        "category": "interest_rates",
        "frequency": "daily",
        "description": "10-Year Treasury Inflation-Indexed Security Rate. Represents the market's implied real interest rate after accounting for inflation expectations.",
        "importance": "high",
    },

    # Equity market (2)
    "SP500": {
        "name": "sp500",
        "category": "equity_market",
        "frequency": "daily",
        "description": "S&P 500 Index. Tracks the performance of 500 leading US companies and provides a broad measure of US large-cap equity-market direction.",
        "importance": "critical",
    },
    "NASDAQ100": {
        "name": "nasdaq_100",
        "category": "equity_market",
        "frequency": "daily",
        "description": "NASDAQ-100 Index. Tracks 100 of the largest non-financial companies listed on Nasdaq and provides insight into large-cap growth and technology-oriented equities.",
        "importance": "high",
    },

    # Volatility and risk (1)
    "VIXCLS": {
        "name": "vix",
        "category": "volatility_risk",
        "frequency": "daily",
        "description": "CBOE Volatility Index. Measures the market's expected 30-day volatility implied by S&P 500 options prices. Serves as the primary indicator of equity-market uncertainty and investor risk sentiment.",
        "importance": "critical",
    },

    # Financial conditions (2)
    "NFCI": {
        "name": "national_financial_conditions",
        "category": "financial_conditions",
        "frequency": "weekly",
        "description": "Chicago Fed National Financial Conditions Index. Summarises financial conditions across money markets, debt and equity markets, and the traditional banking system. Higher values indicate tighter financial conditions.",
        "importance": "high",
    },
    "BAMLH0A0HYM2": {
        "name": "high_yield_credit_spread",
        "category": "financial_conditions",
        "frequency": "daily",
        "description": "ICE BofA US High Yield Index Option-Adjusted Spread. Measures the additional yield investors demand to hold below-investment-grade corporate bonds relative to comparable Treasury securities. Rising spreads can indicate deteriorating credit sentiment.",
        "importance": "high",
    },

    # Commodities and currencies (2)
    "DCOILWTICO": {
        "name": "wti_crude_oil",
        "category": "commodities_currencies",
        "frequency": "daily",
        "description": "West Texas Intermediate crude oil spot price. Provides insight into energy-market conditions, inflationary pressure, and supply-demand dynamics.",
        "importance": "medium",
    },
    "DTWEXBGS": {
        "name": "broad_us_dollar_index",
        "category": "commodities_currencies",
        "frequency": "daily",
        "description": "Nominal Broad US Dollar Index. Measures the US dollar against a broad basket of foreign currencies and provides insight into global currency conditions and financial pressure.",
        "importance": "medium",
    },
}

ALL_FRED_INDICATORS_SERIES_IDS = list(FRED_INDICATORS)

