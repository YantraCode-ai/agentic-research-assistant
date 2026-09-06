import trafilatura
import tiktoken
from pydantic import BaseModel, Field

class WebFetchSchema(BaseModel):
    url: str = Field(description="The URL of the article or paper to scrape.")

def truncate_text(text: str, max_tokens: int = 8000) -> str:
    """Truncates text to prevent blowing up the LLM's context window."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        return text[:30000] 
        
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        return encoding.decode(tokens) + "\n\n[Content truncated due to length...]"
    return text

def scrape_web(url: str) -> str:
    """Fetches and extracts clean text from a webpage."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return f"Error: Could not download content from {url}."
        
        text = trafilatura.extract(downloaded, include_links=False, include_images=False)
        if not text:
            return f"Error: Could not extract text from {url}."
            
        return truncate_text(text)
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"