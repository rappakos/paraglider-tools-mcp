# paraglider-tools-mcp
MCP Server for various paragliding applications

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install fastmcp httpx python-dotenv
```

Copy `.env.example` to `.env` and adjust URLs if needed.

## Run with MCP Inspector

```bash
npx @modelcontextprotocol/inspector --env USE_TLS=false python server.py
```

This opens the MCP Inspector in your browser for interactive tool testing.

## Run

```bash
python server.py
```

Server starts at `http://localhost:8080/mcp` (streamable HTTP transport).
