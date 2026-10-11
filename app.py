import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Loan Approval Analytics", layout="wide")

st.title("Loan Approval Analysis Dashboard")
st.write("CA4 Capstone Project | Business Analytics")

file = st.file_uploader("Upload your loan dataset (CSV)", type=["csv"])

if file is None:
    st.info("Upload your original CSV dataset to view the dashboard.")
    st.stop()

data = pd.read_csv(file)
data.columns = data.columns.str.strip().str.lower()

required = [
    "loan_status", "occupation_status", "product_type",
    "loan_intent", "annual_income", "credit_score",
    "loan_amount", "current_debt"
]

missing = [c for c in required if c not in data.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

data = data.drop_duplicates()

st.sidebar.header("Dashboard Filters")

occupations = sorted(data["occupation_status"].dropna().unique())
selected_occupations = st.sidebar.multiselect(
    "Occupation", occupations, default=occupations
)

products = sorted(data["product_type"].dropna().unique())
selected_products = st.sidebar.multiselect(
    "Product type", products, default=products
)

intents = sorted(data["loan_intent"].dropna().unique())
selected_intents = st.sidebar.multiselect(
    "Loan intent", intents, default=intents
)

filtered = data[
    data["occupation_status"].isin(selected_occupations)
    & data["product_type"].isin(selected_products)
    & data["loan_intent"].isin(selected_intents)
]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

total = len(filtered)
status1 = (filtered["loan_status"] == 1).sum()
status0 = (filtered["loan_status"] == 0).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Applications", f"{total:,}")
c2.metric("Status 1", f"{status1:,}")
c3.metric("Status 0", f"{status0:,}")
c4.metric("Status 1 (%)", f"{status1 / total * 100:.2f}%")

st.caption(
    "Status labels are kept as 0 and 1 until their meanings are verified."
)

left, right = st.columns(2)

with left:
    counts = filtered["loan_status"].value_counts().sort_index()
    chart_df = counts.rename_axis("Loan Status").reset_index(name="Applications")
    fig = px.bar(
        chart_df, x="Loan Status", y="Applications",
        title="Applications by Loan Status"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.histogram(
        filtered, x="credit_score", color="loan_status",
        barmode="overlay", title="Credit Score Distribution by Status"
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    summary = filtered.groupby("occupation_status")["loan_status"].mean()
    summary = (summary * 100).reset_index(name="Average Status Code (%)")
    fig = px.bar(
        summary, x="occupation_status", y="Average Status Code (%)",
        title="Average Status Code by Occupation"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    summary = filtered.groupby("loan_intent")["loan_status"].mean()
    summary = (summary * 100).reset_index(name="Average Status Code (%)")
    fig = px.bar(
        summary, x="loan_intent", y="Average Status Code (%)",
        title="Average Status Code by Loan Intent"
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Financial Summary")
st.dataframe(
    filtered[
        ["annual_income", "credit_score", "current_debt", "loan_amount"]
    ].describe().round(2),
    use_container_width=True
)

st.subheader("Business interpretation")
st.write(
    "Use the charts to compare application patterns across customer groups. "
    "Confirm the meaning of loan_status codes before interpreting them as "
    "approval or rejection. Associations do not prove causation."
)

st.subheader("Data Preview")
st.dataframe(filtered.head(100), use_container_width=True)
