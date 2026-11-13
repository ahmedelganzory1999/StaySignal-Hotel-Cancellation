import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import load_data, rate, cancellation_summary
from utils.charts import LIME, CORAL, finish, bar
from utils.ui import filters, hero, metrics, note, section

base = load_data()
df = filters(base, "ex")

hero("Operations / 02", "The booking <em>pulse.</em>",
     "Track booking activity, cancellations, hotel differences and customer composition. Use sidebar filters to focus on one segment.")
if df.empty:
    st.warning("No bookings match the current filters.")
    st.stop()

metrics(
    ("Bookings", f"{len(df):,}", "Historical records in view"),
    ("Canceled", f"{int(df.is_canceled.sum()):,}", "Observed outcomes"),
    ("Cancellation rate", f"{rate(df):.1%}", "Canceled / total bookings"),
    ("Median lead time", f"{df.lead_time.median():.0f} days", "From reservation to arrival"),
)

section("01 / VOLUME & OUTCOME", "Where are cancellations concentrated?",
        "Compare the number of bookings and the cancellation percentage instead of relying on one measure alone.")
left, right = st.columns(2, gap="large")
with left:
    by_hotel = cancellation_summary(df, "hotel").sort_values("bookings")
    fig = bar(by_hotel, "hotel", "bookings", "Booking volume by hotel", horizontal=True, text="bookings")
    fig.update_layout(xaxis_title="Bookings", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = bar(by_hotel, "hotel", "rate_pct", "Cancellation rate by hotel", horizontal=True, colors=[CORAL], text="rate_pct")
    fig.update_traces(texttemplate="%{text:.1f}%")
    fig.update_layout(xaxis_title="Cancellation rate (%)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

section("02 / THE CUSTOMER MIX", "Who is making the bookings?",
        "Different customer types may have different cancellation patterns. Small groups should be interpreted carefully.")
cust = cancellation_summary(df, "customer_type").sort_values("bookings", ascending=False)
left, right = st.columns([1,1], gap="large")
with left:
    fig = px.bar(cust, x="customer_type", y="bookings", title="Bookings by customer type", color_discrete_sequence=[LIME], text="bookings")
    st.plotly_chart(finish(fig), use_container_width=True)
with right:
    fig = px.bar(cust, x="customer_type", y="rate_pct", title="Cancellation rate by customer type", color_discrete_sequence=[CORAL], text="rate_pct")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(finish(fig,percent=True), use_container_width=True)

section("03 / CHANNELS", "Where did bookings come from?",
        "Channel differences are associations in the historical records, not proof that a channel causes cancellations.")
channel = cancellation_summary(df, "distribution_channel", min_size=10).sort_values("bookings",ascending=False)
fig = px.scatter(channel, x="bookings", y="rate_pct", size="bookings", color="distribution_channel", hover_name="distribution_channel",
                 size_max=52, color_discrete_sequence=[LIME,CORAL,"#79BDF5","#80D4B8"], title="Channel size vs cancellation rate")
fig.update_layout(xaxis_title="Bookings",yaxis_title="Cancellation rate (%)")
st.plotly_chart(finish(fig,height=440,percent=True),use_container_width=True)

note("<strong>Reading the dashboard:</strong> Some small booking groups have extreme rates. Always look at group size before acting on the percentage.")
