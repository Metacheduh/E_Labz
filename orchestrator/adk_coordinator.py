"""
E-Labz Multi-Agent Coordinator — ADK-Powered Swarm Architecture
The central brain that orchestrates all specialized agents.

Architecture:
    Coordinator (this file)
    ├── ResearchAgent → Tavily/Google Search → trending topics
    ├── ContentAgent → humanize.py → tweet/thread generation
    ├── EngagementAgent → reply_engine + memory → relationship building
    ├── RevenueAgent → Stripe MCP → payment operations + revenue tracking
    ├── AnalyticsAgent → self_learn.py → performance analysis + pivots
    ├── VoiceAgent → ElevenLabs → audio content
    └── AgentZero → Deep research, code gen, analysis (specialist)

This module provides the ADK integration layer. Each agent wraps existing
E-Labz modules with ADK's LlmAgent/SequentialAgent/ParallelAgent patterns,
giving them persistent memory, observability, and structured workflows.

The "person behind the brand" — the coordinator thinks like a human operator.
"""

import os
import json
import time
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
    logger = logging.getLogger("adk_coordinator")

from orchestrator.memory_service import get_memory
from orchestrator.revenue_agent import get_revenue_agent

try:
    from orchestrator.agent_zero_bridge import get_agent_zero
except ImportError:
    def get_agent_zero(): return None


# ============================================================
# ADK INTEGRATION LAYER (Graceful — works with or without ADK)
# ============================================================

ADK_AVAILABLE = False

try:
    from google.adk.agents import LlmAgent
    from google.adk.agents.workflow_agents import SequentialAgent, ParallelAgent
    from google.adk.apps import App
    ADK_AVAILABLE = True
    logger.info("🚀 ADK framework loaded — multi-agent mode activated")
except ImportError:
    logger.info("ADK not installed — using lightweight coordinator mode")


# ============================================================
# AGENT DEFINITIONS
# ============================================================

class SwarmCoordinator:
    """
    The central coordinator for the E-Labz agent swarm.
    
    Orchestrates all specialized agents through the daily pipeline.
    thinks like a human operator — prioritizes tasks, adapts strategy,
    and makes decisions based on accumulated memory and performance data.
    """
    
    def __init__(self):
        self.memory = get_memory()
        self.revenue = get_revenue_agent()
        self.agent_zero = get_agent_zero()
        self.adk_mode = ADK_AVAILABLE
        self._init_agents()
        az_status = self.agent_zero.is_available if self.agent_zero else False
        logger.info(f"🧠 Swarm Coordinator initialized (ADK: {self.adk_mode}, AgentZero: {az_status})")
    
    def _init_agents(self):
        """Initialize all specialized agents."""
        if self.adk_mode:
            self._init_adk_agents()
        else:
            self._init_lightweight_agents()
    
    def _init_adk_agents(self):
        """Initialize ADK-native agents with full capabilities."""
        self.research_agent = LlmAgent(
            name="ResearchAgent",
            model="gemini-2.5-flash",
            instruction="""You are the E-Labz Research Agent. Your job is to find 
            trending AI automation topics and extract valuable insights for content creation.
            Focus on: AI agents, automation tools, workflow builders, no-code AI, 
            and money-making with AI. Return structured topic lists with hooks.""",
            description="Finds trending topics and research insights for content creation"
        )
        
        self.content_agent = LlmAgent(
            name="ContentAgent", 
            model="gemini-2.5-flash",
            instruction="""You are the E-Labz Content Agent. You create engaging, 
            human-sounding social media content about AI automation.
            
            CRITICAL RULES:
            - Never use words: leverage, comprehensive, delve, innovative, cutting-edge
            - Write like a helpful friend, not a corporation
            - Use lowercase, casual tone, occasional humor
            - Include specific examples and numbers
            - End with engagement hooks (questions, opinions)
            
            Sound like a real person who's genuinely excited about AI.""",
            description="Creates human-sounding AI/automation content"
        )
        
        self.engagement_agent = LlmAgent(
            name="EngagementAgent",
            model="gemini-2.5-flash", 
            instruction="""You are the E-Labz Engagement Agent. You build real 
            relationships on Twitter by replying to relevant accounts with 
            genuinely helpful, thoughtful responses.
            
            CRITICAL RULES:
            - Check memory for past interactions before replying
            - Never repeat the same talking points to the same person
            - Add real value — share experiences, tools, specific advice
            - Never be salesy or use marketing speak
            - Match the tone of the person you're replying to
            - Remember what you've discussed for next time""",
            description="Builds relationships through authentic engagement"
        )
        
        logger.info("🚀 ADK agents initialized: Research, Content, Engagement")
    
    def _init_lightweight_agents(self):
        """Initialize lightweight agents (no ADK dependency)."""
        # These wrap existing modules directly
        self.agents = {
            "research": self._run_research,
            "content": self._run_content,
            "engagement": self._run_engagement,
            "revenue": self._run_revenue_check,
            "analytics": self._run_analytics,
        }
        logger.info("📦 Lightweight agents initialized")
    
    # ============================================================
    # DAILY PIPELINE
    # ============================================================
    
    def run_daily_pipeline(self) -> Dict:
        """
        Execute the full daily pipeline — the heartbeat of the swarm.
        
        Pipeline:
        1. Research → Find today's trending topics
        2. Content + Analytics (parallel) → Generate content + review performance
        3. Engagement → Reply engagement session  
        4. Revenue → Sync sales + generate report
        5. Memory → Save today's learnings
        
        Returns a summary of what happened.
        """
        logger.info("=" * 60)
        logger.info("🌅 DAILY PIPELINE STARTING")
        logger.info("=" * 60)
        
        results = {}
        start_time = time.time()
        
        # Step 1: Research
        logger.info("\n📊 Step 1: Research Phase")
        results["research"] = self._run_research()
        
        # Step 2: Content + Analytics (parallel in concept, sequential in practice)
        logger.info("\n✍️ Step 2: Content Generation + Analytics Review")
        results["content"] = self._run_content()
        results["analytics"] = self._run_analytics()
        
        # Step 3: Engagement
        logger.info("\n💬 Step 3: Engagement Session")
        results["engagement"] = self._run_engagement()
        
        # Step 4: Revenue
        logger.info("\n💰 Step 4: Revenue Reconciliation")
        results["revenue"] = self._run_revenue_check()
        
        # Step 5: Memory consolidation
        logger.info("\n🧠 Step 5: Memory Consolidation")
        results["memory"] = self._consolidate_daily_memory(results)
        
        elapsed = time.time() - start_time
        results["pipeline_duration_seconds"] = round(elapsed, 1)
        
        logger.info("=" * 60)
        logger.info(f"✅ DAILY PIPELINE COMPLETE ({elapsed:.0f}s)")
        logger.info("=" * 60)
        
        return results
    
    # ============================================================
    # INDIVIDUAL AGENT RUNNERS
    # ============================================================
    
    def _run_research(self) -> Dict:
        """Run research agent — find trending topics. Falls back to Agent Zero for deep research."""
        try:
            from orchestrator.pipeline.research import run_research_cycle
            topics = run_research_cycle()
            
            # Save to memory
            if topics:
                self.memory.remember_strategy(
                    "research_topics",
                    json.dumps(topics[:5]) if isinstance(topics, list) else str(topics),
                    0.5,
                    f"Research cycle {datetime.now().strftime('%Y-%m-%d')}"
                )
            
            # Enhance with Agent Zero deep research if available
            az_insights = None
            if self.agent_zero and self.agent_zero.is_available and topics:
                top_topic = topics[0] if isinstance(topics, list) else str(topics)
                az_insights = self.agent_zero.deep_research(f"AI automation trends: {top_topic}")
                logger.info(f"🤖 Agent Zero enhanced research with deep insights")
            
            return {
                "status": "completed",
                "topics_found": len(topics) if isinstance(topics, list) else 0,
                "agent_zero_enhanced": az_insights is not None
            }
        except Exception as e:
            logger.warning(f"Research phase failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _run_content(self) -> Dict:
        """Run content agent — generate today's posts."""
        try:
            # Content is generated by the scheduler's built-in tweet pools
            # This agent provides strategic guidance on WHAT to post
            best_strategies = self.memory.recall_best_strategies("tweet_style", limit=3)
            revenue_report = self.revenue.get_revenue_report(days=7)
            
            recommendations = []
            
            # If no sales this week, lean into product mentions
            if revenue_report.get("sale_count", 0) == 0:
                recommendations.append("Increase product CTA frequency — no sales this week")
            
            # Use best performing tweet styles
            if best_strategies:
                top_style = best_strategies[0]["strategy_value"]
                recommendations.append(f"Lead with {top_style} — historically best performer")
            
            return {
                "status": "completed",
                "recommendations": recommendations,
                "revenue_context": {
                    "weekly_revenue": revenue_report.get("total_revenue", 0),
                    "target_progress": revenue_report.get("target_progress", 0)
                }
            }
        except Exception as e:
            logger.warning(f"Content phase failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _run_engagement(self) -> Dict:
        """Run engagement agent — reply engagement session with memory."""
        try:
            # The reply engine will be enhanced to check memory before replying
            return {"status": "ready", "message": "Engagement session queued for scheduler"}
        except Exception as e:
            logger.warning(f"Engagement phase failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _run_revenue_check(self) -> Dict:
        """Run revenue agent — sync and report."""
        try:
            # Sync Stripe data
            sync_result = self.revenue.sync_stripe_data()
            
            # Get report
            report = self.revenue.get_revenue_report(days=30)
            
            return {
                "status": "completed",
                "sync": sync_result,
                "report": report
            }
        except Exception as e:
            logger.warning(f"Revenue phase failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _run_analytics(self) -> Dict:
        """Run analytics agent — review performance and suggest pivots."""
        try:
            from orchestrator.intelligence.self_learn import run_daily_review
            review = run_daily_review()
            
            return {"status": "completed", "review": str(review)[:200] if review else "No data"}
        except Exception as e:
            logger.warning(f"Analytics phase failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    # ============================================================
    # MEMORY CONSOLIDATION
    # ============================================================
    
    def _consolidate_daily_memory(self, results: Dict) -> Dict:
        """
        End-of-day memory consolidation.
        
        The swarm reflects on what happened today and stores key learnings
        for tomorrow. This is how it gets smarter over time.
        """
        try:
            # Save daily pipeline performance
            self.memory.remember_strategy(
                "pipeline_health",
                datetime.now().strftime("%Y-%m-%d"),
                1.0 if all(r.get("status") != "failed" for r in results.values() if isinstance(r, dict)) else 0.5,
                f"Research: {results.get('research', {}).get('status', 'unknown')}, "
                f"Revenue: {results.get('revenue', {}).get('report', {}).get('total_revenue', 0)}"
            )
            
            # Save revenue performance
            rev_report = results.get("revenue", {}).get("report", {})
            if rev_report:
                self.memory.remember_strategy(
                    "revenue_trend",
                    datetime.now().strftime("%Y-%m-%d"),
                    rev_report.get("target_progress", 0) / 100,
                    f"${rev_report.get('total_revenue', 0):.2f} of $3000 target"
                )
            
            return {"status": "consolidated", "memories_saved": 2}
        except Exception as e:
            logger.warning(f"Memory consolidation failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    # ============================================================
    # ENGAGEMENT ENHANCEMENT
    # ============================================================
    
    def get_reply_context(self, username: str, tweet_content: str = "") -> str:
        """
        Get enriched context for the reply engine.
        
        Before replying to someone, the coordinator checks:
        1. Have we talked to them before?
        2. What are they interested in?
        3. Should we include a product mention?
        
        Returns a context string the reply engine can use.
        """
        # Get relationship history
        relationship_context = self.memory.get_engagement_context(username)
        
        # Check if there's a product fit
        product_fit = ""
        if tweet_content:
            cta = self.revenue.get_smart_cta(tweet_content)
            if cta:
                product_fit = f"\nIf appropriate, you could softly mention: {cta['product_name']} ({cta['price']})"
        
        return f"{relationship_context}{product_fit}"
    
    def after_reply(self, username: str, reply_text: str, 
                     original_tweet: str = "", topic: str = ""):
        """
        Called after successfully replying to someone.
        Saves the interaction to memory for next time.
        """
        self.memory.remember_relationship(
            username=username,
            interaction_type="replied",
            topic=topic,
            context=f"They said: {original_tweet[:100]}... We replied: {reply_text[:100]}...",
            sentiment="positive",
            engagement_score=0.6
        )
        
        # Check for revenue signals
        revenue_keywords = ["buy", "price", "cost", "how much", "checkout", "purchase", "interested"]
        if any(kw in original_tweet.lower() for kw in revenue_keywords):
            self.memory.remember_revenue_signal(
                username=username,
                signal_type="product_interest",
                context=original_tweet[:200]
            )

    # ============================================================
    # AGENT ZERO DELEGATION
    # ============================================================

    def delegate_to_agent_zero(self, task: str, context: str = "") -> str:
        """
        Delegate a complex task to Agent Zero.
        Use for: deep research, code gen, analysis, long-form content.
        """
        if not self.agent_zero or not self.agent_zero.is_available:
            logger.info("Agent Zero not available — skipping delegation")
            return "Agent Zero not available"

        result = self.agent_zero.send_task(task, context)
        return result.get("result", "No result")


# ============================================================
# SINGLETON
# ============================================================

_coordinator = None

def get_coordinator() -> SwarmCoordinator:
    """Get the singleton swarm coordinator."""
    global _coordinator
    if _coordinator is None:
        _coordinator = SwarmCoordinator()
    return _coordinator


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    coordinator = get_coordinator()
    
    # Test reply context
    context = coordinator.get_reply_context(
        "alexhormozi", 
        "Building AI automations for my business"
    )
    print(f"Reply context:\n{context}")
    
    # Test after_reply
    coordinator.after_reply(
        username="testuser",
        reply_text="great point about automation pipelines!",
        original_tweet="AI agents are the future of business automation",
        topic="AI automation"
    )
    
    # Test revenue report
    report = coordinator.revenue.get_revenue_report()
    print(f"\nRevenue: {json.dumps(report, indent=2)}")
    
    print("\n✅ Swarm coordinator working!")
