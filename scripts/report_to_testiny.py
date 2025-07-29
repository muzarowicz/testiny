import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

def run_pytest(junit_file: Path) -> bool:
    """Run pytest and generate JUnit XML report.
    Returns True if tests were found and run (regardless of pass/fail)."""
    
    print("Running pytest...")
    
    # First check if we have any tests
    try:
        # Collect tests without running them
        collect_cmd = ["pytest", "--collect-only", "-v"]
        result = subprocess.run(collect_cmd, capture_output=True, text=True)
        if "no tests ran" in result.stdout or "no tests collected" in result.stdout:
            print("No tests were found. Make sure you have test files in the 'tests' directory.")
            print("Test files should be named 'test_*.py' or '*_test.py'")
            return False
    except subprocess.CalledProcessError as e:
        print("Failed to collect tests:")
        print(e.stdout)
        print(e.stderr)
        return False

    # Now run the actual tests
    try:
        cmd = [
            "pytest",
            f"--junit-xml={junit_file}",
            "-v",
            "--no-header",  # Cleaner output
            "--tb=short",   # Shorter tracebacks
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Always print test output
        print("\nTest Output:")
        print(result.stdout)
        if result.stderr:
            print("\nTest Errors:")
            print(result.stderr)
        
        # Even if tests fail, we want to report results
        return True
        
    except subprocess.CalledProcessError as e:
        print("Failed to run tests:")
        print(e.stdout)
        print(e.stderr)
        return False

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

    # Base command
    cmd = [
        "npx",
        "@testiny/cli",
        "automation",
        "--project", project_id,
        "--source", "pytest-tests",
        "--junit", junit_file
    ]

    # Handle GitHub Actions environment
    if os.environ.get("GITHUB_ACTIONS"):
        print("Detected GitHub Actions environment")
        # Add --incomplete flag to allow multiple submissions in the same CI run
        cmd.append("--incomplete")
        
        # Add custom run fields to differentiate between test runs
        job_id = os.environ.get("GITHUB_JOB", "unknown")
        attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        cmd.extend([
            "--field-values", f"job_id={job_id},attempt={attempt}",
            "--run-fields", "ci_repository,ci_run_id,job_id,attempt"
        ])
    else:
        # For local runs, add a custom run title
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cmd.extend(["--run-title-pattern", f"Pytest Run - {timestamp}"])

    print(f"Running Testiny CLI command: {' '.join(cmd)}")
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
    # Check if tests directory exists
    if not Path("tests").exists():
        print("Error: 'tests' directory not found!")
        print("Make sure you have a 'tests' directory with your test files.")
        return

    # Create results directory if it doesn't exist
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Generate JUnit XML report directly from pytest
    junit_file = results_dir / "report.xml"
    
    try:
        # Run pytest and generate report
        tests_ran = run_pytest(junit_file)
        
        if tests_ran and junit_file.exists():
            # Submit results to Testiny only if we have results
            submit_to_testiny(str(junit_file))
        else:
            print("No test results to submit to Testiny")
            
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
