import calendar

import pandas as pd
import streamlit as st

from utils.data import load_data, load_model, input_row, MONTHS, MONTH_MAP, BANDS
from utils.ui import hero, note, section

base = load_data()
model, config = load_model()

hero(
    "Machine Learning / 05",
    "Estimate the <em>cancellation signal.</em>",
    "Enter a reservation's details. The saved XGBoost pipeline will apply the same preprocessing used in the notebook and estimate the likelihood of cancellation."
)
note(
    "<strong>Before you try it:</strong> This model was trained on bookings from 2015–2017 in Portugal. "
    "Its scores are not calibrated probabilities, and predictions should not be used as automatic booking decisions. "
    "Parking and special-request fields must be verified as known at the time of booking.",
    warning=True
)


def choices(name):
    return sorted(base[name].astype(str).unique().tolist())


def default_position(options, prefer):
    return options.index(prefer) if prefer in options else 0


with st.form("booking_input", border=True):
    st.markdown("### 01 / Stay details")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        hotel = st.selectbox("Hotel type", choices("hotel"))
        month = st.selectbox("Arrival month", MONTHS, index=6)
        day = st.number_input("Arrival day of month", min_value=1, max_value=31, value=15, step=1)
    with c2:
        lead_time = st.number_input("Days booked in advance", min_value=0, max_value=737, value=60, step=1)
        weekday_nights = st.number_input("Weekday nights", min_value=0, max_value=45, value=3, step=1)
        weekend_nights = st.number_input("Weekend nights", min_value=0, max_value=25, value=2, step=1)
    with c3:
        adr = st.number_input("ADR · average daily rate (dataset units)", min_value=0.0, max_value=5400.0, value=105.0, step=5.0)
        room = st.selectbox("Reserved room type", choices("reserved_room_type"))
        meal = st.selectbox("Meal plan", choices("meal"), index=default_position(choices("meal"), "BB"))

    st.markdown("### 02 / Guests & booking conditions")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        adults = st.number_input("Adults", min_value=1, max_value=15, value=2, step=1)
        children = st.number_input("Children", min_value=0, max_value=10, value=0, step=1)
        babies = st.number_input("Babies", min_value=0, max_value=10, value=0, step=1)
    with c2:
        segment = st.selectbox("Market segment", choices("market_segment"), index=default_position(choices("market_segment"), "Online TA"))
        channel = st.selectbox("Distribution channel", choices("distribution_channel"), index=default_position(choices("distribution_channel"), "TA/TO"))
    with c3:
        deposit = st.selectbox("Deposit type", choices("deposit_type"), index=default_position(choices("deposit_type"), "No Deposit"))
        customer = st.selectbox("Customer type", choices("customer_type"), index=default_position(choices("customer_type"), "Transient"))

    st.markdown("### 03 / Origin and booking requests")
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        country_options = choices("country")
        country = st.selectbox("Guest country code", country_options,
                               index=default_position(country_options, "PRT"))
    with c2:
        agent_options = base["agent"].astype(str).value_counts().index.tolist()
        agent = st.selectbox("Travel agency ID", agent_options,
                             index=default_position(agent_options, "Unknown"))
    with c3:
        special_requests = st.number_input("Special requests", min_value=0, max_value=5, value=0, step=1)
    with c4:
        parking = st.number_input("Parking spaces requested", min_value=0, max_value=8, value=0, step=1)

    st.caption("Use 'Unknown' if the agency is not recorded. Country, agency and requests should reflect what is known at booking time.")
    st.markdown("### 04 / Previous booking history")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        repeated = st.selectbox("Repeated guest?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    with c2:
        previous_cancel = st.number_input("Previous canceled bookings", min_value=0, max_value=26, value=0, step=1)
    with c3:
        previous_completed = st.number_input("Previous bookings not canceled", min_value=0, max_value=72, value=0, step=1)
    st.write("")
    submitted = st.form_submit_button("Estimate cancellation risk", use_container_width=True, type="primary")

if submitted:
    last_day = calendar.monthrange(2016, MONTH_MAP[month])[1]
    if int(day) > last_day:
        st.error(f"{month} has at most {last_day} days. Change the arrival day and try again.")
    elif weekday_nights + weekend_nights == 0:
        st.error("Enter at least one night for the reservation.")
    else:
        values = {
            "hotel": hotel,
            "lead_time": int(lead_time),
            "arrival_date_month": month,
            "arrival_date_day_of_month": int(day),
            "stays_in_weekend_nights": int(weekend_nights),
            "weekday_nights": int(weekday_nights),
            "adults": int(adults), "children": int(children), "babies": int(babies),
            "meal": meal, "market_segment": segment, "distribution_channel": channel,
            "is_repeated_guest": int(repeated),
            "previous_cancellations": int(previous_cancel),
            "previous_bookings_not_canceled": int(previous_completed),
            "reserved_room_type": room, "deposit_type": deposit,
            "customer_type": customer, "adr": float(adr),
            "country": country, "agent": agent,
            "total_of_special_requests": int(special_requests),
            "required_car_parking_spaces": int(parking),
        }
        try:
            row = input_row(values, config["feature_columns"])
            probability = float(model.predict_proba(row)[0, 1])
            flagged = probability >= config["decision_threshold"]
        except Exception as exc:
            st.error("The model could not make a prediction with these inputs.")
            st.exception(exc)
            st.stop()

        section("05 / RESULT", "Your booking's estimated signal")
        left, right = st.columns([1.15, 1], gap="large")
        with left:
            st.metric("Model cancellation score", f"{probability:.1%}")
            st.progress(max(0.0, min(1.0, probability)))
            if flagged:
                st.warning(f"**Flagged by the model** — score is at or above the selected {config['decision_threshold']:.0%} threshold.")
            else:
                st.success(f"**Not flagged by the model** — score is below the selected {config['decision_threshold']:.0%} threshold.")
            st.caption(f"The {config['decision_threshold']:.0%} threshold was selected using validation F1-score. It is not the hotel's recommended intervention threshold.")
        with right:
            st.markdown("### Input summary")
            st.write(f"**{hotel}** · {month} {day} · {weekday_nights+weekend_nights} nights · {adults+children+babies} guests")
            st.write(f"**{lead_time}** days booked ahead · **{deposit}** deposit policy")
            st.write(f"**{segment}** market segment · **{customer}** customer")
            st.caption("The final prediction uses the updated 22 input columns, including agency, country and booking requests.")

        similar = base[(base.hotel == hotel) & (base.market_segment == segment)].copy()
        bins = [-1, 7, 30, 90, 180, 365, float('inf')]
        this_bin = pd.cut(pd.Series([lead_time]), bins=bins, labels=BANDS).iloc[0]
        similar = similar[similar.lead_band == this_bin]
        if len(similar) >= 100:
            section("06 / HISTORICAL CONTEXT", "What happened in comparable records?",
                    "This is an observed group average, not a prediction for the individual booking.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Similar historic bookings", f"{len(similar):,}")
            c2.metric("Observed group cancellation rate", f"{similar.is_canceled.mean():.1%}")
            c3.metric("Current model score", f"{probability:.1%}")
            st.caption("Comparison filters: same hotel, market segment, and lead-time band. The historical comparison also includes records used in model development and should not be used to validate model accuracy.")
        else:
            st.caption("There are too few comparable historical records to show a stable group average.")
        note("<strong>Important:</strong> A higher score does not prove a guest will cancel. The improved model had "
             f"{config['test_scores']['Precision']:.1%} precision and {config['test_scores']['Recall']:.1%} recall "
             "on the historical test period. Because this period was already examined in previous project versions, "
             "the figures are exploratory rather than a new unbiased test.", warning=True)
else:
    st.caption("Enter the booking details above and submit the form to see the model output.")
