"""
title: Country Info Tool
author: Student
version: 1.0.0
description: Fetches live country information via the local tools_server.py Flask app.
"""

import json

import requests


class Tools:
    """Open WebUI Tool that calls the local Flask server for live country data."""

    def __init__(self):
        self.server_base_url = "http://host.docker.internal:5005"

    def get_country_info(self, country: str) -> str:
        """
        Get live/external information about a country (capital, region, population, languages, etc.).

        IMPORTANT — when to use this tool:
        - USE this tool ONLY for live or external country facts (capital, currency, languages,
          region, population, general country profile).
        - DO NOT use this tool for university ranking questions, scores, institutions, or
          any question that should be answered from the World University Rankings Knowledge Base
          (cwurData.csv / timesData.csv). For dataset questions, use the Knowledge Base instead.

        :param country: Country name (e.g. "Japan", "United Kingdom", "USA")
        :return: JSON string with country information or an error message
        """
        country = (country or "").strip()
        if not country:
            return "Error: country name is required."

        url = f"{self.server_base_url}/country-info"
        try:
            response = requests.get(url, params={"country": country}, timeout=20)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except requests.exceptions.ConnectionError:
            return (
                "Error: Could not connect to tools_server.py. "
                "Make sure it is running on port 5005."
            )
        except requests.exceptions.Timeout:
            return "Error: Request to tools_server timed out."
        except requests.exceptions.HTTPError:
            try:
                return json.dumps(response.json(), indent=2)
            except ValueError:
                return f"Error: tools_server returned HTTP {response.status_code}."
        except requests.exceptions.RequestException as exc:
            return f"Error: {exc}"
