# Plan: FastMCP Server for Paragliding Apps

## TL;DR
Create a FastMCP server in `paraglider-tools-mcp` that exposes tools for querying forecast data, site metadata, and certification results from the existing `paraglider-sites` and `paraglider-tests` apps. The MCP server will call the existing FastAPI apps' JSON APIs via HTTP. Some apps need new JSON API endpoints added.

## Phase 1: Extend existing apps with JSON APIs

### paraglider-sites (already has `/api` routes — mostly ready)
- `GET /api/` — list sites ✓ (exists, returns `List[SiteStats]`)
- `GET /api/{site_name}` — site metadata with RF feature importance ✓ (exists)
  - **Extend**: include direction stats in this response (call `get_direction_stats` from `site_service.py`)
- `GET /api/{site_name}/forecast` — forecast ✓ (exists)

### paraglider-tests (currently HTML-only, needs JSON endpoints)
- **New**: `GET /api/search` — search and compare wings
  - Query params: `q` (comma-separated glider name search strings), `weight` (optional takeoff weight), `class` (optional: A/B/C/D)
  - Returns: matching gliders with their certification test results (evaluations + parameters)
  - Supports multiple search terms → enables comparison in a single call

## Phase 2: Create FastMCP server (`paraglider-tools-mcp`)

### Project setup
- `pyproject.toml` with dependencies: `fastmcp`, `httpx`
- `server.py` — main MCP server entry point
- `.env` for configuring upstream app URLs (e.g., `SITES_API_URL`, `TESTS_API_URL`)

### MCP Tools to implement
1. **`get_sites`** — List available paraglider sites (calls `paraglider-sites /api/`)
2. **`get_site_forecast`** (params: site_name, date) — Get forecast (calls `/api/{site_name}/forecast?start_date=...`)
3. **`get_site_metadata`** (params: site_name) — Get site details: flight count, RF feature importance, wind direction stats (calls `/api/{site_name}`). Optional: exclude sections to reduce payload.
4. **`search_wings`** (params: glider_names: list[str], weight: optional int, classification: optional str) — Search and compare paraglider certification results (calls `paraglider-tests /api/search`)

## Phase 3 (later): paraglider-stats integration
- Add JSON API endpoints to `paraglider-stats`
- MCP tools: `get_market_share(year)`, `get_wing_xc_stats(year)`

## Relevant files

### To modify
- `paraglider-sites/glider_sites_app/routes.py` — extend `/api/{site_name}` to include direction stats
- `paraglider-sites/glider_sites_app/services/site_service.py` — merge `get_direction_stats` into `get_site_data`
- `paraglider-tests/glider_tests_app/routes.py` — add `/api/search` JSON endpoint
- `paraglider-tests/glider_tests_app/db.py` — add search query (by name, weight, class)

### To create
- `paraglider-tools-mcp/pyproject.toml`
- `paraglider-tools-mcp/server.py` — MCP server with tools
- `paraglider-tools-mcp/.env.example`

## Deployment / Environment Configuration

Existing apps already support subfolder prefixes behind nginx:
- `paraglider-sites`: `GLIDER_SITES_APP_PREFIX` (e.g., `/sites`)
- `paraglider-tests`: `GLIDER_TESTS_APP_ROOT_PATH` (e.g., `/tests`)
- `paraglider-stats`: `GLIDER_STATS_APP_ROOT_PATH` (e.g., `/stats`)

MCP server `.env` configuration — full base URLs including the prefix:
```
# Local development (ports: sites=3979, tests=3978, stats=3977)
SITES_API_BASE_URL=http://localhost:3979/api
TESTS_API_BASE_URL=http://localhost:3978/api

# Linux server (nginx subfolder proxy)
SITES_API_BASE_URL=https://myserver.example.com/sites/api
TESTS_API_BASE_URL=https://myserver.example.com/tests/api
STATS_API_BASE_URL=https://myserver.example.com/stats/api  # Phase 3
```

This way the MCP server is deployment-agnostic — just change the env vars to switch between local and remote.

### Reference
- `paraglider-sites/glider_sites_app/services/site_service.py` — `get_direction_stats()`, `get_forecast_data()`, `get_site_data()`
- `paraglider-sites/glider_sites_app/schemas.py` — `SiteStats`, `SiteBase`
- `paraglider-tests/glider_tests_app/db.py` — `get_evaluation()`, `get_stats()`, `get_report_details()`

## Verification
1. Start `paraglider-sites` and verify `/api/{site_name}` includes direction stats
2. Start `paraglider-tests` and verify `/api/search?q=...` returns JSON
3. Start MCP server with `fastmcp dev server.py` and test each tool via MCP inspector
4. Connect MCP server to a client (e.g., Claude Desktop) and verify tool invocations

## Decisions
- MCP server communicates with apps via HTTP (not direct DB access) — keeps separation of concerns
- Apps must be running for MCP server to work (documented in README)
- Phase 3 (stats) is explicitly out of scope for now

## Further Considerations
1. **Authentication**: The existing apps have no auth — should the MCP server add API key protection? Recommendation: skip for now (local use), add later if needed.
2. **Error handling**: If upstream app is down, MCP tools should return clear error messages rather than crashing.
3. **Deployment**: All apps run locally — should we add a docker-compose for one-command startup? Recommendation: defer, document manual startup for now.
