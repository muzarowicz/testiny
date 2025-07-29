import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

def submit_to_testiny(junit_file: str) -> None:
    """Submit test results to Testiny using the CLI."""
    api_key = os.environ.get("TESTINY_API_KEY")
    project_id = os.environ.get("TESTINY_PROJECT_ID", "2")
    
    if not api_key:
        raise ValueError("TESTINY_API_KEY environment variable must be set")

    # Install Testiny CLI if not already installed
    try:
        subprocess.run(["npx", "@testiny/cli", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Installing Testiny CLI...")
        subprocess.run(["npm", "install", "-g", "@testiny/cli"], check=True)

    # Set up the environment for the CLI
    env = os.environ.copy()
    env["TESTINY_API_KEY"] = api_key

    # Submit results using Testiny CLI
    cmd = [
        "npx",
        "@testiny/cli",
        "automation",
        "--project", project_id,
        "--source", "pytest-tests",  # Changed to match documentation
        "--junit", junit_file
    ]

    # If running in GitHub Actions, the CLI will automatically detect and add CI environment variables
    if os.environ.get("GITHUB_ACTIONS"):
        print("Detected GitHub Actions environment")
    else:
        # For local runs, add a custom run title
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cmd.extend(["--run-title-pattern", f"Pytest Run - {timestamp}"])

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
    # Create results directory if it doesn't exist
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Generate JUnit XML report directly from pytest
    junit_file = results_dir / "report.xml"
    
    try:
        # Run pytest with JUnit XML report generation
        cmd = [
            "pytest",
            f"--junit-xml={junit_file}",
            "-v",
            "tests"  # Run all tests in the tests directory
        ]
        subprocess.run(cmd, check=True)
        
        # Submit results to Testiny
        submit_to_testiny(str(junit_file))
    except subprocess.CalledProcessError as e:
        print(f"Failed to run tests or generate report: {e}")
    except Exception as e:
        print(f"Failed to submit results: {e}")
    finally:
        # Clean up the results directory
        if junit_file.exists():
            junit_file.unlink()
        if results_dir.exists() and not any(results_dir.iterdir()):
            results_dir.rmdir()

if __name__ == "__main__":
    main()
