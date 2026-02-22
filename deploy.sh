#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Deploy ISACA SD Advisor to Azure Container Apps
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - .env file with all required variables set (see .env.example)
#   - Docker installed and running (only needed for local build; az acr build
#     builds in the cloud so Docker is NOT required)
#
# Usage:
#   bash deploy.sh
#
# What it does:
#   1. Reads config from .env
#   2. Creates resource group (if it doesn't exist)
#   3. Creates Azure Container Registry (if it doesn't exist)
#   4. Builds & pushes the Docker image to ACR (cloud build — no local Docker needed)
#   5. Creates Container Apps environment (if it doesn't exist)
#   6. Deploys / updates the Container App with all secrets
#   7. Prints the public URL
# =============================================================================

set -euo pipefail

# ── Load .env ─────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "ERROR: .env file not found. Copy .env.example to .env and fill it in."
  exit 1
fi
# Export all non-comment lines from .env
set -o allexport
# shellcheck disable=SC1091
source .env
set +o allexport

# ── Required variables ─────────────────────────────────────────────────────────
: "${AZURE_APP_NAME:?Set AZURE_APP_NAME in .env}"
: "${AZURE_RESOURCE_GROUP:?Set AZURE_RESOURCE_GROUP in .env}"
: "${AZURE_LOCATION:=eastus}"
: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY in .env}"
: "${B2C_TENANT_NAME:?Set B2C_TENANT_NAME in .env}"
: "${B2C_CLIENT_ID:?Set B2C_CLIENT_ID in .env}"
: "${B2C_POLICY_NAME:=B2C_1_signupsignin}"
: "${ANTHROPIC_MODEL:=claude-sonnet-4-6}"

ACR_NAME="${AZURE_APP_NAME//[-_]/}acr"   # ACR names: alphanumeric only
IMAGE_NAME="${AZURE_APP_NAME}"
CONTAINER_ENV="${AZURE_APP_NAME}-env"

echo "============================================"
echo "  ISACA SD Advisor — Azure Deployment"
echo "============================================"
echo "  App name  : ${AZURE_APP_NAME}"
echo "  Resource  : ${AZURE_RESOURCE_GROUP}"
echo "  Location  : ${AZURE_LOCATION}"
echo "  ACR       : ${ACR_NAME}.azurecr.io"
echo "============================================"
echo ""

# ── 1. Resource group ──────────────────────────────────────────────────────────
echo "[1/6] Creating resource group (if needed)..."
az group create \
  --name "${AZURE_RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  --output none

# ── 2. Container registry ──────────────────────────────────────────────────────
echo "[2/6] Creating Azure Container Registry (if needed)..."
az acr create \
  --name "${ACR_NAME}" \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --sku Basic \
  --admin-enabled true \
  --output none 2>/dev/null || echo "       (ACR already exists, continuing)"

# ── 3. Build & push image ──────────────────────────────────────────────────────
echo "[3/6] Building image in ACR (cloud build — no local Docker required)..."
az acr build \
  --registry "${ACR_NAME}" \
  --image "${IMAGE_NAME}:latest" \
  .

# ── 4. Get ACR credentials ────────────────────────────────────────────────────
echo "[4/6] Fetching ACR credentials..."
ACR_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer -o tsv)
ACR_PASSWORD=$(az acr credential show --name "${ACR_NAME}" --query "passwords[0].value" -o tsv)

# ── 5. Container Apps environment ─────────────────────────────────────────────
echo "[5/6] Creating Container Apps environment (if needed)..."
az containerapp env create \
  --name "${CONTAINER_ENV}" \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --location "${AZURE_LOCATION}" \
  --output none 2>/dev/null || echo "       (Environment already exists, continuing)"

# ── 6. Deploy / update Container App ──────────────────────────────────────────
echo "[6/6] Deploying Container App..."

# Build the secrets string
SECRETS="anthropic-api-key=${ANTHROPIC_API_KEY}"
SECRETS="${SECRETS} b2c-tenant-name=${B2C_TENANT_NAME}"
SECRETS="${SECRETS} b2c-client-id=${B2C_CLIENT_ID}"
SECRETS="${SECRETS} b2c-policy-name=${B2C_POLICY_NAME}"

# Build the env-vars string (references secrets where sensitive)
ENV_VARS="ANTHROPIC_API_KEY=secretref:anthropic-api-key"
ENV_VARS="${ENV_VARS} ANTHROPIC_MODEL=${ANTHROPIC_MODEL}"
ENV_VARS="${ENV_VARS} B2C_TENANT_NAME=secretref:b2c-tenant-name"
ENV_VARS="${ENV_VARS} B2C_CLIENT_ID=secretref:b2c-client-id"
ENV_VARS="${ENV_VARS} B2C_POLICY_NAME=secretref:b2c-policy-name"
ENV_VARS="${ENV_VARS} LOG_LEVEL=${LOG_LEVEL:-INFO}"

# Check if app already exists
if az containerapp show \
    --name "${AZURE_APP_NAME}" \
    --resource-group "${AZURE_RESOURCE_GROUP}" \
    --output none 2>/dev/null; then
  echo "       Updating existing Container App..."
  az containerapp update \
    --name "${AZURE_APP_NAME}" \
    --resource-group "${AZURE_RESOURCE_GROUP}" \
    --image "${ACR_SERVER}/${IMAGE_NAME}:latest" \
    --set-env-vars ${ENV_VARS} \
    --output none
else
  echo "       Creating new Container App..."
  az containerapp create \
    --name "${AZURE_APP_NAME}" \
    --resource-group "${AZURE_RESOURCE_GROUP}" \
    --environment "${CONTAINER_ENV}" \
    --image "${ACR_SERVER}/${IMAGE_NAME}:latest" \
    --registry-server "${ACR_SERVER}" \
    --registry-username "${ACR_NAME}" \
    --registry-password "${ACR_PASSWORD}" \
    --target-port 8080 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 3 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --secrets ${SECRETS} \
    --env-vars ${ENV_VARS} \
    --output none
fi

# ── Done ───────────────────────────────────────────────────────────────────────
APP_URL=$(az containerapp show \
  --name "${AZURE_APP_NAME}" \
  --resource-group "${AZURE_RESOURCE_GROUP}" \
  --query "properties.configuration.ingress.fqdn" \
  -o tsv)

echo ""
echo "============================================"
echo "  Deployment complete!"
echo "============================================"
echo "  App URL    : https://${APP_URL}"
echo "  Health     : https://${APP_URL}/api/health"
echo ""
echo "  Next step: copy this URL into the chat widget:"
echo "  squarespace/chat-widget.html → API_BASE_URL"
echo "============================================"
