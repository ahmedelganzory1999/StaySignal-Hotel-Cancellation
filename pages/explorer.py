import pandas as pd
import streamlit as st

from utils.data import load_data, rate
from utils.ui import hero, filters, metrics, note, section

base=load_data()
df=filters(base,"explore")

hero("Data Lab / 07", "See the <em>underlying rows.</em>",
     "Explore the cleaned booking records behind the dashboard. No information has been altered for the display beyond adding derived columns.")
if df.empty:
    st.warning("No records match the current filters.")
    st.stop()
metrics(
    ("Rows in view",f"{len(df):,}","Historical bookings"),
    ("Columns",str(len(base.columns)),"Original + derived features"),
    ("Missing values",str(int(df.isna().sum().sum())),"In the cleaned and derived data"),
    ("Cancellation rate",f"{rate(df):.1%}","Bookings in current segment")
)
section("01 / DATA VIEW", "Explore individual records",
        "Select the fields you want to see. The preview is limited to 300 rows for speed.")
main_cols=["hotel","is_canceled","lead_time","arrival_date","total_nights","total_guests","adr","deposit_type","market_segment","customer_type"]
cols=st.multiselect("Columns to display",df.columns.tolist(),default=main_cols)
if not cols:
    st.info("Select at least one column to show the table.")
else:
    st.dataframe(df[cols].head(300),hide_index=True,use_container_width=True,height=460)
    st.caption(f"Showing the first {min(300,len(df)):,} of {len(df):,} filtered records.")
    st.download_button("Download filtered columns as CSV",data=df[cols].to_csv(index=False).encode("utf-8"),
                       file_name="staysignal_filtered_bookings.csv",mime="text/csv")

section("02 / QUALITY NOTES", "What was changed during cleaning?",
        "These are the decisions documented in the final project notebook.")
st.markdown("""
- Four records with missing `children` were excluded from the analytical dataset.
- Missing `country`, `agent`, and `company` values were labeled `Unknown` rather than guessed.
- Fully identical rows were not automatically deleted, because the dataset has no unique booking identifier.
- Unusual prices and zero-guest records were investigated and retained rather than being silently removed.
- Three features were created for modeling: `total_nights`, `total_guests`, and `has_children`.
""")
note("<strong>Data-source note:</strong> The 32 original columns include post-booking information that is useful for descriptive analysis but must not be fed to an advance cancellation predictor. This app's predictor uses only the 18 selected input features.")
