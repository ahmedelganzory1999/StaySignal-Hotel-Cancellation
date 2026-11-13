import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from utils.data import load_data, load_model
from utils.charts import finish, LIME, CORAL
from utils.ui import hero, metrics, note, section

model, config = load_model()
base = load_data()

hero("Model Lab / 06", "Measure what the model <em>misses.</em>",
     "The improved classifier was compared with earlier versions on later-arriving bookings. The same test period had already been inspected in earlier experiments.")

@st.cache_data(show_spinner=False)
def evaluate_test():
    test = base[base.arrival_date >= pd.Timestamp(config["train_split_date"])].copy()
    actual = test["is_canceled"].astype(int)
    probabilities = model.predict_proba(test[config["feature_columns"]])[:, 1]
    predicted = (probabilities >= float(config["decision_threshold"])).astype(int)
    scores = {
        "Accuracy": accuracy_score(actual, predicted),
        "Precision": precision_score(actual, predicted, zero_division=0),
        "Recall": recall_score(actual, predicted, zero_division=0),
        "F1": f1_score(actual, predicted, zero_division=0),
    }
    matrix = confusion_matrix(actual, predicted, labels=[0,1])
    breakdown = pd.DataFrame({"Hotel":test.hotel.to_numpy(),"Actual":actual.to_numpy(),"Predicted":predicted})
    return len(test), scores, matrix, breakdown

count, scores, matrix, breakdown = evaluate_test()
metrics(
    ("Test accuracy", f"{scores['Accuracy']:.1%}", "All correctly classified bookings"),
    ("Precision", f"{scores['Precision']:.1%}", "Of the flagged bookings, canceled"),
    ("Recall", f"{scores['Recall']:.1%}", "Of cancellations, detected"),
    ("F1-score", f"{scores['F1']:.3f}", "Balances precision and recall"),
)

section("01 / CONFUSION MATRIX", "What did we get right and wrong?",
        f"Results from {count:,} reservations arriving from 22 April to 31 August 2017, using the {config['decision_threshold']:.0%} threshold.")
left, right = st.columns([1.1,.9], gap="large")
with left:
    fig=px.imshow(matrix,x=["Predicted not canceled","Predicted canceled"],
                  y=["Actually not canceled","Actually canceled"],
                  text_auto=",d", color_continuous_scale=["#254437","#61956B",LIME],
                  title="Final test confusion matrix",aspect="auto")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(finish(fig,height=410),use_container_width=True)
with right:
    tn,fp,fn,tp=matrix.ravel()
    st.markdown("### Four possible outcomes")
    st.write(f"**{tp:,}** canceled bookings correctly flagged")
    st.write(f"**{fn:,}** cancellations missed")
    st.write(f"**{fp:,}** false cancellation alarms")
    st.write(f"**{tn:,}** not-canceled bookings correctly identified")
    note("<strong>Trade-off:</strong> Detecting more cancellations came with more false alarms. The model is useful for illustrating the ML workflow, not automatically rejecting bookings.",warning=True)

section("02 / IMPROVEMENT", "Did the revised model do better?",
        "A comparison on the same test period. Because we already saw this period during development, these scores are exploratory.")
comparison=pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1"],
    "Original model": [config["old_test_scores"][k] for k in ["Accuracy", "Precision", "Recall", "F1"]],
    "Improved model": [scores[k] for k in ["Accuracy", "Precision", "Recall", "F1"]],
})
fig=px.bar(comparison.melt(id_vars="Metric",var_name="Model",value_name="Score"),
           x="Metric",y="Score",color="Model",barmode="group",
           title="Original versus improved test-period scores",
           color_discrete_sequence=[CORAL,LIME])
fig.update_layout(yaxis_range=[0,1])
st.plotly_chart(finish(fig,height=390),use_container_width=True)
st.write("The revised model includes travel agency, guest country, special requests and parking spaces. "
         "The model and threshold were chosen using an earlier validation period. "
         "These improvements should be verified on reservations from a truly new period.")

section("03 / PERFORMANCE BY HOTEL", "Does one hotel get better results?",
        "A combined model score can hide differences between hotels.")
rows=[]
for name,part in breakdown.groupby("Hotel"):
    rows.append({"Hotel":name,"Bookings":len(part),"Precision":precision_score(part.Actual,part.Predicted,zero_division=0),
                 "Recall":recall_score(part.Actual,part.Predicted,zero_division=0),
                 "F1":f1_score(part.Actual,part.Predicted,zero_division=0)})
results=pd.DataFrame(rows)
st.dataframe(results.style.format({"Precision":"{:.1%}","Recall":"{:.1%}","F1":"{:.3f}"}),hide_index=True,use_container_width=True)

section("04 / THE INPUTS", "What does the model actually know?",
        "A single pipeline contains StandardScaler, OneHotEncoder and the revised XGBoost classifier.")
with st.expander(f"See the {len(config['feature_columns'])} model input features"):
    st.write(", ".join(f"`{name}`" for name in config["feature_columns"]))
with st.expander("Columns intentionally excluded"):
    st.write("`reservation_status`, `reservation_status_date`, `assigned_room_type`, `booking_changes`, `days_in_waiting_list`, and other columns not selected for modeling.")

note("<strong>Limits:</strong> The dataset covers two hotels in Portugal from 2015–2017. Splitting by arrival date is not identical to splitting by reservation creation date. The probabilities are not calibrated. Parking and special requests need booking-time verification. The test period has been reused, so scores should not be treated as fresh evidence of real-world performance.",warning=True)
