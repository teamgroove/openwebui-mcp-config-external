"""
sharepoint_tool – Mini-API für Open WebUI
----------------------------------------

• OAuth-Client-Credentials-Flow mit MSAL
• Endpunkte:
    GET /sites?q=Suchbegriff          – alle SharePoint-Sites durchsuchen
    GET /site/{site_id}/items         – Items (z. B. Kalenderlisten) einer Site abrufen
• OpenAPI-Version wird auf 3.0.3 „heruntergedreht“, damit WebUI ≤ 0.6.x sie parsen kann
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, time, httpx, msal

# --------------------------------------------------------------------
# Umgebungsvariablen (in docker-compose.yaml setzen oder .env mounten)
# --------------------------------------------------------------------
TENANT  = os.getenv("AZ_TENANT_ID")
CLIENT  = os.getenv("AZ_CLIENT_ID")
SECRET  = os.getenv("AZ_CLIENT_SECRET")

if not all([TENANT, CLIENT, SECRET]):
    raise RuntimeError("⚠️  AZ_TENANT_ID, AZ_CLIENT_ID oder AZ_CLIENT_SECRET fehlt!")

# --------------------------------------------------------------------
# FastAPI-Instanz + CORS (nur nötig, wenn Nutzer das Tool manuell hinzufügt)
# --------------------------------------------------------------------
app = FastAPI(title="sharepoint_tool", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # in Produktion einschränken
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# OpenAPI 3.0.3 erzwingen – wichtig für Open WebUI 0.6.15
# --------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    schema["openapi"] = "3.0.3"   # ← Downgrade
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

# --------------------------------------------------------------------
# Einfacher Token-Cache (~60 Minuten gültig)
# --------------------------------------------------------------------
_token: dict[str, str | int] = {"value": None, "exp": 0}

def get_token() -> str:
    # Noch gültig? (Restlaufzeit >5 Min)
    if _token["value"] and _token["exp"] - time.time() > 300:
        return _token["value"]

    cca = msal.ConfidentialClientApplication(
        CLIENT,
        authority=f"https://login.microsoftonline.com/{TENANT}",
        client_credential=SECRET,
    )
    result = cca.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise HTTPException(
            status_code=502,
            detail=f"Token Error: {result.get('error_description', 'unbekannt')}",
        )
    _token["value"] = result["access_token"]
    _token["exp"]   = int(time.time()) + int(result["expires_in"])
    return _token["value"]

# --------------------------------------------------------------------
# Endpunkte
# --------------------------------------------------------------------
GRAPH = "https://graph.microsoft.com/v1.0"

@app.get("/sites", summary="Search Sites")
def search_sites(q: str = Query("*", description="Suchbegriff (Wildcard = *)")):
    """Alle Sites, deren Name <q> enthält (SharePoint & Teams-Sites)."""
    token = get_token()
    resp = httpx.get(
        f"{GRAPH}/sites",
        params={"search": q},
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["value"]

@app.get("/site/{site_id}/items", summary="List Items")
def list_items(site_id: str, expand: str = "fields"):
    """Items einer Site abrufen (inkl. Listeneinträge, Kalender, …)."""
    token = get_token()
    url = f"{GRAPH}/sites/{site_id}/items"
    resp = httpx.get(url, params={"expand": expand}, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json()["value"]

# --------------------------------------------------------------------
# Lokaler Test:  uvicorn main:app --reload --port 8001
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
