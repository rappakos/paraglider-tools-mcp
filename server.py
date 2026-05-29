import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

SITES_API_BASE_URL = os.getenv("SITES_API_BASE_URL", "http://localhost:3979/api")
TESTS_API_BASE_URL = os.getenv("TESTS_API_BASE_URL", "http://localhost:3978/api")

mcp = FastMCP("paraglider-tools")


async def _get(base_url: str, path: str, params: dict | None = None) -> dict:
    """HTTP GET helper with error handling."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{base_url}{path}"
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def get_sites() -> list[dict]:
    """List all available paraglider launch sites with basic statistics (name, coordinates, flight count, last flight date)."""
    return await _get(SITES_API_BASE_URL, "/")


@mcp.tool()
async def get_site_forecast(site_name: str, date: Optional[str] = None) -> dict:
    """Get 5-day flyability forecast for a paraglider site.

    Args:
        site_name: Name of the launch site (use get_sites to see available names).
        date: Start date in YYYY-MM-DD format. Defaults to today.
    """
    params = {}
    if date:
        params["start_date"] = date
    return await _get(SITES_API_BASE_URL, f"/{site_name}/forecast", params=params)


@mcp.tool()
async def get_site_metadata(site_name: str) -> dict:
    """Get detailed metadata for a paraglider site including flight counts, RF model feature importance, and wind direction statistics.

    Args:
        site_name: Name of the launch site (use get_sites to see available names).
    """
    return await _get(SITES_API_BASE_URL, f"/{site_name}")


@mcp.tool()
async def search_wings(
    glider_names: list[str],
    weight: Optional[int] = None,
    classification: Optional[str] = None,
) -> dict:
    """Search and compare paraglider certification test results.

    Args:
        glider_names: List of glider name search strings (e.g. ["Advance Xi", "Nova Mentor"]).
        weight: Optional takeoff weight in kg to filter by weight range.
        classification: Optional glider class filter (A, B, C, or D). Comma-separated for multiple.
    """
    params = {"q": ",".join(glider_names)}
    if weight is not None:
        params["weight"] = weight
    if classification:
        params["classification"] = classification
    return await _get(TESTS_API_BASE_URL, "/search", params=params)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
