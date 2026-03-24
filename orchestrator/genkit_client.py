import requests
import os
import json
from typing import Dict, Any

GENKIT_SERVER_URL = os.getenv("GENKIT_SERVER_URL", "http://localhost:3400")

def run_genkit_flow(flow_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a Genkit flow via HTTP."""
    url = f"{GENKIT_SERVER_URL}/{flow_name}"
    try:
        response = requests.post(url, json={"data": payload}, timeout=120)
        response.raise_for_status()
        return response.json().get("result", {})
    except Exception as e:
        print(f"❌ Genkit Flow Error [{flow_name}]: {e}")
        return {}

def generate_product_campaign(topic: str, audience: str = "aspiring creators"):
    """Trigger a full campaign (Ebook, Blog, Email, Site, X)."""
    payload = {"topic": topic, "targetAudience": audience}
    return run_genkit_flow("campaignFlow", payload)
