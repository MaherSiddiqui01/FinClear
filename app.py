import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from utils.email_sender import send_email
from agent.email_agent import generate_email
from agent.risk_agent import risk_score
from utils.db import save_log


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="CollectIQ AI",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.markdown("""
<style>

/* Background */
.stApp{
    background:linear-gradient(135deg,#f8fafc,#eef2ff,#fefce8);
}

/* Hide Branding */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* Global Text */
html, body, p, span, div, label{
    color:#111827 !important;
}

/* Title */
.main-title{
    font-size:42px;
    font-weight:800;
    color:#16a34a;
    text-align:center;
    margin-top:10px;
}

.sub-title{
    text-align:center;
    color:#475569;
    font-size:18px;
    margin-bottom:30px;
}

/* Cards */
.card{
    background:white;
    padding:22px;
    border-radius:22px;
    border:1px solid #e5e7eb;
    box-shadow:0 10px 25px rgba(0,0,0,0.08);
}

.metric-number{
    font-size:32px;
    font-weight:800;
}

.metric-label{
    color:#64748b;
}

/* Buttons */
.stButton>button{
    background:linear-gradient(90deg,#22c55e,#16a34a);
    color:white !important;
    border:none;
    border-radius:14px;
    padding:12px;
    font-weight:700;
    width:100%;
}

/* Upload */
section[data-testid="stFileUploader"]{
    background:white;
    border:2px dashed #16a34a;
    padding:18px;
    border-radius:18px;
}

/* Headings */
.block-title{
    font-size:26px;
    font-weight:700;
    margin-top:20px;
    margin-bottom:10px;
}

/* Email Box */
.email-box{
    background:white;
    border-left:6px solid #22c55e;
    padding:20px;
    border-radius:16px;
    box-shadow:0 8px 18px rgba(0,0,0,0.06);
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:white;
}

</style>

<div class="main-title">💸 CollectIQ AI</div>
<div class="sub-title">Smart Finance Recovery Dashboard with AI Automation</div>

""", unsafe_allow_html=True)


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.markdown(
"""
<h2 style='color:#16a34a;font-weight:800;'>📌 Navigation</h2>
""",
unsafe_allow_html=True
)

st.sidebar.info("Upload invoice CSV file")
st.sidebar.success("AI System Active")


# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------
st.markdown(
'<div class="block-title">📤 Upload Invoice CSV</div>',
unsafe_allow_html=True
)

file = st.file_uploader(
    "Choose CSV File",
    type=["csv"]
)


# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------
if file:

    df = pd.read_csv(file)

    today = datetime.today()

    df["due_date"] = pd.to_datetime(df["due_date"])
    df["days_overdue"] = (
        today - df["due_date"]
    ).dt.days

    df["risk_score"] = df.apply(
        lambda row: risk_score(
            row["days_overdue"],
            row["amount"]
        ),
        axis=1
    )

    total_invoices = len(df)
    pending_amount = df["amount"].sum()
    high_risk = len(df[df["risk_score"] > 60])

    if "status" in df.columns:
        paid_count = len(
            df[df["status"].str.lower() == "paid"]
        )
    else:
        paid_count = 0

    # ---------------------------------------------------
    # KPI
    # ---------------------------------------------------
    st.markdown(
    '<div class="block-title">📊 Dashboard Overview</div>',
    unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="card">
        <div class="metric-number">{total_invoices}</div>
        <div class="metric-label">Total Invoices</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
        <div class="metric-number">₹{pending_amount:,.0f}</div>
        <div class="metric-label">Pending Amount</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
        <div class="metric-number">{high_risk}</div>
        <div class="metric-label">High Risk Clients</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="card">
        <div class="metric-number">{paid_count}</div>
        <div class="metric-label">Paid Invoices</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------
    # CHART
    # ---------------------------------------------------
    st.markdown(
    '<div class="block-title">📈 Risk Analytics</div>',
    unsafe_allow_html=True
    )

    fig = px.bar(
        df,
        x="client_name",
        y="risk_score",
        color="risk_score",
        text="risk_score",
        color_continuous_scale="greens",
        height=450
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------------------------
    # TABLE
    # ---------------------------------------------------
    st.markdown(
    '<div class="block-title">⚡ Priority Recovery List</div>',
    unsafe_allow_html=True
    )

    priority_df = df.sort_values(
        "risk_score",
        ascending=False
    )

    st.dataframe(
        priority_df,
        use_container_width=True
    )

    # ---------------------------------------------------
    # EMAIL
    # ---------------------------------------------------
    st.markdown(
    '<div class="block-title">📧 AI Payment Reminder</div>',
    unsafe_allow_html=True
    )

    if st.button("Generate + Send Email"):

        row = priority_df.iloc[0]

        stage = 1

        if row["days_overdue"] > 15:
            stage = 2
        if row["days_overdue"] > 30:
            stage = 3
        if row["days_overdue"] > 60:
            stage = 4

        email_text = generate_email(
            row["client_name"],
            row["amount"],
            row["days_overdue"],
            stage
        )

        st.markdown(
        f"""
        <div class="email-box">
        {email_text}
        </div>
        """,
        unsafe_allow_html=True
        )

        # SEND EMAIL
        try:
            send_email(
                row["email"],
                "Payment Reminder - CollectIQ AI",
                email_text
            )

            save_log(
                row["client_name"],
                row["email"],
                row["amount"],
                "Email Sent"
            )

            st.success(
                f"Email sent to {row['email']} ✅"
            )

        except Exception as e:

            save_log(
                row["client_name"],
                row["email"],
                row["amount"],
                "Failed"
            )

            st.error(
                f"Email Failed: {str(e)}"
            )

else:
    st.info(
    "Please upload invoice CSV file to continue."
    )