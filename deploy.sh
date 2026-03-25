#!/bin/bash
# E-Labz Swarm — Deploy to Google Cloud Run
# Usage: ./deploy.sh
#
# Uses prompt-design-480413 (your GCP project with Cloud Run enabled)
# Injects all API keys via --env-vars-file (handles special chars)

set -e

PROJECT_ID="prompt-design-480413"
REGION="us-east4"
SERVICE="e-labz-swarm"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE"

echo "🚀 Deploying E-Labz Swarm to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region:  $REGION"
echo "   Service: $SERVICE"

# Load env vars from config/.env for injection
ENV_FILE="$(dirname "$0")/config/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ config/.env not found. Cannot deploy without API keys."
    exit 1
fi

# Create a YAML env-vars file for Cloud Run (handles special chars safely)
YAML_ENV="/tmp/e-labz-env-vars.yaml"
echo "# Auto-generated env vars for Cloud Run" > "$YAML_ENV"
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    # Extract key and value
    key=$(echo "$line" | cut -d'=' -f1 | xargs)
    value=$(echo "$line" | cut -d'=' -f2-)
    [ -z "$key" ] && continue
    [ -z "$value" ] && continue
    # Write as YAML (quote value to handle special chars)
    echo "${key}: '${value}'" >> "$YAML_ENV"
done < "$ENV_FILE"

# Add system vars
echo "TZ: 'America/New_York'" >> "$YAML_ENV"
echo "PYTHONUNBUFFERED: '1'" >> "$YAML_ENV"

echo "   Env vars file: $YAML_ENV ($(wc -l < "$YAML_ENV" | xargs) vars)"

# Step 1: Build and push Docker image via Cloud Build
# (Skip if image was recently built — check with --tag)
echo ""
echo "📦 Building Docker image via Cloud Build..."
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID" --timeout=600

# Step 2: Deploy to Cloud Run with env vars file
echo ""
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy "$SERVICE" \
    --image "$IMAGE" \
    --platform managed \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 3 \
    --timeout 3600 \
    --env-vars-file "$YAML_ENV" \
    --allow-unauthenticated

# Cleanup
rm -f "$YAML_ENV"

# Step 3: Get the URL
echo ""
URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT_ID" --format='value(status.url)')
echo "✅ Deployed!"
echo "   Dashboard:  $URL"
echo "   Health:     $URL/health"
echo "   Metrics:    $URL/api/metrics"
echo "   Swarm:      $URL/api/swarm"
echo "   Revenue:    $URL/api/revenue"
echo "   Webhooks:   Configure Stripe webhook URL to: $URL/webhooks/stripe"
