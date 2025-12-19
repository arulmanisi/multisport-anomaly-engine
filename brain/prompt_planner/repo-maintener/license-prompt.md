You are my coding agent.

I want to finish the licensing and open-source setup for this repository.

Goal:
Add the Apache-2.0 license badge, add a “No Enterprise Data Used” disclaimer to README.md, 
and create a CONTRIBUTING.md file.

---------------------------------------------------------------------
# TASK 1 — Add License Badge to README
---------------------------------------------------------------------
1. Open README.md.
2. Add this badge below the project title (or at the top if no title formatting exists):

   [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

3. Make sure the badge links correctly to the LICENSE file.
4. Keep formatting clean and avoid modifying unrelated README content.

---------------------------------------------------------------------
# TASK 2 — Add 'No Enterprise Data Used' Disclaimer
---------------------------------------------------------------------
1. In README.md, add a new section at the bottom:

   ## Disclaimer

   This project is fully open-source and uses only publicly available, synthetic, 
   or self-generated data. No enterprise, confidential, or proprietary data from 
   any employer (past or present) has been used in developing this project.

2. Do not alter any other README sections.

---------------------------------------------------------------------
# TASK 3 — Create CONTRIBUTING.md
---------------------------------------------------------------------
1. Create a new file at the root of the project: CONTRIBUTING.md
2. Populate it with the following sections:

   # Contributing to Cricket Anomaly Engine

   Thank you for considering contributing to this project! All contributions, big or small, are welcome.

   ## How to File Issues
   - Use GitHub Issues to report bugs, propose enhancements, or request documentation.
   - Provide clear reproduction steps when reporting bugs.

   ## How to Submit Pull Requests
   1. Fork the repository.
   2. Create a new branch for your feature or fix.
   3. Ensure all tests pass (`pytest`).
   4. Submit a pull request with a clear description of the changes.

   ## Coding Standards
   - Follow Python best practices (PEP8).
   - Write modular, testable, well-documented code.
   - Keep functions focused and concise.

   ## Testing Requirements
   - All new code must include unit tests.
   - Mock external dependencies.
   - Test coverage should not decrease.

   ## License Notice
   By contributing to this project, you agree that your contributions will be
   licensed under the Apache License 2.0.

---------------------------------------------------------------------

After completing all tasks, show me:
- the updated README.md content
- the full CONTRIBUTING.md file
- confirmation that the LICENSE badge and disclaimer were inserted correctly.
