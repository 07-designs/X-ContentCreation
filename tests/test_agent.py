import unittest
import json
from pathlib import Path
import tempfile
from history_manager import HistoryManager
from generator import ThreadGenerator
from config import MAX_CHARS_PER_TWEET

class TestAgentComponents(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.topics_path = Path(self.temp_dir.name) / "topics.json"
        self.history_path = Path(self.temp_dir.name) / "history.json"

        # Mock topics
        self.mock_topics = [
            {"id": "topic_1", "title": "Topic One", "category": "Cat 1", "keywords": ["kw1"]},
            {"id": "topic_2", "title": "Topic Two", "category": "Cat 2", "keywords": ["kw2"]},
        ]
        with open(self.topics_path, "w", encoding="utf-8") as f:
            json.dump(self.mock_topics, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_history_manager_selection_and_recording(self):
        hm = HistoryManager(topics_path=self.topics_path, history_path=self.history_path)
        
        # Initial topic should be topic_1
        topic = hm.get_next_topic()
        self.assertEqual(topic["id"], "topic_1")

        # Record topic_1 as posted
        hm.record_posted(topic, ["12345", "12346"], ["Tweet 1", "Tweet 2"])

        # Stats check
        stats = hm.stats()
        self.assertEqual(stats["total_topics"], 2)
        self.assertEqual(stats["posted_count"], 1)
        self.assertEqual(stats["remaining_count"], 1)

        # Next topic should now be topic_2
        next_topic = hm.get_next_topic()
        self.assertEqual(next_topic["id"], "topic_2")

    def test_generator_parsing(self):
        gen = ThreadGenerator(api_key="fake-key")
        
        # JSON markdown block
        raw_json = '```json\n["Tweet 1", "Tweet 2", "Tweet 3"]\n```'
        parsed = gen._parse_response(raw_json)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], "Tweet 1")

    def test_tweet_sanitization_and_character_limit(self):
        gen = ThreadGenerator(api_key="fake-key")
        
        # Overly long tweet
        long_text = "This is a very long sentence. " * 20
        raw_tweets = [
            "Hook text about engineering systems under the hood.",
            long_text,
            "Summary text with CTA"
        ]

        sanitized = gen._validate_and_sanitize_tweets(raw_tweets, "Test Topic")
        self.assertEqual(len(sanitized), 3)

        # Check character limit
        for idx, t in enumerate(sanitized):
            self.assertLessEqual(len(t), MAX_CHARS_PER_TWEET, f"Tweet {idx} exceeded max chars")

        # Check numbering prefix
        self.assertTrue(sanitized[0].startswith("🧵 1/3") or "1/3" in sanitized[0])
        self.assertTrue("2/3" in sanitized[1])
        self.assertTrue("3/3" in sanitized[2])

if __name__ == "__main__":
    unittest.main()
