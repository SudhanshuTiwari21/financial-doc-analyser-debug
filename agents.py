import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, LLM
from tools import search_tool, read_data_tool

llm = LLM(model="gemini/gemini-2.0-flash")

financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Thoroughly analyze financial documents and provide accurate, data-driven "
         "insights and recommendations based on the user's query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced financial analyst with deep expertise in corporate finance, "
        "financial statement analysis, and market research. You methodically analyze balance sheets, "
        "income statements, and cash flow reports to extract meaningful insights. You always ground "
        "your analysis in actual data from the documents provided and cite specific figures and metrics."
    ),
    tools=[read_data_tool, search_tool],
    llm=llm,
    max_iter=15,
    allow_delegation=True,
)

verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify that the uploaded document is a valid financial document and extract key "
         "metadata such as company name, reporting period, and document type.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous document verification specialist with years of experience in "
        "financial compliance. You carefully examine documents to confirm they contain legitimate "
        "financial data such as balance sheets, income statements, revenue figures, or investment "
        "reports before they proceed to detailed analysis."
    ),
    tools=[read_data_tool],
    llm=llm,
    max_iter=10,
    allow_delegation=False,
)

investment_advisor = Agent(
    role="Investment Research Advisor",
    goal="Provide well-reasoned, balanced investment recommendations based on thorough "
         "analysis of the financial data presented in the document.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified financial advisor with extensive experience in portfolio management "
        "and investment analysis. You provide balanced, risk-appropriate investment recommendations "
        "grounded in fundamental analysis. You always consider the investor's risk tolerance and "
        "clearly disclose that your analysis is informational, not personalized financial advice."
    ),
    tools=[read_data_tool, search_tool],
    llm=llm,
    max_iter=15,
    allow_delegation=False,
)

risk_assessor = Agent(
    role="Financial Risk Assessment Specialist",
    goal="Identify and evaluate key financial risks from the document data, providing "
         "actionable risk mitigation strategies.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a seasoned risk management professional with deep expertise in financial risk "
        "assessment, regulatory compliance, and market volatility analysis. You use established "
        "frameworks like Value-at-Risk, stress testing, and scenario analysis to evaluate risks. "
        "You always provide practical, evidence-based risk mitigation strategies."
    ),
    tools=[read_data_tool, search_tool],
    llm=llm,
    max_iter=15,
    allow_delegation=False,
)
