# Deploy notes (App Service for Containers)

## A) Docker Hub (simplest)
1) Build locally:
```bash
docker build -t <dockerhub_user>/recipefinder:v1 .
docker push <dockerhub_user>/recipefinder:v1
```

2) App Service -> Deployment Center -> Container Registry:
- Registry Source: Docker Hub
- Image: <dockerhub_user>/recipefinder
- Tag: v1

3) App Service -> Configuration -> Application settings:
Copy values from your `.env` (do NOT include quotes).

Important keys:
- BLOB_CONNECTION_STRING
- BLOB_CONTAINER_NAME
- CUSTOM_VISION_PREDICTION_ENDPOINT
- CUSTOM_VISION_PREDICTION_KEY
- CUSTOM_VISION_PROJECT_ID
- CUSTOM_VISION_PUBLISHED_NAME
- COSMOS_ENDPOINT
- COSMOS_KEY
- COSMOS_DATABASE
- COSMOS_CONTAINER
- RECIPE_MODE (auto recommended)
- SPOONACULAR_API_KEY (optional)

4) Restart App Service, then open the URL.

## B) Azure Container Registry (ACR) (recommended for Azure)
```bash
az acr create -n <acrName> -g <rg> --sku Basic
az acr login -n <acrName>

ACR_LOGIN_SERVER=$(az acr show -n <acrName> -g <rg> --query loginServer -o tsv)

docker build -t $ACR_LOGIN_SERVER/recipefinder:v1 .
docker push $ACR_LOGIN_SERVER/recipefinder:v1

az webapp config container set -g <rg> -n <appName>   --docker-custom-image-name $ACR_LOGIN_SERVER/recipefinder:v1
```
