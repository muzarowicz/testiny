import json
import os
from datetime import datetime
from typing import Dict, List

import requests
from requests.exceptions import RequestException

class TestinyReporter:
    def __init__(self, api_token: str, project_id: str):
        self.base_url = "https://api.testiny.io/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.project_id = "2"

    def create_test_run(self, name: str) -> str:
        """Create a new test run and return its ID."""
        url = f"{self.base_url}/testrun"
        payload = {
            "project_id": self.project_id,
            "name": name,
            "start_time": datetime.utcnow().isoformat(),
            "status": "IN_PROGRESS"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()["id"]
        except RequestException as e:
            print(f"Failed to create test run: {e}")
            raise

    def update_test_case_result(self, test_run_id: str, test_case_external_id: str, status: str, comment: str) -> None:
        """Update test case result in the test run."""
        url = f"{self.base_url}/testrun/{test_run_id}/testcase/{test_case_external_id}/result"
        
        payload = {
            "status": status,
            "comment": comment,
            "execution_time": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Updated test case {test_case_external_id} with status {status}")
        except RequestException as e:
            print(f"Failed to update test case {test_case_external_id}: {e}")

    def finalize_test_run(self, test_run_id: str, status: str = "COMPLETED") -> None:
        """Finalize the test run with the given status."""
        url = f"{self.base_url}/testrun/{test_run_id}"
        payload = {
            "status": status,
            "end_time": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"Finalized test run {test_run_id} with status {status}")
        except RequestException as e:
            print(f"Failed to finalize test run: {e}")

def main():
    # Load environment variables
    api_token = os.environ.get("TESTINY_TOKEN")
    project_id = "2"
    
    if not api_token or not "2":
        raise ValueError("TESTINY_TOKEN and TESTINY_PROJECT_ID environment variables must be set")

    # Load test results
    try:
        with open('results.json') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("results.json file not found")
        return
    except json.JSONDecodeError:
        print("Invalid JSON in results.json")
        return

    # Initialize reporter
    reporter = TestinyReporter(api_token, project_id)

    # Create test run
    test_run_name = f"Automated Test Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    try:
        test_run_id = reporter.create_test_run(test_run_name)
    except RequestException:
        print("Failed to create test run. Aborting.")
        return

    # Mapping of test names to external IDs
    external_id_map = {
        "test_valid_login": "TC_LOGIN_001",
        "test_invalid_login": "TC_LOGIN_002"
    }

    # Process test results
    for test in results.get('tests', []):
        test_name = test.get("name")
        outcome = test.get("outcome")

        external_id = external_id_map.get(test_name)
        if not external_id:
            print(f"Skipping test without external ID mapping: {test_name}")
            continue

        status = "PASSED" if outcome == "passed" else "FAILED"
        comment = f"Automated test execution - {outcome}"
        
        reporter.update_test_case_result(
            test_run_id=test_run_id,
            test_case_external_id=external_id,
            status=status,
            comment=comment
        )

    # Finalize test run
    reporter.finalize_test_run(test_run_id)

if __name__ == "__main__":
    main()
