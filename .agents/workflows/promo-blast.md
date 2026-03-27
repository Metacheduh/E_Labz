---
description: Promote 2-3 AutoTech products this week on X using outcome-focused copy. Run weekly on Monday.
---

# Promo Blast Workflow

Systematically promote products from the 23-tool catalog. Never post generic "check out my product" copy — always outcome first, price anchor, one CTA. See `/promo-voice-rules` for copy standards.

## Weekly Rotation Schedule

Each week, pick products from a different category:

| Week | Focus | Products |
|---|---|---|
| Week 1 | Legal & Docs | Legal Edge, Court Docs in Seconds, StrykePt ebook |
| Week 2 | Content & Social | Content Factory, Content Multiplier, Anti-AI Detection |
| Week 3 | AI Agents & Kits | AI Team, 5 AI Workers, AI Starter Kit |
| Week 4 | Business Systems | Autopilot Business, Never Chase Payments, Launch Playbook |

## Steps

### 1. Pick this week's 2 products

Check which products haven't been promoted recently by reviewing X post history. Avoid promoting the same product in back-to-back weeks.

### 2. Verify Stripe checkout links are live

```bash
# Check product links from index.html are returning 200
python3 -c "
import urllib.request
stripe_links = [
    'https://buy.stripe.com/YOUR_LINK_1',
    'https://buy.stripe.com/YOUR_LINK_2',
]
for link in stripe_links:
    try:
        code = urllib.request.urlopen(link, timeout=5).getcode()
        print(f'✅ {link[:50]} → {code}')
    except Exception as e:
        print(f'❌ {link[:50]} → {e}')
"
```

### 3. Write the promo thread (follow `/promo-voice-rules`)

Structure every promo post as:

```
[OUTCOME hook — what they get]

Most people [frustrating problem].

[Product name] fixes this.

Here's what you get:
→ [Benefit 1]
→ [Benefit 2]  
→ [Benefit 3]

This used to cost $[anchor price] in consulting.

Now it's $[your price].

Grab it → [Stripe link]
```

### 4. Post via the orchestrator

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate

python3 -c "
from orchestrator.publish.twitter import post_tweet

# Post 1: Hook (single tweet)
post_tweet('''
Never chase a late payment again.

I built an automated invoice follow-up system that:
→ Sends reminder emails at day 1, 3, 7
→ Escalates tone automatically  
→ Tracks every payment in a sheet

Used to cost \$300/hr to set up.

Now \$19: https://buy.stripe.com/YOUR_LINK
''', humanize=True)
"
```

### 5. Post a follow-up reply (social proof angle)

2-4 hours after the main post, reply to it:

```bash
python3 -c "
from orchestrator.publish.twitter import post_tweet
# Reply to the tweet ID from Step 4
post_tweet('Already sold 3 copies this morning. Simple stuff that just works.', humanize=True)
"
```

### 6. Log the promo

```bash
echo "$(date +%Y-%m-%d): Promoted [PRODUCT NAME] at \$[PRICE] — Tweet ID: [ID]" \
  >> "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/logs/promo_log.txt"
```

## Quick Promo (Single Tweet)

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate
python3 -c "
from orchestrator.publish.twitter import post_tweet
TWEET = '''YOUR PROMO COPY HERE'''
post_tweet(TWEET, humanize=True)
print('Posted.')
"
```

## Notes
- Post promo content at 9am-11am ET or 7pm-9pm ET for max reach
- Never post more than 1 promo per day — breaks the value-to-promo ratio
- Always run `/sale-check` the next morning to confirm any purchases were delivered
