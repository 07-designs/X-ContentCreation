import json
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

TOPIC_IDEATOR_SYSTEM_PROMPT = """
You are a viral Tech Storyteller & Chief Content Curator for X (Twitter).
Your job is to discover fascinating, "under-the-hood" technology topics that satisfy the "Dual-Audience Rule":
1. **Curious Non-Techies**: Intrigued because it solves an everyday mystery they've experienced (e.g., Netflix black screen on screenshots, food app live tracking, why banks still use 1960s code, how Shazam hears through loud bars).
2. **Software Engineers**: Captivated because it explains the real architecture, protocols, and computer science under the hood (e.g., Widevine DRM, Kalman filters, COBOL mainframe queues, Spectrogram hashing).

CRITERIA FOR A 10/10 TOPIC:
- Must have an intuitive "Wait, how does that actually work?" reaction.
- Must explain a real, everyday product or piece of technology (Apple, Netflix, Zomato, Google, Spotify, Airplane systems, UPI, Amazon, etc.).
- Must NOT be dry academic theory (e.g., avoid "Introduction to Binary Trees").
- Must have a clear non-tech analogy alongside real technical mechanics.
"""

class TopicIdeator:
    """Autonomously invents fresh, high-impact tech topics for X threads."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name
        self._client = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not set.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def brainstorm_topic(self, past_posted_titles: List[str]) -> Dict[str, Any]:
        """
        Dynamically invents a novel, viral tech topic that hasn't been covered yet.
        """
        past_list_str = "\n".join(f"- {t}" for t in past_posted_titles[-40:]) if past_posted_titles else "None yet."

        prompt = f"""
Brainstorm 1 ultra-compelling, fresh software/technology topic to explain in an X (Twitter) thread today.

PAST TOPICS ALREADY POSTED (DO NOT DUPLICATE OR OVERLAP WITH THESE):
{past_list_str}

REQUIREMENTS:
- Must appeal to BOTH software engineers and curious non-tech people.
- Focus on real-world systems, apps, or everyday tech mysteries.
- Provide output as JSON with this exact schema:
{{
  "id": "short_unique_snake_case_id",
  "title": "Clear, engaging title (e.g. Why Netflix turns into a black screen when you take a screenshot)",
  "category": "Consumer Tech / System Design / Mobile / Security etc.",
  "mystery_hook": "The everyday question or mystery that hooks non-techies",
  "analogy": "A simple real-world analogy to explain the complex concept",
  "keywords": ["Core Tech Keyword 1", "Core Tech Keyword 2", "Core Protocol/Algorithm"]
}}

Return ONLY the raw JSON object.
"""

        candidate_models = [self.model_name, "gemini-2.0-flash", "gemini-1.5-flash"]
        models_to_try = list(dict.fromkeys(candidate_models))

        last_error = None
        for model in models_to_try:
            try:
                logger.info(f"Brainstorming a fresh autonomous topic using {model}...")
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=TOPIC_IDEATOR_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.85,
                    )
                )
                text = response.text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                
                data = json.loads(text.strip())
                return data
            except Exception as e:
                logger.warning(f"Topic ideation with {model} failed: {e}. Trying fallback model...")
                last_error = e

        raise last_error
