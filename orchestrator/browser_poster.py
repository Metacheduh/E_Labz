"""
Free Cash Flow — Browser-Based Twitter Poster (Playwright Edition)
Uses Playwright for posting tweets and replies via browser.
Playwright's real keyboard typing works with React state management.
"""

import os
import pickle
import json
import re
import asyncio
from pathlib import Path
from urllib.parse import quote


# ─── Content Sanitizer ──────────────────────────────────────────────────────
# Strips markdown, HTML, internal annotations, and formatting artifacts
# that should never appear in posted tweets or replies.
# ────────────────────────────────────────────────────────────────────────────

def sanitize_content(text: str) -> str:
    """Clean content before posting to Twitter.

    Removes:
    - Markdown headers (# Header)
    - HTML tags (<p>, <br>, etc.)
    - Internal annotations (## Related Answers, ## Section, etc.)
    - Markdown bold/italic markers (**, __, *)
    - Markdown links [text](url) → text
    - Markdown images ![alt](url) → removed
    - Bullet points (- item, * item)
    - Blockquotes (> text)
    - Horizontal rules (---, ***)
    - Excessive whitespace and newlines
    - Leading/trailing whitespace
    """
    if not text or not isinstance(text, str):
        return text

    original = text

    # Remove markdown images entirely
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Convert markdown links to just the text
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove markdown headers (lines starting with # through ######)
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)

    # Remove blockquotes
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Remove markdown bold/italic markers but keep the text
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # ***bold italic***
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # **bold**
    text = re.sub(r'__(.+?)__', r'\1', text)            # __bold__
    text = re.sub(r'\*(.+?)\*', r'\1', text)            # *italic*
    text = re.sub(r'_(.+?)_', r'\1', text)              # _italic_

    # Remove markdown bullet points (- item, * item) → keep text
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)

    # Remove numbered list markers (1. item) → keep text
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove code backticks
    text = re.sub(r'```[\s\S]*?```', '', text)  # Code blocks
    text = re.sub(r'`([^`]+)`', r'\1', text)    # Inline code

    # Collapse multiple newlines to single space (tweets are single-line flow)
    text = re.sub(r'\n{2,}', ' ', text)
    text = re.sub(r'\n', ' ', text)

    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # If sanitization obliterated the content, return original stripped
    if len(text) < 10 and len(original.strip()) >= 10:
        return original.strip()

    return text

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

COOKIES_PATH = Path(__file__).parent.parent / "data" / "x_cookies.pkl"
COOKIES_JSON = Path(__file__).parent.parent / "data" / "x_cookies.json"
COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_event_loop():
    """Get or create an event loop."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


class BrowserPoster:
    """Post tweets and replies using Playwright browser automation."""

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self.logged_in = False

    async def _ensure_browser(self):
        """Start Playwright browser if not running."""
        if self._page is not None:
            try:
                await self._page.title()
                return  # Browser is still alive
            except Exception:
                self._page = None
                self._context = None
                self._browser = None

        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().__aenter__()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                '--ignore-certificate-errors',
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        self._context = await self._browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self._page = await self._context.new_page()

    async def _load_cookies(self) -> bool:
        """Load saved cookies into the browser context."""
        cookie_sources = [COOKIES_JSON, COOKIES_PATH]
        
        for cookie_file in cookie_sources:
            if not cookie_file.exists():
                continue
            try:
                if cookie_file.suffix == '.json':
                    with open(cookie_file, 'r') as f:
                        cookies = json.load(f)
                    # Playwright JSON cookies can be loaded directly
                    await self._context.add_cookies(cookies)
                    print("  🍪 Loaded cookies from JSON")
                    return True
                else:
                    # Pickle format (Selenium-style cookies)
                    with open(cookie_file, 'rb') as f:
                        selenium_cookies = pickle.load(f)
                    # Convert Selenium cookies to Playwright format
                    pw_cookies = []
                    for sc in selenium_cookies:
                        pc = {
                            'name': sc['name'],
                            'value': sc['value'],
                            'domain': sc.get('domain', '.x.com'),
                            'path': sc.get('path', '/'),
                        }
                        if 'expiry' in sc:
                            pc['expires'] = sc['expiry']
                        if sc.get('secure'):
                            pc['secure'] = True
                        if sc.get('httpOnly'):
                            pc['httpOnly'] = True
                        # Playwright requires sameSite
                        pc['sameSite'] = 'Lax'
                        pw_cookies.append(pc)
                    await self._context.add_cookies(pw_cookies)
                    print("  🍪 Loaded cookies from pickle")
                    return True
            except Exception as e:
                print(f"  ⚠️  Cookie load error ({cookie_file.name}): {e}")
                continue
        return False

    async def _verify_login(self) -> bool:
        """Navigate to X home and verify we're logged in."""
        try:
            await self._page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=30000)
            await self._page.wait_for_timeout(3000)
            url = self._page.url
            title = await self._page.title()
            if 'home' in url and 'login' not in url:
                self.logged_in = True
                print("  ✅ Verified login via cookies")
                return True
            else:
                print(f"  ❌ Not logged in (URL: {url[:60]}, Title: {title[:30]})")
                return False
        except Exception as e:
            print(f"  ❌ Login verify error: {e}")
            return False

    async def _login(self):
        """Load cookies and verify we're logged in."""
        if self.logged_in:
            return

        cookies_loaded = await self._load_cookies()
        if cookies_loaded:
            if await self._verify_login():
                return
        
        print("  ❌ Could not log in. Run 'python3 /tmp/x_login.py' to refresh cookies.")
        raise RuntimeError("X login failed — cookies expired or missing. Run /tmp/x_login.py to re-login.")

    async def _async_post(self, text: str) -> dict:
        """Post a tweet via browser."""
        await self._ensure_browser()
        await self._login()

        # Sanitize content before posting
        text = sanitize_content(text)

        if len(text) > 280:
            text = text[:277] + "..."

        # Navigate to compose
        await self._page.goto('https://x.com/compose/post', wait_until='domcontentloaded', timeout=30000)
        await self._page.wait_for_timeout(3000)

        # Find textbox and type
        try:
            textbox = await self._page.wait_for_selector('div[role="textbox"]', timeout=10000)
            await textbox.click()
            await self._page.keyboard.type(text, delay=20)
            await self._page.wait_for_timeout(1000)
        except Exception as e:
            return {"status": "failed", "reason": f"Could not find textbox: {e}"}

        # Click post button
        try:
            post_btn = await self._page.wait_for_selector('button[data-testid="tweetButton"]', timeout=5000)
            is_disabled = await post_btn.get_attribute('aria-disabled')
            if is_disabled == 'true':
                await self._page.wait_for_timeout(2000)
            await post_btn.click()
            await self._page.wait_for_timeout(3000)
            print(f"  ✅ Tweet posted via browser ({len(text)} chars)")
            return {"status": "posted", "text": text, "length": len(text), "method": "browser"}
        except Exception as e:
            await self._page.screenshot(path='/tmp/x_post_fail.png')
            return {"status": "failed", "reason": f"Post button error: {e}"}

    async def _async_reply(self, tweet_url: str, reply_text: str) -> dict:
        """Reply to a specific tweet via browser.
        
        Strategy order:
        1. Navigate to tweet → click reply → type → post
        2. Intent URL fallback → pre-fill → post
        """
        await self._ensure_browser()
        await self._login()

        # Sanitize content before replying
        reply_text = sanitize_content(reply_text)

        if len(reply_text) > 280:
            reply_text = reply_text[:277] + "..."

        # Extract tweet ID from URL
        match = re.search(r'/status/(\d+)', tweet_url)
        if not match:
            return {"status": "failed", "reason": f"Invalid tweet URL: {tweet_url}"}
        tweet_id = match.group(1)

        # ── STRATEGY 1: Navigate to tweet page and reply directly ──
        try:
            await self._page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await self._page.wait_for_timeout(4000)

            # Check for login wall
            if 'login' in self._page.url:
                self.logged_in = False
                await self._login()
                await self._page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
                await self._page.wait_for_timeout(4000)

            # Click the reply input area on the tweet page
            reply_selectors = [
                'div[data-testid="tweetTextarea_0"]',
                'div[data-testid="tweetTextarea_0RichTextInputContainer"]',
                'div[role="textbox"][data-testid="tweetTextarea_0"]',
                'div[role="textbox"]',
                '[aria-label="Post your reply"]',
                '[aria-label="Reply"]',
                '[placeholder="Post your reply"]',
            ]

            textbox = None
            for sel in reply_selectors:
                try:
                    textbox = await self._page.wait_for_selector(sel, timeout=3000)
                    if textbox:
                        break
                except Exception:
                    continue

            if textbox:
                await textbox.click()
                await self._page.wait_for_timeout(500)
                await self._page.keyboard.type(reply_text, delay=15)
                await self._page.wait_for_timeout(1000)

                # Click the reply/post button
                post_selectors = [
                    'button[data-testid="tweetButtonInline"]',
                    'button[data-testid="tweetButton"]',
                ]
                for sel in post_selectors:
                    try:
                        btn = await self._page.wait_for_selector(sel, timeout=3000)
                        if btn:
                            is_disabled = await btn.get_attribute('aria-disabled')
                            if is_disabled != 'true':
                                await btn.click()
                                await self._page.wait_for_timeout(3000)
                                print(f"  ✅ Reply posted via browser — direct ({len(reply_text)} chars)")
                                return {
                                    "status": "posted",
                                    "text": reply_text,
                                    "length": len(reply_text),
                                    "method": "browser_reply",
                                    "tweet_url": tweet_url,
                                }
                    except Exception:
                        continue
        except Exception as e:
            print(f"  ⚠️ Strategy 1 (direct reply) failed: {e}")

        # ── STRATEGY 2: Intent URL (pre-fills text) ──
        try:
            intent_url = f"https://x.com/intent/post?in_reply_to={tweet_id}&text={quote(reply_text)}"
            await self._page.goto(intent_url, wait_until='domcontentloaded', timeout=30000)
            await self._page.wait_for_timeout(5000)

            if 'login' in self._page.url:
                self.logged_in = False
                await self._login()
                await self._page.goto(intent_url, wait_until='domcontentloaded', timeout=30000)
                await self._page.wait_for_timeout(5000)

            # Intent URL pre-fills the text — just need to click post
            for attempt in range(10):
                for sel in ['button[data-testid="tweetButton"]', 'button[data-testid="tweetButtonInline"]']:
                    try:
                        btn = await self._page.query_selector(sel)
                        if btn:
                            is_disabled = await btn.get_attribute('aria-disabled')
                            if is_disabled != 'true':
                                await btn.click()
                                await self._page.wait_for_timeout(3000)
                                print(f"  ✅ Reply posted via browser — intent ({len(reply_text)} chars)")
                                return {
                                    "status": "posted",
                                    "text": reply_text,
                                    "length": len(reply_text),
                                    "method": "browser_reply",
                                    "tweet_url": tweet_url,
                                }
                    except Exception:
                        pass
                await self._page.wait_for_timeout(1000)

            # If button never enabled, try typing manually into any textbox
            textboxes = await self._page.query_selector_all('div[role="textbox"]')
            if textboxes:
                textbox = textboxes[-1]
                await textbox.click()
                await self._page.keyboard.press('Meta+a')
                await self._page.keyboard.type(reply_text, delay=15)
                await self._page.wait_for_timeout(1000)

                for sel in ['button[data-testid="tweetButton"]', 'button[data-testid="tweetButtonInline"]']:
                    btn = await self._page.query_selector(sel)
                    if btn:
                        is_disabled = await btn.get_attribute('aria-disabled')
                        if is_disabled != 'true':
                            await btn.click()
                            await self._page.wait_for_timeout(3000)
                            print(f"  ✅ Reply posted via browser — intent manual ({len(reply_text)} chars)")
                            return {
                                "status": "posted",
                                "text": reply_text,
                                "length": len(reply_text),
                                "method": "browser_reply",
                                "tweet_url": tweet_url,
                            }
        except Exception as e:
            print(f"  ⚠️ Strategy 2 (intent URL) failed: {e}")

        # Save screenshot for debugging
        try:
            await self._page.screenshot(path='/tmp/x_reply_fail.png')
            print("  📸 Failure screenshot saved to /tmp/x_reply_fail.png")
        except Exception:
            pass

        return {"status": "failed", "reason": "Could not find reply textbox"}

    async def _async_close(self):
        """Close the browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
        if self._playwright:
            await self._playwright.__aexit__(None, None, None)
            self._playwright = None
        self.logged_in = False

    # Sync wrappers for compatibility
    def post(self, text: str) -> dict:
        loop = _get_event_loop()
        return loop.run_until_complete(self._async_post(text))

    def reply(self, tweet_url: str, reply_text: str) -> dict:
        loop = _get_event_loop()
        return loop.run_until_complete(self._async_reply(tweet_url, reply_text))

    def close(self):
        loop = _get_event_loop()
        loop.run_until_complete(self._async_close())


# Singleton
_poster = None


def get_poster() -> BrowserPoster:
    global _poster
    if _poster is None:
        _poster = BrowserPoster()
    return _poster


def browser_post_tweet(text: str) -> dict:
    """Post a tweet using the browser (no API fees)."""
    poster = get_poster()
    return poster.post(text)


def browser_reply_to_tweet(tweet_url: str, reply_text: str) -> dict:
    """Reply to a specific tweet using the browser (no API fees)."""
    poster = get_poster()
    return poster.reply(tweet_url, reply_text)


def check_cookie_health() -> dict:
    """Check if X cookies are valid and report status.
    
    Returns dict with:
        - healthy: bool
        - message: str  
        - cookie_age_hours: float or None
        - needs_refresh: bool
    """
    import time
    
    # Check if cookie files exist
    if not COOKIES_JSON.exists() and not COOKIES_PATH.exists():
        return {
            "healthy": False,
            "message": "🚨 No cookies found. Run: python3 scripts/refresh_x_cookies.py",
            "cookie_age_hours": None,
            "needs_refresh": True,
        }
    
    # Check cookie age
    cookie_file = COOKIES_JSON if COOKIES_JSON.exists() else COOKIES_PATH
    age_seconds = time.time() - cookie_file.stat().st_mtime
    age_hours = age_seconds / 3600
    
    # Cookies older than 7 days are risky
    if age_hours > 168:  # 7 days
        return {
            "healthy": False,
            "message": f"⚠️ Cookies are {age_hours/24:.0f} days old — likely expired. Run: python3 scripts/refresh_x_cookies.py",
            "cookie_age_hours": age_hours,
            "needs_refresh": True,
        }
    
    # Try a quick login test
    try:
        poster = get_poster()
        loop = _get_event_loop()
        
        async def _test():
            await poster._ensure_browser()
            cookies_loaded = await poster._load_cookies()
            if not cookies_loaded:
                return False
            return await poster._verify_login()
        
        is_valid = loop.run_until_complete(_test())
        
        if is_valid:
            return {
                "healthy": True,
                "message": f"✅ Cookies valid ({age_hours:.0f}h old)",
                "cookie_age_hours": age_hours,
                "needs_refresh": False,
            }
        else:
            return {
                "healthy": False,
                "message": f"🚨 Cookies expired ({age_hours:.0f}h old). Run: python3 scripts/refresh_x_cookies.py",
                "cookie_age_hours": age_hours,
                "needs_refresh": True,
            }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"⚠️ Cookie check failed: {e}. Run: python3 scripts/refresh_x_cookies.py",
            "cookie_age_hours": age_hours,
            "needs_refresh": True,
        }
