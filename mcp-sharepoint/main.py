"""
SharePoint MCP Server for Open WebUI
-----------------------------------

A FastMCP implementation of the SharePoint tool for Open WebUI.
"""

import os
import time
import httpx
import msal
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP, Function, Parameter, ParameterType

# --------------------------------------------------------------------
# Environment variables (set in docker-compose.yaml or mount .env)
# --------------------------------------------------------------------
TENANT = os.getenv("AZ_TENANT_ID")
CLIENT = os.getenv("AZ_CLIENT_ID")
SECRET = os.getenv("AZ_CLIENT_SECRET")

if not all([TENANT, CLIENT, SECRET]):
    raise RuntimeError("⚠️  AZ_TENANT_ID, AZ_CLIENT_ID or AZ_CLIENT_SECRET missing!")

# --------------------------------------------------------------------
# FastAPI instance + CORS (needed if users manually add the tool)
# --------------------------------------------------------------------
app = FastAPI(title="sharepoint_mcp", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # restrict in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# Simple token cache (~60 minutes valid)
# --------------------------------------------------------------------
_token: dict[str, str | int] = {"value": None, "exp": 0}

def get_token() -> str:
    # Still valid? (Remaining time >5 min)
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
            detail=f"Token Error: {result.get('error_description', 'unknown')}",
        )
    _token["value"] = result["access_token"]
    _token["exp"]   = int(time.time()) + int(result["expires_in"])
    return _token["value"]

# --------------------------------------------------------------------
# Graph API endpoint
# --------------------------------------------------------------------
GRAPH = "https://graph.microsoft.com/v1.0"

# --------------------------------------------------------------------
# FastMCP implementation
# --------------------------------------------------------------------
mcp = FastMCP(
    name="sharepoint-mcp",
    description="SharePoint MCP Server for Open WebUI",
    version="0.1.0",
)

@mcp.function(
    name="search_sites",
    description="Search for SharePoint sites by name (SharePoint & Teams sites)",
    parameters=[
        Parameter(
            name="query",
            type=ParameterType.STRING,
            description="Search term (wildcard = *)",
            required=True,
        )
    ]
)
async def search_sites(query: str):
    """Search for SharePoint sites by name (SharePoint & Teams sites)."""
    token = get_token()
    resp = httpx.get(
        f"{GRAPH}/sites",
        params={"search": query},
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["value"]

@mcp.function(
    name="list_items",
    description="List items of a SharePoint site (including list entries, calendars, etc.)",
    parameters=[
        Parameter(
            name="site_id",
            type=ParameterType.STRING,
            description="SharePoint site ID",
            required=True,
        ),
        Parameter(
            name="expand",
            type=ParameterType.STRING,
            description="Properties to expand",
            required=False,
            default="fields",
        )
    ]
)
async def list_items(site_id: str, expand: str = "fields"):
    """List items of a SharePoint site (including list entries, calendars, etc.)."""
    token = get_token()
    url = f"{GRAPH}/sites/{site_id}/items"
    resp = httpx.get(url, params={"expand": expand}, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json()["value"]

# Mount the FastMCP router to the FastAPI app
app.include_router(mcp.router)

# --------------------------------------------------------------------
# Local test: uvicorn main:app --reload --port 8001
# --------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
