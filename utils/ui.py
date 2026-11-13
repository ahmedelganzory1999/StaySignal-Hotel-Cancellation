import html
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#090F0D; --panel:#121C17; --ink:#EFF3EB; --muted:#A8B6AD; --lime:#C9FC62; --coral:#FF8471; --line:rgba(239,243,235,.14); }
html, body, [class*="css"] {font-family:'Manrope',sans-serif;}
.stApp {background:radial-gradient(circle at 82% 6%,rgba(201,252,98,.12),transparent 30rem),radial-gradient(circle at 12% 58%,rgba(121,189,245,.045),transparent 30rem),#090F0D; color:var(--ink)}
[data-testid="stHeader"] {background:transparent}
[data-testid="stSidebar"] {background:linear-gradient(160deg,#111B16,#080D0A);border-right:1px solid var(--line)}
[data-testid="stSidebarNav"] a {border-radius:10px;margin:2px 5px;transition:all .15s}
[data-testid="stSidebarNav"] a:hover {background:rgba(201,252,98,.08)}
.block-container {max-width:1450px;padding-top:2.0rem;padding-bottom:5.5rem}
h1,h2,h3,h4 {font-family:'Fraunces',Georgia,serif !important;letter-spacing:-.025em;color:var(--ink)!important}
h1 {font-size:clamp(2.9rem,5.2vw,5.4rem)!important;line-height:1.01!important}
p,li,label {color:var(--ink)}
.stCaption,small,[data-testid="stCaptionContainer"] {color:var(--muted)}
.eyebrow {color:var(--lime);font-size:.75rem;font-weight:800;letter-spacing:.22em;text-transform:uppercase;margin-bottom:.75rem}
.hero {padding:1.2rem 0 1.8rem 0;border-bottom:1px solid var(--line);margin-bottom:1.6rem}
.hero h1 {margin:.15rem 0 1.1rem 0}
.hero h1 em {font-style:normal;color:var(--lime)}
.hero p {max-width:870px;font-size:1.04rem;line-height:1.72;color:#C3D1C6}
.metric {border:1px solid var(--line);background:linear-gradient(160deg,rgba(33,51,40,.65),rgba(18,28,23,.85));border-radius:15px;padding:1.2rem 1.25rem;min-height:144px;margin-bottom:10px}
.metric .name {font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.13em;color:#B1C0B5;margin-bottom:.8rem}
.metric .value {font-family:'Fraunces',Georgia,serif;font-size:clamp(1.6rem,2.5vw,2.6rem);color:var(--lime);line-height:1.05}
.metric .hint {color:#ACBDB1;margin-top:.65rem;font-size:.76rem}
.section {margin:2.3rem 0 .8rem;border-top:1px solid var(--line);padding-top:1.55rem}
.section .tag {font-size:.68rem;letter-spacing:.2em;font-weight:800;color:var(--lime);margin-bottom:.55rem}
.section h2 {font-size:2.05rem;margin:0 0 .5rem}
.section p {font-size:.92rem;color:#B8C6BB;max-width:860px}
.insight {border-left:3px solid var(--lime);background:rgba(201,252,98,.055);padding:1rem 1.15rem;border-radius:0 10px 10px 0;margin:1.2rem 0 1.5rem;color:#D8E5DA;line-height:1.6}
.insight.warning {border-left-color:var(--coral);background:rgba(255,132,113,.06)}
.insight strong {color:var(--ink)}
.brand {padding:.35rem 0 1.0rem}
.brand .monogram {display:inline-block;padding:.32rem .54rem;background:var(--lime);color:#09110A;border-radius:8px;font-weight:800;letter-spacing:-.04em;margin-right:7px}
.brand strong {color:var(--ink);font-weight:800;letter-spacing:-.03em;font-size:1.25rem}
.brand small {display:block;color:var(--muted);font-size:.72rem;letter-spacing:.13em;text-transform:uppercase;margin-top:.65rem}
.footer {margin-top:3.5rem;padding-top:1rem;border-top:1px solid var(--line);color:#91A399;font-size:.76rem}
[data-testid="stForm"] {border:1px solid var(--line);border-radius:17px;background:rgba(18,28,23,.6)}
div[data-testid="stButton"] button[kind="primary"],div[data-testid="stFormSubmitButton"] button {background:var(--lime);color:#0C160E;border-color:var(--lime);font-weight:800}
[data-testid="stMetric"] {background:rgba(22,35,27,.8);border:1px solid var(--line);padding:1rem;border-radius:12px}
[data-testid="stMetricValue"] {color:var(--lime)}
[data-testid="stDataFrame"] {border-radius:12px;overflow:hidden}
[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label {font-weight:600}
@media (max-width:700px) {.block-container {padding-top:1rem}.metric {min-height:122px}.hero {padding-top:.6rem}}
</style>
"""


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)


def brand():
    st.sidebar.markdown(
        '<div class="brand"><span class="monogram">S/S</span><strong>StaySignal</strong>'
        '<small>Hotel intelligence / ML lab</small></div>', unsafe_allow_html=True
    )
    st.sidebar.caption("119,386 historical hotel bookings · Portugal · 2015–2017")


def hero(tag, title, description):
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{html.escape(tag)}</div>'
        f'<h1>{title}</h1><p>{html.escape(description)}</p></div>',
        unsafe_allow_html=True
    )


def metrics(*items):
    cols = st.columns(len(items), gap="medium")
    for col, (name, value, hint) in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="metric"><div class="name">{html.escape(str(name))}</div>'
                f'<div class="value">{html.escape(str(value))}</div>'
                f'<div class="hint">{html.escape(str(hint))}</div></div>',
                unsafe_allow_html=True
            )


def section(kicker, heading, description=""):
    st.markdown(
        f'<div class="section"><div class="tag">{html.escape(kicker.upper())}</div>'
        f'<h2>{html.escape(heading)}</h2><p>{html.escape(description)}</p></div>',
        unsafe_allow_html=True
    )


def note(text, *, warning=False):
    st.markdown(f'<div class="insight{" warning" if warning else ""}">{text}</div>', unsafe_allow_html=True)


def filters(df, key, *, years=True):
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### Explore a segment")
    hotel = st.sidebar.selectbox("Hotel", ["All hotels"] + sorted(df.hotel.unique().tolist()), key=key+"_hotel")
    year = st.sidebar.selectbox("Arrival year", ["All years"] + sorted(df.arrival_date_year.unique().tolist()), key=key+"_year") if years else "All years"
    customer = st.sidebar.selectbox("Customer type", ["All types"] + sorted(df.customer_type.unique().tolist()), key=key+"_customer")
    output = df
    if hotel != "All hotels": output = output[output.hotel == hotel]
    if year != "All years": output = output[output.arrival_date_year == year]
    if customer != "All types": output = output[output.customer_type == customer]
    st.sidebar.caption(f"{len(output):,} bookings in view")
    return output


def footer():
    st.markdown(
        '<div class="footer">STAYSIGNAL / Epsilon ML Final Project · Historical data only. '
        'Relationships are descriptive, not causal. Predictions are estimates, not booking decisions.</div>',
        unsafe_allow_html=True
    )
