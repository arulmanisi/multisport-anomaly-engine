You are my coding agent.

I have completed Day 1–10 of the Cricket Anomaly Engine MVP.
Tests for Day 1–5 already exist.
Now I want you to generate a FULL test suite for Days 6–10 + the Inference Interfaces + Core UPS Logic.

Create all tests using pytest, with clean, modular structure, mocks/stubs, and no real data dependencies.

---------------------------------------------------------------------
# COMPONENTS THAT NEED TESTS
---------------------------------------------------------------------

### Day 6
FeatureExtractor module:
- match context features
- team-level features
- player-level features
- venue/weather features

### Day 7
LabelCreator module:
- baseline labels (winner, run margin)
- anomaly labels (UPS Score, BowlingSpellAnomaly, BattingCollapseIndicator,
  MomentumShiftScore, ContextualUpsetIndicator, OutlierEventTag)
- label registry

### Day 8
DataPipeline module:
- load_raw_data()
- clean()
- generate_features()
- generate_labels()
- assemble_dataset()
- train_validation_split()

### Day 9
ModelWrapper / AnomalyModel:
- fit(X, y)
- predict(X)
- predict_proba(X)
- save_model()
- load_model()

### Day 10
TrainingEngine:
- run_training()
- run_evaluation()
- log_metrics()
- ensure anomaly-aware evaluation flow

### UPS Core Logic
UPSScorer:
- compute_player_baseline()
- compute_match_performance()
- compute_ups_score()
- is_anomalous()

### Inference Layers
CLI Inference:
- predict-single
- predict-batch
- argument parsing
- output formatting

REST API Inference (FastAPI-style mock):
- POST /predict/single
- POST /predict/batch
- TestClient-based tests or similar
- response schema validation

### Integration Flow Test:
A thin smoke test wiring together:
- DataPipeline (stub)
- LabelCreator or UPSScorer (stub)
- ModelWrapper (fake model)
- TrainingEngine
- Ensure training & evaluation run end-to-end without real ML logic.

---------------------------------------------------------------------
# TEST REQUIREMENTS
---------------------------------------------------------------------

Create individual pytest test files for each component:

1. test_feature_extractor.py  
2. test_label_creator.py  
3. test_data_pipeline.py  
4. test_model_wrapper.py  
5. test_training_engine.py  
6. test_ups_scorer.py  
7. test_cli_inference.py  
8. test_rest_api.py  
9. test_integration_flow.py  

Each file must:

- Use only mock/stub implementations where logic is incomplete.
- Rely only on in-memory objects (no file I/O).
- Use pytest style (not unittest).
- Include docstrings and comments clarifying expected behavior.
- Focus on schema, structure, contracts, and orchestration.
- Avoid real ML, real stats, or full cricket logic (use TODO markers).
- Ensure UPS Score anomaly flow is reflected where relevant.

---------------------------------------------------------------------
# DETAILED EXPECTATIONS PER TEST FILE
---------------------------------------------------------------------

## test_feature_extractor.py  
- Feed small fake match JSON.
- Assert output dict structure.
- Check handling of missing/extra fields.
- Verify feature buckets exist.

## test_label_creator.py  
- Test registry:
    - register_label()
    - get_label_output()
- Test UPS Score output placeholder.
- Test unknown label handling.

## test_data_pipeline.py  
- Use fake:
    - data_loader
    - cleaner
    - feature_extractor
    - label_creator
- Validate orchestrated flow for:
    * load_raw_data()
    * clean()
    * generate_features()
    * generate_labels()
    * assemble_dataset()
    * train_validation_split()

## test_model_wrapper.py  
- Create FakeModel inside the test file.
- Validate:
    - fit called
    - predict output shape
    - predict_proba optional behavior
    - save/load callable

## test_training_engine.py  
- Fake DataPipeline & ModelWrapper.
- Validate:
    - run_training calls fit
    - run_evaluation calls predict
    - evaluation returns metrics skeleton
    - log_metrics is callable

## test_ups_scorer.py  
- Use small numeric examples:
    - baseline: avg runs = 25
    - current: 70 runs
- Ensure UPS score > threshold triggers is_anomalous.
- Test:
    - baseline structure
    - ups score monotonic behavior

## test_cli_inference.py  
- Monkeypatch dependencies.
- Simulate predict-single + predict-batch.
- Capture stdout and assert output contains:
    - "UPS Score"
    - "is_anomalous"

## test_rest_api.py  
- Use TestClient or equivalent mock pattern.
- POST single + batch payloads.
- Assert:
    - status code 200
    - json includes ups_score + is_anomalous fields

## test_integration_flow.py  
- Wire together all modules via stubs.
- Call:
    - run_training()
    - run_evaluation()
- Assert training executed and evaluation returns a metrics dict.
- Purpose: smoke test of the entire architecture.

---------------------------------------------------------------------
# OUTPUT EXPECTATION
---------------------------------------------------------------------

Return all 9 test files, each fully written, ready for pytest, with:
- consistent structure
- placeholders/TODOs where full logic is not implemented
- no missing imports or syntax errors

This should form a complete test suite for Days 5–10 and the inference/UPS logic.

---------------------------------------------------------------------

Generate now.
