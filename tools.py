import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()


@tool("Read Financial Document")
def read_data_tool(file_path: str = "data/sample.pdf") -> str:
    """Read and extract text content from a financial PDF document.

    Args:
        file_path: Path to the PDF file. Defaults to 'data/sample.pdf'.

    Returns:
        Full text content of the financial document.
    """
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    full_report = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            content = text
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
            full_report += content + "\n"

    return full_report
