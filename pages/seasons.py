import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import load_data, MONTHS
from utils.charts import finish, LIME, CORAL
from utils.ui import hero, metrics, section, note

base=load_data()
hero("Calendar / 04", "When bookings <em>change.</em>",
     "Explore arrival-season patterns, booking volume, cancellation rates and average daily rate (ADR) without treating incomplete years as complete.")

selected=st.selectbox("Choose arrival year",[2016,2015,2017],format_func=lambda y:f"{y} · {'complete year' if y==2016 else 'partial year'}")
df=base[base.arrival_date_year==selected]
metrics(
    ("Bookings",f"{len(df):,}",f"Arrivals recorded in {selected}"),
    ("Canceled",f"{int(df.is_canceled.sum()):,}","Observed booking outcomes"),
    ("Cancellation rate",f"{df.is_canceled.mean():.1%}","For months present in data"),
    ("Median ADR",f"{df.adr.median():.1f}","Dataset ADR units; not total revenue"),
)
if selected!=2016:
    note(f"<strong>{selected} is not a full calendar year.</strong> The data starts in July 2015 and ends in August 2017. Compare available months, not full-year totals.",warning=True)

section("01 / ARRIVAL CALENDAR","A year of arrivals","Check both booking volume and the percentage canceled.")
monthly=df.groupby("month_number",as_index=False).agg(bookings=("is_canceled","size"),canceled=("is_canceled","sum"),rate=("is_canceled","mean"),median_adr=("adr","median"))
monthly["Month"]=monthly.month_number.map({i:m[:3] for i,m in enumerate(MONTHS,1)})
monthly["Rate (%)"]=monthly.rate*100
left,right=st.columns(2,gap="large")
with left:
    fig=px.bar(monthly,x="Month",y="bookings",title=f"Monthly booking volume · {selected}",text="bookings",color_discrete_sequence=[LIME])
    st.plotly_chart(finish(fig),use_container_width=True)
with right:
    fig=px.line(monthly,x="Month",y="Rate (%)",markers=True,title=f"Monthly cancellation rate · {selected}",color_discrete_sequence=[CORAL])
    fig.update_traces(line_width=3,marker_size=9)
    st.plotly_chart(finish(fig,percent=True),use_container_width=True)

section("02 / PRICING","How does ADR vary?",
        "ADR is a daily-rate field. It is not the same as collected revenue or profit. Extreme values are kept visible as data-quality signals.")
valid=df[df.adr.between(0,1000)].copy()
valid["Outcome"]=valid.is_canceled.map({0:"Not canceled",1:"Canceled"})
left,right=st.columns([1.15,.85],gap="large")
with left:
    f=px.box(valid,x="hotel",y="adr",color="hotel",points=False,
             color_discrete_sequence=[LIME,CORAL],title="ADR distribution by hotel · values 0–1000")
    f.update_layout(xaxis_title="",yaxis_title="ADR (dataset units)")
    st.plotly_chart(finish(f),use_container_width=True)
with right:
    f=px.line(monthly,x="Month",y="median_adr",markers=True,title="Median ADR by arrival month",color_discrete_sequence=[LIME])
    f.update_traces(line_width=3,marker_size=9)
    f.update_layout(yaxis_title="Median ADR (dataset units)")
    st.plotly_chart(finish(f),use_container_width=True)

section("03 / ARRIVAL MIX","Different months, different hotels",
        "The heatmap compares the cancellation rate for each hotel in each available month.")
heat=df.groupby(["hotel","month_number"],as_index=False).is_canceled.mean()
heat["rate_pct"]=heat.is_canceled*100
pvt=heat.pivot(index="hotel",columns="month_number",values="rate_pct").reindex(columns=range(1,13))
pvt.columns=[m[:3] for m in MONTHS]
fig=px.imshow(pvt,labels=dict(x="Arrival month",y="Hotel",color="Cancellation rate (%)"),
              color_continuous_scale=["#26483A","#83BA77",LIME],aspect="auto",title="Cancellation rate · hotel × month")
fig.update_traces(hovertemplate="Hotel: %{y}<br>Month: %{x}<br>Rate: %{z:.1f}%<extra></extra>")
st.plotly_chart(finish(fig,height=330),use_container_width=True)
note("<strong>Interpretation:</strong> Monthly differences can reflect seasonality, guest mix and booking conditions. This dataset does not establish what caused the differences.")
