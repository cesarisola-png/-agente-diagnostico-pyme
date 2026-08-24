import json
import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


class DiagRequest(BaseModel):
    system_prompt: str
    user_text: str


@app.post("/chat")
async def chat_endpoint(req: DiagRequest):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={"response_mime_type": "application/json"},
        )

        full_prompt = (
            f"{req.system_prompt}\n\nENTRADA DEL CEO:\n{req.user_text}"
        )
        response = model.generate_content(full_prompt)

        raw_text = response.text.strip()

        # Limpieza por si el modelo devuelve bloques de código markdown ```json ... ```
        if "```" in raw_text:
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)

        return json.loads(raw_text)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en el servidor: {str(e)}"