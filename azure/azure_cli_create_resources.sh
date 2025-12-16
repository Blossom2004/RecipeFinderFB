#!/usr/bin/env bash
set -euo pipefail

# --------- CONFIG (edit these) ----------
LOCATION="westeurope"
RG="rg-recipefinder"
APP_NAME="recipefinder-app-$RANDOM"
PLAN_NAME="recipefinder-plan"
STORAGE_NAME="rfstorage$RANDOM"     # must be globally unique, lowercase
CONTAINER_NAME="uploads"
COSMOS_NAME="recipefinder-cosmos-$RANDOM"
COSMOS_DB="RecipeFinderDB"
COSMOS_CONTAINER="recipeRuns"
CUSTOM_VISION_RESOURCE_NAME="recipefinder-cv-$RANDOM"

# If using ACR:
ACR_NAME="recipefinderacr$RANDOM"   # must be globally unique, lowercase
IMAGE_NAME="recipefinder"
IMAGE_TAG="v1"
# ---------------------------------------

echo "Creating resource group..."
az group create -n "$RG" -l "$LOCATION"

echo "Creating Storage Account + Blob container..."
az storage account create -n "$STORAGE_NAME" -g "$RG" -l "$LOCATION" --sku Standard_LRS
STORAGE_CONN=$(az storage account show-connection-string -g "$RG" -n "$STORAGE_NAME" --query connectionString -o tsv)
az storage container create --name "$CONTAINER_NAME" --connection-string "$STORAGE_CONN"

echo "Creating Cosmos DB (SQL API) + DB + Container..."
az cosmosdb create -n "$COSMOS_NAME" -g "$RG" --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=false
COSMOS_ENDPOINT=$(az cosmosdb show -n "$COSMOS_NAME" -g "$RG" --query documentEndpoint -o tsv)
COSMOS_KEY=$(az cosmosdb keys list -n "$COSMOS_NAME" -g "$RG" --type keys --query primaryMasterKey -o tsv)
az cosmosdb sql database create -a "$COSMOS_NAME" -g "$RG" -n "$COSMOS_DB"
az cosmosdb sql container create -a "$COSMOS_NAME" -g "$RG" -d "$COSMOS_DB" -n "$COSMOS_CONTAINER" -p "/sessionId" --throughput 400

echo "Creating App Service plan (Linux) + Web App for Containers..."
az appservice plan create -n "$PLAN_NAME" -g "$RG" --is-linux --sku B1
az webapp create -n "$APP_NAME" -g "$RG" -p "$PLAN_NAME" --runtime "PYTHON|3.11"

echo
echo "NEXT STEPS:"
echo "1) Build & push your container (Docker Hub or ACR)."
echo "2) Configure the Web App to use your image."
echo "3) Set application settings (.env) in App Service."
echo
echo "Useful outputs:"
echo "STORAGE_NAME=$STORAGE_NAME"
echo "BLOB_CONTAINER_NAME=$CONTAINER_NAME"
echo "BLOB_CONNECTION_STRING=$STORAGE_CONN"
echo "COSMOS_ENDPOINT=$COSMOS_ENDPOINT"
echo "COSMOS_KEY=$COSMOS_KEY"
echo "APP_NAME=$APP_NAME"
