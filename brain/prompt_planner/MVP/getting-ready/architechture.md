You are my coding agent.

Goal:
Add a simple architecture diagram to README.md to illustrate the MVP flow.

Requirements:
1. In README.md, add a section "Architecture Overview".
2. Inside it, include a Mermaid diagram (GitHub-compatible) that shows this flow:

   Raw Input (match/innings)
     -> FeatureExtractor
     -> UPSScorer (baseline + UPS score)
     -> Feature Vector (UPS + context)
     -> ModelWrapper (Logistic Regression)
     -> Anomaly Prediction (probability + label)
     -> CLI / REST Response

3. Use a `mermaid` fenced code block, for example:

   ```mermaid
   flowchart LR
      ...
