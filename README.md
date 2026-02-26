# Financial Document Analyzer

AI-powered financial document analysis system built with [CrewAI](https://docs.crewai.com/), FastAPI, and Google Gemini. Upload a financial PDF and receive comprehensive analysis including financial metrics, investment insights, and risk assessment.

## Features

- Upload financial documents (PDF format)
- AI-powered multi-agent financial analysis pipeline
- Investment recommendations grounded in document data
- Comprehensive risk assessment
- Document verification before analysis
- Web search integration for market context

## Setup and Usage

### 1. Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- A [Serper.dev API key](https://serper.dev/) (for web search)

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example env file and fill in your API keys:

```sh
cp .env.example .env
```

Edit `.env` and add your keys:

```
GEMINI_API_KEY=your-gemini-api-key
SERPER_API_KEY=your-serper-api-key
```

### 4. Prepare Sample Data

The repo includes Tesla's Q2 2025 financial update at `data/TSLA-Q2-2025-Update.pdf`. To use it as the default sample:

```sh
cp data/TSLA-Q2-2025-Update.pdf data/sample.pdf
```

Or upload any financial PDF through the API.

### 5. Run the Server

```sh
python main.py
```

The API starts at `http://localhost:8000`.

### 6. Test the API

**Health check:**

```sh
curl http://localhost:8000/
```

**Analyze a document:**

```sh
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What are the key financial metrics and investment outlook for Tesla?"
```

## API Documentation

### `GET /`

Health check endpoint.

**Response:**
```json
{"message": "Financial Document Analyzer API is running"}
```

### `POST /analyze`

Upload a financial PDF and receive AI-powered analysis.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File (PDF) | Yes | The financial document to analyze |
| `query` | string | No | Analysis question (defaults to general investment analysis) |

**Response:**
```json
{
  "status": "success",
  "query": "your query here",
  "analysis": "comprehensive multi-agent analysis...",
  "file_processed": "filename.pdf"
}
```

**Error Response:**
```json
{
  "detail": "Error processing financial document: <error message>"
}
```

## Architecture

The system uses a **sequential multi-agent pipeline** powered by CrewAI:

1. **Document Verifier** — Validates the uploaded file is a legitimate financial document and extracts metadata (company, period, type).
2. **Senior Financial Analyst** — Performs detailed financial analysis extracting key metrics, trends, and insights grounded in document data.
3. **Investment Research Advisor** — Provides balanced investment recommendations based on the financial analysis.
4. **Risk Assessment Specialist** — Identifies financial risks and provides mitigation strategies.

Each agent has access to a custom PDF reading tool and a web search tool (Serper) for market context.

---

## Bugs Found and Fixes Applied

### Deterministic Bugs (Code That Would Not Run)

#### 1. `tools.py:6` — Wrong import

```python
# BUG: 'tools' does not exist in crewai_tools as a module-level import
from crewai_tools import tools

# FIX: Import the @tool decorator from crewai.tools
from crewai.tools import tool
```

#### 2. `tools.py:13-37` — Tools defined as broken class methods

The `FinancialDocumentTool` class defined methods without the `@tool` decorator and without subclassing `BaseTool`. CrewAI cannot use plain class methods as tools.

```python
# BUG: Class method without @tool decorator or BaseTool subclass
class FinancialDocumentTool():
    async def read_data_tool(path='data/sample.pdf'):
        ...

# FIX: Use @tool decorator on standalone functions
@tool("Read Financial Document")
def read_data_tool(file_path: str = "data/sample.pdf") -> str:
    """Read and extract text from a financial PDF document."""
    ...
```

#### 3. `tools.py:24` — `Pdf` class is undefined

```python
# BUG: Pdf is never imported — NameError at runtime
docs = Pdf(file_path=path).load()

# FIX: Use pypdf.PdfReader which is a standard PDF reading library
from pypdf import PdfReader
reader = PdfReader(file_path)
```

#### 4. `agents.py:7` — Wrong import path for Agent

```python
# BUG: Agent is not at crewai.agents
from crewai.agents import Agent

# FIX: Agent is a top-level export from crewai
from crewai import Agent, LLM
```

#### 5. `agents.py:12` — Self-referential LLM assignment (NameError)

```python
# BUG: 'llm' is not yet defined — raises NameError
llm = llm

# FIX: Initialize LLM properly using CrewAI's LLM class
from crewai import LLM
llm = LLM(model="gemini/gemini-2.0-flash")
```

#### 6. `agents.py:28` — Wrong parameter name (`tool` vs `tools`)

```python
# BUG: The Agent parameter is 'tools' (plural), not 'tool'
tool=[FinancialDocumentTool.read_data_tool],

# FIX: Use the correct parameter name
tools=[read_data_tool, search_tool],
```

#### 7. `agents.py` (all agents) — `max_iter=1` and `max_rpm=1`

All agents had `max_iter=1` (default is 20) which prevents the agent from completing multi-step reasoning, and `max_rpm=1` which severely throttles requests.

```python
# BUG: Too restrictive — agent can barely do anything
max_iter=1,
max_rpm=1,

# FIX: Use reasonable values
max_iter=15,
# max_rpm removed (let it use default)
```

#### 8. `task.py:69` — Indentation error on `verification` task

```python
# BUG: verification task is indented (IndentationError at module level)
    verification = Task(
        ...
    )

# FIX: Proper module-level indentation
verification = Task(
    ...
)
```

#### 9. `task.py:79` — Wrong agent assigned to verification task

```python
# BUG: Verification task uses financial_analyst instead of verifier
agent=financial_analyst,

# FIX: Use the verifier agent
agent=verifier,
```

#### 10. `main.py:8,29` — Endpoint function shadows imported task name

```python
# BUG: Both the import and the endpoint function are named 'analyze_financial_document'
from task import analyze_financial_document  # line 8

@app.post("/analyze")
async def analyze_financial_document(...)  # line 29 — shadows the import!

# FIX: Rename the endpoint function
@app.post("/analyze")
async def analyze_document(...)
```

#### 11. `main.py:20` — `file_path` not passed in kickoff inputs

```python
# BUG: file_path parameter is accepted but never forwarded to the crew
result = financial_crew.kickoff({'query': query})

# FIX: Pass file_path so tasks can reference {file_path}
result = financial_crew.kickoff(inputs={'query': query, 'file_path': file_path})
```

#### 12. `main.py:14-18` — Crew only includes 1 agent and 1 task

```python
# BUG: Only financial_analyst and one task — no verification, investment, or risk analysis
financial_crew = Crew(
    agents=[financial_analyst],
    tasks=[analyze_financial_document],
    ...
)

# FIX: Include the full pipeline
financial_crew = Crew(
    agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
    tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
    ...
)
```

#### 13. `README.md:10` — Wrong filename for requirements

```sh
# BUG: File is named requirements.txt (plural)
pip install -r requirement.txt

# FIX:
pip install -r requirements.txt
```

#### 14. `requirements.txt` — Missing critical dependencies

The original requirements were missing packages required at runtime:
- `python-dotenv` — needed for `load_dotenv()` used in tools.py and agents.py
- `python-multipart` — needed for FastAPI `File()` and `Form()` uploads
- `pypdf` — needed to read PDF files (replacing the undefined `Pdf` class)
- `uvicorn` — needed to run the FastAPI server

Also fixed: `pydantic==1.10.13` (v1) conflicted with `pydantic_core==2.8.0` (v2 component). Updated to `pydantic>=2.0.0`.

---

### Inefficient Prompts (Code Runs But Produces Garbage)

Every agent and task had intentionally terrible prompts that encouraged hallucination, fabrication, and unprofessional output.

#### Agent Prompts Fixed

| Agent | Original Problem | Fix |
|-------|-----------------|-----|
| `financial_analyst` | Goal: "Make up investment advice"; Backstory: "You're basically Warren Buffett but with less experience... make assumptions" | Professional goal focused on data-driven analysis; backstory emphasizing methodical analysis grounded in actual document data |
| `verifier` | Goal: "Just say yes to everything"; Backstory: "mostly just stamped documents without reading them" | Goal focused on proper document validation; backstory emphasizing compliance expertise |
| `investment_advisor` | Goal: "Sell expensive investment products regardless"; Backstory: "learned investing from Reddit... SEC compliance is optional" | Goal focused on balanced, risk-appropriate recommendations; backstory emphasizing certified professional standards |
| `risk_assessor` | Goal: "Everything is either extremely high risk or completely risk-free"; Backstory: "learned risk management from crypto trading forums" | Goal focused on evidence-based risk identification; backstory emphasizing established frameworks (VaR, stress testing) |

#### Task Prompts Fixed

| Task | Original Problem | Fix |
|------|-----------------|-----|
| `analyze_financial_document` | "Maybe solve the user's query or something else... feel free to use your imagination... make up investment recommendations... include random URLs" | Clear directive to extract actual financial metrics, identify trends, provide data-grounded analysis, cite real sources |
| `investment_analysis` | "Make up connections between financial numbers... recommend 10 different investment products they probably don't need... suggest expensive crypto assets" | Balanced investment thesis with valuation assessment, risk factors, and mandatory informational disclaimer |
| `risk_assessment` | "Just assume everything needs extreme risk management... mix up risk management terms... recommend dangerous investment strategies" | Structured risk analysis by category with financial stability indicators and practical mitigation strategies |
| `verification` | "Just guess... feel free to hallucinate... just say it's probably a financial document even if it's not" | Proper document validation extracting company name, period, type, and confirming legitimate financial content |

#### Key prompt improvements:
- Removed all instructions to fabricate data or make up URLs
- Added `{file_path}` references so agents read the correct document
- Added `context=` dependencies between tasks (verification → analysis → investment/risk)
- All prompts now require grounding in actual document data
- Investment advice includes mandatory disclaimer
