"""Integrations for paragliding query-capable applications."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class QueryIntegrationError(RuntimeError):
    """Raised when an upstream query integration fails."""


@dataclass(frozen=True)
class IntegrationConfig:
    base_url: str
    routes: dict[str, str]


def _default_integrations() -> dict[str, IntegrationConfig]:
    return {
        "paraglider-sites": IntegrationConfig(
            base_url=os.getenv("PARAGLIDER_SITES_URL", "http://localhost:8001"),
            routes={
                "forecasting": "api/query/forecasting",
                "statistics": "api/query/statistics",
                "bayes_network_statistics": "api/query/bayes-network-statistics",
            },
        ),
        "paraglider-tests": IntegrationConfig(
            base_url=os.getenv("PARAGLIDER_TESTS_URL", "http://localhost:8002"),
            routes={
                "recent_certifications": "api/query/recent-certifications",
                "safety_feature_comparison": "api/query/safety-feature-comparison",
            },
        ),
        "paragliding-stats": IntegrationConfig(
            base_url=os.getenv("PARAGLIDING_STATS_URL", "http://localhost:8003"),
            routes={
                "wing_type_analysis": "api/query/wing-type-analysis",
            },
        ),
    }


class ParagliderQueryService:
    """Unified query service across paragliding applications."""

    def __init__(self, integrations: dict[str, IntegrationConfig] | None = None, timeout: float = 10.0) -> None:
        self._integrations = integrations or _default_integrations()
        self._timeout = timeout

    def available_queries(self) -> dict[str, list[str]]:
        return {
            name: sorted(config.routes.keys())
            for name, config in sorted(self._integrations.items(), key=lambda item: item[0])
        }

    def query(self, integration: str, query_name: str, params: dict[str, Any] | None = None) -> Any:
        config = self._integrations.get(integration)
        if config is None:
            raise QueryIntegrationError(f"Unknown integration '{integration}'.")

        route = config.routes.get(query_name)
        if route is None:
            raise QueryIntegrationError(
                f"Unknown query '{query_name}' for integration '{integration}'."
            )

        return self._perform_get(config.base_url, route, params or {})

    def _perform_get(self, base_url: str, route: str, params: dict[str, Any]) -> Any:
        clean_base = base_url.rstrip("/")
        clean_route = route.lstrip("/")
        query_string = urlencode(params, doseq=True)
        url = f"{clean_base}/{clean_route}"
        if query_string:
            url = f"{url}?{query_string}"

        request = Request(url, headers={"Accept": "application/json"}, method="GET")

        try:
            with urlopen(request, timeout=self._timeout) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            raise QueryIntegrationError(f"Upstream returned HTTP {exc.code} for {url}") from exc
        except URLError as exc:
            raise QueryIntegrationError(f"Could not reach upstream for {url}") from exc

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise QueryIntegrationError(f"Upstream returned invalid JSON for {url}") from exc
