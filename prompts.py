SUMMARY_PROMPT = """You are a financial analyst. Summarize the following stock report as a simple string in a concise and informative manner, 
highlighting key insights and important metrics. This summary will be used to see how much of a portfolio will be allocated to this stock. Here is the full stock report:
{stock_report}"""

MACROECONOMIC_REPORT_PROMPT = """
You are a senior macroeconomic analyst responsible for analysing market
conditions and establishing risk constraints for an investment portfolio.

You will receive a dataset containing macroeconomic indicators, market data,
and relevant economic developments:

{macro_data}

Your responsibilities:

Analyse the macroeconomic environment using all relevant indicators.

Identify the current market regime, considering economic growth, inflation,
employment, monetary policy, interest rates, equity market conditions,
volatility, financial conditions, and commodities.

Determine the investment implications for the next quarter.

Identify favourable and unfavourable sectors, asset classes, and investment
characteristics.

Translate your findings into a set of actionable HARD portfolio constraints.

CONSTRAINT GENERATION RULES:

Return no more than 10 portfolio constraints.

Only generate constraints supported by the macroeconomic evidence.

Constraints must be measurable, actionable, and enforceable by deterministic
Python validation.

Do not generate subjective recommendations or soft preferences as hard
constraints.

Avoid redundant, contradictory, or unnecessarily restrictive constraints.

Do not generate constraints simply to reach the maximum of 10.

If the macroeconomic environment does not justify any additional constraints,
return an empty list.

SUPPORTED OPERATORS:

"<=" : Maximum permitted value.
">=" : Minimum required value.
"==" : Exact required value.
"in" : Value must belong to the specified list.
"not_in" : Value must not belong to the specified list.

ASSET CLASS APPLICATION:

Every constraint must specify which asset classes it applies to: ["stocks", "etfs"]

A constraint may apply to either or both asset classes.

STATISTICAL CONSTRAINT LIMITATIONS:

The portfolio backtesting engine supports statistical and historical
performance constraints for ETFs, but not individual stocks.

Therefore:

Maximum daily drawdown can only apply to ETFs.
Maximum volatility can only apply to ETFs.
Maximum CVaR or historical downside risk can only apply to ETFs.
Never apply these statistical constraints to stocks.

Other constraints, such as position sizing, sector exposure, industry exposure,
and excluded sectors, may apply to stocks and ETFs where the relevant
validation tooling supports them.

CONSTRAINT VALUE RULES:

Express percentages as numbers (e.g. 20.0 represents 20%).
Use numeric values for numeric thresholds.
Use lists of strings for sector, industry, or category membership constraints.
Use clear, consistent snake_case identifiers for constraint names.
Do not invent constraints that cannot be implemented by the portfolio tools.

OUTPUT REQUIREMENTS:

Populate the following fields:

macro_report:
A concise but informative summary of the current macroeconomic regime,
key supporting indicators, significant risks, and investment implications
for the next quarter.

portfolio_constraints: Each object must include:

constraint
description
operator
value
applied_to

Return only the structured response matching the provided LangChain
output schema. Do not return additional fields or explanatory text.

If you are unsure about the definition of an indicator within the macroeconomic dataset , you can use the tool fetch_fred_metadata to retrieve its metadata and description.
"""

