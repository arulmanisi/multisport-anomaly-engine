You are my coding agent.
We are working on Day 7 of the Cricket Anomaly Engine MVP.

Goal:
Create a LabelCreator module that supports BOTH traditional ML labels and anomaly-specific labels.

Requirements:

1. Create a LabelCreator class that supports:
   - Baseline labels:
       * winner
       * run_margin (future)
       * first_innings_score (future)
   - Anomaly labels:
       * UPS Score (Unexpected Performance Spike) ← primary MVP label
       * BowlingSpellAnomaly
       * BattingCollapseIndicator
       * MomentumShiftScore
       * ContextualUpsetIndicator
       * OutlierEventTag

2. For each label type:
   - Create a method signature.
   - Only write docstrings + TODO comments.
   - No implementation logic.

3. Add a "label registry" mechanism:
   - register_label(name, function)
   - get_label_output(name, match_json)

4. Add clean input/output schemas:
   Input: match_json (structured after feature extraction)
   Output: dictionary of label_name → label_value

5. Create a UPS Score label method with clear docstring:
   - Detect anomalous player/team performance compared to historical baseline.
   - Binary or numeric scalable output.

6. Ensure the architecture is future-proof:
   - Should be extendable to multi-sport label creation.
   - Should support ensemble labels (multiple anomalies combined).

7. Present everything as production-ready structure 
   with TODOs and placeholder logic only.

Produce the full module design in Python, 
with clear class structure, docstrings, and comments.
