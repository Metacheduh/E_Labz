"""
Semi-manual X login: Opens browser, waits for you to login, then saves cookies.
Much simpler and more reliable than full automation.
"""
import asyncio
from playwright.async_api import async_playwright
import json, pickle, os
from pathlib import Path

COOKIE_PATH = Path('/Users/eslynjosephhernandez/Documents/Free_Cash_Flow/data/x_cookies.pkl')
COOKIE_JSON = Path('/Users/eslynjosephhernandez/Documents/Free_Cash_Flow/data/x_cookies.json')

async def main():
    async with async_playwright() as p:
        # Launch VISIBLE browser
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--ignore-certificate-errors',
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check',
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        print("🌐 Opening X login page...")
        print("=" * 50)
        await page.goto('https://x.com/i/flow/login', wait_until='domcontentloaded', timeout=60000)
        
        print()
        print("👉 PLEASE LOG IN MANUALLY in the browser window!")
        print("   Use Google Sign-In or username/password")
        print("   The script will detect when you're logged in")
        print("=" * 50)
        print()
        
        # Wait up to 120 seconds for login
        logged_in = False
        for i in range(120):
            await page.wait_for_timeout(1000)
            url = page.url
            try:
                title = await page.title()
            except:
                title = ''
            
            # Check if we're on the home page (logged in)
            if 'home' in url and 'login' not in url:
                logged_in = True
                print(f"\n✅ LOGIN DETECTED after {i+1} seconds!")
                break
            
            # Progress indicator every 10 seconds
            if i % 10 == 0 and i > 0:
                print(f"   ⏳ Waiting... ({i}s elapsed, URL: {url[:50]})")
        
        if logged_in:
            # Wait a bit more for all cookies to be set
            await page.wait_for_timeout(3000)
            
            # Extract cookies
            cookies = await context.cookies()
            print(f"   Got {len(cookies)} cookies")
            
            # Convert to Selenium format
            selenium_cookies = []
            for c in cookies:
                sc = {
                    'name': c['name'],
                    'value': c['value'],
                    'domain': c['domain'],
                    'path': c['path'],
                    'secure': c.get('secure', False),
                    'httpOnly': c.get('httpOnly', False),
                }
                if c.get('expires', -1) > 0:
                    sc['expiry'] = int(c['expires'])
                selenium_cookies.append(sc)
            
            # Save
            COOKIE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(COOKIE_PATH, 'wb') as f:
                pickle.dump(selenium_cookies, f)
            print(f"   Saved {len(selenium_cookies)} cookies to {COOKIE_PATH}")
            
            with open(COOKIE_JSON, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            # Show auth cookies
            auth_found = False
            for c in cookies:
                if c['name'] in ('auth_token', 'ct0', 'twid'):
                    print(f"   🔑 {c['name']}: {c['value'][:20]}...")
                    auth_found = True
            
            if auth_found:
                print("\n🎉 Cookies saved! Browser automation will now work for replies!")
            else:
                print("\n⚠️  No auth cookies found. The login may not have completed fully.")
        else:
            print("\n❌ Login not detected within 120 seconds.")
            print("   Please try running this script again and log in faster.")
        
        await browser.close()
        print("\nDone!")

if __name__ == '__main__':
    asyncio.run(main())
