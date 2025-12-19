Architectural Gap Analysis Report
Executive Summary
The multisport-anomaly-engine project is currently in a "strangled migration" state, with significant duplication between the legacy cae (Cricket Anomaly Engine) and the new 
plaix
 (Multi-sport Platform) architectures. This has led to confusing entry points, circular dependencies, and inconsistent project structure.

Key Findings
1. Duplicate & Confusing Entry Points
There are three distinct entry points, causing confusion about the "source of truth":

backend/cae/api/app.py
: Legacy cricket-only app.
backend/plaix/api/main.py
: The intended new multi-sport system.
backend/app/main.py
: A redundant wrapper that points to 
plaix
.
Recommendation: Consolidate into a single entry point (e.g., plaix.api.main) and deprecate cae and backend/app.

2. Inverted/Messy Dependencies
backend/plaix/api/main.py imports from backend/app (from app import anomaly_feed...).
This treats the "application user interface" (app) as a library for the "core platform" (plaix), which is an architectural anti-pattern.
Modules like anomaly_feed, live_match, and report_export are loosely placed in backend/app but contain business logic that belongs in plaix.services or plaix.core.
Recommendation: Move anomaly_feed.py, live_match.py, etc., into plaix/services/ or plaix/features/ and remove backend/app.

3. Incomplete Core Implementation
plaix.core.ups_scorer.UPSScorer contains placeholder TODOs for critical features:
get_team_role_baseline (returns None)
get_global_role_baseline (returns None)
The core scoring logic relies on these fallback mechanisms which are not yet implemented.
Recommendation: Prioritize implementing these baseline fallbacks to ensure robust scoring for new players/teams.

4. Project Structure Inconsistency
The backend/ directory is a mix of packages (cae, plaix) and loose module directories (data, llm, models, scripts, tests, app).
It is unclear which data or models directory belongs to cae vs plaix.
Recommendation: Enforce a strict package structure. Move shared/loose directories into plaix if they are the future, or clearly separate them.

5. Documentation Fragmentation
README.md references all three entry points and mixes instructions for "PLAIX MVP", "Day 2", etc., without clearly marking legacy paths as deprecated.
Recommendation: Update documentation to clearly define the standard development workflow and mark cae instructions as legacy.

Proposed Next Steps
Refactor: Move backend/app/*.py modules into plaix structure.
Cleanup: Deprecate and eventually remove backend/cae.
Standardize: Update README.md to point to a single entry point.
Implement: Fill in the missing TODOs in ups_scorer.py.