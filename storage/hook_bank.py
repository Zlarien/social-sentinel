"""
Hook Bank - Storage Layer
SQLite + JSON storage with cosine similarity deduplication.
"""

import hashlib
import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import List, Optional

from social_sentinel.config import config

logger = logging.getLogger(__name__)


class HookBank:
    """Persistent storage for unique hooks with deduplication."""

    def __init__(self):
        self.db_path = config.storage.sqlite_path
        self.json_path = config.storage.json_path
        self._ensure_dirs()
        self._init_db()

    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)

    def _init_db(self):
        """Create SQLite tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hooks (
                    id TEXT PRIMARY KEY,
                    hook_text TEXT NOT NULL,
                    hook_type TEXT,
                    niche TEXT,
                    niche_score REAL,
                    platform TEXT,
                    author TEXT,
                    emotional_trigger TEXT,
                    why_viral TEXT,
                    post_id TEXT,
                    created_at TEXT,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    embedding_hash TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_niche ON hooks(niche)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_niche_score ON hooks(niche_score DESC)
            """)
            conn.commit()
        logger.info(f"HookBank initialized: {self.db_path}")

    def _compute_hash(self, text: str) -> str:
        """Compute a simple hash for quick dedup checks."""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Simple word-level cosine similarity for dedup."""
        def tokenize(text: str) -> dict:
            words = text.lower().split()
            freq = {}
            for w in words:
                freq[w] = freq.get(w, 0) + 1
            return freq

        def dot_product(v1: dict, v2: dict) -> float:
            common_keys = set(v1.keys()) & set(v2.keys())
            return sum(v1[k] * v2[k] for k in common_keys)

        def magnitude(v: dict) -> float:
            return sum(x ** 2 for x in v.values()) ** 0.5

        vec1 = tokenize(text1)
        vec2 = tokenize(text2)

        mag1 = magnitude(vec1)
        mag2 = magnitude(vec2)

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product(vec1, vec2) / (mag1 * mag2)

    def is_duplicate(self, hook_text: str) -> bool:
        """Check if a hook already exists (hash match + similarity check)."""
        hook_hash = self._compute_hash(hook_text)

        with sqlite3.connect(self.db_path) as conn:
            # Exact hash match
            cursor = conn.execute(
                "SELECT hook_text FROM hooks WHERE embedding_hash = ?", (hook_hash,)
            )
            exact_match = cursor.fetchone()
            if exact_match:
                return True

            # Similarity check against recent hooks
            cursor = conn.execute(
                "SELECT hook_text FROM hooks ORDER BY added_at DESC LIMIT 100"
            )
            rows = cursor.fetchall()

        for (existing_text,) in rows:
            similarity = self._cosine_similarity(hook_text, existing_text)
            if similarity >= config.storage.similarity_threshold:
                logger.debug(f"Duplicate detected (similarity: {similarity:.2f})")
                return True

        return False

    def add_hook(self, hook_text: str, analysis: dict, post=None) -> bool:
        """Add a hook to the bank. Returns False if duplicate."""
        if self.is_duplicate(hook_text):
            logger.info(f"Skipping duplicate hook: {hook_text[:50]}...")
            return False

        hook_hash = self._compute_hash(hook_text)
        hook_id = hashlib.sha256(f"{hook_text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO hooks (
                    id, hook_text, hook_type, niche, niche_score,
                    platform, author, emotional_trigger, why_viral,
                    post_id, created_at, embedding_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hook_id,
                hook_text,
                analysis.get("hook_type", ""),
                analysis.get("niche", ""),
                analysis.get("niche_score", 0),
                post.platform if post else "",
                post.author if post else "",
                analysis.get("emotional_trigger", ""),
                analysis.get("why_viral", ""),
                post.id if post else "",
                post.created_at if post else datetime.now().isoformat(),
                hook_hash,
            ))
            conn.commit()

        self._sync_json()
        logger.info(f"Added new hook: {hook_text[:50]}...")
        return True

    def add_batch(self, analyzed_posts: List[dict]) -> int:
        """Add multiple hooks from analyzed posts. Returns count added."""
        added = 0
        for item in analyzed_posts:
            post = item["post"]
            analysis = item["analysis"]
            hook_text = analysis.get("hook", post.hook)
            if self.add_hook(hook_text, analysis, post):
                added += 1
        logger.info(f"Added {added} new hooks out of {len(analyzed_posts)} processed.")
        return added

    def get_top_hooks(self, limit: int = 10, niche: Optional[str] = None) -> List[dict]:
        """Get top hooks by niche score."""
        with sqlite3.connect(self.db_path) as conn:
            if niche:
                cursor = conn.execute(
                    "SELECT * FROM hooks WHERE niche = ? ORDER BY niche_score DESC LIMIT ?",
                    (niche, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM hooks ORDER BY niche_score DESC LIMIT ?",
                    (limit,)
                )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_trending_niches(self, limit: int = 5) -> List[dict]:
        """Get niches with highest average scores and most hooks."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT niche,
                       COUNT(*) as hook_count,
                       AVG(niche_score) as avg_score,
                       MAX(niche_score) as max_score
                FROM hooks
                WHERE niche != ''
                GROUP BY niche
                ORDER BY avg_score DESC, hook_count DESC
                LIMIT ?
            """, (limit,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        """Get overall Hook Bank statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM hooks").fetchone()[0]
            niches = conn.execute(
                "SELECT COUNT(DISTINCT niche) FROM hooks WHERE niche != ''"
            ).fetchone()[0]
            platforms = conn.execute(
                "SELECT COUNT(DISTINCT platform) FROM hooks WHERE platform != ''"
            ).fetchone()[0]
            avg_score = conn.execute(
                "SELECT AVG(niche_score) FROM hooks"
            ).fetchone()[0] or 0

        return {
            "total_hooks": total,
            "unique_niches": niches,
            "platforms_tracked": platforms,
            "avg_niche_score": round(avg_score, 2),
        }

    def _sync_json(self):
        """Sync SQLite data to JSON file for portability."""
        hooks = self.get_top_hooks(limit=1000)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(hooks, f, indent=2, ensure_ascii=False)
        logger.debug(f"Synced {len(hooks)} hooks to {self.json_path}")

    def export_json(self) -> str:
        """Export entire hook bank as JSON string."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM hooks ORDER BY niche_score DESC")
            columns = [desc[0] for desc in cursor.description]
            hooks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return json.dumps(hooks, indent=2, ensure_ascii=False)
