"""
AI Analysis Engine - Hook Extraction, Pattern Classification, Niche Scoring
Uses OpenAI GPT-4o with structured JSON output for consistent results.
"""

import json
import logging
from typing import List, Optional

from openai import OpenAI

from social_sentinel.config import config
from social_sentinel.core.scraper import SocialPost

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """AI-powered analysis engine for social media posts."""

    def __init__(self):
        self.client = OpenAI(api_key=config.openai.api_key)

    def analyze_post(self, post: SocialPost) -> dict:
        """Analyze a single post: extract hook, classify pattern, score niche."""
        if not config.openai.is_configured:
            return self._fallback_analysis(post)

        system_prompt = """You are an expert growth hacker and content strategist.
Analyze social media posts and extract the following as JSON:

{
    "hook": "The exact hook (first 1-2 lines that grab attention)",
    "hook_type": "One of: List, Counter-Intuitive, Storytelling, FOMO, How-To, Hot Take, Data-Driven, Personal Story, Question, Metaphor",
    "niche": "Specific niche topic (e.g., 'AI Agents', 'Vibe Coding', 'LLM Monitoring')",
    "niche_score": 1-10 integer rating of this niche's profitability/virality potential",
    "why_viral": "Brief explanation of why this post performs well (max 50 words)",
    "emotional_trigger": "Primary emotion: Curiosity, Fear, Excitement, Validation, Urgency, Surprise"
}

Be precise. The hook should be the actual opening lines, not a summary."""

        user_prompt = f"""Analyze this post:

Platform: {post.platform}
Author: {post.author}
Text:
{post.text}

Engagement: {post.likes} likes, {post.reposts} reposts, {post.replies} replies"""

        try:
            response = self.client.chat.completions.create(
                model=config.openai.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=config.openai.temperature,
                max_tokens=config.openai.max_tokens_analysis,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"Analyzed post from {post.author} - Niche: {result.get('niche', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            # Fallback: basic heuristic analysis
            return self._fallback_analysis(post)

    def _fallback_analysis(self, post: SocialPost) -> dict:
        """Heuristic fallback when API is unavailable."""
        text = post.text.lower()

        # Pattern detection via keyword heuristics
        if any(w in text for w in ["unpopular opinion", "hot take", "contrarian"]):
            hook_type = "Counter-Intuitive"
        elif any(w in text for w in ["how i", "how to", "step by step", "here's how"]):
            hook_type = "How-To"
        elif any(w in text for w in ["story", "i spent", "i built", "i tried"]):
            hook_type = "Storytelling"
        elif any(w in text for w in ["don't miss", "before it's", "last chance", "everyone is"]):
            hook_type = "FOMO"
        elif any(w in text for w in ["data", "analyzed", "study", "research", "statistics"]):
            hook_type = "Data-Driven"
        elif any(w in text for w in ["stop", "never", "don't", "avoid", "mistake"]):
            hook_type = "Hot Take"
        else:
            hook_type = "List"

        # Niche detection
        niche_keywords = {
            "AI Agents": ["agent", "autonomous", "agentic"],
            "Vibe Coding": ["vibe coding", "vibecoding", "replit", "bolt.new"],
            "LLM Monitoring": ["monitoring", "observability", "llm ops", "tracing"],
            "AI Automation": ["automation", "workflow", "pipeline", "no-code"],
        }

        niche = "AI General"
        for n, keywords in niche_keywords.items():
            if any(k in text for k in keywords):
                niche = n
                break

        # Simple scoring based on engagement
        engagement = post.likes + (post.reposts * 2)
        niche_score = min(10, max(1, int(engagement / 500) + 3))

        return {
            "hook": post.hook,
            "hook_type": hook_type,
            "niche": niche,
            "niche_score": niche_score,
            "why_viral": f"High engagement ({engagement} score) on {post.platform}",
            "emotional_trigger": "Curiosity",
        }

    def analyze_batch(self, posts: List[SocialPost]) -> List[dict]:
        """Analyze multiple posts and enrich them with AI insights."""
        results = []

        for post in posts:
            analysis = self.analyze_post(post)
            post.niche = analysis.get("niche", "")
            post.pattern = analysis.get("hook_type", "")
            post.niche_score = analysis.get("niche_score", 0)
            results.append({
                "post": post,
                "analysis": analysis,
            })

        return results

    def generate_post(self, hooks_data: List[dict], platform: str = "linkedin") -> str:
        """Generate an optimized social post based on top-performing hooks."""
        if not config.openai.is_configured:
            return self._fallback_generate(hooks_data, platform)

        top_hooks = sorted(hooks_data, key=lambda x: x["analysis"].get("niche_score", 0), reverse=True)[:5]

        hooks_context = "\n".join([
            f"- Hook: \"{h['analysis'].get('hook', '')}\" | Pattern: {h['analysis'].get('hook_type', '')} | Niche: {h['analysis'].get('niche', '')}"
            for h in top_hooks
        ])

        system_prompt = f"""You are an expert social media content creator specializing in {platform} posts about AI, tech, and developer tools.

Generate a viral-optimized post for {platform} with these characteristics:
- Tone: Modern, technical but accessible, efficiency-focused (Vibe Coding style)
- Structure: Strong hook → Value delivery → Call to action
- Length: {"150-300 words for LinkedIn with line breaks for readability" if platform == "linkedin" else "200-280 characters for X/Twitter"}
- Use the best-performing hook patterns from the examples below

Format your response as plain text — no markdown, no explanations, just the post."""

        user_prompt = f"""Top performing hooks to draw inspiration from:

{hooks_context}

Generate a fresh, original post about AI Agents / Vibe Coding that uses the winning patterns above but is NOT a copy of any existing hook."""

        try:
            response = self.client.chat.completions.create(
                model=config.openai.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
                max_tokens=config.openai.max_tokens_generation,
            )

            generated = response.choices[0].message.content.strip()
            logger.info(f"Generated {platform} post ({len(generated)} chars)")
            return generated

        except Exception as e:
            logger.error(f"Post generation failed: {e}")
            return self._fallback_generate(top_hooks, platform)

    def _fallback_generate(self, hooks_data: List[dict], platform: str) -> str:
        """Template-based fallback post generation."""
        templates = {
            "linkedin": """🚀 The AI landscape is shifting faster than ever.

I've been tracking the top-performing content in AI Agents and Vibe Coding.

Here's what's working right now:

1️⃣ Authentic experimentation beats polished tutorials
2️⃣ "Build in public" generates 3x more engagement than announcements
3️⃣ Technical depth + simple language = viral combination

The creators winning right now aren't the ones with the biggest audience.
They're the ones shipping real projects and sharing the messy middle.

What AI tool changed your workflow this week? Drop it below 👇

#AIAgents #VibeCoding #BuildInPublic #AI""",
            "twitter": """Hot take: Vibe Coding isn't a trend -- it's the new default.

I analyzed 500+ viral AI posts this week. The pattern is clear:

People don't want tutorials. They want proof.

Ship something. Share the messy parts. Repeat.

The best AI builders aren't teaching -- they're showing.""",
        }
        return templates.get(platform, templates["linkedin"])
