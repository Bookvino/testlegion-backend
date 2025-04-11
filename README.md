# Testlegion Backend (MVP)

Dette er en simpel backend bygget med FastAPI.

Formålet er at modtage en URL fra en formular (på testlegion.com) og bekræfte modtagelsen.
Senere vil den:
- Kalde PageSpeed Insights API
- Bruge OpenAI til at generere analyseforslag

## Endpoints

### POST /analyse

Modtager JSON:
```json
{ "url": "https://eksempel.dk/kontakt" }
```

Returnerer:
```json
{ "status": "received", "url": "https://eksempel.dk/kontakt" }
```

## Sådan kører du den lokalt

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Teknologi
- Python
- FastAPI
- Klar til deployment på DigitalOcean App Platform
