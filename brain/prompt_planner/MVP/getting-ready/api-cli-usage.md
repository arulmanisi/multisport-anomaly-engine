You are my coding agent.

Goal:
Document how to use the CLI and REST API for the Cricket Anomaly Engine MVP.

Tasks:

1) CLI Usage
- In README.md, add a section "CLI Usage".
- Show an example `predict-single` command using cli.py with realistic arguments such as:
    player_id, match_format, current_runs, baseline_mean_runs, baseline_std_runs.
- Show a sample textual output block with:
    UPS Score, UPS Bucket, Baseline Anomaly Flag, Model Anomaly Probability, Model Anomaly Label.

2) REST API Usage
- In README.md, add a section "REST API Usage".
- Show an example curl command for POST /predict/single with a JSON body matching the API input.
- Show a sample JSON response with:
    ups_score,
    ups_bucket,
    ups_anomaly_flag_baseline,
    model_anomaly_probability,
    model_anomaly_label.

3) Formatting
- Use proper Markdown headings and fenced code blocks.
- Keep examples minimal but realistic.
- Do not change unrelated parts of the README.

After editing, show me the updated sections of README.md.
