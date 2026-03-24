---
description: Create a new digital product (ebook, prompt pack, or template) and list it on Gumroad.
---

# Create Product Workflow

## Steps

### 1. Pick a topic from research data

```bash
cd ~/Documents/Free_Cash_Flow
source .venv/bin/activate
python -c "
import json, glob

# Get latest research
files = sorted(glob.glob('output/research/*.json'))
if files:
    with open(files[-1]) as f:
        research = json.load(f)
    for i, topic in enumerate(research.get('recommended_product_ideas', [])):
        print(f'{i+1}. {topic[\"title\"]} — \${topic[\"price\"]} ({topic[\"format\"]})')
else:
    print('No research data found. Run /daily-pipeline first.')
"
```

### 2. Generate the product

```bash
python -c "
from orchestrator.product import create_product

product = create_product({
    'title': 'PRODUCT_TITLE_HERE',
    'type': 'ebook',  # or 'prompt_pack' or 'template'
    'price': 19,
    'chapters': 8,  # for ebooks
    'niche': 'AI agents'
})
print(f'Product created: {product[\"file_path\"]}')
"
```

### 3. Quality check

- [ ] Open the PDF and verify formatting
- [ ] Check table of contents accuracy
- [ ] Verify all links work
- [ ] Ensure Autostack HQ friendly voice is consistent
- [ ] Confirm price is set correctly

### 4. List on Gumroad

```bash
python -c "
from orchestrator.product import list_on_gumroad

url = list_on_gumroad({
    'title': 'PRODUCT_TITLE_HERE',
    'description': 'PRODUCT_DESCRIPTION_HERE',
    'price': 19,
    'file_path': 'output/products/FILENAME.pdf',
    'slug': 'product-slug'
})
print(f'Listed on Gumroad: {url}')
"
```

### 5. Promote on X

```bash
python -c "
from orchestrator.twitter import post_to_twitter

post_to_twitter(
    content='GUMROAD_URL_HERE',
    post_type='product_promo',
    product_name='PRODUCT_TITLE_HERE',
    price=19
)
print('Product promotion thread posted!')
"
```

## Product Checklist

- [ ] Topic is validated by research data
- [ ] Content is 100% actionable (not theory)
- [ ] Title is clear and benefit-driven
- [ ] PDF formatting is clean
- [ ] Listed on Gumroad with preview image
- [ ] Promo thread posted on X
- [ ] Product logged in `output/products/catalog.json`
