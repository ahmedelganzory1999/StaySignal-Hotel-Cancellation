import streamlit as st
import pandas as pd

from utils.data import load_data, rate
from utils.charts import donut, line
from utils.ui import hero, metrics, section, note

base = load_data()

hero(
    "Welcome / 01",
    "Every booking leaves <em>a signal.</em>",
    "An analysis of hotel reservations, cancellations and guest behavior — with a machine learning predictor trained on historical data from two hotels in Portugal."
)
metrics(
    ("Bookings analyzed", f"{len(base):,}", "Cleaned reservation records"),
    ("Observed cancellation rate", f"{rate(base):.1%}", "Across 2015–2017"),
    ("Hotels studied", str(base.hotel.nunique()), "City Hotel + Resort Hotel"),
    ("Prediction model", "XGBoost", "22 features · threshold 0.25"),
)

section("01 / THE QUESTION", "Why do some bookings disappear?",
        "The goal is to understand the patterns behind cancellation and estimate risk using details that could be available at booking time.")
left, right = st.columns([1.05, 1], gap="large")
with left:
    outcome = pd.DataFrame({
        "Status": ["Not canceled", "Canceled"],
        "Bookings": [int((base.is_canceled == 0).sum()), int((base.is_canceled == 1).sum())]
    })
    st.plotly_chart(donut(outcome, "Status", "Bookings", "What happened to the bookings?"), use_container_width=True)
with right:
    by_hotel = base.groupby("hotel")["is_canceled"].agg(["mean", "size"])
    st.markdown("### A different story at each hotel")
    for hotel, row in by_hotel.iterrows():
        st.metric(hotel, f"{row['mean']:.1%} canceled", f"{int(row['size']):,} reservations", delta_color="off")
    note("<strong>The overall average hides an important difference.</strong> City and Resort hotels have different cancellation patterns, so comparing them separately is useful.")

section("02 / THE TIMELINE", "Cancellations across time",
        "Monthly cancellation rate for 2016, the only full calendar year in the dataset.")
year = base[base.arrival_date_year == 2016]
monthly = year.groupby("month_number", as_index=False).agg(cancellation_rate=("is_canceled", "mean"), bookings=("is_canceled", "size"))
monthly["Cancellation rate (%)"] = monthly.cancellation_rate * 100
monthly["Month"] = monthly.month_number.map({i:month[:3] for i,month in enumerate([
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
], 1)})
st.plotly_chart(line(monthly, "Month", "Cancellation rate (%)", "Monthly cancellation rate · 2016"), use_container_width=True)

section("03 / FIND YOUR WAY", "From insight to prediction")
a, b, c = st.columns(3, gap="large")
with a:
    with st.container(border=True):
        st.markdown("#### 📊 Executive Pulse")
        st.write("An overall view of booking volume and cancellation patterns.")
        st.page_link("pages/executive.py", label="Open overview", icon="📊")
with b:
    with st.container(border=True):
        st.markdown("#### 📉 Cancellation Drivers")
        st.write("Compare how customer and booking characteristics relate to cancellations.")
        st.page_link("pages/drivers.py", label="Explore drivers", icon="📉")
with c:
    with st.container(border=True):
        st.markdown("#### 🎯 Cancellation Predictor")
        st.write("Enter booking details and get an estimated cancellation score.")
        st.page_link("pages/predictor.py", label="Try predictor", icon="🎯")

note("<strong>Data note:</strong> These are historical observations from July 2015 to August 2017. They are not current hotel-market statistics, and the model has not been validated on present-day reservations.", warning=True)
