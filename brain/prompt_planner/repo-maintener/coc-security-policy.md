You are my coding agent.

I want to finalize the open-source foundation of this repository by adding:
1. CODE_OF_CONDUCT.md
2. SECURITY.md
3. A GitHub Actions CI workflow to run pytest on every push and pull request.

Please complete the following tasks.

---------------------------------------------------------------------
# TASK 1 — Create CODE_OF_CONDUCT.md
---------------------------------------------------------------------
Create a file at the project root named: CODE_OF_CONDUCT.md  
Populate it with the following:

# Code of Conduct

## Our Pledge
We are committed to providing a harassment-free, inclusive, and welcoming environment for everyone.  
All participants—contributors, maintainers, users—should feel respected and safe.

## Our Standards
Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language  
- Being respectful of differing viewpoints and experiences  
- Accepting constructive criticism  
- Focusing on what is best for the community  
- Showing empathy toward others  

Examples of unacceptable behavior:
- Harassment, trolling, or insulting comments  
- Public or private sexualized language or imagery  
- Personal attacks  
- Publishing private information without permission  
- Any other conduct inappropriate in a professional setting  

## Our Responsibilities
Project maintainers are responsible for:
- Clarifying standards of acceptable behavior  
- Taking fair and reasonable corrective action  
- Removing or rejecting inappropriate contributions  

## Enforcement
Violations may be reported by opening an issue or contacting the project maintainer directly.  
All complaints will be reviewed and investigated confidentially.

## Attribution
This Code of Conduct is adapted from the Contributor Covenant, version 2.1.

---------------------------------------------------------------------
# TASK 2 — Create SECURITY.md
---------------------------------------------------------------------
Create a file at the project root named: SECURITY.md  
Populate it with the following:

# Security Policy

## Supported Versions
This project is currently in active development.  
Security updates and patches will be applied on a best-effort basis.

## Reporting a Vulnerability
If you discover a security issue, please report it responsibly.

To report:
- Open a GitHub security advisory **OR**
- Email the project maintainer directly

Please include:
- Description of the vulnerability  
- Steps to reproduce  
- Potential impact  
- Suggested fix (if any)

We appreciate responsible disclosure.  
Do **not** create public GitHub issues containing security vulnerabilities.

---------------------------------------------------------------------
# TASK 3 — GitHub Actions CI Workflow
---------------------------------------------------------------------
Create a directory: .github/workflows  
Inside it, create a file named: ci.yml  

Populate it with the following CI pipeline:

name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest

    - name: Run Tests
      run: |
        pytest --maxfail=1 --disable-warnings -q

---------------------------------------------------------------------

After completing all tasks, show me:
- CODE_OF_CONDUCT.md
- SECURITY.md
- .github/workflows/ci.yml

Ensure they are clean, well-formatted, and correctly placed.
