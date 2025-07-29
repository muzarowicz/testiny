import json
import os
import requests

# Wczytanie wyników testów z pliku (np. wygenerowanego przez pytest)
with open('results.json') as f:
    results = json.load(f)

API_URL = "https://api.testiny.io/api/test-executions"
API_TOKEN = os.environ.get("TESTINY_TOKEN")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Zakładamy, że każda pozycja ma: name, outcome
for test in results['tests']:
    test_name = test["name"]
    outcome = test["outcome"]

    # Mapowanie externalId
    external_id_map = {
        "test_valid_login": "TC_LOGIN_001",
        "test_invalid_login": "TC_LOGIN_002"
    }

    external_id = external_id_map.get(test_name)
    if not external_id:
        print(f"Pomijam test bez externalId: {test_name}")
        continue

    payload = {
        "testCaseExternalId": external_id,
        "status": "PASSED" if outcome == "passed" else "FAILED",
        "comment": "Zgłoszone automatycznie z GitHub Actions"
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    print(f"[{test_name}] → {response.status_code} {response.text}")
