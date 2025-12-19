You are my coding agent.

Feature 2: "Live Match Mode" (simulated real-time innings updates).

Goal (Backend):
Add endpoints that simulate an innings unfolding over time (balls/overs),
and return incremental anomaly evaluation at each step:
- current runs so far
- UPS score and bucket
- model probability and label
- narrative headline/summary (optional, rate-limited)

We will simulate the stream (not scrape live feeds).

Tasks:

1) Create module:
   backend/app/live_match.py

2) Implement an in-memory simulator:
- Define a function generate_innings_stream(seed, overs=20) that produces a list of steps:
    step_index, over, ball, runs_this_ball, cumulative_runs, cumulative_balls

- Use deterministic randomness (random.Random(seed)) so demo is repeatable.
- Provide a few “scenario” presets:
    - "normal": steady scoring around baseline
    - "breakout": strong acceleration after powerplay
    - "collapse": early wickets / low run rate
  Even if wickets not modeled, simulate run patterns.

3) Endpoint:
   POST /live/start

Request:
{
  "player_id": str,
  "match_format": str,
  "scenario": str ("normal"|"breakout"|"collapse"),
  "baseline_mean_runs": float,
  "baseline_std_runs": float,
  "overs": int (default 20),
  "tone": str (default "commentator"),
  "include_narrative": bool (default false)
}

Response:
{
  "session_id": str,
  "total_steps": int
}

- session_id can be a uuid4.
- Store the generated steps in a global dict keyed by session_id (MVP ok).

4) Endpoint:
   GET /live/step/{session_id}?i=<index>&include_narrative=<bool>&tone=<tone>

Response:
{
  "session_id": str,
  "index": int,
  "over": int,
  "ball": int,
  "cumulative_runs": float,
  "cumulative_balls": int,
  "baseline_mean_runs": float,
  "baseline_std_runs": float,
  "ups_score": float,
  "ups_bucket": str,
  "ups_anomaly_flag_baseline": int,
  "model_anomaly_probability": float,
  "model_anomaly_label": int,
  "headline": str,              # rule-based (sports style)
  "key_drivers": [..],
  "narrative_title": optional str,
  "narrative_summary": optional str
}

- For each step, run the same scoring pipeline you use in /predict/single
  but using current_runs=cumulative_runs.
- If include_narrative is true, call narrator.generate_description(event, tone=tone).
  Otherwise omit narrative fields.

5) Cleanup endpoint (optional):
   POST /live/stop/{session_id} deletes stored session.

6) Wire routers into FastAPI main.

After implementing, show:
- backend/app/live_match.py
- Example start response and a step response (i=0 and i=10).
