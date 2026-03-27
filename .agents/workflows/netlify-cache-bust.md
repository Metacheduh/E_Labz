---
description: Force Netlify to redeploy and serve the latest version of the landing page — use after every code push.
---

# Netlify Cache Bust Workflow

Run this after every `git push` to guarantee the live site reflects your latest changes immediately.

## Setup (One-Time)

Get your Netlify deploy hook URL:
1. Go to https://app.netlify.com → Your site → **Site configuration** → **Build & deploy** → **Build hooks**
2. Create a hook named "Manual Deploy"
3. Copy the URL — it looks like: `https://api.netlify.com/build_hooks/XXXXXXXXXXXXXXXX`
4. Save it: `echo 'NETLIFY_HOOK=https://api.netlify.com/build_hooks/YOUR_HOOK_ID' >> /Users/eslynjosephhernandez/Documents/untitled\ folder/E_Labz/config/.env`

## Steps

### 1. Push code to GitHub

```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz"
git add portfolio/index.html portfolio/style.css
git commit -m "fix: landing page update"
git push origin main
```

### 2. Trigger Netlify redeploy

```bash
source "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/config/.env"
curl -X POST "$NETLIFY_HOOK"
echo "🚀 Deploy triggered. Takes ~30-60 seconds."
```

### 3. Wait and verify

```bash
sleep 60
LIVE_TITLE=$(curl -s https://e-labz-portfolio.netlify.app/ | grep -o '<title>[^<]*</title>' | head -1)
echo "Live page title: $LIVE_TITLE"

# Pass: should contain "AutoTech"
# Fail: still shows "AutoStack HQ" — wait another 30s and retry
```

### 4. Smoke test key elements

```bash
curl -s https://e-labz-portfolio.netlify.app/ | python3 -c "
import sys
html = sys.stdin.read()
checks = {
    'AutoTech branding':    'AutoTech' in html,
    'No old branding':      'AutoStack HQ' not in html,
    'Carnegie products':    'Legal Edge' in html,
    'Sticky CTA':           'Browse All 23 Tools' in html,
    'How Easy section':     'It\'s This Easy' in html,
    'Video showcase':       'See What You\'re Getting' in html,
}
all_pass = True
for check, result in checks.items():
    icon = '✅' if result else '❌'
    print(f'{icon} {check}')
    if not result:
        all_pass = False
print()
print('🟢 DEPLOY VERIFIED' if all_pass else '🔴 DEPLOY FAILED — check above')
"
```

## Full One-Liner (Push + Deploy + Verify)

// turbo
```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz" && \
git add portfolio/index.html portfolio/style.css portfolio/script.js && \
git diff --cached --stat && \
git commit -m "chore: deploy update $(date +%Y-%m-%d)" && \
git push origin main && \
source config/.env && \
curl -X POST "$NETLIFY_HOOK" && \
echo "⏳ Waiting 60s for deploy..." && sleep 60 && \
curl -s https://e-labz-portfolio.netlify.app/ | grep -o '<title>[^<]*</title>'
```
