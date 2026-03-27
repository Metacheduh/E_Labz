---
description: Push portfolio changes to GitHub and force Netlify to serve the latest version immediately.
---

# Deploy Workflow

One-command deploy. Runs launch checklist, commits, pushes, and triggers Netlify redeploy.

## Quick Deploy (Most Common)

// turbo
```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz" && \
source config/.env && \
git add portfolio/ && \
git status --short && \
git diff --cached --stat
```

Then commit and push:

// turbo
```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz" && \
source config/.env && \
git commit -m "chore: deploy $(date +%Y-%m-%d-%H%M)" && \
git push origin main && \
curl -X POST "$NETLIFY_HOOK" && \
echo "🚀 Deploy triggered at $(date)" && \
echo "⏳ Live in ~60 seconds: https://e-labz-portfolio.netlify.app/"
```

## Verify Deploy Succeeded

// turbo
```bash
sleep 60 && \
curl -s https://e-labz-portfolio.netlify.app/ | python3 -c "
import sys, re
html = sys.stdin.read()
title = re.search(r'<title>(.*?)</title>', html)
print(f'Live title: {title.group(1) if title else \"UNKNOWN\"}')
checks = [
    ('AutoTech', 'AutoTech' in html),
    ('No old branding', 'AutoStack HQ' not in html),
    ('Carnegie names', 'Legal Edge' in html),
]
for name, ok in checks:
    print(f'{\"✅\" if ok else \"❌\"} {name}')
"
```

## Full Deploy + Verify (One Block)

// turbo
```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz" && \
source config/.env && \
git add portfolio/ && \
git commit -m "chore: deploy $(date +%Y-%m-%d-%H%M)" 2>/dev/null || echo "Nothing new to commit" && \
git push origin main && \
curl -X POST "$NETLIFY_HOOK" -s && echo "Deploy triggered." && \
sleep 65 && \
curl -s https://e-labz-portfolio.netlify.app/ | python3 -c "
import sys
html = sys.stdin.read()
ok = 'AutoTech' in html and 'AutoStack HQ' not in html
print('🟢 DEPLOY VERIFIED — AutoTech is live' if ok else '🔴 DEPLOY NOT YET LIVE — wait 30s and retry')
"
```

## Setup (One-Time)

### Get your Netlify deploy hook

1. https://app.netlify.com → Your site → Site configuration → Build & deploy → Build hooks
2. Create new hook: name it "CLI Deploy"
3. Add to config/.env:
   ```
   NETLIFY_HOOK=https://api.netlify.com/build_hooks/YOUR_HOOK_ID
   ```

## Notes
- Always run `/launch-checklist` before deploying if making major changes
- Netlify deploy takes 30–90 seconds after trigger
- If Netlify still shows old content after 3 minutes → check Netlify dashboard for build errors
