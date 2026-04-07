"""
Scraper Module - Social Media Data Extraction
Supports Apify actors for X/Twitter, LinkedIn, Threads.
Falls back to mock data for development/testing.
"""

import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from social_sentinel.config import config

logger = logging.getLogger(__name__)


@dataclass
class SocialPost:
    """Normalized social media post representation."""
    id: str
    platform: str
    author: str
    author_handle: str
    text: str
    hook: str  # First 2 lines
    likes: int
    reposts: int
    replies: int
    engagement_score: float
    url: str
    created_at: str
    niche: str = ""
    pattern: str = ""
    niche_score: float = 0.0

    def __post_init__(self):
        if not self.engagement_score:
            self.engagement_score = self.likes + (self.reposts * 2)


class MockDataGenerator:
    """Generate realistic mock data for development/testing."""

    MOCK_AUTHORS = [
        ("Andrej Karpathy", "@karpathy"),
        ("Jim Fan", "@DrJimFan"),
        ("Andrew Ng", "@AndrewYNg"),
        ("Swaroop CH", "@swaroopch"),
        ("Elon Musk", "@elonmusk"),
        ("Ethan Mollick", "@emorick"),
        ("Lilian Weng", "@lilianweng"),
        ("Clem Delangue", "@clem"),
        ("Arav Srinivas", "@aravsrinivas"),
        ("Amjad Masad", "@amasad"),
    ]

    MOCK_HOOKS_TEMPLATES = [
        "I spent 100 hours building AI agents. Here's what nobody tells you:\n\n{detail}",
        "Unpopular opinion: {detail}\n\nHere's why I'm right:",
        "The AI tool that changed my workflow forever:\n\n{detail}",
        "Stop using {tool} for AI automation. Use this instead:\n\n{detail}",
        "I analyzed 10,000 AI agent workflows. The pattern is clear:\n\n{detail}",
        "Everyone is sleeping on this AI trend:\n\n{detail}\n\nThread 🧵",
        "How I built a $10k/mo AI automation agency in 30 days:\n\n{detail}",
        "The biggest lie about AI Agents in 2026:\n\n{detail}",
        "Vibe Coding just killed traditional development. Here's the proof:\n\n{detail}",
        "LLM monitoring is the next gold rush. Here's my playbook:\n\n{detail}",
        "I replaced 5 tools with one AI agent. Here's the stack:\n\n{detail}",
        "Hot take: {detail}\n\nAnd here's the data to prove it.",
    ]

    MOCK_DETAILS = [
        "Most agents fail at context retention after 3 turns.",
        "The real bottleneck isn't the model — it's the orchestration layer.",
        "Replit Agent changed how I prototype. 10x faster.",
        "LangGraph is overkill for 90% of use cases.",
        "The best AI agents use simple state machines, not complex graphs.",
        "Prompt engineering is dead. Context engineering is the future.",
        "Vibe coding means writing code through conversation, not syntax.",
        "Autonomous agents will replace 40% of SaaS tools by 2027.",
        "The companies winning at AI aren't using the biggest models.",
        "Your AI agent needs memory, not more parameters.",
    ]

    MOCK_TOOLS = ["LangChain", "AutoGen", "CrewAI", "LangGraph", "LlamaIndex"]

    NICHES = [
        "AI Agents", "Vibe Coding", "LLM Monitoring", "AI Automation",
        "Agentic Workflows", "AI Coding Assistants", "Autonomous Agents",
        "AI Infrastructure",
    ]

    @classmethod
    def generate_posts(cls, count: int = 20) -> List[SocialPost]:
        """Generate realistic mock social posts."""
        posts = []
        for i in range(count):
            author, handle = random.choice(cls.MOCK_AUTHORS)
            detail = random.choice(cls.MOCK_DETAILS)
            template = random.choice(cls.MOCK_HOOKS_TEMPLATES)
            tool = random.choice(cls.MOCK_TOOLS)
            niche = random.choice(cls.NICHES)

            hook = template.format(detail=detail, tool=tool)
            full_text = hook + "\n\n" + " ".join(random.sample(cls.MOCK_DETAILS, k=3))

            likes = random.randint(50, 15000)
            reposts = random.randint(10, 3000)
            replies = random.randint(5, 500)

            platform = random.choice(["twitter", "linkedin", "threads"])

            post = SocialPost(
                id=f"mock_{platform}_{i}_{int(time.time())}",
                platform=platform,
                author=author,
                author_handle=handle,
                text=full_text,
                hook=hook.split("\n\n")[0] if "\n\n" in hook else hook[:150],
                likes=likes,
                reposts=reposts,
                replies=replies,
                engagement_score=likes + (reposts * 2),
                url=f"https://{platform}.com/post/{i}",
                created_at=(datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
                niche=niche,
            )
            posts.append(post)

        # Sort by engagement score descending
        posts.sort(key=lambda p: p.engagement_score, reverse=True)
        return posts


class SocialScraper:
    """Main scraper orchestrator. Routes to Apify or mock data."""

    def __init__(self):
        self.apify_client = None
        if not config.scraping.use_mock_data and config.apify.api_key:
            try:
                from apify_client import ApifyClient
                self.apify_client = ApifyClient(config.apify.api_key)
                logger.info("Apify client initialized successfully.")
            except ImportError:
                logger.warning("apify-client not installed. Falling back to mock data.")
                config.scraping.use_mock_data = True

    def scrape_all(self) -> List[SocialPost]:
        """Scrape posts from all configured platforms."""
        all_posts = []

        if config.scraping.use_mock_data or not self.apify_client:
            logger.info("Using mock data generator.")
            all_posts = MockDataGenerator.generate_posts(
                count=config.scraping.max_posts_per_keyword
            )
        else:
            for keyword in config.scraping.keywords:
                for platform in config.scraping.platforms:
                    posts = self._scrape_platform(keyword, platform)
                    all_posts.extend(posts)
                    time.sleep(1)  # Rate limiting courtesy

        # Filter by minimum engagement
        filtered = [
            p for p in all_posts
            if p.engagement_score >= config.scraping.min_engagement_score
        ]

        logger.info(f"Scraped {len(all_posts)} posts, {len(filtered)} passed engagement filter.")
        return filtered

    def _scrape_platform(self, keyword: str, platform: str) -> List[SocialPost]:
        """Scrape a specific platform for a keyword via Apify."""
        posts = []

        try:
            if platform == "twitter":
                posts = self._scrape_twitter(keyword)
            elif platform == "linkedin":
                posts = self._scrape_linkedin(keyword)
            elif platform == "threads":
                posts = self._scrape_threads(keyword)
        except Exception as e:
            logger.error(f"Error scraping {platform} for '{keyword}': {e}")

        return posts

    def _scrape_twitter(self, keyword: str) -> List[SocialPost]:
        """Scrape Twitter/X via Apify quacker actor."""
        run_input = {
            "searchTerms": [keyword],
            "maxTweets": config.scraping.max_posts_per_keyword,
            "sort": "Top",
        }

        run = self.apify_client.actor(config.apify.twitter_scraper_actor).call(run_input=run_input)
        posts = []

        for item in self.apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append(SocialPost(
                id=item.get("id", f"tw_{random.randint(1000, 9999)}"),
                platform="twitter",
                author=item.get("author", {}).get("name", "Unknown"),
                author_handle=item.get("author", {}).get("userName", ""),
                text=item.get("fullText", item.get("text", "")),
                hook=item.get("fullText", item.get("text", ""))[:200],
                likes=item.get("metrics", {}).get("likes", 0),
                reposts=item.get("metrics", {}).get("retweets", 0),
                replies=item.get("metrics", {}).get("replies", 0),
                engagement_score=item.get("metrics", {}).get("likes", 0) +
                                item.get("metrics", {}).get("retweets", 0) * 2,
                url=item.get("url", ""),
                created_at=item.get("createdAt", datetime.now().isoformat()),
            ))

        return posts

    def _scrape_linkedin(self, keyword: str) -> List[SocialPost]:
        """Scrape LinkedIn via Apify data-slayer actor."""
        run_input = {
            "searchKeywords": [keyword],
            "maxPosts": config.scraping.max_posts_per_keyword,
        }

        run = self.apify_client.actor(config.apify.linkedin_scraper_actor).call(run_input=run_input)
        posts = []

        for item in self.apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append(SocialPost(
                id=item.get("id", f"li_{random.randint(1000, 9999)}"),
                platform="linkedin",
                author=item.get("authorName", "Unknown"),
                author_handle=item.get("authorUrl", ""),
                text=item.get("text", ""),
                hook=item.get("text", "")[:200],
                likes=item.get("likes", 0),
                reposts=item.get("reposts", 0),
                replies=item.get("comments", 0),
                engagement_score=item.get("likes", 0) + item.get("reposts", 0) * 2,
                url=item.get("url", ""),
                created_at=item.get("timestamp", datetime.now().isoformat()),
            ))

        return posts

    def _scrape_threads(self, keyword: str) -> List[SocialPost]:
        """Scrape Threads via Apify automation-lab actor."""
        run_input = {
            "searchQuery": keyword,
            "maxThreads": config.scraping.max_posts_per_keyword,
        }

        run = self.apify_client.actor(config.apify.threads_scraper_actor).call(run_input=run_input)
        posts = []

        for item in self.apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append(SocialPost(
                id=item.get("id", f"th_{random.randint(1000, 9999)}"),
                platform="threads",
                author=item.get("username", "Unknown"),
                author_handle=item.get("username", ""),
                text=item.get("text", ""),
                hook=item.get("text", "")[:200],
                likes=item.get("like_count", 0),
                reposts=item.get("repost_count", 0),
                replies=item.get("reply_count", 0),
                engagement_score=item.get("like_count", 0) + item.get("repost_count", 0) * 2,
                url=item.get("url", ""),
                created_at=item.get("timestamp", datetime.now().isoformat()),
            ))

        return posts
