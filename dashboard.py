import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ----------------------------
# META APP SETTINGS
# ----------------------------

APP_ID = "1544270896651729"
APP_SECRET = "38bd5e7004efa0af270e773505daefd9"

REDIRECT_URI = "https://meta-ads-command-center.streamlit.app/"

GRAPH = "https://graph.facebook.com/v19.0"

st.title("🚀 Meta Ads Command Center")

# ----------------------------
# LOGIN BUTTON
# ----------------------------

login_url = (
    f"https://www.facebook.com/v19.0/dialog/oauth?"
    f"client_id={APP_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=ads_read,ads_management,business_management"
)

st.markdown(
    f"""
    <a href="{login_url}" target="_self">
        <button style="
        background:#1877F2;
        color:white;
        padding:12px 20px;
        border:none;
        border-radius:8px;
        font-size:16px;
        cursor:pointer;">
        Login with Meta
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# GET AUTH CODE
# ----------------------------

params = st.query_params

if "code" not in params:
    st.stop()

code = params["code"]

# ----------------------------
# EXCHANGE CODE FOR TOKEN
# ----------------------------

token_response = requests.get(
    f"{GRAPH}/oauth/access_token",
    params={
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
).json()

# Debug in case of failure
if "access_token" not in token_response:

    st.error("OAuth Login Failed")

    st.write("Meta Response:", token_response)

    st.stop()

access_token = token_response["access_token"]

st.success("Meta Account Connected")

# ----------------------------
# FETCH AD ACCOUNTS
# ----------------------------

accounts_response = requests.get(
    f"{GRAPH}/me/adaccounts",
    params={
        "fields": "name,account_id,currency",
        "access_token": access_token
    }
).json()

if "data" not in accounts_response:

    st.error("Could not fetch ad accounts")

    st.write(accounts_response)

    st.stop()

accounts = accounts_response["data"]

account_names = [a["name"] for a in accounts]

selected_account = st.sidebar.selectbox(
    "Select Ad Account",
    account_names
)

account_id = None
currency = "USD"

for a in accounts:
    if a["name"] == selected_account:
        account_id = a["account_id"]
        currency = a["currency"]

# ----------------------------
# FILTERS
# ----------------------------

date_range = st.sidebar.selectbox(
    "Date Range",
    ["today", "yesterday", "last_7d", "last_30d"]
)

level = st.sidebar.selectbox(
    "Data Level",
    ["campaign", "adset", "ad"]
)

# ----------------------------
# FETCH INSIGHTS
# ----------------------------

fields = """
campaign_name,
adset_name,
ad_name,
spend,
ctr,
cpc,
cpm,
frequency,
impressions,
reach,
clicks
"""

insights_response = requests.get(
    f"{GRAPH}/act_{account_id}/insights",
    params={
        "fields": fields,
        "level": level,
        "date_preset": date_range,
        "limit": 500,
        "access_token": access_token
    }
).json()

if "data" not in insights_response:

    st.error("Insights API failed")

    st.write(insights_response)

    st.stop()

df = pd.DataFrame(insights_response["data"])

# ----------------------------
# NUMERIC CONVERSION
# ----------------------------

numeric_cols = [
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "frequency",
    "impressions",
    "reach",
    "clicks"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col])

# ----------------------------
# KPI METRICS
# ----------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Spend", f"{currency} {df.spend.sum():,.0f}")
c2.metric("Avg CTR", f"{df.ctr.mean():.2f}%")
c3.metric("Avg CPC", f"{currency} {df.cpc.mean():.2f}")
c4.metric("Avg CPM", f"{currency} {df.cpm.mean():.2f}")

# ----------------------------
# PERFORMANCE CHART
# ----------------------------

if "campaign_name" in df.columns:

    fig = px.bar(
        df,
        x="campaign_name",
        y="spend",
        title="Campaign Spend"
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# DATA TABLE
# ----------------------------

st.subheader("Performance Data")

st.dataframe(df)
