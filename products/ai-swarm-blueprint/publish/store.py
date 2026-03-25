"""
Free Cash Flow — Digital Store Integration
Platform-agnostic product sales & revenue tracking.
Supports: Stripe (primary — lowest fees), Gumroad (fallback).

Currently configured for Stripe — 2.9% + 30¢, no platform commission.
To switch platforms, change STORE_PLATFORM in .env
"""

import os
import json
from datetime import date, datetime
from pathlib import Path
from orchestrator import PROJECT_ROOT
from typing import Optional

import requests
from dotenv import load_dotenv

# Load env
ENV_PATH = PROJECT_ROOT / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

STORE_PLATFORM = os.getenv("STORE_PLATFORM", "stripe")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
GUMROAD_TOKEN = os.getenv("GUMROAD_ACCESS_TOKEN", "")


# ============================================================
# STRIPE (Primary — 2.9% + 30¢, no platform fee)
# ============================================================

class StripeStore:
    BASE_URL = "https://api.stripe.com/v1"

    def __init__(self):
        self.key = STRIPE_SECRET_KEY
        self.headers = {"Authorization": f"Bearer {self.key}"}

    def _get(self, endpoint: str, params: dict = None) -> dict:
        if not self.key:
            return {"error": "No STRIPE_SECRET_KEY configured"}
        resp = requests.get(f"{self.BASE_URL}/{endpoint}", headers=self.headers, params=params)
        return resp.json()

    def _post(self, endpoint: str, data: dict = None) -> dict:
        if not self.key:
            return {"error": "No STRIPE_SECRET_KEY configured"}
        resp = requests.post(f"{self.BASE_URL}/{endpoint}", headers=self.headers, data=data)
        return resp.json()

    def list_products(self) -> list[dict]:
        """List all Stripe products."""
        data = self._get("products", {"limit": 100, "active": "true"})
        if "error" in data:
            print(f"⚠️ Stripe: {data['error'].get('message', data['error'])}")
            return []

        products = []
        for p in data.get("data", []):
            products.append({
                "id": p["id"],
                "name": p.get("name", ""),
                "description": p.get("description", ""),
                "active": p.get("active", False),
                "url": p.get("url", ""),
                "created": p.get("created", 0),
            })
        return products

    def create_product(self, name: str, price_usd: float, description: str = "") -> dict:
        """Create a product + price + payment link on Stripe."""
        # 1. Create the product
        product_data = self._post("products", {
            "name": name,
            "description": description,
        })
        if "error" in product_data:
            print(f"❌ Stripe product error: {product_data['error'].get('message')}")
            return {}

        product_id = product_data["id"]

        # 2. Create a price for it
        price_data = self._post("prices", {
            "product": product_id,
            "unit_amount": int(price_usd * 100),  # cents
            "currency": "usd",
        })
        if "error" in price_data:
            print(f"❌ Stripe price error: {price_data['error'].get('message')}")
            return {}

        price_id = price_data["id"]

        # 3. Create a payment link (shareable URL)
        link_data = self._post("payment_links", {
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": 1,
        })
        if "error" in link_data:
            print(f"❌ Stripe link error: {link_data['error'].get('message')}")
            return {"id": product_id, "name": name, "price": price_usd}

        checkout_url = link_data.get("url", "")
        print(f"✅ Product created: {name} (${price_usd:.2f}) → {checkout_url}")

        return {
            "id": product_id,
            "name": name,
            "price": price_usd,
            "price_id": price_id,
            "checkout_url": checkout_url,
        }

    def get_orders(self, after: str = None) -> list[dict]:
        """Get successful payments (charges)."""
        params = {"limit": 100}
        if after:
            # Convert date string to unix timestamp
            try:
                dt = datetime.fromisoformat(after)
                params["created[gte]"] = int(dt.timestamp())
            except (ValueError, TypeError):
                pass

        data = self._get("charges", params)
        if "error" in data:
            return []

        orders = []
        for ch in data.get("data", []):
            if ch.get("status") != "succeeded":
                continue
            orders.append({
                "id": ch["id"],
                "total": ch.get("amount", 0) / 100,
                "status": ch.get("status", ""),
                "created_at": datetime.fromtimestamp(ch.get("created", 0)).isoformat(),
                "refunded": ch.get("refunded", False),
                "email": ch.get("billing_details", {}).get("email", ""),
            })
        return orders

    def get_revenue(self) -> dict:
        """Get current month revenue summary."""
        today = date.today()
        first_of_month = today.replace(day=1).isoformat()

        orders = self.get_orders(after=first_of_month)
        total = sum(o["total"] for o in orders if not o["refunded"])
        count = len([o for o in orders if not o["refunded"]])

        days_elapsed = max(1, (today - today.replace(day=1)).days + 1)
        projected = (total / days_elapsed) * 30

        return {
            "month": today.strftime("%Y-%m"),
            "total_revenue": total,
            "total_sales": count,
            "projected_monthly": projected,
            "target": 3000,
            "on_track": projected >= 3000,
            "gap": max(0, 3000 - projected),
            "platform": "stripe",
        }

    def get_balance(self) -> dict:
        """Get Stripe account balance."""
        data = self._get("balance")
        if "error" in data:
            return {"available": 0, "pending": 0}

        available = sum(b.get("amount", 0) for b in data.get("available", [])) / 100
        pending = sum(b.get("amount", 0) for b in data.get("pending", [])) / 100

        return {"available": available, "pending": pending}


# ============================================================
# GUMROAD (Fallback — 10% commission)
# ============================================================

class GumroadStore:
    BASE_URL = "https://api.gumroad.com/v2"

    def __init__(self):
        self.token = GUMROAD_TOKEN

    def _get(self, endpoint: str, params: dict = None) -> dict:
        if not self.token:
            return {"success": False, "error": "No GUMROAD_ACCESS_TOKEN"}
        params = params or {}
        params["access_token"] = self.token
        resp = requests.get(f"{self.BASE_URL}/{endpoint}", params=params)
        return resp.json()

    def list_products(self) -> list[dict]:
        data = self._get("products")
        if not data.get("success"):
            return []
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p.get("price", 0) / 100,
                "sales_count": p.get("sales_count", 0),
                "url": p.get("short_url", ""),
            }
            for p in data.get("products", [])
        ]

    def get_orders(self, after: str = None) -> list[dict]:
        params = {"after": after} if after else {}
        data = self._get("sales", params)
        if not data.get("success"):
            return []
        return [
            {
                "id": s["id"],
                "total": s.get("price", 0) / 100,
                "created_at": s.get("created_at", ""),
                "refunded": s.get("refunded", False),
            }
            for s in data.get("sales", [])
        ]

    def get_revenue(self) -> dict:
        today = date.today()
        orders = self.get_orders(after=today.replace(day=1).isoformat())
        total = sum(o["total"] for o in orders if not o["refunded"])
        count = len([o for o in orders if not o["refunded"]])
        days_elapsed = max(1, (today - today.replace(day=1)).days + 1)
        projected = (total / days_elapsed) * 30
        return {
            "month": today.strftime("%Y-%m"),
            "total_revenue": total,
            "total_sales": count,
            "projected_monthly": projected,
            "target": 3000,
            "on_track": projected >= 3000,
            "gap": max(0, 3000 - projected),
            "platform": "gumroad",
        }


# ============================================================
# UNIFIED INTERFACE
# ============================================================

def get_store():
    """Get the configured store backend."""
    if STORE_PLATFORM == "stripe" and STRIPE_SECRET_KEY:
        return StripeStore()
    elif STORE_PLATFORM == "gumroad" and GUMROAD_TOKEN:
        return GumroadStore()
    elif STRIPE_SECRET_KEY:
        return StripeStore()
    elif GUMROAD_TOKEN:
        return GumroadStore()
    else:
        print("⚠️ No store configured — set STRIPE_SECRET_KEY or GUMROAD_ACCESS_TOKEN in .env")
        return None


def get_revenue() -> dict:
    """Get revenue data from whatever store is configured."""
    store = get_store()
    if store:
        return store.get_revenue()
    return {
        "total_revenue": 0, "total_sales": 0, "projected_monthly": 0,
        "target": 3000, "on_track": False, "gap": 3000, "platform": "none",
    }


def list_products() -> list[dict]:
    """List products from whatever store is configured."""
    store = get_store()
    return store.list_products() if store else []


def create_product(name: str, price_usd: float, description: str = "") -> dict:
    """Create a product (Stripe only — auto-generates payment link)."""
    store = get_store()
    if store and hasattr(store, "create_product"):
        return store.create_product(name, price_usd, description)
    print("⚠️ Product creation requires Stripe")
    return {}
