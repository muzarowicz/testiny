import json
import os
from datetime import datetime
from typing import Dict, List

import requests
from requests.exceptions import RequestException

class TestinyReporter:
    def __init__(self, api_token: str, project_id: int):
        self.base_url = "https://app.testiny.io/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.project_id = 2

    def create_automation_test_run(self, name: str) -> str:
        """Create a new automation test run and return its ID."""
        url = f"{self.base_url}/automation-test-run"
        payload = {
            "project_id": self.project_id,
            "title": name,
            "start_time": datetime.utcnow().isoformat(),
            "status": "IN_PROGRESS",
            "description": "Automated test execution from CI/CD pipeline",
            "source": "pytest"  # Indicate the source of automation
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code != 200:
                print(f"Response content: {response.text}")
            response.raise_for_status()
            return response.json()["id"]
        except RequestException as e:
            print(f"Failed to create automation test run: {e}")
            raise

    def update_automation_test_case_result(self, test_run_id: str, test_case_external_id: str, status: str, comment: str) -> None:
        """Update automation test case result in the test run."""
        url = f"{self.base_url}/automation-test-run/{test_run_id}/test-case/{test_case_external_id}/result"
        
        payload = {
            "status": status,
            "comment": comment,
            "execution_time": datetime.utcnow().isoformat(),
            "automation_source": "pytest"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code != 200:
                print(f"Response content: {response.text}")
            response.raise_for_status()
            print(f"Updated automation test case {test_case_external_id} with status {status}")
        except RequestException as e:
            print(f"Failed to update automation test case {test_case_external_id}: {e}")

    def complete_automation_test_run(self, test_run_id: str) -> None:
        """Complete the automation test run."""
        url = f"{self.base_url}/automation-test-run/{test_run_id}/complete"
        payload = {
            "status": "COMPLETED",
            "end_time": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code != 200:
                print(f"Response content: {response.text}")
            response.raise_for_status()
            print(f"Completed automation test run {test_run_id}")
        except RequestException as e:
            print(f"Failed to complete automation test run: {e}")

def main():
    # Load environment variables
    api_token = os.environ.get("TESTINY_TOKEN")
    project_id = 2
    
    if not api_token:
        raise ValueError("TESTINY_TOKEN environment variable must be set")
    
    if not project_id:
        raise ValueError(
            "TESTINY_PROJECT_ID environment variable must be set.\n"
            "You can find your project ID in the URL when viewing your project in Testiny:\n"
            "https://app.testiny.io/projects/YOUR-PROJECT-ID/..."
        )

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

    # Create automation test run
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_run_name = f"Pytest Automation Run [{timestamp}]"
    try:
        test_run_id = reporter.create_automation_test_run(test_run_name)
    except RequestException:
        print("Failed to create automation test run. Aborting.")
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
        comment = f"Automated test execution from pytest - {outcome}"
        
        reporter.update_automation_test_case_result(
            test_run_id=test_run_id,
            test_case_external_id=external_id,
            status=status,
            comment=comment
        )

    # Complete automation test run
    reporter.complete_automation_test_run(test_run_id)

if __name__ == "__main__":
    main()
