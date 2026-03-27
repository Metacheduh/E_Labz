---
description: Pre-deploy quality gate — run before every landing page update goes live. Zero broken deploys.
---

# Launch Checklist

Run this BEFORE pushing any landing page changes. If any check fails, fix it first.

## Steps

### 1. Branding check — no old names

```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/portfolio"

python3 -c "
with open('index.html') as f:
    html = f.read()

banned = ['AutoStack HQ', 'autostack-hq', 'AutoStack', 'I Built This Entire Business']
for term in banned:
    if term.lower() in html.lower():
        print(f'❌ FAIL: Found old branding: \"{term}\"')
    else:
        print(f'✅ Clean: No \"{term}\"')
"
```

### 2. Stripe links check — all 23 checkout URLs are present

```bash
python3 -c "
import re
with open('index.html') as f:
    html = f.read()
links = re.findall(r'https://buy\.stripe\.com/[a-zA-Z0-9]+', html)
unique = list(set(links))
print(f'Found {len(unique)} Stripe links (expected: 23)')
if len(unique) < 23:
    print('❌ FAIL: Missing Stripe links')
else:
    print('✅ PASS: All Stripe links present')
for link in unique[:3]:
    print(f'  Sample: {link}')
"
```

### 3. Mobile title tag check

```bash
python3 -c "
import re
with open('index.html') as f:
    html = f.read()

title = re.search(r'<title>(.*?)</title>', html)
print(f'Title: {title.group(1) if title else \"MISSING\"}')
print('✅ PASS' if title and 'AutoTech' in title.group(1) else '❌ FAIL: Title should contain AutoTech')

viewport = '<meta name=\"viewport\"' in html
print(f'Viewport meta: {\"✅ PASS\" if viewport else \"❌ FAIL: Add viewport meta tag\"}')
"
```

### 4. Delivery server health

```bash
source "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/config/.env"
DELIVERY_URL=$(gcloud run services describe product-delivery \
  --region us-east1 \
  --format 'value(status.url)' \
  --project=gen-lang-client-0276729648 2>/dev/null)

if [ -z "$DELIVERY_URL" ]; then
  echo "❌ FAIL: Could not find delivery server URL"
else
  STATUS=$(curl -s "$DELIVERY_URL/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','error'))" 2>/dev/null)
  echo "Delivery server: $STATUS"
  [ "$STATUS" = "ok" ] && echo "✅ PASS" || echo "❌ FAIL: Delivery server down"
fi
```

### 5. Git status — nothing uncommitted

```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz"
DIRTY=$(git status --short portfolio/)
if [ -z "$DIRTY" ]; then
  echo "✅ PASS: Nothing uncommitted in portfolio/"
else
  echo "⚠️  Uncommitted changes:"
  echo "$DIRTY"
  echo "Run: git add portfolio/ && git commit -m 'fix: update'"
fi
```

### 6. Final go/no-go

```bash
echo ""
echo "=============================="
echo "  LAUNCH CHECKLIST SUMMARY"
echo "=============================="
echo "If all ✅ above → run /netlify-cache-bust to deploy"
echo "If any ❌ above → fix before deploying"
echo ""
echo "Deploy command:"
echo "  source config/.env && curl -X POST \"\$NETLIFY_HOOK\""
```

## Quick Run (All Checks)

// turbo
```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/portfolio" && \
python3 -c "
import re
with open('index.html') as f: html = f.read()

results = []
results.append(('No old branding', 'AutoStack HQ' not in html and 'AutoStack' not in html))
results.append(('AutoTech in title', 'AutoTech' in html))
results.append(('Has Stripe links', 'buy.stripe.com' in html))
results.append(('Carnegie names present', 'Legal Edge' in html and 'Never Chase' in html))
results.append(('Sticky CTA', 'Browse All 23 Tools' in html))
results.append(('Video section', 'See What You' in html))
results.append(('Easy steps section', 'This Easy' in html))

all_pass = all(r for _, r in results)
for name, result in results:
    print(f'{\"✅\" if result else \"❌\"} {name}')
print()
print('🟢 READY TO DEPLOY' if all_pass else '🔴 FIX ISSUES BEFORE DEPLOYING')
"
```
