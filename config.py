import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "nvidia/nemotron-3.5-lightning:free"