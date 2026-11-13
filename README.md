# StaySignal | Hotel Booking Intelligence

**Epsilon Machine Learning Final Project** — historical hotel-booking exploration and an interactive Streamlit cancellation-risk *demonstration*.

## What is included

- Seven Streamlit sections: Home, Executive Pulse, Cancellation Drivers, Seasonality & Pricing, Cancellation Predictor, Model Performance, and Data Explorer.
- `app.py` plus `pages/` and `utils/` source files.
- `model/hotel_cancellation_pipeline.joblib`: saved XGBoost classifier with the preprocessing pipeline (StandardScaler, OneHotEncoder and ColumnTransformer).
- `model/hotel_cancellation_config.json`: the model settings and **22 required input columns**.
- `data/hotel_bookings_cleaned.csv`: 119,386 historical records after documented cleaning.
- `verify_model.py`: independent smoke test of saved-model predictions against the historical test split.

This repository also includes `hotel_bookings.csv` (original uncleaned dataset) and `Hotel Booking - Final Project.ipynb` (the full analysis notebook).

## Reproduced historical results

The saved model uses threshold **0.25**, selected on the validation period using F1. On the **24,041** records with arrival dates from **22 April to 31 August 2017**:

| Metric | Value |
|---|---:|
| Accuracy | 79.13% |
| Precision | 71.63% |
| Recall | 81.20% |
| F1 | 76.12% |

The test period was reviewed during previous versions of this project and therefore is **not an untouched prospective evaluation**. Scores are not calibrated real-world probabilities.

## Run locally

Use Python **3.11 or newer** in a *new* virtual environment. From the folder containing `app.py`:

```bash
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python verify_model.py
streamlit run app.py
```

The browser normally opens at `http://localhost:8501`.



## Important limitations

- Historical data covers only **two hotels in Portugal, 2015–2017**; applicability to other hotels or later periods is unknown.
- `required_car_parking_spaces` and `total_of_special_requests` show unusually strong cancellation associations. Their **booking-creation-time availability must be verified** before operational deployment.
- Arrival-date chronological splitting is not equivalent to a real-time booking-creation-time evaluation.
- The classification score is **not calibrated** and the 0.25 decision threshold is a *validation choice*, not a justified business intervention rule.
- Avoid automatic booking rejection or penalties. A flagged booking is a reason for contextual review, not a definitive cancellation.
- Multiple rows appear identical but lack unique reservation identifiers; these rows were retained and explicitly documented in the notebook.

**Source:** Hotel Booking Demand dataset, António, de Almeida & Nunes (2019). Analyses and illustrations derive from the supplied student notebook.
