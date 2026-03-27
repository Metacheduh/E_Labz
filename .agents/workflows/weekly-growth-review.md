---
description: Sunday review — connects this week's content performance to revenue. Outputs one concrete action for next week.
---

# Weekly Growth Review

Run every Sunday. Takes ~10 minutes. Connects the dots between what you posted, who followed, and what sold.

## Steps

### 1. Check follower growth this week

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate
python3 -c "
from orchestrator.metrics import get_growth_metrics
g = get_growth_metrics()
print('=== FOLLOWER GROWTH ===')
print(f'Total followers:  {g[\"total_followers\"]:,}')
print(f'This week:        +{g.get(\"week_growth\", \"N/A\")}')
print(f'This month:       +{g.get(\"month_growth\", \"N/A\")}')
print(f'Target pace:       +500/week to hit 10K by Month 5')
pace = g.get('week_growth', 0)
print(f'On pace:          {\"✅ YES\" if pace >= 500 else \"❌ NO — need to post more value content\"}')
"
```

### 2. Check which tweet categories performed best

```bash
python3 -c "
from orchestrator.metrics import get_top_tweets
tweets = get_top_tweets(limit=5, days=7)
print()
print('=== TOP TWEETS THIS WEEK ===')
for i, t in enumerate(tweets, 1):
    print(f'{i}. [{t.get(\"category\",\"?\"):12}] {t.get(\"impressions\",0):,} impr | {t.get(\"likes\",0)} likes | {t.get(\"text\",\"\")[:60]}...')
print()
print('INSIGHT: Post more of the top category next week.')
"
```

### 3. Check revenue this week

```bash
python3 -c "
from orchestrator.metrics import get_revenue_dashboard
d = get_revenue_dashboard()
print('=== REVENUE ===')
print(f'This month so far: \${d[\"current_month_revenue\"]:,.2f}')
print(f'Target:            \$3,000.00')
print(f'Gap:               \${3000 - d[\"current_month_revenue\"]:,.2f}')
print(f'Daily needed:      \${d[\"daily_needed\"]:,.2f}/day to hit target')
print(f'On track:          {\"✅ YES\" if d[\"on_track\"] else \"❌ NO\"}')
"
```

### 4. Check Stripe for this week's sales

```bash
source "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/config/.env"
curl -s "https://api.stripe.com/v1/payment_intents?limit=20&created[gte]=$(python3 -c 'import time; print(int(time.time()) - 604800)')" \
  -u "$STRIPE_SECRET_KEY:" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
payments = [p for p in data.get('data', []) if p.get('status') == 'succeeded']
total = sum(p['amount'] for p in payments) / 100
print(f'Sales this week: {len(payments)} transactions = \${total:.2f}')
for p in payments:
    print(f'  \${p[\"amount\"]/100:.2f} — {p.get(\"description\", \"unknown product\")}')
"
```

### 5. Check promo log — what was promoted vs. what sold

```bash
echo
echo "=== PROMO LOG THIS WEEK ==="
tail -7 "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/logs/promo_log.txt" 2>/dev/null || echo "No promo log yet. Start running /promo-blast weekly."
```

### 6. Generate next week's action

Based on the above, answer these 3 questions and write the answer:

```bash
echo
echo "=== NEXT WEEK ACTION ==="
echo "1. CONTENT: Post more of: [fill from Step 2 top category]"
echo "2. PROMO:  Feature these 2 products: [pick from rotation in /promo-blast]"
echo "3. FIX:    [one thing broken this week — delivery, copy, schedule, etc.]"
echo
echo "Revenue gap: need \$X more this month = Y sales of \$Z product"
```

## Quick Summary (One-Liner)

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate && \
python3 -c "
from orchestrator.metrics import get_growth_metrics, get_revenue_dashboard
g = get_growth_metrics()
d = get_revenue_dashboard()
print(f'Week Summary: +{g.get(\"week_growth\",\"?\")} followers | \${d[\"current_month_revenue\"]:.2f} revenue | Gap: \${3000-d[\"current_month_revenue\"]:.2f}')
"
```

## Notes
- Run every Sunday before planning next week
- If revenue gap > $1,500 with 2 weeks left in month → double promo frequency
- If follower growth < 200/week → review content voice, increase value-to-promo ratio to 10:1
- The goal isn't vanity metrics — it's: **more followers → landing page traffic → sales**
