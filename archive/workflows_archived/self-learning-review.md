---
description: Run the weekly self-learning review that analyzes performance and auto-adjusts all agent configurations.
---

# Self-Learning Review Workflow

Run this to manually trigger the weekly self-learning cycle (normally runs automatically Sunday at midnight).

## Steps

### 1. Activate environment

```bash
cd ~/Documents/Free_Cash_Flow
source .venv/bin/activate
export $(cat config/.env | xargs)
```

### 2. Collect metrics

```bash
python -c "
from orchestrator.self_learn import collect_all_metrics
from datetime import date, timedelta

week_end = date.today()
week_start = week_end - timedelta(days=7)

metrics = collect_all_metrics(week_start, week_end)
print(f'Twitter impressions: {metrics[\"twitter\"][\"total_impressions\"]}')
print(f'Gumroad revenue: \${metrics[\"gumroad\"][\"total_revenue\"]}')
print(f'Follower growth: +{metrics[\"twitter\"][\"follower_growth\"]}')
print(f'Posts published: {metrics[\"content\"][\"posts_published\"]}')
"
```

### 3. Analyze performance

```bash
python -c "
from orchestrator.self_learn import analyze_performance, collect_all_metrics
from datetime import date, timedelta

metrics = collect_all_metrics(date.today() - timedelta(days=7), date.today())
insights = analyze_performance(metrics)

print('=== Revenue ===')
print(f'Monthly rate: \${insights[\"revenue\"][\"monthly_rate\"]}')
print(f'Target: \$3,000')
print(f'Gap: \${insights[\"revenue\"][\"gap\"]}')
print(f'On track: {insights[\"revenue\"][\"on_track\"]}')

print()
print('=== Content ===')
print(f'Best hook type: {insights[\"content\"][\"best_hook_type\"]}')
print(f'Best post time: {insights[\"content\"][\"best_time\"]}')
print(f'Best content type: {insights[\"content\"][\"best_type\"]}')

print()
print('=== Growth ===')
print(f'Days to 10K followers: {insights[\"growth\"][\"days_to_10k\"]}')
print(f'Velocity: {insights[\"growth\"][\"velocity\"]}')
"
```

### 4. Apply configuration updates

```bash
python -c "
from orchestrator.self_learn import apply_updates, analyze_performance, collect_all_metrics
from datetime import date, timedelta

metrics = collect_all_metrics(date.today() - timedelta(days=7), date.today())
insights = analyze_performance(metrics)
changes = apply_updates(insights)

print('Changes applied:')
for change in changes:
    print(f'  • {change}')
"
```

### 5. Verify updated configs

```bash
echo "=== niche.yaml ===" && cat config/niche.yaml
echo ""
echo "=== schedule.yaml ===" && cat config/schedule.yaml
```

### 6. View the review report

```bash
cat data/performance/weekly_review_$(date +%Y-%m-%d).json | python -m json.tool
```

## Quick Run (All Steps)

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate
python -c "from orchestrator.self_learn import run_weekly_review; run_weekly_review()"
```

## What Gets Updated

| File | What Changes | Max Change/Week |
|------|-------------|-----------------|
| `config/niche.yaml` | Topic weights, secondary niches | ±50% per weight |
| `config/schedule.yaml` | Post times, engagement windows | ±2 hours per slot |
| `data/templates/hooks.json` | Hook template probabilities | ±50% per weight |
| `config/agents.yaml` | Agent-specific tuning | Parameters only |

## Safety Checks

- Previous configs are backed up to `data/performance/backups/`
- No config value changes by more than 50% in one review
- At least 7 days of data required before changes
- Review report is always generated, even if no changes are made
