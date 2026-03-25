"""
E-Labz Memory Service — Powered by GoodMem ADK Plugin
Persistent, searchable memory across all conversations and engagements.

This gives the swarm a "brain" that remembers:
- Who it talked to and what they care about
- Which content strategies performed best
- Audience preferences and relationship history
- Revenue patterns and product interest signals

Install: pip install goodmem-adk google-adk
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("memory_service")

# ============================================================
# CONFIGURATION
# ============================================================

GOODMEM_BASE_URL = os.getenv("GOODMEM_BASE_URL", "http://localhost:8080")
GOODMEM_API_KEY = os.getenv("GOODMEM_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MEMORY_DB = Path(__file__).parent.parent / "data" / "memory.db"


class MemoryService:
    """
    Persistent memory for the E-Labz swarm.
    
    Two modes:
    1. LOCAL mode (default) — SQLite-backed memory with vector-like search
       Works without external dependencies, good for development.
    2. GOODMEM mode — Full vector-based semantic memory via GoodMem plugin
       Production-grade, requires GoodMem instance + API key.
    
    The swarm remembers relationships, strategies, and performance data
    across all sessions — just like a person would.
    """
    
    def __init__(self, mode: str = "auto"):
        """
        Initialize memory service.
        
        Args:
            mode: "local" (SQLite), "goodmem" (cloud), or "auto" (try goodmem, fall back to local)
        """
        self.mode = mode
        self._goodmem_available = False
        
        if mode in ("auto", "goodmem"):
            self._try_init_goodmem()
        
        if not self._goodmem_available:
            self.mode = "local"
            self._init_local()
            
        logger.info(f"🧠 Memory service initialized in {self.mode} mode")
    
    # ============================================================
    # GOODMEM INTEGRATION
    # ============================================================
    
    def _try_init_goodmem(self):
        """Try to initialize GoodMem plugin."""
        if not GOODMEM_API_KEY:
            logger.info("No GOODMEM_API_KEY set, falling back to local memory")
            return
            
        try:
            from goodmem_adk import GoodmemPlugin, GoodmemSaveTool, GoodmemFetchTool
            
            self._plugin = GoodmemPlugin(
                base_url=GOODMEM_BASE_URL,
                api_key=GOODMEM_API_KEY,
                top_k=5,
            )
            self._save_tool = GoodmemSaveTool(
                base_url=GOODMEM_BASE_URL,
                api_key=GOODMEM_API_KEY,
            )
            self._fetch_tool = GoodmemFetchTool(
                base_url=GOODMEM_BASE_URL,
                api_key=GOODMEM_API_KEY,
                top_k=5,
            )
            self._goodmem_available = True
            self.mode = "goodmem"
            logger.info("🧠 GoodMem plugin initialized successfully")
        except ImportError:
            logger.info("goodmem-adk not installed, using local memory")
        except Exception as e:
            logger.warning(f"GoodMem init failed: {e}, using local memory")
    
    # ============================================================
    # LOCAL SQLITE MEMORY (Works without GoodMem)
    # ============================================================
    
    def _init_local(self):
        """Initialize SQLite-backed local memory."""
        MEMORY_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(MEMORY_DB))
        c = conn.cursor()
        
        # Relationship memory — who we've talked to and what they care about
        c.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                interaction_type TEXT NOT NULL,  -- replied, liked, mentioned
                topic TEXT,
                sentiment TEXT,  -- positive, neutral, negative
                context TEXT,  -- what we said / what they said
                engagement_score REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, interaction_type, context)
            )
        """)
        
        # Strategy memory — what content approaches worked
        c.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_type TEXT NOT NULL,  -- tweet_style, topic, cta_type, time_slot
                strategy_value TEXT NOT NULL,
                performance_score REAL DEFAULT 0,
                sample_count INTEGER DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                UNIQUE(strategy_type, strategy_value)
            )
        """)
        
        # Content memory — what content has been created and its performance
        c.execute("""
            CREATE TABLE IF NOT EXISTS content_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                content_type TEXT,  -- tweet, thread, reply
                content_text TEXT,
                topic TEXT,
                performance_score REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Revenue memory — product interest signals
        c.execute("""
            CREATE TABLE IF NOT EXISTS revenue_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                signal_type TEXT,  -- clicked_link, asked_about, mentioned_product
                product_id TEXT,
                context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"🧠 Local memory initialized: {MEMORY_DB}")
    
    # ============================================================
    # PUBLIC API — Same interface regardless of backend
    # ============================================================
    
    def remember_relationship(self, username: str, interaction_type: str,
                               topic: str = "", context: str = "",
                               sentiment: str = "neutral",
                               engagement_score: float = 0.0):
        """
        Remember an interaction with someone.
        
        E-Labz remembers everyone it talks to, just like a real person.
        """
        if self.mode == "goodmem":
            self._goodmem_save(
                space="engagement_memory",
                content=f"Interaction with @{username}: {interaction_type} about {topic}. "
                        f"Context: {context}. Sentiment: {sentiment}",
                metadata={"username": username, "type": interaction_type}
            )
        else:
            self._local_save_relationship(
                username, interaction_type, topic, context, sentiment, engagement_score
            )
    
    def recall_relationship(self, username: str) -> List[Dict]:
        """
        Recall everything we know about someone.
        
        Returns past interactions, their interests, and relationship history.
        """
        if self.mode == "goodmem":
            return self._goodmem_fetch(
                space="engagement_memory",
                query=f"interactions with @{username}"
            )
        else:
            return self._local_get_relationship(username)
    
    def remember_strategy(self, strategy_type: str, strategy_value: str,
                          performance_score: float, notes: str = ""):
        """
        Remember what content strategies work.
        
        The swarm learns from its own performance data.
        """
        if self.mode == "goodmem":
            self._goodmem_save(
                space="strategy_memory",
                content=f"Strategy: {strategy_type}={strategy_value}, "
                        f"score={performance_score}. {notes}"
            )
        else:
            self._local_save_strategy(
                strategy_type, strategy_value, performance_score, notes
            )
    
    def recall_best_strategies(self, strategy_type: str = None, limit: int = 5) -> List[Dict]:
        """
        Recall the best-performing strategies.
        """
        if self.mode == "goodmem":
            query = f"best performing {strategy_type or 'content'} strategies"
            return self._goodmem_fetch(space="strategy_memory", query=query)
        else:
            return self._local_get_best_strategies(strategy_type, limit)
    
    def remember_content(self, content_text: str, content_type: str,
                         topic: str = "", performance_score: float = 0.0):
        """Remember content that was created."""
        import hashlib
        content_hash = hashlib.md5(content_text.encode()).hexdigest()
        
        if self.mode == "goodmem":
            self._goodmem_save(
                space="content_memory",
                content=f"[{content_type}] {content_text[:200]}"
            )
        else:
            self._local_save_content(content_hash, content_type, content_text, topic, performance_score)
    
    def recall_similar_content(self, query: str, limit: int = 5) -> List[Dict]:
        """Find content similar to a query — avoid repeating ourselves."""
        if self.mode == "goodmem":
            return self._goodmem_fetch(space="content_memory", query=query)
        else:
            return self._local_search_content(query, limit)
    
    def remember_revenue_signal(self, username: str, signal_type: str,
                                 product_id: str = "", context: str = ""):
        """Track product interest signals for targeted selling."""
        if self.mode == "goodmem":
            self._goodmem_save(
                space="revenue_memory",
                content=f"Revenue signal: @{username} {signal_type} product {product_id}. {context}"
            )
        else:
            self._local_save_revenue_signal(username, signal_type, product_id, context)
    
    def get_engagement_context(self, username: str) -> str:
        """
        Get a natural-language context summary for replying to someone.
        
        Returns something like:
        "You've talked to @username 3 times before. They're interested in 
        AI automation workflows. Last time you discussed n8n vs Zapier.
        They seem warm to product recommendations."
        """
        memories = self.recall_relationship(username)
        if not memories:
            return f"First time interacting with @{username}. No prior history."
        
        interactions = len(memories)
        topics = list(set(m.get("topic", "") for m in memories if m.get("topic")))
        last_context = memories[-1].get("context", "") if memories else ""
        
        context = f"You've interacted with @{username} {interactions} time(s) before."
        if topics:
            context += f" They're interested in: {', '.join(topics[:3])}."
        if last_context:
            context += f" Last interaction: {last_context[:100]}."
        
        return context
    
    # ============================================================
    # GOODMEM BACKEND
    # ============================================================
    
    def _goodmem_save(self, space: str, content: str, metadata: dict = None):
        """Save to GoodMem vector memory."""
        try:
            # The save tool handles space creation and embedding automatically
            self._save_tool.run(content=content, space_name=space)
        except Exception as e:
            logger.warning(f"GoodMem save failed: {e}")
            # Fall back to local
            self._local_fallback_save(space, content)
    
    def _goodmem_fetch(self, space: str, query: str) -> List[Dict]:
        """Fetch from GoodMem vector memory."""
        try:
            results = self._fetch_tool.run(query=query, space_name=space)
            return [{"content": r.get("content", ""), "score": r.get("score", 0)} 
                    for r in results] if results else []
        except Exception as e:
            logger.warning(f"GoodMem fetch failed: {e}")
            return []
    
    # ============================================================
    # LOCAL SQLITE BACKEND
    # ============================================================
    
    def _local_save_relationship(self, username, interaction_type, topic, 
                                  context, sentiment, engagement_score):
        """Save relationship to SQLite."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO relationships 
                (username, interaction_type, topic, context, sentiment, engagement_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, interaction_type, topic, context, sentiment, engagement_score))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Memory save failed: {e}")
    
    def _local_get_relationship(self, username: str) -> List[Dict]:
        """Get all memories about a user."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            c.execute("""
                SELECT interaction_type, topic, context, sentiment, 
                       engagement_score, created_at
                FROM relationships WHERE username = ?
                ORDER BY created_at DESC LIMIT 20
            """, (username,))
            rows = c.fetchall()
            conn.close()
            return [
                {
                    "interaction_type": r[0], "topic": r[1], "context": r[2],
                    "sentiment": r[3], "engagement_score": r[4], "created_at": r[5]
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning(f"Memory recall failed: {e}")
            return []
    
    def _local_save_strategy(self, strategy_type, strategy_value, 
                              performance_score, notes):
        """Save strategy performance."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            c.execute("""
                INSERT INTO strategies (strategy_type, strategy_value, 
                                        performance_score, sample_count, notes)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(strategy_type, strategy_value) DO UPDATE SET
                    performance_score = (performance_score * sample_count + ?) / (sample_count + 1),
                    sample_count = sample_count + 1,
                    last_updated = CURRENT_TIMESTAMP,
                    notes = ?
            """, (strategy_type, strategy_value, performance_score, 
                  notes, performance_score, notes))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Strategy save failed: {e}")
    
    def _local_get_best_strategies(self, strategy_type=None, limit=5) -> List[Dict]:
        """Get top-performing strategies."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            
            if strategy_type:
                c.execute("""
                    SELECT strategy_type, strategy_value, performance_score, 
                           sample_count, notes
                    FROM strategies WHERE strategy_type = ?
                    ORDER BY performance_score DESC LIMIT ?
                """, (strategy_type, limit))
            else:
                c.execute("""
                    SELECT strategy_type, strategy_value, performance_score, 
                           sample_count, notes
                    FROM strategies
                    ORDER BY performance_score DESC LIMIT ?
                """, (limit,))
            
            rows = c.fetchall()
            conn.close()
            return [
                {
                    "strategy_type": r[0], "strategy_value": r[1],
                    "performance_score": r[2], "sample_count": r[3], "notes": r[4]
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning(f"Strategy recall failed: {e}")
            return []
    
    def _local_save_content(self, content_hash, content_type, content_text,
                             topic, performance_score):
        """Save content to local memory."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO content_memory 
                (content_hash, content_type, content_text, topic, performance_score)
                VALUES (?, ?, ?, ?, ?)
            """, (content_hash, content_type, content_text, topic, performance_score))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Content save failed: {e}")
    
    def _local_search_content(self, query: str, limit: int = 5) -> List[Dict]:
        """Simple keyword search in local content memory."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            # Simple LIKE search — GoodMem would do semantic vector search
            c.execute("""
                SELECT content_type, content_text, topic, performance_score, created_at
                FROM content_memory 
                WHERE content_text LIKE ? OR topic LIKE ?
                ORDER BY performance_score DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            rows = c.fetchall()
            conn.close()
            return [
                {
                    "content_type": r[0], "content_text": r[1][:200],
                    "topic": r[2], "performance_score": r[3], "created_at": r[4]
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning(f"Content search failed: {e}")
            return []
    
    def _local_save_revenue_signal(self, username, signal_type, product_id, context):
        """Save revenue signal to local memory."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            c.execute("""
                INSERT INTO revenue_signals (username, signal_type, product_id, context)
                VALUES (?, ?, ?, ?)
            """, (username, signal_type, product_id, context))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Revenue signal save failed: {e}")
    
    def _local_fallback_save(self, space, content):
        """Fallback save when GoodMem is down."""
        try:
            conn = sqlite3.connect(str(MEMORY_DB))
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS goodmem_fallback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    space TEXT, content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("INSERT INTO goodmem_fallback (space, content) VALUES (?, ?)",
                      (space, content))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Fallback save failed: {e}")


# ============================================================
# SINGLETON — One memory service for the whole swarm
# ============================================================

_memory = None

def get_memory() -> MemoryService:
    """Get the singleton memory service."""
    global _memory
    if _memory is None:
        _memory = MemoryService(mode="auto")
    return _memory


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    mem = get_memory()
    
    # Test relationship memory
    mem.remember_relationship(
        username="testuser",
        interaction_type="replied",
        topic="AI automation",
        context="Discussed building autonomous agents with ADK",
        sentiment="positive",
        engagement_score=0.8
    )
    
    # Test recall
    memories = mem.recall_relationship("testuser")
    print(f"memories for @testuser: {json.dumps(memories, indent=2)}")
    
    # Test context generation
    context = mem.get_engagement_context("testuser")
    print(f"\nContext: {context}")
    
    # Test strategy memory
    mem.remember_strategy("tweet_style", "question_hook", 0.85, "Questions get 2x replies")
    mem.remember_strategy("tweet_style", "tutorial_thread", 0.72, "Threads get saves")
    
    best = mem.recall_best_strategies("tweet_style")
    print(f"\nBest strategies: {json.dumps(best, indent=2)}")
    
    print("\n✅ Memory service working!")
