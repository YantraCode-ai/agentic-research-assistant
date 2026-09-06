from .arxiv_tool import search_arxiv, ArxivSearchSchema
from .search_tool import search_tavily, TavilySearchSchema
from .web_fetch import scrape_web, WebFetchSchema
from .sandbox_tool import run_python, SandboxSchema

AVAILABLE_TOOLS = {
    "arxiv_search": {
        "function": search_arxiv,
        "schema": ArxivSearchSchema,
        "description": "Search arXiv for academic papers and abstracts."
    },
    "tavily_search": {
        "function": search_tavily,
        "schema": TavilySearchSchema,
        "description": "Search the web for general context and recent news."
    },
    "web_fetch": {
        "function": scrape_web,
        "schema": WebFetchSchema,
        "description": "Fetch and extract clean article text from a URL."
    },
    "python_sandbox": {
        "function": run_python,
        "schema": SandboxSchema,
        "description": "Run Python code to analyze data, compute statistics, or format text."
    }
}