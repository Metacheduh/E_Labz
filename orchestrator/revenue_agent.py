"""
E-Labz Revenue Agent — Stripe MCP + Payment Intelligence
Autonomous revenue tracking, payment link generation, and customer management.

This replaces the webhook_handler.py stub with a full Stripe-powered agent
that can create checkout links, track sales, manage customers, and provide
revenue intelligence to the self-learning engine.

Requires: STRIPE_SECRET_KEY in config/.env
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
    logger = logging.getLogger("revenue_agent")

# ============================================================
# CONFIGURATION
# ============================================================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
METRICS_DB = Path(__file__).parent.parent / "data" / "metrics.db"

# Product catalog — maps our products to Stripe
PRODUCT_CATALOG = {
    "ai-agent-starter": {
        "name": "AI Agent Starter Kit",
        "price": 4900,  # cents
        "description": "Pre-built agent templates with ADK — research, content, engagement",
        "category": "starter_kit"
    },
    "ai-swarm-course": {
        "name": "Build Your AI Agent Swarm",
        "price": 9900,
        "description": "Complete course on building autonomous multi-agent business systems",
        "category": "course"
    },
    "voice-brand-kit": {
        "name": "AI Voice Brand Kit",
        "price": 7900,
        "description": "ElevenLabs voice clone + audio content pipeline + social templates",
        "category": "toolkit"
    },
    "automation-blueprint": {
        "name": "AI Automation Blueprint",
        "price": 14900,
        "description": "Full business automation architecture with n8n, ADK, and GoodMem",
        "category": "premium"
    },
    "swarm-consultation": {
        "name": "1-on-1 Swarm Setup",
        "price": 29900,
        "description": "Personal walkthrough setting up your AI agent swarm",
        "category": "service"
    }
}


class RevenueAgent:
    """
    Autonomous revenue tracking and payment operations.
    
    Capabilities:
    - Create Stripe payment links on-the-fly
    - Track revenue and customer data
    - Generate revenue reports for self_learn.py
    - Identify product interest signals from engagement data
    - Generate targeted CTAs based on audience behavior
    """
    
    def __init__(self):
        self.stripe = None
        self._init_stripe()
        self._init_db()
    
    def _init_stripe(self):
        """Initialize Stripe client."""
        if not STRIPE_SECRET_KEY or STRIPE_SECRET_KEY == "sk_live_...":
            logger.info("No valid STRIPE_SECRET_KEY, revenue agent in offline mode")
            return
            
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            self.stripe = stripe
            logger.info("💰 Stripe client initialized")
        except ImportError:
            logger.info("stripe package not installed, using offline mode")
    
    def _init_db(self):
        """Initialize revenue tracking database."""
        METRICS_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(METRICS_DB))
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,  -- sale, refund, subscription
                product_id TEXT,
                product_name TEXT,
                amount_cents INTEGER DEFAULT 0,
                currency TEXT DEFAULT 'usd',
                customer_email TEXT,
                source TEXT,  -- twitter, website, direct
                stripe_id TEXT UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS payment_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                payment_url TEXT,
                short_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ============================================================
    # PAYMENT OPERATIONS
    # ============================================================
    
    def create_payment_link(self, product_key: str) -> Optional[str]:
        """
        Create a Stripe payment link for a product.
        
        Returns the payment URL or None if offline.
        """
        product = PRODUCT_CATALOG.get(product_key)
        if not product:
            logger.warning(f"Unknown product: {product_key}")
            return None
        
        if not self.stripe:
            # Return Lemon Squeezy fallback link
            return self._get_fallback_link(product_key)
        
        try:
            # Create or get Stripe price
            stripe_price = self.stripe.Price.create(
                unit_amount=product["price"],
                currency="usd",
                product_data={
                    "name": product["name"],
                    "description": product["description"]
                }
            )
            
            # Create payment link
            link = self.stripe.PaymentLink.create(
                line_items=[{"price": stripe_price.id, "quantity": 1}],
                after_completion={"type": "redirect", "redirect": {"url": "https://e-labz.netlify.app/thank-you"}}
            )
            
            # Cache the link
            self._save_payment_link(product_key, link.url)
            
            logger.info(f"💰 Created payment link for {product['name']}: {link.url}")
            return link.url
            
        except Exception as e:
            logger.warning(f"Stripe payment link creation failed: {e}")
            return self._get_fallback_link(product_key)
    
    def _get_fallback_link(self, product_key: str) -> str:
        """Get Lemon Squeezy link as fallback."""
        # These are the existing LS checkout links
        LS_LINKS = {
            "ai-agent-starter": "https://e-labz.lemonsqueezy.com/buy/ai-agent-starter",
            "ai-swarm-course": "https://e-labz.lemonsqueezy.com/buy/ai-swarm-course",
            "voice-brand-kit": "https://e-labz.lemonsqueezy.com/buy/voice-brand-kit",
            "automation-blueprint": "https://e-labz.lemonsqueezy.com/buy/automation-blueprint",
        }
        return LS_LINKS.get(product_key, "https://e-labz.netlify.app/#products")
    
    def _save_payment_link(self, product_id: str, url: str):
        """Cache a payment link."""
        try:
            conn = sqlite3.connect(str(METRICS_DB))
            c = conn.cursor()
            c.execute("""
                INSERT INTO payment_links (product_id, payment_url)
                VALUES (?, ?)
            """, (product_id, url))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Payment link save failed: {e}")
    
    # ============================================================
    # REVENUE TRACKING
    # ============================================================
    
    def record_sale(self, product_id: str, amount_cents: int,
                    customer_email: str = "", source: str = "website",
                    stripe_id: str = ""):
        """Record a sale."""
        product = PRODUCT_CATALOG.get(product_id, {})
        try:
            conn = sqlite3.connect(str(METRICS_DB))
            c = conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO revenue 
                (event_type, product_id, product_name, amount_cents, 
                 customer_email, source, stripe_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("sale", product_id, product.get("name", product_id),
                  amount_cents, customer_email, source, stripe_id))
            conn.commit()
            conn.close()
            logger.info(f"💰 Sale recorded: ${amount_cents/100:.2f} from {product_id}")
        except Exception as e:
            logger.warning(f"Sale recording failed: {e}")
    
    def get_revenue_report(self, days: int = 30) -> Dict:
        """
        Generate a revenue report for the self-learning engine.
        
        Returns:
            Dict with total_revenue, sale_count, top_products, avg_sale, trend
        """
        try:
            conn = sqlite3.connect(str(METRICS_DB))
            c = conn.cursor()
            
            c.execute("""
                SELECT 
                    COUNT(*) as sale_count,
                    COALESCE(SUM(amount_cents), 0) as total_cents,
                    COALESCE(AVG(amount_cents), 0) as avg_cents
                FROM revenue 
                WHERE event_type = 'sale'
                AND datetime(created_at) > datetime('now', ?)
            """, (f"-{days} days",))
            
            row = c.fetchone()
            
            # Top products
            c.execute("""
                SELECT product_name, COUNT(*) as count, SUM(amount_cents) as total
                FROM revenue 
                WHERE event_type = 'sale'
                AND datetime(created_at) > datetime('now', ?)
                GROUP BY product_name
                ORDER BY total DESC LIMIT 5
            """, (f"-{days} days",))
            
            top_products = [
                {"product": r[0], "sales": r[1], "revenue": r[2] / 100}
                for r in c.fetchall()
            ]
            
            # Revenue by source
            c.execute("""
                SELECT source, SUM(amount_cents) as total
                FROM revenue WHERE event_type = 'sale'
                AND datetime(created_at) > datetime('now', ?)
                GROUP BY source ORDER BY total DESC
            """, (f"-{days} days",))
            
            by_source = {r[0]: r[1] / 100 for r in c.fetchall()}
            
            conn.close()
            
            return {
                "period_days": days,
                "total_revenue": row[1] / 100 if row[1] else 0,
                "sale_count": row[0] or 0,
                "avg_sale": row[2] / 100 if row[2] else 0,
                "top_products": top_products,
                "by_source": by_source,
                "monthly_target": 3000,  # $3K/month goal
                "target_progress": (row[1] / 300000 * 100) if row[1] else 0
            }
        except Exception as e:
            logger.warning(f"Revenue report failed: {e}")
            return {"total_revenue": 0, "sale_count": 0, "error": str(e)}
    
    # ============================================================
    # SMART CTA GENERATION
    # ============================================================
    
    def get_smart_cta(self, context: str = "general") -> Dict:
        """
        Generate a context-aware product CTA.
        
        Based on what topics are being discussed, recommend the right product
        and return a natural, non-salesy CTA.
        """
        # Map topics to products
        TOPIC_PRODUCT_MAP = {
            "automation": "automation-blueprint",
            "agent": "ai-agent-starter",
            "swarm": "ai-swarm-course",
            "voice": "voice-brand-kit",
            "build": "ai-agent-starter",
            "scale": "ai-swarm-course",
            "ai": "ai-agent-starter",
            "workflow": "automation-blueprint",
            "brand": "voice-brand-kit",
        }
        
        # Find best matching product
        product_key = "ai-agent-starter"  # default
        for keyword, prod_id in TOPIC_PRODUCT_MAP.items():
            if keyword in context.lower():
                product_key = prod_id
                break
        
        product = PRODUCT_CATALOG[product_key]
        link = self._get_fallback_link(product_key)
        
        # Natural CTAs — sounds like a person sharing something useful
        SOFT_CTAS = [
            f"I actually put together a {product['name'].lower()} for this exact thing → {link}",
            f"Been working on something that helps with this — {product['name'].lower()} — check it out if you want: {link}",
            f"This is exactly why I built the {product['name'].lower()}. might help: {link}",
            f"If you're serious about this, I made a {product['name'].lower()} that walks through everything: {link}",
        ]
        
        import random
        return {
            "product_key": product_key,
            "product_name": product["name"],
            "price": f"${product['price']/100:.0f}",
            "cta_text": random.choice(SOFT_CTAS),
            "link": link
        }
    
    # ============================================================
    # STRIPE SYNC (Pull real data)
    # ============================================================
    
    def sync_stripe_data(self) -> Dict:
        """
        Sync recent Stripe data — pull real sales, customers, subscriptions.
        
        Call this daily from the scheduler.
        """
        if not self.stripe:
            return {"status": "offline", "message": "Stripe not configured"}
        
        try:
            # Get recent charges
            charges = self.stripe.Charge.list(limit=20)
            new_sales = 0
            
            for charge in charges.data:
                if charge.paid and not charge.refunded:
                    self.record_sale(
                        product_id=charge.metadata.get("product_id", "unknown"),
                        amount_cents=charge.amount,
                        customer_email=charge.billing_details.email or "",
                        source="stripe",
                        stripe_id=charge.id
                    )
                    new_sales += 1
            
            # Get balance
            balance = self.stripe.Balance.retrieve()
            available = sum(b.amount for b in balance.available) / 100
            
            logger.info(f"💰 Stripe sync: {new_sales} new sales, ${available:.2f} available")
            
            return {
                "status": "synced",
                "new_sales": new_sales,
                "available_balance": available,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Stripe sync failed: {e}")
            return {"status": "error", "message": str(e)}


# ============================================================
# SINGLETON
# ============================================================

_revenue_agent = None

def get_revenue_agent() -> RevenueAgent:
    """Get the singleton revenue agent."""
    global _revenue_agent
    if _revenue_agent is None:
        _revenue_agent = RevenueAgent()
    return _revenue_agent


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    agent = get_revenue_agent()
    
    # Test revenue report
    report = agent.get_revenue_report()
    print(f"Revenue report: {json.dumps(report, indent=2)}")
    
    # Test smart CTA
    cta = agent.get_smart_cta("building AI automation workflows")
    print(f"\nSmart CTA: {json.dumps(cta, indent=2)}")
    
    # Test payment link (offline)
    link = agent.create_payment_link("ai-agent-starter")
    print(f"\nPayment link: {link}")
    
    print("\n✅ Revenue agent working!")
