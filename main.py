import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Permitir solicitudes desde el HTML local o desplegado
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
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        full_prompt = f"{req.system_prompt}\n\nENTRADA DEL CEO:\n{req.user_text}"
        response = model.generate_content(full_prompt)
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))