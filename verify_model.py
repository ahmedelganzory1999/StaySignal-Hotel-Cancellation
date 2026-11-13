"""Optional smoke test for the model package (does not use Streamlit)."""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

HERE = Path(__file__).resolve().parent
config = json.loads((HERE / "model" / "hotel_cancellation_config.json").read_text(encoding="utf-8"))
model = joblib.load(HERE / "model" / "hotel_cancellation_pipeline.joblib")
df = pd.read_csv(HERE / "data" / "hotel_bookings_cleaned.csv")

months = {name: i for i, name in enumerate([
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December"
], 1)}
arrival = pd.to_datetime(dict(year=df.arrival_date_year,
                              month=df.arrival_date_month.map(months),
                              day=df.arrival_date_day_of_month))
df["total_nights"] = df.stays_in_week_nights + df.stays_in_weekend_nights
df["total_guests"] = df.adults + df.children + df.babies
df["has_children"] = ((df.children + df.babies) > 0).astype(int)
assert list(model.feature_names_in_) == config["feature_columns"]

test = df.loc[arrival >= pd.Timestamp(config["train_split_date"])]
y = test.is_canceled.astype(int)
probability = model.predict_proba(test[config["feature_columns"]])[:, 1]
prediction = (probability >= config["decision_threshold"]).astype(int)
scores = {
    "Accuracy": accuracy_score(y, prediction),
    "Precision": precision_score(y, prediction, zero_division=0),
    "Recall": recall_score(y, prediction, zero_division=0),
    "F1": f1_score(y, prediction, zero_division=0),
}
print("Test bookings:", len(test))
for name, value in scores.items():
    expected = config["test_scores"][name]
    print(f"{name}: {value:.5f} (improved model expected: {expected:.5f})")
    assert abs(value - expected) < 0.0001
print("Model and package checks passed.")
