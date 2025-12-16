# RecipeFinder (Azure 5 services)

## Azure services
- App Service (Container)
- Docker container
- Blob Storage (uploads)
- Custom Vision (ingredient recognition)
- Cosmos DB (history + runs)

## Run locally
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill keys in .env

uvicorn app.main:app --reload --port 8000
```
Open: http://127.0.0.1:8000

## Recipe modes
- RECIPE_MODE=spoonacular -> always Spoonacular
- RECIPE_MODE=offline -> only local dataset
- RECIPE_MODE=auto -> Spoonacular if key set, else offline

## Deploy to Azure App Service (Container)
See `azure/azure_cli_create_resources.sh` and `azure/DEPLOY_NOTES.md`.
