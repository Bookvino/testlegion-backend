from pydantic import BaseModel, EmailStr
from datetime import datetime

# --------- Bruger-skemaer ---------
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True  # Pydantic v2 (erstatter orm_mode = True)


# --------- AnalyseInput til PageSpeed ---------
class AnalyseInput(BaseModel):
    url: str

class PageSpeedAnalysisCreate(BaseModel):
    url: str
    strategy: str
    performance_score: float

class PageSpeedAnalysisOut(BaseModel):
    id: int
    url: str
    strategy: str
    performance_score: float
    created_at: datetime

    class Config:
        from_attributes = True  # Vigtigt for Pydantic v2 + SQLAlchemy
