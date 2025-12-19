You are my coding assistant for the PLAIX project.

Goal:
I want to refactor PLAIX from a cricket-specific anomaly engine into a generic multi-sport intelligence engine, while still supporting cricket as one sport, and adding a clean structure for future sports (e.g., football, basketball, etc.).

High-level requirements:

Rename and generalize:

Anywhere the code or docs talk specifically about “cricket” or “cricket events”, generalize to “sport” or “sports events”, except in sport-specific modules (e.g., cricket-specific implementation).

Keep the brand name PLAIX as-is. This is now a “multi-sport anomaly and intelligence platform”, not just a cricket tool.

Architecture shift:

Introduce a clear separation between:

Core, sport-agnostic abstractions (shared types, base interfaces, orchestration).

Sport-specific implementations (cricket, and at least one placeholder for another sport like “generic” or “football”).

I want the design to look like:

plaix.core → base types, interfaces, shared utilities, generic anomaly pipeline orchestration.

plaix.sports.cricket → cricket-specific event schema, baselines, anomaly logic, mappings.

plaix.sports.<other_sport> → stub or placeholder for a second sport (e.g., football) so the pattern is clear.

The scoring pipeline should work in terms of:

A “sport_type” or similar field.

A registry/dispatcher that routes events to the correct sport-specific implementation.

Pipelines and sport-specific implementations:

Design and implement a sport pipeline pattern:

There should be a clear way to:

Register a sport.

Define its event schema / mapping into core fields.

Plug in sport-specific baselines and anomaly logic.

For now, actual full logic is required only for cricket, but the structure must make it easy to add other sports.

Keep the current anomaly scoring behavior for cricket (z-score style or whatever is implemented), but move it into the cricket-specific implementation.

Add a second sport implementation as a stub with very basic or placeholder behavior (e.g., a “generic” or “football” implementation that just returns non-anomalous results), so the pattern is demonstrated.

API behavior:

The FastAPI API should now:

Accept an indication of which sport an event belongs to (for example, a “sport” field in the request model).

Use that “sport” information to dispatch to the correct sport-specific pipeline.

If an unsupported or unknown sport is requested, return a clear, safe error response.

Ensure that existing test flows still work for cricket when “sport” is set appropriately.

Data and models:

Generalize request/response models so they are sport-agnostic at the core level, but allow sport-specific extensions or mappings.

For cricket, keep the existing event attributes, but make sure they are now part of the cricket-specific layer or clearly mapped from a sport-agnostic structure.

It should be obvious from the structure where to add new sport-specific schemas later.

Tests:

Update existing tests to:

Use the new “sport” mechanism for cricket.

Verify that cricket-specific scoring still works and that anomalies are detected as before.

Add at least one test for:

Unsupported sport → expected error behavior.

A placeholder second sport (e.g., “football”) → verify that the dispatcher routes correctly and returns a valid response (even if the logic is trivial for now).

Do not remove test coverage; where behavior changes, adapt tests thoughtfully.

Documentation:

Update README and any design docs so they:

Refer to PLAIX as a multi-sport intelligence / anomaly engine.

Explain the architecture split:

core vs sport-specific modules.

how a new sport can be registered and implemented.

Add a short section that explains:

How a developer can add a new sport (steps: define schema, implement pipeline, register sport, update tests).

Constraints and style:

Preserve public API shapes unless there is a strong reason to change them; where you do change them, make the new design clearly better and consistent with the multi-sport goal.

Keep code modular, with clear responsibilities.

Maintain or improve type hints and docstrings.

Keep logging and config patterns consistent with what already exists.

Do not over-engineer; focus on a clean, understandable structure that can be extended.

Action:

Scan the current PLAIX codebase under src/plaix/ and the tests under tests/, as well as README and any design docs if present.

Propose a short, high-level plan (in comments or as a summary) for:

How you will introduce plaix.core and plaix.sports.<sport>.

How you will change the API models and dispatcher.

Then implement the refactor in small, coherent steps:

Introduce core vs sports structure.

Move cricket-specific logic into plaix.sports.cricket.

Add the sport dispatcher.

Update API models and endpoints.

Update tests.

Update docs.

As you modify files, keep the changes cohesive and explain in comments (briefly) where needed why a major structural change was made.

When you are done, summarize:

What changed structurally.

How a new sport would be added.

Which tests cover the new behavior.