from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, read_data_tool

verification = Task(
    description=(
        "Read the uploaded financial document located at {file_path} and verify that it is a "
        "legitimate financial report.\n"
        "Identify the company name, reporting period, and document type (e.g., quarterly report, "
        "annual report, earnings update).\n"
        "Confirm that the document contains standard financial data such as revenue, expenses, "
        "balance sheet items, or cash flow statements.\n"
        "If the document is not a valid financial report, clearly state so and explain why."
    ),
    expected_output=(
        "A verification summary containing:\n"
        "- Document type (quarterly report, annual report, earnings update, etc.)\n"
        "- Company name and reporting period\n"
        "- Confirmation of whether the document is a valid financial report\n"
        "- Key financial sections identified in the document"
    ),
    agent=verifier,
    tools=[read_data_tool],
    async_execution=False,
)

analyze_financial_document = Task(
    description=(
        "Analyze the financial document at {file_path} thoroughly to answer the user's query: {query}\n"
        "Read the complete document and extract key financial metrics including revenue, net income, "
        "margins, EPS, and other relevant data.\n"
        "Identify trends by comparing current period data with prior periods where available.\n"
        "Provide a comprehensive financial analysis grounded in the actual data from the document.\n"
        "Search the internet for relevant market context and industry benchmarks to enhance the analysis."
    ),
    expected_output=(
        "A detailed financial analysis report containing:\n"
        "- Executive summary of key findings\n"
        "- Key financial metrics with actual figures from the document\n"
        "- Period-over-period comparison and trend analysis\n"
        "- Revenue and profitability analysis\n"
        "- Notable items, risks, or opportunities identified in the data\n"
        "- Relevant market context from current research\n"
        "- Sources and references for all external data cited"
    ),
    agent=financial_analyst,
    tools=[read_data_tool, search_tool],
    context=[verification],
    async_execution=False,
)

investment_analysis = Task(
    description=(
        "Based on the financial analysis, provide investment insights and recommendations "
        "for the user's query: {query}\n"
        "Evaluate the company's financial health, growth prospects, and competitive position.\n"
        "Assess valuation metrics such as P/E ratio, P/B ratio, and dividend yield where applicable.\n"
        "Provide balanced investment considerations including both opportunities and concerns.\n"
        "Clearly state that this is informational analysis, not personalized financial advice."
    ),
    expected_output=(
        "An investment analysis report containing:\n"
        "- Overall investment thesis (bullish/bearish/neutral) with supporting rationale\n"
        "- Key financial strengths and growth drivers\n"
        "- Valuation assessment relative to peers and historical averages\n"
        "- Investment considerations and potential catalysts\n"
        "- Risk factors that could impact investment performance\n"
        "- Disclaimer that this analysis is for informational purposes only"
    ),
    agent=investment_advisor,
    tools=[read_data_tool, search_tool],
    context=[analyze_financial_document],
    async_execution=False,
)

risk_assessment = Task(
    description=(
        "Conduct a comprehensive risk assessment based on the financial document at {file_path} "
        "and prior analysis.\n"
        "Identify key financial risks including market risk, credit risk, operational risk, "
        "and liquidity risk.\n"
        "Evaluate the company's debt levels, cash flow adequacy, and financial stability.\n"
        "Provide risk ratings and practical risk mitigation strategies.\n"
        "Consider both company-specific risks and broader market/industry risks."
    ),
    expected_output=(
        "A comprehensive risk assessment containing:\n"
        "- Risk summary with overall risk rating (Low/Medium/High)\n"
        "- Detailed breakdown of identified risks by category\n"
        "- Financial stability indicators (debt-to-equity, current ratio, etc.)\n"
        "- Company-specific risk factors from the financial document\n"
        "- Market and industry-level risk factors\n"
        "- Recommended risk mitigation strategies\n"
        "- Key metrics to monitor going forward"
    ),
    agent=risk_assessor,
    tools=[read_data_tool, search_tool],
    context=[analyze_financial_document],
    async_execution=False,
)
