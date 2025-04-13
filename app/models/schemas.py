from pydantic import BaseModel

class AnalyseInput(BaseModel):
    url: str
