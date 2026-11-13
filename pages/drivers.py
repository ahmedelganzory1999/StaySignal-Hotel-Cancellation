import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import load_data, cancellation_summary, BANDS
from utils.charts import LIME, CORAL, finish, bar
from utils.ui import filters, hero, metrics, note, section

base = load_data()
df = filters(base, "drivers")
hero("Intelligence / 03", "Look behind the <em>cancellation.</em>",
     "Compare the patterns linked to cancellation: booking lead time, deposits, customer history and market segments.")
if df.empty:
    st.warning("No bookings match the current filters.")
    st.stop()

section("01 / BOOKING WINDOW", "How far ahead was it booked?",
        "Lead time is the number of days between booking and planned arrival.")
lead = cancellation_summary(df, "lead_band").sort_values("lead_band")
fig = bar(lead, "lead_band", "rate_pct", "Cancellation rate by booking lead time", colors=[CORAL], text="rate_pct")
fig.update_traces(texttemplate="%{text:.1f}%")
fig.update_layout(xaxis_title="Days before planned arrival", yaxis_title="Cancellation rate (%)")
st.plotly_chart(fig, use_container_width=True)
with st.expander("See booking counts for each lead-time group"):
    st.dataframe(lead[["lead_band","bookings","canceled","rate_pct"]].rename(columns={"rate_pct":"Cancellation rate (%)"}).round(1), hide_index=True, use_container_width=True)

section("02 / DEPOSIT RULES", "Does deposit type make a difference?",
        "Deposit categories may be connected to booking policies and customer decisions, so they should not be interpreted as a causal experiment.")
left,right=st.columns([1.25,.75],gap="large")
with left:
    deposit=cancellation_summary(df,"deposit_type").sort_values("rate_pct")
    fig=bar(deposit,"deposit_type","rate_pct","Cancellation rate by deposit type",horizontal=True,colors=[CORAL],text="rate_pct")
    fig.update_traces(texttemplate="%{text:.1f}%")
    fig.update_layout(xaxis_title="Cancellation rate (%)",yaxis_title="")
    st.plotly_chart(fig,use_container_width=True)
with right:
    st.markdown("### Check the denominators")
    st.dataframe(deposit[["deposit_type","bookings","rate_pct"]].rename(columns={"rate_pct":"Rate (%)"}).round(1),hide_index=True,use_container_width=True)
    note("<strong>A striking pattern is not automatically a cause.</strong> Deposits may reflect the hotel's booking conditions or a customer's original reservation type.",warning=True)

section("03 / CUSTOMER HISTORY", "Previous cancellations matter",
        "Compare bookings with any recorded previous cancellation against bookings with none.")
history=df.copy()
history["history_group"]=history.previous_cancellations.gt(0).map({True:"At least one",False:"None"})
h=cancellation_summary(history,"history_group")
fig=bar(h,"history_group","rate_pct","Cancellation by recorded previous-cancellation history",text="rate_pct",colors=[CORAL])
fig.update_traces(texttemplate="%{text:.1f}%")
fig.update_layout(xaxis_title="Previous cancellations",yaxis_title="Cancellation rate (%)")
st.plotly_chart(fig,use_container_width=True)

section("04 / MARKET SEGMENTS", "Do booking segments behave alike?",
        "Only segments with at least 100 bookings are shown in the chart to avoid overemphasizing very small groups.")
segments=cancellation_summary(df,"market_segment",min_size=100).sort_values("rate_pct")
fig=bar(segments,"market_segment","rate_pct","Cancellation rate by market segment",horizontal=True,colors=[LIME],text="rate_pct",height=450)
fig.update_traces(texttemplate="%{text:.1f}%")
fig.update_layout(xaxis_title="Cancellation rate (%)",yaxis_title="")
st.plotly_chart(fig,use_container_width=True)

section("05 / LENGTH OF STAY", "What about total nights?",
        "Longer stays may have a different mix of booking channels, prices and customer types.")
plot_data=df[(df.total_nights>=1)&(df.total_nights<=21)].copy()
plot_data["Outcome"]=plot_data.is_canceled.map({1:"Canceled",0:"Not canceled"})
fig=px.box(plot_data, x="Outcome", y="total_nights", color="Outcome", points=False,
           color_discrete_map={"Canceled":CORAL,"Not canceled":LIME},title="Length of stay by booking outcome")
fig.update_layout(yaxis_title="Total nights",xaxis_title="")
st.plotly_chart(finish(fig),use_container_width=True)
note("<strong>Analysis limitation:</strong> The data shows historical relationships, not what would happen if a hotel changed its booking policies. Also, the model does not use post-booking variables such as the final reservation status.")
