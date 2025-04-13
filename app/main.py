from fastapi import FastAPI
from app.models.schemas import AnalyseInput
from app.services.pagespeed import run_pagespeed_analysis

app = FastAPI()

@app.post("/analyse")
async def analyse(input: AnalyseInput):
    return await run_pagespeed_analysis(input.url)


