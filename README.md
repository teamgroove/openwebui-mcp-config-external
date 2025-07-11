# OpenWebUI with MCP (Model Context Protocol) Support

This project sets up OpenWebUI with MCP functionality using the `mcpo` (MCP-to-OpenAPI proxy) server. The setup includes:

- **OpenWebUI**: The main web interface
- **MCPO Server**: MCP-to-OpenAPI proxy server that enables OpenWebUI to communicate with MCP servers
- **Supabase MCP Server**: Example MCP server for Supabase integration

## Architecture

```
OpenWebUI <-> MCPO Server <-> MCP Server (Supabase)
```

The MCPO server acts as a bridge, converting MCP protocol calls to OpenAPI endpoints that OpenWebUI can consume.

## Prerequisites

- Docker and Docker Compose
- Supabase account and access token

## Setup

1. **Clone/Navigate to the project directory:**
   ```bash
   cd bws-openwebui-mcp
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables:**
   Edit `.env` and set your Supabase access token:
   ```
   SUPABASE_ACCESS_TOKEN=your_actual_supabase_token_here
   ```

4. **Start the services:**
   ```bash
   docker-compose up -d
   ```

5. **Access OpenWebUI:**
   Open your browser and navigate to `http://localhost:3000`

## Configuration Files

### Docker Compose (`docker-compose.yml`)
- Defines the OpenWebUI and MCPO server containers
- Sets up networking between services
- Configures environment variables and volumes

### MCPO Configuration (`mcpo-config/config.json`)
- Configures the MCP servers that MCPO should manage
- Defines how to start the Supabase MCP server

### OpenAPI Servers Configuration (`openwebui-config/openapi_servers.json`)
- Tells OpenWebUI about available OpenAPI servers
- Includes authentication configuration for the MCPO server

## Services

### OpenWebUI
- **Port**: 3000 (mapped to container port 8080)
- **Image**: `ghcr.io/open-webui/open-webui:main`
- **Purpose**: Main chat interface with MCP support

### MCPO Server
- **Port**: 8000
- **Image**: `ghcr.io/open-webui/mcpo:main`
- **Purpose**: Proxy server that converts MCP calls to OpenAPI endpoints

## Usage

1. Start the containers with `docker-compose up -d`
2. Access OpenWebUI at `http://localhost:3000`
3. In OpenWebUI, you should see the Supabase MCP server available as a tool
4. Use the chat interface to interact with Supabase through MCP

## Troubleshooting

### Check container logs:
```bash
docker-compose logs openwebui
docker-compose logs mcpo-server
```

### Verify services are running:
```bash
docker-compose ps
```

### Test MCPO server directly:
```bash
curl http://localhost:8000/openapi.json
```

### Restart services:
```bash
docker-compose restart
```

## Development

To modify the configuration:

1. Edit the relevant configuration files
2. Restart the services: `docker-compose restart`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_ACCESS_TOKEN` | Your Supabase access token | Required |
| `WEBUI_NAME` | Name displayed in OpenWebUI | "OpenWebUI with MCP" |
| `WEBUI_AUTH` | Enable authentication | false |

## Additional MCP Servers

To add more MCP servers, edit `mcpo-config/config.json` and add new server configurations. Make sure to also update the OpenAPI servers configuration in `openwebui-config/openapi_servers.json`.

## Links

- [OpenWebUI Documentation](https://docs.openwebui.com/)
- [MCPO GitHub Repository](https://github.com/open-webui/mcpo)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Supabase MCP Server](https://github.com/supabase/mcp-server-supabase)
