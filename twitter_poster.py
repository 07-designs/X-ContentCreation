import time
import logging
from typing import List, Optional
import tweepy
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)

logger = logging.getLogger(__name__)

class TwitterPoster:
    """Publishes connected multi-tweet threads to X (Twitter) using API v2."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
    ):
        self.api_key = api_key or TWITTER_API_KEY
        self.api_secret = api_secret or TWITTER_API_SECRET
        self.access_token = access_token or TWITTER_ACCESS_TOKEN
        self.access_token_secret = access_token_secret or TWITTER_ACCESS_TOKEN_SECRET
        self._client = None

    def _get_client(self) -> tweepy.Client:
        """Initializes and returns an authenticated tweepy.Client."""
        if self._client is not None:
            return self._client

        missing = []
        if not self.api_key: missing.append("TWITTER_API_KEY")
        if not self.api_secret: missing.append("TWITTER_API_SECRET")
        if not self.access_token: missing.append("TWITTER_ACCESS_TOKEN")
        if not self.access_token_secret: missing.append("TWITTER_ACCESS_TOKEN_SECRET")

        if missing:
            raise ValueError(
                f"Missing Twitter credentials: {', '.join(missing)}.\n"
                "Please add them to your .env file or repository secrets.\n"
                "Get your keys for free at: https://developer.x.com\n"
                "NOTE: In the Twitter Developer Portal, ensure your App permissions are set to 'Read and Write'!"
            )

        self._client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        return self._client

    def test_connection(self) -> bool:
        """Tests if credentials can authenticate with X API v2."""
        try:
            client = self._get_client()
            me = client.get_me()
            logger.info(f"Successfully authenticated as @{me.data.username} (ID: {me.data.id})")
            return True
        except Exception as e:
            logger.error(f"Twitter authentication test failed: {e}")
            return False

    def post_thread(self, tweets: List[str], delay_between_tweets: float = 2.0) -> List[str]:
        """
        Posts a series of tweets sequentially, chaining each as a reply to the previous tweet.
        Returns the list of created Tweet IDs.
        """
        if not tweets:
            raise ValueError("Cannot post an empty tweet thread.")

        client = self._get_client()
        tweet_ids = []
        previous_id = None

        logger.info(f"Starting publication of {len(tweets)}-part thread to X...")

        for idx, tweet_text in enumerate(tweets, 1):
            try:
                if previous_id is None:
                    # First tweet of the thread
                    logger.info(f"Publishing Tweet 1/{len(tweets)} (The Hook)...")
                    response = client.create_tweet(text=tweet_text)
                else:
                    # Subsequent tweets reply to previous
                    logger.info(f"Publishing Tweet {idx}/{len(tweets)} as reply to ID {previous_id}...")
                    response = client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_id
                    )

                new_id = response.data["id"]
                tweet_ids.append(new_id)
                previous_id = new_id

                # Brief sleep between posts to respect rate limits and order
                if idx < len(tweets):
                    time.sleep(delay_between_tweets)

            except tweepy.TweepyException as e:
                logger.error(f"Error publishing tweet {idx}: {e}")
                # If subsequent tweet failed, we still return the tweet IDs published so far
                raise e

        logger.info(f"Thread published successfully! First Tweet URL: https://x.com/i/web/status/{tweet_ids[0]}")
        return tweet_ids
