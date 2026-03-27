---
description: Verify every Stripe sale in the last 24h was received, processed, and delivered to the customer.
---

# Sale Check Workflow

Run this daily or whenever you want to verify the full purchase → delivery loop is working.

## Steps

### 1. Check Stripe for recent payments

```bash
curl -s https://api.stripe.com/v1/checkout/sessions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "limit=10" \
  -d "status=complete" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
sessions = data.get('data', [])
print(f'Last {len(sessions)} completed sessions:')
for s in sessions:
    print(f'  [{s[\"created\"]}] {s[\"customer_details\"][\"email\"]} — \${s[\"amount_total\"]/100:.2f}')
"
```

### 2. Check delivery server health

```bash
curl -s https://product-delivery-[YOUR-HASH]-ue.a.run.app/health \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ Delivery server UP' if d.get('status')=='ok' else '❌ DELIVERY SERVER DOWN')"
```

> **Find your Cloud Run URL:** `gcloud run services describe product-delivery --region us-east1 --format 'value(status.url)'`

### 3. Check delivery server logs for webhook events

```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=product-delivery AND textPayload:webhook" \
  --limit=20 \
  --format="table(timestamp,textPayload)" \
  --project=gen-lang-client-0276729648
```

### 4. Look for any failed deliveries (no download token generated)

```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=product-delivery AND (textPayload:ERROR OR textPayload:failed)" \
  --limit=10 \
  --format="table(timestamp,textPayload)" \
  --project=gen-lang-client-0276729648
```

### 5. Spot-check a delivery token manually

```bash
# Replace SESSION_ID with a real Stripe session ID from Step 1
SESSION_ID="cs_live_XXXXX"
DELIVERY_URL=$(gcloud run services describe product-delivery --region us-east1 --format 'value(status.url)')

curl -s "$DELIVERY_URL/download?token=$SESSION_ID" -o /dev/null -w "%{http_code}"
# Expected: 200 (file download) or 302 (redirect to file)
# If 404: token generation failed for this session
```

## Pass/Fail Criteria

| Check | Pass | Fail Action |
|---|---|---|
| Delivery server health | Status `ok` | Redeploy: `gcloud run deploy product-delivery --region us-east1` |
| Webhook received | Log entry per Stripe session | Check Stripe webhook dashboard, re-register endpoint |
| Download token | HTTP 200/302 | Check server.js token generation logic |
| No ERROR logs | Zero errors | Check Cloud Run logs for cause |

## Quick One-Liner (Summary Only)

```bash
DELIVERY_URL=$(gcloud run services describe product-delivery --region us-east1 --format 'value(status.url)' --project=gen-lang-client-0276729648 2>/dev/null)
echo "Delivery URL: $DELIVERY_URL"
curl -s "$DELIVERY_URL/health" && echo "" && echo "Run full check above to verify recent sales."
```
