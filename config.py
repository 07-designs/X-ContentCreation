import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Default model: gemini-2.5-flash (fast, high-intelligence, free-tier supported)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Twitter API v2 Credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# Creator Profile Configuration
TWITTER_HANDLE = os.getenv("TWITTER_HANDLE", "YourHandle")

# Content Formatting Rules
MAX_CHARS_PER_TWEET = 270  # Safe boundary below Twitter's 280-char limit
MIN_TWEETS_PER_THREAD = 5
MAX_TWEETS_PER_THREAD = 7

# Paths
TOPICS_FILE = BASE_DIR / "topics.json"
HISTORY_FILE = BASE_DIR / "posted_history.json"
