You are my coding agent.
We are on Day 8 of the Cricket Anomaly Engine MVP.

Goal:
Create a high-level DataPipeline class that orchestrates the modules built so far.

Context:
- We already defined:
  * FeatureExtractor (Day 6)
  * LabelCreator with anomaly labels including UPS Score (Day 7)
- We are still in "design only" mode, not full implementation.

Requirements:

1. Create a DataPipeline (or similar) class that:
   - Accepts as constructor dependencies:
       * data_loader (callable or object)
       * cleaner
       * feature_extractor
       * label_creator
   - Orchestrates the steps:
       * load_raw_data()
       * clean()
       * generate_features()
       * generate_labels()
       * assemble_dataset()
       * train_validation_split()

2. For each step:
   - Define clear method signatures.
   - Add docstrings describing:
       * inputs
       * outputs
       * assumptions (e.g., schema expectations).
   - Use TODO comments where implementation is needed.

3. Make it anomaly-focused:
   - Explicitly mention that labels may include anomaly labels like:
       * UPS Score
       * BowlingSpellAnomaly
       * BattingCollapseIndicator
       * etc.

4. Make it sport-extensible:
   - Design so that in future we can plug in:
       * cricket_feature_extractor
       * football_feature_extractor, etc.
   - You can use abstract base classes or interfaces if helpful.

5. Do NOT implement real logic.
   - Focus on clean, production-style structure
   - Add type hints, docstrings, and comments.

Return one complete Python module with just structure + TODOs.
