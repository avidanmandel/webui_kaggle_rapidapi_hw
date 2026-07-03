"""
Flask server that proxies country information requests to RapidAPI.
Used by the Open WebUI Tool (openwebui_tool.py).
"""

import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
RAPIDAPI_URL = os.getenv("RAPIDAPI_URL")
RAPIDAPI_COUNTRY_PARAM = os.getenv("RAPIDAPI_COUNTRY_PARAM", "country")
RAPIDAPI_MODE = os.getenv("RAPIDAPI_MODE", "all_filter")

# Used only when the configured RapidAPI /all endpoint is unavailable.
FALLBACK_ALL_URL = "https://countriesnow.space/api/v0.1/countries"

print(f"[tools_server] loaded RAPIDAPI_URL={RAPIDAPI_URL}")
print(f"[tools_server] loaded RAPIDAPI_MODE={RAPIDAPI_MODE}")


def _missing_env_vars():
    missing = []
    if not RAPIDAPI_KEY:
        missing.append("RAPIDAPI_KEY")
    if not RAPIDAPI_HOST:
        missing.append("RAPIDAPI_HOST")
    if not RAPIDAPI_URL:
        missing.append("RAPIDAPI_URL")
    return missing


def _rapidapi_headers():
    return {
        "Content-Type": "application/json",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }


def _country_name_value(entry):
    """Extract a comparable country name string from a country record."""
    if not isinstance(entry, dict):
        return str(entry)

    name = entry.get("name", "")
    if isinstance(name, dict):
        for key in ("common", "official"):
            if name.get(key):
                return str(name[key])
        return ""

    if name:
        return str(name)

    if entry.get("country"):
        return str(entry["country"])

    return ""


def _name_matches(entry, query):
    """Case-insensitive match on primary country name."""
    return _country_name_value(entry).lower() == query.strip().lower()


def _find_country_in_list(countries, query):
    """Return the first country whose name matches query (case-insensitive)."""
    for entry in countries:
        if _name_matches(entry, query):
            return entry
    return None


def _extract_country_list(payload):
    """Normalize different API payloads into a list of country objects."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            return payload["data"]
        if isinstance(payload.get("countries"), list):
            return payload["countries"]
    raise ValueError("Expected a JSON list of countries from the API response")


def _build_direct_request(country: str):
    """
    Build RapidAPI request for direct mode.

    - Path format: RAPIDAPI_URL contains {country} → format URL, no query params.
    - Query format: RAPIDAPI_URL has no placeholder → use RAPIDAPI_COUNTRY_PARAM.
    """
    if "{country}" in RAPIDAPI_URL:
        url = RAPIDAPI_URL.format(country=quote(country.strip()))
        return url, None
    return RAPIDAPI_URL, {RAPIDAPI_COUNTRY_PARAM: country.strip()}


def _fetch_all_countries_list():
    """
    Fetch the full country list for all_filter mode.

    Tries RapidAPI first, then a public fallback if RapidAPI is down.
    """
    response = requests.get(
        RAPIDAPI_URL,
        headers=_rapidapi_headers(),
        timeout=30,
    )
    print(f"[tools_server] RapidAPI HTTP status code={response.status_code}")

    if response.ok:
        countries = _extract_country_list(response.json())
        print(f"[tools_server] countries returned={len(countries)} (source=rapidapi)")
        return countries, "rapidapi"

    rapidapi_detail = response.text[:500] or "(empty response body)"
    print(f"[tools_server] RapidAPI error body={rapidapi_detail}")

    print(
        "[tools_server] RapidAPI /all unavailable; "
        f"HTTP {response.status_code}. Trying fallback list source."
    )
    fallback = requests.get(FALLBACK_ALL_URL, timeout=30)
    print(f"[tools_server] fallback HTTP status code={fallback.status_code}")
    fallback.raise_for_status()
    countries = _extract_country_list(fallback.json())
    print(f"[tools_server] countries returned={len(countries)} (source=fallback)")
    return countries, "fallback"


def _fetch_country_all_filter(country: str):
    """Fetch all countries and filter locally by name."""
    countries, source = _fetch_all_countries_list()
    match = _find_country_in_list(countries, country)
    if not match:
        matched_name = "NOT FOUND"
        print(f"[tools_server] matched country name={matched_name} for query={country}")
        return None, {"error": "Country not found", "country": country}

    matched_name = _country_name_value(match)
    print(f"[tools_server] matched country name={matched_name} (source={source})")
    return match, None


def _fetch_country_direct(country: str):
    """Call RapidAPI with country embedded in URL path or query params."""
    url, params = _build_direct_request(country)
    response = requests.get(
        url,
        headers=_rapidapi_headers(),
        params=params,
        timeout=30,
    )
    print(f"[tools_server] RapidAPI HTTP status code={response.status_code}")
    if not response.ok:
        print(f"[tools_server] RapidAPI error body={response.text[:500]}")
    response.raise_for_status()
    return response.json(), None


@app.route("/health", methods=["GET"])
def health():
    """Simple health check for Docker / Open WebUI connectivity."""
    return jsonify({"status": "ok", "service": "tools_server"})


@app.route("/country-info", methods=["GET"])
def country_info():
    """Return live country information from RapidAPI."""
    country = request.args.get("country", "").strip()
    if not country:
        return jsonify({"error": "Missing required query parameter: country"}), 400

    missing = _missing_env_vars()
    if missing:
        return jsonify(
            {
                "error": "Missing environment variables",
                "missing": missing,
                "hint": "Copy .env.example to .env and add your RapidAPI credentials.",
            }
        ), 500

    try:
        if RAPIDAPI_MODE == "all_filter":
            data, not_found = _fetch_country_all_filter(country)
            if not_found:
                return jsonify(not_found), 404
        else:
            data, _ = _fetch_country_direct(country)

        return jsonify({"country": country, "data": data})
    except requests.exceptions.Timeout:
        return jsonify({"error": "RapidAPI request timed out"}), 504
    except requests.exceptions.HTTPError as exc:
        detail = exc.response.text[:500] if exc.response is not None else str(exc)
        status_code = exc.response.status_code if exc.response is not None else 502
        print(f"[tools_server] HTTP error status={status_code} detail={detail}")
        return jsonify(
            {
                "error": "RapidAPI returned an error",
                "status_code": status_code,
                "detail": detail,
            }
        ), 502
    except requests.exceptions.RequestException as exc:
        print(f"[tools_server] Request failed: {exc}")
        return jsonify({"error": "Failed to reach RapidAPI", "detail": str(exc)}), 502
    except ValueError as exc:
        print(f"[tools_server] JSON parse error: {exc}")
        return jsonify({"error": "Invalid JSON response from RapidAPI", "detail": str(exc)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
