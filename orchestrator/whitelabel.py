"""
E-Labz White-Label Swarm Configuration
Allows the entire swarm to be rebranded and configured for clients.

Usage:
    from orchestrator.whitelabel import get_brand_config
    brand = get_brand_config()
    brand.name  # "E-Labz" by default
"""

import json
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class BrandConfig:
    """White-label brand configuration."""
    # Core identity
    name: str = "E-Labz"
    tagline: str = "AI Products Shipped in Weeks, Not Months"
    handle: str = "@AutoStackHQ"
    website: str = "https://e-labz.netlify.app"
    email: str = "hello@e-labz.com"

    # Voice / tone
    voice_style: str = "casual-expert"  # casual-expert, professional, friendly, technical
    emoji_level: str = "moderate"  # none, minimal, moderate, heavy

    # Content settings
    niche: str = "AI automation"
    content_pillars: list = field(default_factory=lambda: [
        "AI agents & automation",
        "Building in public",
        "No-code / low-code tools",
        "Revenue from AI products",
        "Behind-the-scenes engineering"
    ])

    # Revenue
    store_url: str = "https://autostackhq.lemonsqueezy.com"
    stripe_enabled: bool = True
    lemonsqueezy_enabled: bool = True

    # Platform settings
    twitter_enabled: bool = True
    linkedin_enabled: bool = False
    medium_enabled: bool = False
    devto_enabled: bool = False
    newsletter_enabled: bool = False

    # Posting schedule
    tweets_per_day: int = 6
    threads_per_week: int = 3
    reply_targets: list = field(default_factory=lambda: [
        "alexhormozi", "levelsio", "naval", "dhaboross",
        "swyx", "aisolopreneur", "mcaborj"
    ])

    # Agent toggles
    research_enabled: bool = True
    content_enabled: bool = True
    engagement_enabled: bool = True
    revenue_tracking_enabled: bool = True
    voice_enabled: bool = False
    memory_enabled: bool = True

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def save(self, path: str = None):
        if path is None:
            path = str(Path(__file__).parent.parent / "config" / "brand.json")
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str = None) -> "BrandConfig":
        if path is None:
            path = str(Path(__file__).parent.parent / "config" / "brand.json")
        if Path(path).exists():
            data = json.loads(Path(path).read_text())
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls()


# ============================================================
# SINGLETON
# ============================================================

_config = None

def get_brand_config() -> BrandConfig:
    """Get the brand config singleton. Loads from brand.json if it exists."""
    global _config
    if _config is None:
        _config = BrandConfig.load()
    return _config


if __name__ == "__main__":
    config = get_brand_config()
    print(f"Brand: {config.name}")
    print(f"Handle: {config.handle}")
    print(f"Pillars: {config.content_pillars}")
    print(f"Tweets/day: {config.tweets_per_day}")
    print(f"Platforms: Twitter={config.twitter_enabled}, LinkedIn={config.linkedin_enabled}")

    # Save default config
    config.save()
    print(f"\n✅ Config saved to config/brand.json")
