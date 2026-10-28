import argparse
import logging
import sys
from pathlib import Path
from typing import Optional
from history_manager import HistoryManager
from generator import ThreadGenerator
from twitter_poster import TwitterPoster
from config import MAX_CHARS_PER_TWEET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def print_thread_preview(topic: dict, tweets: list):
    """Prints a beautiful formatted preview of the generated thread."""
    print("\n" + "=" * 70)
    print(f"📌 TOPIC: {topic.get('title')}")
    print(f"🏷️  CATEGORY: {topic.get('category')}")
    print(f"🔢 TWEETS: {len(tweets)}")
    print("=" * 70)

    for i, tweet in enumerate(tweets, 1):
        char_count = len(tweet)
        status = "✅ OK" if char_count <= MAX_CHARS_PER_TWEET else "⚠️ OVER LIMIT"
        print(f"\n--- [TWEET {i}/{len(tweets)}] ({char_count}/{MAX_CHARS_PER_TWEET} chars - {status}) ---")
        print(tweet)

    print("\n" + "=" * 70 + "\n")

def run(topic_query: Optional[str] = None, dry_run: bool = True, auto_brainstorm: bool = False):
    """Main execution workflow."""
    history = HistoryManager()
    generator = ThreadGenerator()

    # 1. Select Topic (from catalog or autonomously brainstormed)
    topic = history.get_next_topic(topic_query, auto_brainstorm=auto_brainstorm)
    logger.info(f"Selected Topic: '{topic['title']}' (ID: {topic['id']})")

    # 2. Generate Thread with Gemini
    tweets = generator.generate_thread(topic)

    # 3. Preview Thread
    print_thread_preview(topic, tweets)

    # 4. Handle Publishing or Dry Run
    if dry_run:
        logger.info("⚡ [DRY RUN MODE] Thread generated and verified. No tweets were posted to X.")
        logger.info("To post to Twitter, run: python main.py --post")
        return tweets

    # 5. Live Posting to Twitter (X)
    logger.info("🚀 [LIVE MODE] Initiating publication to X (Twitter)...")
    poster = TwitterPoster()
    tweet_ids = poster.post_thread(tweets)

    # 6. Record to History
    history.record_posted(topic, tweet_ids, tweets)
    logger.info("🎉 Thread successfully published and recorded to history!")
    return tweets

def main():
    parser = argparse.ArgumentParser(
        description="Automated System Design & Tech Deep-Dive Thread Agent for X (Twitter)"
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Publish the generated thread directly to X (requires Twitter API credentials)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Generate and preview the thread without posting to X (Default behavior if --post is not set)."
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Specify a custom topic title or topic ID to write about."
    )
    parser.add_argument(
        "--list-topics",
        action="store_true",
        help="List all topics in the catalog and their posted status."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics on posted vs remaining topics."
    )
    parser.add_argument(
        "--brainstorm",
        action="store_true",
        help="Use AI to brainstorm a brand new, highly viral dual-audience topic on the fly."
    )
    parser.add_argument(
        "--test-twitter",
        action="store_true",
        help="Test connection to Twitter API v2 using configured credentials."
    )

    args = parser.parse_args()
    history = HistoryManager()

    if args.list_topics:
        topics = history.load_topics()
        posted_ids = history.get_posted_ids()
        print(f"\n📚 CATALOG OF TOPICS ({len(topics)} total):")
        print("-" * 75)
        for idx, t in enumerate(topics, 1):
            status = "✅ POSTED" if t["id"] in posted_ids else "⏳ PENDING"
            print(f"{idx:2d}. [{status}] {t['title']} ({t['category']})")
        print("-" * 75 + "\n")
        return

    if args.stats:
        s = history.stats()
        print("\n📊 AGENT TOPIC STATISTICS:")
        print(f"   Total Topics in Bank : {s['total_topics']}")
        print(f"   Already Posted       : {s['posted_count']}")
        print(f"   Remaining Queue      : {s['remaining_count']}\n")
        return

    if args.test_twitter:
        poster = TwitterPoster()
        success = poster.test_connection()
        sys.exit(0 if success else 1)

    # Default to dry-run unless --post is explicitly specified
    is_dry_run = not args.post or args.dry_run

    try:
        run(topic_query=args.topic, dry_run=is_dry_run, auto_brainstorm=args.brainstorm)
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
