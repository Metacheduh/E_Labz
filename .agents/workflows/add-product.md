---
description: Full pipeline to onboard a new product — Stripe, delivery server, landing page, deploy. One clear sequence.
---

# Add Product Workflow

Use this every time you ship a new digital product. Covers: ZIP → Stripe → Landing Page → Deploy → Verify.

## Required Info Before Starting

Fill these in before running any steps:

```bash
# Edit these:
PRODUCT_NAME="Your Outcome-Focused Product Name"   # Carnegie style — outcome first
PRODUCT_DESC="One sentence: what they get + result"
PRODUCT_PRICE=29                                    # in USD, no decimals
PRODUCT_FILE="/path/to/your-product.zip"
PRODUCT_CATEGORY="Agents & Kits"                   # Options: Agents & Kits | Workflows | Content Packs | Templates
PRODUCT_BADGE="NEW"                                 # Options: NEW | TOP SELLER | HOT | (leave blank)
```

## Steps

### 1. Package the product ZIP

```bash
# Make sure ZIP has a README inside with setup instructions
zip -r "$(basename $PRODUCT_FILE)" "$(dirname $PRODUCT_FILE)/$(basename $PRODUCT_FILE .zip)/"
echo "ZIP size: $(du -sh $PRODUCT_FILE | cut -f1)"
echo "ZIP contents:"
unzip -l "$PRODUCT_FILE" | head -20
```

### 2. Copy ZIP to delivery server folder

```bash
cp "$PRODUCT_FILE" \
  "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/products/delivery-server/files/"
echo "✅ File staged for delivery server"
ls -lh "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/products/delivery-server/files/"
```

### 3. Create Stripe product + price + payment link

```bash
source "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/config/.env"

# Create product
STRIPE_PRODUCT=$(curl -s https://api.stripe.com/v1/products \
  -u "$STRIPE_SECRET_KEY:" \
  -d "name=$PRODUCT_NAME" \
  -d "description=$PRODUCT_DESC")
PRODUCT_ID=$(echo $STRIPE_PRODUCT | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Product ID: $PRODUCT_ID"

# Create price
STRIPE_PRICE=$(curl -s https://api.stripe.com/v1/prices \
  -u "$STRIPE_SECRET_KEY:" \
  -d "product=$PRODUCT_ID" \
  -d "unit_amount=$(( PRODUCT_PRICE * 100 ))" \
  -d "currency=usd")
PRICE_ID=$(echo $STRIPE_PRICE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Price ID: $PRICE_ID"

# Create payment link
STRIPE_LINK=$(curl -s https://api.stripe.com/v1/payment_links \
  -u "$STRIPE_SECRET_KEY:" \
  -d "line_items[0][price]=$PRICE_ID" \
  -d "line_items[0][quantity]=1")
CHECKOUT_URL=$(echo $STRIPE_LINK | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])")
echo "✅ Checkout URL: $CHECKOUT_URL"
```

### 4. Map filename in delivery server

Open `products/delivery-server/server.js` and add the product to the `PRODUCT_FILE_MAP` object:

```javascript
// In server.js → PRODUCT_FILE_MAP
"price_YOUR_PRICE_ID": "your-product-filename.zip",
```

### 5. Add product card to landing page

Open `portfolio/index.html` and add a card in the correct tab section.

Card template (copy-paste and fill in):

```html
<div class="product-card" data-category="agents">
  <div class="card-badge">NEW</div>
  <img src="YOUR_IMAGE_URL" alt="PRODUCT_NAME" class="card-img" loading="lazy">
  <div class="card-body">
    <h3 class="card-title">PRODUCT_NAME</h3>
    <p class="card-desc">PRODUCT_DESC</p>
    <ul class="card-features">
      <li>✓ Feature one</li>
      <li>✓ Feature two</li>
      <li>✓ Feature three</li>
    </ul>
    <a href="CHECKOUT_URL" class="btn-buy" target="_blank">
      Get It → $PRODUCT_PRICE
    </a>
  </div>
</div>
```

### 6. Run launch checklist

```bash
# Verify the page passes all checks before deploying
# Follow /launch-checklist workflow
```

### 7. Deploy to Netlify

```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz"
git add portfolio/index.html products/delivery-server/
git commit -m "feat: add product — $PRODUCT_NAME at \$$PRODUCT_PRICE"
git push origin main
source config/.env && curl -X POST "$NETLIFY_HOOK"
echo "⏳ Waiting 60s..." && sleep 60
```

### 8. Rebuild and redeploy delivery server

```bash
cd "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/products/delivery-server"
gcloud run deploy product-delivery \
  --source . \
  --region us-east1 \
  --project gen-lang-client-0276729648
```

### 9. Verify end-to-end

- [ ] Click Stripe checkout URL → reaches Stripe checkout
- [ ] Run `/sale-check` to confirm delivery server is healthy
- [ ] Do a test purchase if possible
- [ ] Confirm download link works

### 10. Add to promo rotation

```bash
echo "Added: $PRODUCT_NAME at \$$PRODUCT_PRICE — $(date +%Y-%m-%d)" \
  >> "/Users/eslynjosephhernandez/Documents/untitled folder/E_Labz/logs/products.txt"
echo "Next step: schedule this product in /promo-blast for next week's rotation"
```
