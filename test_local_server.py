"""
Simple local test for tools_server.py.
Run tools_server.py first, then: python test_local_server.py
"""

import requests

BASE_URL = "http://localhost:5005"


def main():
    print("=== GET http://localhost:5005/health ===")
    health = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"HTTP status code: {health.status_code}")
    print(f"Response body: {health.text}")
    print()

    print("=== GET http://localhost:5005/country-info?country=Japan ===")
    country = requests.get(
        f"{BASE_URL}/country-info",
        params={"country": "Japan"},
        timeout=60,
    )
    print(f"HTTP status code: {country.status_code}")
    print(f"Response body: {country.text}")


if __name__ == "__main__":
    main()
