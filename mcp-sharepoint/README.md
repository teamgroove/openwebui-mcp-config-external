# SharePoint FastMCP Server for OpenWebUI

This is a FastMCP implementation of the SharePoint tool for OpenWebUI. It provides access to SharePoint sites and their items through the Microsoft Graph API.

## Features

- OAuth Client Credentials Flow with MSAL
- Endpoints:
  - `search_sites`: Search for SharePoint sites by name
  - `list_items`: List items of a SharePoint site (including list entries, calendars, etc.)

## Requirements

- Python 3.8+
- FastAPI
- FastMCP
- HTTPX
- MSAL

## Environment Variables

The following environment variables must be set:

- `AZ_TENANT_ID`: Azure tenant ID
- `AZ_CLIENT_ID`: Azure client ID
- `AZ_CLIENT_SECRET`: Azure client secret

## Usage

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8001
```

### Docker

```bash
# Build the image
docker build -t sharepoint-mcp .

# Run the container
docker run -p 8001:8000 \
  -e AZ_TENANT_ID=your-tenant-id \
  -e AZ_CLIENT_ID=your-client-id \
  -e AZ_CLIENT_SECRET=your-client-secret \
  sharepoint-mcp
```

## Integration with OpenWebUI

Update your `mcpo-config/config.json` to include the SharePoint MCP server:

```json
{
  "mcpServers": {
    "mcp-sharepoint": {
      "command": "uvicorn",
      "args": ["main:app", "--host", "0.0.0.0", "--port", "8000"],
      "cwd": "/path/to/mcp-sharepoint",
      "env": {
        "AZ_TENANT_ID": "your-tenant-id",
        "AZ_CLIENT_ID": "your-client-id",
        "AZ_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```
