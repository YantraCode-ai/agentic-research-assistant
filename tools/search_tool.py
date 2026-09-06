from tavily import TavilyClient
from pydantic import BaseModel, Field
from config import TAVILY_API_KEY

class TavilySearchSchema(BaseModel):
    query: str = Field(description="The search query for the web.")

def search_tavily(query: str) -> str:
    """Searches the general web using Tavily."""
    if not TAVILY_API_KEY:
        return "Error: TAVILY_API_KEY not found in environment."
    
    client = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        response = client.search(query=query, max_results=5)
        
        results = []
        for res in response.get("results", []):
            results.append(
                f"Title: {res.get('title')}\n"
                f"URL: {res.get('url')}\n"
                f"Content: {res.get('content')}\n"
                "---"
            )
        return "\n".join(results) if results else "No results found on Tavily."
    except Exception as e:
        return f"Error searching Tavily: {str(e)}"