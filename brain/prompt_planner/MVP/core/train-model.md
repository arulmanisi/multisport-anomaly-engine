You are my coding agent.

Now I want to implement a minimal real ML model for anomaly prediction and train it on the synthetic UPS dataset.

Goal:
Wire a simple Logistic Regression (from scikit-learn) into the existing ModelWrapper and add a training script that produces a trained model artifact.

Requirements:

1. In the ModelWrapper (or AnomalyModel) module:
   - Add a concrete implementation that, when model_type="logistic_regression", internally uses sklearn.linear_model.LogisticRegression.
   - ModelWrapper should:
       * On fit(X, y):
            - instantiate LogisticRegression with reasonable defaults
            - fit it on the provided features and labels
       * On predict(X):
            - return the predicted labels (0/1)
       * On predict_proba(X):
            - return probabilities ([:,1] for anomaly class)
       * On save_model(path):
            - use joblib or pickle to dump the underlying model to disk
       * On load_model(path):
            - load the saved model back into ModelWrapper.

2. Create a training script, e.g., scripts/train_ups_model.py

   The script should:
   - Load data/synthetic_ups_dataset.csv using pandas.
   - Choose features such as:
       * baseline_mean_runs
       * baseline_std_runs
       * current_runs
       * venue_flatness
       * opposition_strength
       * batting_position
   - Use ups_anomaly_flag as the label y.
   - Split into train/validation (e.g., 80/20).
   - Instantiate ModelWrapper with model_type="logistic_regression".
   - Call fit() on the training data.
   - Optionally evaluate on validation:
       * compute simple metrics (accuracy, precision, recall) and print them.
   - Save the trained model to e.g. models/ups_logreg.pkl using ModelWrapper.save_model().

3. Keep all paths configurable at the top of the script or via simple constants.

4. After implementation, the script should be runnable as:
   python scripts/train_ups_model.py

After you finish, show me:
- the updated ModelWrapper
- the train_ups_model.py script
- a sample of the printed metrics.
