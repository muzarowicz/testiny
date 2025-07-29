import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def convert_to_junit_format(pytest_results: Dict) -> str:
    """Convert pytest JSON results to JUnit XML format."""
    # Create a temporary directory for reports if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate a unique filename for this run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    junit_file = reports_dir / f"pytest_results_{timestamp}.xml"
    
    # We'll use pytest's built-in JUnit XML generation
    # Re-run the failed tests to generate XML report
    test_names = [test["name"] for test in pytest_results.get("tests", [])]
    if test_names:
        cmd = [
            "pytest",
            *test_names,
            f"--junitxml={junit_file}",
            "-v"
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to generate JUnit XML report: {e}")
            return None
        
        return str(junit_file)
    return None

def submit_to_testiny(junit_file: str) -> None:
    """Submit test results to Testiny using the CLI."""
    api_key = os.environ.get("TESTINY_TOKEN")
    project_id = os.environ.get("TESTINY_PROJECT_ID", "2")
    
    if not api_key:
        raise ValueError("TESTINY_TOKEN environment variable must be set")

    # Install Testiny CLI if not already installed
    try:
        subprocess.run(["npx", "@testiny/cli", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Installing Testiny CLI...")
        subprocess.run(["npm", "install", "-g", "@testiny/cli"], check=True)

    # Set up the environment for the CLI
    env = os.environ.copy()
    env["TESTINY_API_KEY"] = api_key

    # Generate a unique run key for this test execution
    run_key = f"pytest_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Submit results using Testiny CLI
    cmd = [
        "npx",
        "@testiny/cli",
        "automation",
        "--project", project_id,
        "--source", "pytest",
        "--field-values", f"run_key={run_key}",
        "--run-fields", "run_key",
        "--junit", junit_file
    ]

    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print("Successfully submitted results to Testiny")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to submit results to Testiny: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        raise

def main():
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

    # Convert results to JUnit format
    junit_file = convert_to_junit_format(results)
    if not junit_file:
        print("No test results to submit")
        return

    # Submit results to Testiny
    try:
        submit_to_testiny(junit_file)
    except Exception as e:
        print(f"Failed to submit results: {e}")
    finally:
        # Clean up the reports directory
        if os.path.exists(junit_file):
            os.remove(junit_file)

if __name__ == "__main__":
    main()
