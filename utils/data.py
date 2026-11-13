from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
MONTHS = [
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December"
]
MONTH_MAP = {month: number for number, month in enumerate(MONTHS, start=1)}
BANDS = ["0–7 days", "8–30 days", "31–90 days", "91–180 days", "181–365 days", "366+ days"]


@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(ROOT / "data" / "hotel_bookings_cleaned.csv")
    df["month_number"] = df["arrival_date_month"].map(MONTH_MAP)
    df["arrival_date"] = pd.to_datetime(
        dict(year=df["arrival_date_year"], month=df["month_number"], day=df["arrival_date_day_of_month"])
    )
    df["total_nights"] = df["stays_in_week_nights"] + df["stays_in_weekend_nights"]
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]
    df["has_children"] = ((df["children"] + df["babies"]) > 0).astype(int)
    df["lead_band"] = pd.cut(
        df["lead_time"], bins=[-1, 7, 30, 90, 180, 365, np.inf], labels=BANDS
    )
    df["arrival_period"] = df["arrival_date"].dt.to_period("M").astype(str)
    return df


@st.cache_resource(show_spinner=False)
def load_model():
    with open(ROOT / "model" / "hotel_cancellation_config.json", encoding="utf-8") as f:
        config = json.load(f)
    pipeline = joblib.load(ROOT / "model" / "hotel_cancellation_pipeline.joblib")
    return pipeline, config


def input_row(inputs, feature_columns):
    """Same three engineered features as the notebook."""
    weekday_nights = int(inputs["weekday_nights"])
    weekend_nights = int(inputs["stays_in_weekend_nights"])
    adults = int(inputs["adults"])
    children = int(inputs["children"])
    babies = int(inputs["babies"])
    result = dict(inputs)
    result["total_nights"] = weekday_nights + weekend_nights
    result["total_guests"] = adults + children + babies
    result["has_children"] = int(children + babies > 0)
    return pd.DataFrame([{col: result[col] for col in feature_columns}], columns=feature_columns)


def cancellation_summary(df, column, min_size=0):
    summary = df.groupby(column, observed=True)["is_canceled"].agg(
        bookings="size", rate="mean", canceled="sum"
    ).reset_index()
    summary = summary[summary["bookings"] >= min_size].copy()
    summary["rate_pct"] = summary["rate"] * 100
    return summary


def rate(df):
    return df["is_canceled"].mean() if len(df) else 0


def safe_options(df, column):
    return sorted(df[column].dropna().unique().tolist(), key=str)
