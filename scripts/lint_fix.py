#!/usr/bin/env python3
"""
A helper script to run pre-commit checks and auto-fix linting issues when possible.
This script is designed to be run before considering a task complete.
"""

import shlex
import subprocess  # nosec B404 - This is a controlled use for specific commands
import sys
from typing import List, Tuple


def run_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a shell command and return the exit code, stdout, and stderr."""
    # We're only running known pre-commit commands with fixed arguments
    # not user inputs, so this is safe and doesn't need shell=True
    process = subprocess.Popen(  # nosec B603 - We're only running pre-defined commands
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def run_initial_checks():
    """Run the initial pre-commit checks."""
    print("🔍 Running pre-commit checks...")
    returncode, stdout, stderr = run_command(["pre-commit", "run", "--all-files"])

    if returncode == 0:
        print("✅ All checks passed!")
        return True, "", ""

    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    return False, stdout, stderr


def run_auto_fixes():
    """Run auto-fixes for hooks that support automatic fixing."""
    print("\n🔧 Attempting to automatically fix linting issues...")

    auto_fix_hooks = [
        "trailing-whitespace",
        "end-of-file-fixer",
        "black",
        "isort",
        "nbstripout",
        "nbqa-black",
        "nbqa-isort",
    ]

    for hook in auto_fix_hooks:
        print(f"Running auto-fix for {hook}...")
        returncode, stdout, stderr = run_command(["pre-commit", "run", hook, "--all-files"])
        if stdout.strip():
            print(stdout)


def check_fixes():
    """Re-run checks to see if issues were fixed."""
    print("\n🔍 Re-running pre-commit checks after auto-fixes...")
    returncode, stdout, stderr = run_command(["pre-commit", "run", "--all-files"])

    if returncode == 0:
        print("✅ All issues fixed automatically!")
        return True, "", ""

    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    return False, stdout, stderr


def extract_files_with_issues(stdout):
    """Extract list of files with issues from pre-commit output."""
    files_with_issues = set()

    for line in stdout.splitlines():
        if line.startswith("Files were modified by this hook"):
            continue

        if ".py" in line or ".ipynb" in line or ".md" in line or ".yml" in line:
            parts = line.split()
            for part in parts:
                if (
                    part.endswith(".py")
                    or part.endswith(".ipynb")
                    or part.endswith(".md")
                    or part.endswith(".yml")
                    or part.endswith(".yaml")
                ):
                    files_with_issues.add(part)

    return files_with_issues


def main():
    """Run pre-commit checks and attempt to fix linting issues."""
    # Disable the complexity check for this function
    # flake8: noqa: C901

    # Run initial checks
    checks_passed, stdout, stderr = run_initial_checks()
    if checks_passed:
        return 0

    # Attempt to fix issues
    run_auto_fixes()

    # Check if fixes worked
    fixed, stdout, stderr = check_fixes()
    if fixed:
        return 0

    # Report remaining issues
    print("\n⚠️ Some issues could not be fixed automatically. Please address them manually:")

    files_with_issues = extract_files_with_issues(stdout)

    if files_with_issues:
        print("Files with linting issues:")
        for file in sorted(files_with_issues):
            print(f"  - {file}")

    print("\n🚨 Task cannot be considered complete until all linting issues are resolved.")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
