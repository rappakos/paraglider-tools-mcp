# paraglider-tools-mcp
MCP Server for various paragliding applications

## Integrated query capabilities

This repository now contains a minimal shared query integration layer that unifies selected query features from:

- `paraglider-sites`
  - `forecasting`
  - `statistics`
  - `bayes_network_statistics`
- `paraglider-tests`
  - `recent_certifications`
  - `safety_feature_comparison`
- `paragliding-stats`
  - `wing_type_analysis`

## Configuration

Set upstream base URLs through environment variables (defaults shown):

- `PARAGLIDER_SITES_URL` (`http://localhost:8001`)
- `PARAGLIDER_TESTS_URL` (`http://localhost:8002`)
- `PARAGLIDING_STATS_URL` (`http://localhost:8003`)

## Example usage

```python
from paraglider_tools_mcp import ParagliderQueryService

service = ParagliderQueryService()
forecast = service.query("paraglider-sites", "forecasting", {"location": "annecy", "days": 3})
recent_certs = service.query("paraglider-tests", "recent_certifications", {"limit": 20})
wing_analysis = service.query("paragliding-stats", "wing_type_analysis", {"country": "FR"})
```
