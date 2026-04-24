from fastapi import FastAPI, Body, HTTPException
import httpx
import json
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"

with open(CONFIG_DIR / "params.json", encoding="utf-8") as f:
    PARAMS = json.load(f)

AI_API_URL = PARAMS.get("ai_api_url")
AI_API_MODEL = PARAMS.get("ai_api_model", "gpt-5-nano")
AI_API_KEY = PARAMS.get("ai_api_key")
AI_TEMPERATURE = PARAMS.get("temperature")
DEBUG_HTTP = PARAMS.get("debug_http", False)

if not AI_API_URL:
    raise RuntimeError("La clé 'ai_api_url' est manquante dans config/params.json")

if not AI_API_MODEL:
    raise RuntimeError("La clé 'ai_api_model' est manquante dans config/params.json")

if not AI_API_KEY:
    raise RuntimeError("La clé 'ai_api_key' est manquante dans config/params.json")


def extract_processed_text(res_json: dict) -> str:
    output_text = res_json.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = res_json.get("output", [])
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                return text

    raise HTTPException(status_code=502, detail="Réponse IA vide ou non reconnue")


def _preview(text: str, size: int = 300) -> str:
    if not isinstance(text, str):
        return str(text)
    return text if len(text) <= size else text[:size] + "..."


def _masked_auth_header(api_key: str) -> str:
    if not api_key:
        return "Bearer <missing>"
    if len(api_key) <= 10:
        return "Bearer ***"
    return f"Bearer {api_key[:7]}...{api_key[-3:]}"


@app.post("/process")
async def process_task(
    text: str = Body(..., embed=True),
    prompt: str = Body(..., embed=True)
):
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt manquant")

    request_payload = {
        "model": AI_API_MODEL,
        "instructions": prompt,
        "input": text,
    }

    if AI_TEMPERATURE is not None:
        request_payload["temperature"] = AI_TEMPERATURE

    if DEBUG_HTTP:
        print("[AI REQUEST]", {
            "url": AI_API_URL,
            "headers": {
                "Authorization": _masked_auth_header(AI_API_KEY),
                "Content-Type": "application/json",
            },
            "json": {
                "model": AI_API_MODEL,
                "instructions_preview": _preview(prompt),
                "input_preview": _preview(text),
                "temperature": AI_TEMPERATURE,
            },
        })

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                AI_API_URL,
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_payload,
                timeout=60.0
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if DEBUG_HTTP:
                print("[AI ERROR]", {
                    "status_code": e.response.status_code,
                    "url": str(e.request.url),
                    "response_text": e.response.text,
                })
            raise HTTPException(
                status_code=502,
                detail=f"Erreur API IA ({e.response.status_code}): {e.response.text}"
            )

        res_json = response.json()
        return {"processed_text": extract_processed_text(res_json)}