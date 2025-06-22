#!/usr/bin/env python3
"""
Test Runner | Cannlytics

Script to run different types of tests with various options.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Cannlytics tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "api", "data", "lims", "all"],
        default="unit",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast", 
        action="store_true",
        help="Skip slow tests"
    )

    args = parser.parse_args()

    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add options based on arguments
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=cannlytics", "--cov-report=html", "--cov-report=term-missing"])
    
    if args.parallel:
        cmd.extend(["-n", "auto"])
    
    if args.fast:
        cmd.append("-m")
        cmd.append("not slow")

    # Add test type filters
    if args.type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.type == "api":
        cmd.extend(["-m", "api"])
    elif args.type == "data":
        cmd.extend(["-m", "data"])
    elif args.type == "lims":
        cmd.extend(["-m", "lims"])
    elif args.type == "all":
        pass  # Run all tests

    # Run the tests
    success = run_command(cmd, f"{args.type.title()} Tests")
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 