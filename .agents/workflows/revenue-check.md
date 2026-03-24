---
description: Check revenue metrics, growth progress, and whether the swarm is on track to hit $3K/month.
---

# Revenue Check Workflow

## Quick Revenue Dashboard

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate
python -c "
from orchestrator.metrics import get_revenue_dashboard
from datetime import date

d = get_revenue_dashboard()
print('╔══════════════════════════════════╗')
print('║   FREE CASH FLOW DASHBOARD      ║')
print('╠══════════════════════════════════╣')
print(f'║  Month: {date.today().strftime(\"%B %Y\")}            ║')
print(f'║  Revenue: \${d[\"current_month_revenue\"]:,.2f}          ║')
print(f'║  Target:  \$3,000.00              ║')
print(f'║  Gap:     \${3000 - d[\"current_month_revenue\"]:,.2f}          ║')
print(f'║  Daily avg: \${d[\"daily_average\"]:,.2f}            ║')
print(f'║  Daily needed: \${d[\"daily_needed\"]:,.2f}         ║')
print(f'║  On track: {\"✅ YES\" if d[\"on_track\"] else \"❌ NO\"}               ║')
print('╚══════════════════════════════════╝')
"
```

## Follower Growth Check

```bash
python -c "
from orchestrator.metrics import get_growth_metrics

g = get_growth_metrics()
print(f'Followers: {g[\"total_followers\"]:,}')
print(f'This week: +{g[\"week_growth\"]}')
print(f'This month: +{g[\"month_growth\"]}')
print(f'Days to 10K: {g[\"days_to_10k\"]}')
print(f'Monthly target: 10,000 by Month 5')
"
```

## Product Sales Breakdown

```bash
python -c "
from orchestrator.metrics import get_product_metrics

products = get_product_metrics()
print('Product Performance:')
print(f'{\"Product\":<35} {\"Sales\":>6} {\"Revenue\":>10}')
print('-' * 55)
for p in products:
    print(f'{p[\"name\"]:<35} {p[\"sales\"]:>6} \${p[\"revenue\"]:>9,.2f}')
print('-' * 55)
print(f'{\"TOTAL\":<35} {sum(p[\"sales\"] for p in products):>6} \${sum(p[\"revenue\"] for p in products):>9,.2f}')
"
```

## Revenue Breakdown by Stream

```bash
python -c "
from orchestrator.metrics import get_revenue_by_stream

streams = get_revenue_by_stream()
print('Revenue by Stream:')
print(f'{\"Stream\":<25} {\"Monthly\":>10} {\"Target\":>10} {\"Status\":>8}')
print('-' * 58)
for s in streams:
    status = '✅' if s['current'] >= s['target'] * 0.8 else '⚠️' if s['current'] >= s['target'] * 0.5 else '❌'
    print(f'{s[\"name\"]:<25} \${s[\"current\"]:>9,.2f} \${s[\"target\"]:>9,.2f} {status:>6}')
"
```
