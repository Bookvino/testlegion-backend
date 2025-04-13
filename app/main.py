from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import AnalyseInput
from app.services.pagespeed import run_pagespeed_analysis

app = FastAPI()

# 🔐 CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://testlegion.com", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyse")
async def analyse(input: AnalyseInput):
    return await run_pagespeed_analysis(input.url)

