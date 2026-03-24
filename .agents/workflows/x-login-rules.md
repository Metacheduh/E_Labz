---
description: Rules for logging into X/Twitter - always use Google Sign-In
---

# X/Twitter Login Rules

## Rule 1: Always Use Google Sign-In
When logging into X/Twitter (x.com), **always use the Google Sign-In option** instead of entering username/password directly.

### Steps:
1. Navigate to https://x.com/login
2. Click "Sign in with Google" button
3. Select the Google account: hernandezeslyn@gmail.com
4. Complete any Google auth prompts

### Why:
- More reliable than username/password
- Avoids X's suspicious login detection
- Works better with browser automation
- No password entry needed (already signed into Google)

## Rule 2: Cookie Persistence
- After first login, save cookies to `data/x_cookies.pkl`
- On subsequent runs, load cookies first to skip login entirely
- Only re-login if cookies are expired/invalid

## Rule 3: Browser Posting is Primary
- Use browser-based posting (Selenium/Playwright) — it's FREE
- Twitter API posting costs $200/month — avoid
- Typefully API is preferred fallback if browser fails
- Twitter API is read-only (for metrics/analytics only)
