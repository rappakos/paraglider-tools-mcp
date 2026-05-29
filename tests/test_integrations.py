import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from paraglider_tools_mcp.integrations import IntegrationConfig, ParagliderQueryService, QueryIntegrationError


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class ParagliderQueryServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = ParagliderQueryService(
            integrations={
                "paraglider-sites": IntegrationConfig(
                    base_url="http://sites.local",
                    routes={"forecasting": "api/query/forecasting"},
                ),
                "paraglider-tests": IntegrationConfig(
                    base_url="http://tests.local/",
                    routes={"recent_certifications": "/api/query/recent-certifications"},
                ),
            }
        )

    @patch("paraglider_tools_mcp.integrations.urlopen")
    def test_query_builds_expected_url_and_decodes_json(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse({"ok": True})

        result = self.service.query("paraglider-sites", "forecasting", {"location": "chamonix", "days": 3})

        self.assertEqual({"ok": True}, result)
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            "http://sites.local/api/query/forecasting?location=chamonix&days=3",
            request.full_url,
        )

    @patch("paraglider_tools_mcp.integrations.urlopen")
    def test_query_normalizes_route_slashes(self, mock_urlopen):
        mock_urlopen.return_value = _FakeResponse({"ok": True})

        self.service.query("paraglider-tests", "recent_certifications")

        request = mock_urlopen.call_args.args[0]
        self.assertEqual("http://tests.local/api/query/recent-certifications", request.full_url)

    @patch("paraglider_tools_mcp.integrations.urlopen")
    def test_query_wraps_network_errors(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("no route")

        with self.assertRaises(QueryIntegrationError):
            self.service.query("paraglider-sites", "forecasting")

    def test_query_rejects_unknown_integration(self):
        with self.assertRaises(QueryIntegrationError):
            self.service.query("missing", "forecasting")

    def test_query_rejects_unknown_query_name(self):
        with self.assertRaises(QueryIntegrationError):
            self.service.query("paraglider-sites", "missing")

    def test_available_queries_returns_sorted_mapping(self):
        self.assertEqual(
            {
                "paraglider-sites": ["forecasting"],
                "paraglider-tests": ["recent_certifications"],
            },
            self.service.available_queries(),
        )


if __name__ == "__main__":
    unittest.main()
