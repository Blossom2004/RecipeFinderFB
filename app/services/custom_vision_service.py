import os
import requests
from typing import List, Dict, Any

class CustomVisionService:
    def __init__(self):
        self.endpoint = os.getenv("CUSTOM_VISION_PREDICTION_ENDPOINT", "").rstrip("/")
        self.key = os.getenv("CUSTOM_VISION_PREDICTION_KEY", "")
        self.project_id = os.getenv("CUSTOM_VISION_PROJECT_ID", "")
        self.published_name = os.getenv("CUSTOM_VISION_PUBLISHED_NAME", "Iteration1")

        self.threshold = float(os.getenv("CUSTOM_VISION_THRESHOLD", "0.60"))
        self.top_k = int(os.getenv("CUSTOM_VISION_TOP_K", "8"))

    def predict(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        if not (self.endpoint and self.key and self.project_id and self.published_name):
            return []

        url = f"{self.endpoint}/customvision/v3.0/Prediction/{self.project_id}/classify/iterations/{self.published_name}/image"
        headers = {"Prediction-Key": self.key, "Content-Type": "application/octet-stream"}

        r = requests.post(url, headers=headers, data=image_bytes, timeout=20)
        r.raise_for_status()
        payload = r.json()

        preds = payload.get("predictions", [])
        out = [{"tag": p.get("tagName"), "p": float(p.get("probability", 0.0))} for p in preds]
        out.sort(key=lambda x: x["p"], reverse=True)
        return out

    def extract_ingredients(self, predictions: List[Dict[str, Any]]) -> List[str]:
        if not predictions:
            return []
        selected = [p["tag"] for p in predictions if p.get("p", 0.0) >= self.threshold and p.get("tag")]
        selected = selected[: self.top_k]

        seen = set()
        ingredients = []
        for s in selected:
            t = s.strip().lower()
            if t and t not in seen:
                seen.add(t)
                ingredients.append(t)
        return ingredients
