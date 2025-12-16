import os
import json
import requests
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_PATH = os.path.join(BASE_DIR, "data", "recipes_offline.json")

class RecipeEngine:
    def __init__(self):
        self._mode = os.getenv("RECIPE_MODE", "auto").strip().lower()
        self.api_key = os.getenv("SPOONACULAR_API_KEY", "").strip()
        self.number = int(os.getenv("SPOONACULAR_NUMBER", "12"))

        try:
            with open(OFFLINE_PATH, "r", encoding="utf-8") as f:
                self.offline = json.load(f)
        except Exception:
            self.offline = []

    def mode(self) -> str:
        if self._mode in ("spoonacular", "offline"):
            return self._mode
        return "spoonacular" if self.api_key else "offline"

    def get_recipes(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        if not ingredients:
            return []
        m = self.mode()
        if m == "spoonacular":
            try:
                return self._from_spoonacular(ingredients)
            except Exception:
                return self._from_offline(ingredients)
        return self._from_offline(ingredients)

    def _from_spoonacular(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Spoonacular key missing.")

        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "apiKey": self.api_key,
            "ingredients": ",".join(ingredients),
            "number": self.number,
            "ranking": 2,
            "ignorePantry": True,
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        out = []
        for item in data:
            out.append({
                "title": item.get("title"),
                "image": item.get("image"),
                "usedIngredients": [x.get("name") for x in item.get("usedIngredients", []) if x.get("name")],
                "missedIngredients": [x.get("name") for x in item.get("missedIngredients", []) if x.get("name")],
                "source": "spoonacular",
                "score": self._score_used_missed(item),
                "url": f"https://spoonacular.com/recipes/{(item.get('title') or 'recipe').replace(' ', '-')}-{item.get('id')}"
            })
        out.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return out

    def _score_used_missed(self, item: Dict[str, Any]) -> float:
        used = len(item.get("usedIngredients", []) or [])
        missed = len(item.get("missedIngredients", []) or [])
        denom = max(1, used + missed)
        return used / denom

    def _from_offline(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        ing_set = set([x.lower().strip() for x in ingredients if x.strip()])
        scored = []

        for r in self.offline:
            req = set([x.lower().strip() for x in r.get("ingredients", [])])
            if not req:
                continue
            matched = len(req.intersection(ing_set))
            if matched == 0:
                continue
            score = matched / max(1, len(req))
            scored.append({
                "title": r.get("title"),
                "image": r.get("image"),
                "usedIngredients": sorted(list(req.intersection(ing_set))),
                "missedIngredients": sorted(list(req.difference(ing_set))),
                "source": "offline",
                "score": score,
                "url": r.get("url", ""),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[: self.number]
