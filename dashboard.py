import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -----------------------------
# META APP DETAILS
# -----------------------------

APP_ID = "1544270896651729"
APP_SECRET = "38bd5e7004efa0af270e773505daefd9"

REDIRECT_URI = "https://meta-ads-command-center.streamlit.app/"

GRAPH = "https://graph.facebook.com/v19.0"

st.title("🚀 Meta Ads AI Dashboard")

# -----------------------------
# LOGIN BUTTON
# -----------------------------

login_url = (
    f"https://www.facebook.com/v19.0/dialog/oauth?"
    f"client_id={APP_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=ads_read,ads_management,business_management"
)

st.markdown(
    f"""
    <a href="{login_url}" target="_blank">
        <button style="
        background:#1877F2;
        color:white;
        padding:12px;
        border:none;
        border-radius:8px;
        font-size:16px;">
        Login with Meta
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# GET CODE FROM URL
# -----------------------------

params = st.query_params

if "code" not in params:
    st.stop()

code = params["code"]

# -----------------------------
# EXCHANGE CODE FOR TOKEN
# -----------------------------

token_response = requests.get(
    f"{GRAPH}/oauth/access_token",
    params={
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
).json()

access_token = token_response["access_token"]

st.success("Meta account connected")

# -----------------------------
# GET AD ACCOUNTS
# -----------------------------

accounts = requests.get(
    f"{GRAPH}/me/adaccounts",
    params={
        "fields": "name,account_id,currency",
        "access_token": access_token
    }
).json()

account_names = [a["name"] for a in accounts["data"]]

selected_account = st.sidebar.selectbox(
    "Select Ad Account",
    account_names
)

account_id = None
currency = "USD"

for a in accounts["data"]:
    if a["name"] == selected_account:
        account_id = a["account_id"]
        currency = a["currency"]

# -----------------------------
# DATE FILTER
# -----------------------------

date_range = st.sidebar.selectbox(
    "Date Range",
    ["today", "yesterday", "last_7d", "last_30d"]
)

level = st.sidebar.selectbox(
    "Level",
    ["campaign", "adset", "ad"]
)

# -----------------------------
# GET INSIGHTS
# -----------------------------

fields = """
campaign_name,
adset_name,
ad_name,
spend,
ctr,
cpc,
cpm,
frequency,
reach,
impressions,
clicks
"""

insights = requests.get(
    f"{GRAPH}/act_{account_id}/insights",
    params={
        "fields": fields,
        "level": level,
        "date_preset": date_range,
        "limit": 500,
        "access_token": access_token
    }
).json()

if "data" not in insights:
    st.error("No data returned")
    st.stop()

df = pd.DataFrame(insights["data"])

numeric_cols = [
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "frequency",
    "reach",
    "impressions",
    "clicks"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col])

# -----------------------------
# KPI METRICS
# -----------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Spend", f"{currency} {df.spend.sum():,.0f}")
c2.metric("Average CTR", f"{df.ctr.mean():.2f}%")
c3.metric("Average CPC", f"{currency} {df.cpc.mean():.2f}")
c4.metric("Average CPM", f"{currency} {df.cpm.mean():.2f}")

# -----------------------------
# PERFORMANCE CHART
# -----------------------------

fig = px.bar(
    df,
    x="campaign_name",
    y="spend",
    title="Campaign Spend"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------

st.subheader("Performance Data")

st.dataframe(df)
