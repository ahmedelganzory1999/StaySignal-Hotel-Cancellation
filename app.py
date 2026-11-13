import streamlit as st

from utils.ui import apply_style, brand, footer

st.set_page_config(
    page_title="StaySignal | Hotel Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_style()
brand()

pages = {
    "OVERVIEW": [
        st.Page("pages/home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/executive.py", title="Executive Pulse", icon="📊"),
    ],
    "INTELLIGENCE": [
        st.Page("pages/drivers.py", title="Cancellation Drivers", icon="📉"),
        st.Page("pages/seasons.py", title="Seasonality & Pricing", icon="🗓️"),
    ],
    "MACHINE LEARNING": [
        st.Page("pages/predictor.py", title="Cancellation Predictor", icon="🎯"),
        st.Page("pages/model.py", title="Model Performance", icon="🧠"),
    ],
    "DATA LAB": [
        st.Page("pages/explorer.py", title="Data Explorer", icon="🔎"),
    ],
}

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
footer()
