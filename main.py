"""
Social Sentinel - Main Orchestrator
Ties together scraping, analysis, storage, and content generation.
"""

import logging
import os
import sys
import io
from datetime import datetime

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from social_sentinel.config import config
from social_sentinel.core.scraper import SocialScraper
from social_sentinel.core.analyzer import AnalysisEngine
from social_sentinel.storage.hook_bank import HookBank

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "data", "sentinel.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class SocialSentinel:
    """Main orchestrator for the Social Sentinel pipeline."""

    def __init__(self):
        self.scraper = SocialScraper()
        self.analyzer = AnalysisEngine()
        self.hook_bank = HookBank()

    def run_pipeline(self, generate_post: bool = True, platform: str = "linkedin") -> dict:
        """
        Execute the full Social Sentinel pipeline:
        1. Scrape posts from social platforms
        2. Analyze with AI (hook extraction, pattern classification, niche scoring)
        3. Store unique hooks in Hook Bank
        4. Generate optimized content
        5. Return summary report
        """
        logger.info("=" * 60)
        logger.info("SOCIAL SENTINEL - Pipeline Started")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)

        # Step 1: Scrape
        logger.info("Step 1: Scraping social posts...")
        posts = self.scraper.scrape_all()
        logger.info(f"  -> {len(posts)} posts collected")

        if not posts:
            logger.warning("No posts found. Check your API configuration.")
            return {"status": "no_data", "posts_scraped": 0}

        # Step 2: Analyze
        logger.info("Step 2: Analyzing posts with AI...")
        analyzed = self.analyzer.analyze_batch(posts)
        logger.info(f"  -> {len(analyzed)} posts analyzed")

        # Step 3: Store hooks
        logger.info("Step 3: Storing unique hooks...")
        hooks_added = self.hook_bank.add_batch(analyzed)
        logger.info(f"  -> {hooks_added} new hooks added to bank")

        # Step 4: Generate content
        generated_post = None
        if generate_post:
            logger.info(f"Step 4: Generating optimized {platform} post...")
            generated_post = self.analyzer.generate_post(analyzed, platform=platform)
            logger.info(f"  -> Post generated ({len(generated_post)} chars)")

        # Step 5: Build report
        stats = self.hook_bank.get_stats()
        trending = self.hook_bank.get_trending_niches(limit=5)
        top_hooks = self.hook_bank.get_top_hooks(limit=5)

        report = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "posts_scraped": len(posts),
            "posts_analyzed": len(analyzed),
            "hooks_added": hooks_added,
            "generated_post": generated_post,
            "stats": stats,
            "trending_niches": trending,
            "top_hooks": top_hooks,
        }

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"  Posts: {len(posts)} | Hooks Added: {hooks_added} | Total in Bank: {stats['total_hooks']}")
        logger.info("=" * 60)

        return report


def print_report(report: dict):
    """Print a formatted markdown-style report to console."""
    if report.get("status") != "success":
        print(f"\nPipeline status: {report.get('status', 'unknown')}")
        return

    print("\n" + "=" * 60)
    print("📊 SOCIAL SENTINEL - DAILY REPORT")
    print("=" * 60)

    stats = report["stats"]
    print(f"\n📈 Hook Bank Stats:")
    print(f"   Total Hooks: {stats['total_hooks']}")
    print(f"   Unique Niches: {stats['unique_niches']}")
    print(f"   Avg Niche Score: {stats['avg_niche_score']}/10")

    trending = report.get("trending_niches", [])
    if trending:
        print(f"\n🔥 Trending Niches:")
        for i, niche in enumerate(trending, 1):
            print(f"   {i}. {niche['niche']} (Score: {niche['avg_score']:.1f}, {niche['hook_count']} hooks)")

    top = report.get("top_hooks", [])
    if top:
        print(f"\n🏆 Top Hook of the Day:")
        best = top[0]
        print(f"   \"{best['hook_text'][:120]}...\"")
        print(f"   Pattern: {best['hook_type']} | Niche: {best['niche']} | Score: {best['niche_score']}/10")

    post = report.get("generated_post")
    if post:
        print(f"\n📝 Generated Post (ready to publish):")
        print("-" * 40)
        print(post)
        print("-" * 40)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Social Sentinel - Automated Content Intelligence")
    parser.add_argument("--platform", choices=["linkedin", "twitter"], default="linkedin",
                        help="Target platform for generated post")
    parser.add_argument("--no-generate", action="store_true",
                        help="Skip content generation")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress console output")
    args = parser.parse_args()

    sentinel = SocialSentinel()
    report = sentinel.run_pipeline(
        generate_post=not args.no_generate,
        platform=args.platform,
    )

    if not args.quiet:
        print_report(report)
