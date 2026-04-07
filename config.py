"""
Social Sentinel - Configuration Module
Centralized settings, API keys, and threshold management.
"""

import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    temperature: float = 0.7
    max_tokens_analysis: int = 1024
    max_tokens_generation: int = 2048

    @property
    def is_configured(self) -> bool:
        """Check if API key is set and looks valid."""
        return bool(self.api_key and self.api_key.startswith("sk-"))


@dataclass
class ApifyConfig:
    """Apify scraping configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("APIFY_API_KEY", ""))
    twitter_scraper_actor: str = "quacker/twitter-scraper"
    linkedin_scraper_actor: str = "data-slayer/linkedin-post-analytics-scraper"
    threads_scraper_actor: str = "automation-lab/threads-scraper"


@dataclass
class ScrapingConfig:
    """Scraping parameters and keyword lists."""
    keywords: List[str] = field(default_factory=lambda: [
        "AI Agents",
        "Vibe Coding",
        "LLM monitoring",
        "AI Automation",
        "agentic workflows",
        "AI coding assistant",
        "autonomous agents",
        "AI infrastructure",
    ])
    platforms: List[str] = field(default_factory=lambda: ["twitter", "linkedin", "threads"])
    min_engagement_score: float = 5.0  # Minimum likes+reposts threshold
    max_posts_per_keyword: int = 20
    use_mock_data: bool = field(default_factory=lambda: os.getenv("USE_MOCK_DATA", "true").lower() == "true")


@dataclass
class StorageConfig:
    """Storage paths and dedup settings."""
    sqlite_path: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "hook_bank.db"
    ))
    json_path: str = field(default_factory=lambda: os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "hook_bank.json"
    ))
    similarity_threshold: float = 0.85  # Cosine similarity threshold for dedup


@dataclass
class AppConfig:
    """Master configuration."""
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    apify: ApifyConfig = field(default_factory=ApifyConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


# Global config instance
config = AppConfig()
