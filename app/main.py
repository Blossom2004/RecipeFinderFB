import os
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.services.blob_service import BlobService
from app.services.custom_vision_service import CustomVisionService
from app.services.cosmos_service import CosmosService
from app.services.recipe_engine import RecipeEngine

load_dotenv()

app = FastAPI(title="RecipeFinder")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

blob = BlobService()
vision = CustomVisionService()
cosmos = CosmosService()
recipes = RecipeEngine()

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_session_id(request: Request) -> str:
    sid = request.cookies.get("sessionId")
    if not sid:
        sid = "sess_" + uuid.uuid4().hex[:12]
    return sid

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    sid = ensure_session_id(request)
    resp = templates.TemplateResponse("index.html", {"request": request})
    resp.set_cookie("sessionId", sid, httponly=True, samesite="lax")
    return resp

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    sid = ensure_session_id(request)
    items = cosmos.list_runs(session_id=sid, limit=15)
    resp = templates.TemplateResponse("history.html", {"request": request, "items": items})
    resp.set_cookie("sessionId", sid, httponly=True, samesite="lax")
    return resp

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(...)):
    sid = ensure_session_id(request)

    if not file.content_type or not file.content_type.startswith("image/"):
        return templates.TemplateResponse(
            "results.html",
            {"request": request, "error": "Please upload an image file (jpg/png)."},
            status_code=400,
        )

    image_bytes = await file.read()
    if not image_bytes:
        return templates.TemplateResponse(
            "results.html",
            {"request": request, "error": "Empty file uploaded."},
            status_code=400,
        )

    # 1) Upload to Blob
    run_id = "run_" + uuid.uuid4().hex[:10]
    blob_name = f"{sid}/{run_id}_{file.filename}".replace(" ", "_")
    image_url = blob.upload_image(blob_name=blob_name, data=image_bytes, content_type=file.content_type)

    # 2) Custom Vision prediction
    predictions = vision.predict(image_bytes=image_bytes)
    ingredients = vision.extract_ingredients(predictions)

    # 3) Recipes (Spoonacular + Offline)
    recipe_mode = recipes.mode()
    found_recipes = recipes.get_recipes(ingredients)

    # 4) Save to Cosmos
    doc = {
        "id": run_id,
        "sessionId": sid,
        "createdAt": now_utc_iso(),
        "imageUrl": image_url,
        "fileName": file.filename,
        "predictions": predictions,
        "ingredients": ingredients,
        "recipeMode": recipe_mode,
        "recipes": found_recipes,
    }
    cosmos.upsert_run(doc)

    resp = templates.TemplateResponse(
        "results.html",
        {"request": request, "run": doc, "error": None if ingredients else "No confident ingredients detected. Try a clearer photo."},
    )
    resp.set_cookie("sessionId", sid, httponly=True, samesite="lax")
    return resp
