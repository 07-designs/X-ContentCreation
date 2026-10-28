import json
import logging
import re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_CHARS_PER_TWEET,
    MIN_TWEETS_PER_THREAD,
    MAX_TWEETS_PER_THREAD,
    TWITTER_HANDLE,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""
You are a viral Tech Storyteller & Software Architecture creator on X (Twitter).
Your mission is to explain fascinating "under the hood" engineering systems that power everyday technology (e.g., Zomato live rider tracking, Google Maps traffic, Netflix screenshot blackout, Flipkart flash sales, AI GPU cooling, Shazam song detection).

CRITICAL PHILOSOPHY: THE "DUAL-AUDIENCE RULE" (TECHIES + NON-TECHIES)
Your threads must captivate BOTH:
1. **Curious Non-Techies**: They must easily understand the core idea through intuitive everyday analogies and relatable mysteries (e.g. "Think of it like a textbook index", "Think of it like walking with your eyes closed for 5 seconds").
2. **Software Engineers**: They must gain real technical value by learning the exact algorithms, protocols, data structures, and trade-offs (e.g., Kalman Filters, MQTT, Widevine DRM, BGP Anycast, Kafka queues, Zero-Copy).

### FORMAT & LENGTH RULES:
1. Generate an engaging thread of exactly 5 to 6 tweets.
2. Output MUST be valid JSON: an array of strings, where each string is the exact text of one tweet.
3. STRICT LENGTH: MAXIMUM 35 TO 45 WORDS PER TWEET (approx 200–240 characters).
   Every tweet MUST fit completely under {MAX_CHARS_PER_TWEET} characters WITHOUT being cut off.
4. Thread numbering: Number each tweet at the start (e.g., "🧵 1/6", "2/6", "3/6", etc.).
5. Tweet 1 (The Everyday Curiosity Hook):
   - Start with "🧵 1/N"
   - Hook with a relatable everyday mystery.
   - 2-3 short, punchy lines.
   - End with: "Here's how it actually works under the hood 🧵👇"
6. Tweet 2 (The Naive Trap / The Big Problem):
   - Why the obvious solution (pinging GPS every second, querying SQL directly) crashes in production.
   - 3 bullet points with emojis (🔋, 💥, 📶).
7. Tweets 3 to 5 (The Core Architecture with Analogies):
   - 1 core tech concept per tweet.
   - Include the real CS term (e.g. Kalman Filter, MQTT, Map-Matching).
   - Add a 1-sentence crystal-clear analogy ("💡 Analogy: Think of it like...").
8. Final Tweet (Summary & Call to Action):
   - 2 bullet summary of takeaways.
   - Call to action:
     "If you enjoyed this breakdown:
     1. Follow @{TWITTER_HANDLE} for daily tech & system design deep-dives.
     2. Retweet tweet #1 to share with fellow devs & tech lovers! 🔁"
"""

class ThreadGenerator:
    """Generates viral, strictly-formatted Twitter threads using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name
        self._client = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not set! Please set it in your .env file or environment variables.\n"
                    "Get a free key at: https://aistudio.google.com/app/api-keys"
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_thread(self, topic: Dict[str, Any]) -> List[str]:
        """
        Takes a topic dictionary and returns a validated list of tweet strings.
        """
        title = topic.get("title", "")
        category = topic.get("category", "Software Engineering")
        keywords = ", ".join(topic.get("keywords", []))

        prompt = f"""
Write an in-depth, eye-catching X (Twitter) thread on the following topic:

Topic: {title}
Category: {category}
Key Architectural Concepts / Keywords to include: {keywords}

Remember:
- Return ONLY a valid JSON array of strings.
- Target 5 to 6 tweets total.
- Strict limit: Every single tweet MUST be under {MAX_CHARS_PER_TWEET} characters.
"""

        logger.info(f"Generating thread for topic: {title} using {self.model_name}...")
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.7,
            )
        )

        tweets = self._parse_response(response.text)
        validated_tweets = self._validate_and_sanitize_tweets(tweets, title)
        return validated_tweets

    def _parse_response(self, text: str) -> List[str]:
        """Safely parses JSON array from LLM output."""
        text = text.strip()
        # Clean any accidental markdown code fence formatting
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            data = json.loads(text)
            if isinstance(data, list) and all(isinstance(x, str) for x in data):
                return data
            elif isinstance(data, dict) and "tweets" in data:
                return data["tweets"]
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse direct JSON: {e}. Attempting regex extraction.")
            # Fallback regex extraction of quoted strings in an array
            matches = re.findall(r'"((?:[^"\\]|\\.)*)"', text)
            if matches:
                return [m.encode('utf-8').decode('unicode_escape') for m in matches]
        
        raise ValueError("Could not parse LLM response into an array of tweet strings.")

    def _validate_and_sanitize_tweets(self, tweets: List[str], topic_title: str) -> List[str]:
        """Ensures every tweet is strictly within Twitter's 280-char limit."""
        sanitized = []
        total = len(tweets)

        for idx, tweet in enumerate(tweets, 1):
            clean_tweet = tweet.strip()

            # Ensure proper prefix if missing
            prefix = f"{idx}/{total}"
            if idx == 1 and not clean_tweet.startswith("🧵"):
                if not clean_tweet.startswith("1/"):
                    clean_tweet = f"🧵 {prefix}\n" + clean_tweet
            elif idx > 1 and not re.match(r"^\d+/\d+", clean_tweet):
                clean_tweet = f"{prefix}\n" + clean_tweet

            # If tweet exceeds limit, intelligently truncate gracefully
            if len(clean_tweet) > MAX_CHARS_PER_TWEET:
                logger.warning(f"Tweet {idx} exceeded {MAX_CHARS_PER_TWEET} chars ({len(clean_tweet)} chars). Trimming gracefully.")
                clean_tweet = clean_tweet[:MAX_CHARS_PER_TWEET - 3].rsplit(" ", 1)[0] + "..."

            sanitized.append(clean_tweet)

        return sanitized
