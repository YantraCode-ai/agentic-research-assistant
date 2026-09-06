from langchain_core.tools import tool
from tools.arxiv_tool import search_arxiv
from tools.search_tool import search_tavily
from tools.web_fetch import scrape_web
from tools.sandbox_tool import run_python

@tool
def arxiv_search(query: str, max_results: int = 5) -> str:
    """Search arXiv for academic papers, authors, and abstracts."""
    return search_arxiv(query=query, max_results=max_results)

@tool
def tavily_search(query: str) -> str:
    """Search the web for general context, articles, and recent news."""
    return search_tavily(query=query)

@tool
def web_fetch(url: str) -> str:
    """Fetch and extract clean text from a specific webpage or paper URL."""
    return scrape_web(url=url)

@tool
def python_sandbox(code: str) -> str:
    """Execute Python code in an isolated sandbox to process extracted metrics, calculate averages, or inspect tables. Use print() to output results."""
    return run_python(code=code)

TOOLS = [arxiv_search, tavily_search, web_fetch, python_sandbox]