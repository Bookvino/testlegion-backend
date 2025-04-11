from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class AnalyseInput(BaseModel):
    url: str

@app.post("/analyse")
async def analyse(input: AnalyseInput):
    return {
        "status": "received",
        "url": input.url
    }
