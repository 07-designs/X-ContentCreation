import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from config import TOPICS_FILE, HISTORY_FILE

logger = logging.getLogger(__name__)

class HistoryManager:
    """Manages the catalog of topics and tracks already-posted threads to prevent duplicates."""

    def __init__(self, topics_path: Path = TOPICS_FILE, history_path: Path = HISTORY_FILE):
        self.topics_path = topics_path
        self.history_path = history_path
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Creates the history file if it doesn't exist."""
        if not self.history_path.exists():
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump({"posted": []}, f, indent=2)

    def load_topics(self) -> List[Dict[str, Any]]:
        """Loads all available topics from topics.json."""
        if not self.topics_path.exists():
            return []
        with open(self.topics_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_history(self) -> Dict[str, Any]:
        """Loads the posted history."""
        self._ensure_history_file()
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"posted": []}

    def get_posted_ids(self) -> set:
        """Returns a set of topic IDs that have already been posted."""
        history = self.load_history()
        return {item["id"] for item in history.get("posted", []) if "id" in item}

    def get_posted_titles(self) -> List[str]:
        """Returns a list of topic titles that have already been posted."""
        history = self.load_history()
        return [item.get("title", "") for item in history.get("posted", []) if "title" in item]

    def get_next_topic(
        self,
        requested_id_or_title: Optional[str] = None,
        auto_brainstorm: bool = False
    ) -> Dict[str, Any]:
        """
        Picks the next unposted topic.
        If auto_brainstorm is True or all seed topics are posted, dynamically invents a fresh topic using Gemini.
        """
        all_topics = self.load_topics()
        posted_ids = self.get_posted_ids()

        if requested_id_or_title:
            # Check if it matches an existing topic ID or title
            for t in all_topics:
                if t["id"].lower() == requested_id_or_title.lower() or requested_id_or_title.lower() in t["title"].lower():
                    return t
            # Otherwise treat as custom user topic
            return {
                "id": "custom_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
                "title": requested_id_or_title,
                "category": "Custom Request",
                "keywords": []
            }

        # If user explicitly requests dynamic discovery OR seed topics are exhausted
        unposted = [t for t in all_topics if t["id"] not in posted_ids]
        if auto_brainstorm or not unposted:
            logger.info("Using AI Topic Ideator to invent a brand new viral topic...")
            try:
                from topic_ideator import TopicIdeator
                ideator = TopicIdeator()
                new_topic = ideator.brainstorm_topic(self.get_posted_titles())

                # Append newly brainstormed topic to topics.json
                all_topics.append(new_topic)
                with open(self.topics_path, "w", encoding="utf-8") as f:
                    json.dump(all_topics, f, indent=2)

                logger.info(f"AI brainstormed topic: '{new_topic.get('title')}'")
                return new_topic
            except Exception as e:
                logger.warning(f"Dynamic topic ideation fallback: {e}")
                if unposted:
                    return unposted[0]

        # Return first unposted topic from catalog
        return unposted[0]

    def record_posted(self, topic: Dict[str, Any], tweet_ids: List[str], thread_tweets: List[str]):
        """Records a successfully posted thread into history."""
        history = self.load_history()
        history["posted"].append({
            "id": topic.get("id"),
            "title": topic.get("title"),
            "category": topic.get("category", "General"),
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "tweet_ids": tweet_ids,
            "tweet_count": len(thread_tweets),
            "preview_hook": thread_tweets[0] if thread_tweets else ""
        })

        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def stats(self) -> Dict[str, int]:
        """Returns count of posted vs total topics."""
        all_topics = self.load_topics()
        posted_ids = self.get_posted_ids()
        return {
            "total_topics": len(all_topics),
            "posted_count": len(posted_ids),
            "remaining_count": max(0, len(all_topics) - len(posted_ids))
        }
