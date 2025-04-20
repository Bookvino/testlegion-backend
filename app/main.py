import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, BackgroundTasks
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
async def analyse(input: AnalyseInput, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pagespeed_analysis, input.url)
    return {"message": "Analysen er startet i baggrunden"}
