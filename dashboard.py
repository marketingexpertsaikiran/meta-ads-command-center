import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

GRAPH = "https://graph.facebook.com/v19.0"

APP_ID = "1544270896651729"
APP_SECRET = "38bd5e7004efa0af270e773505daefd9"

REDIRECT_URI = "https://meta-ads-command-center.streamlit.app/"

st.title("🚀 Meta Ads Command Center")

# ------------------------------------------------
# LOGIN BUTTON
# ------------------------------------------------

login_url = (
    f"https://www.facebook.com/v19.0/dialog/oauth?"
    f"client_id={APP_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    "&scope=ads_read,ads_management,business_management"
)

st.link_button("Login with Meta", login_url)

# ------------------------------------------------
# GET ACCESS TOKEN
# ------------------------------------------------

params = st.query_params

if "access_token" not in st.session_state:

    if "code" not in params:
        st.info("Login with Meta to continue")
        st.stop()

    code = params["code"]

    token_response = requests.get(
        f"{GRAPH}/oauth/access_token",
        params={
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code
        }
    ).json()

    if "access_token" not in token_response:
        st.error("OAuth Login Failed")
        st.write(token_response)
        st.stop()

    st.session_state.access_token = token_response["access_token"]

access_token = st.session_state.access_token

st.success("Meta Login Successful")

# ------------------------------------------------
# FETCH AD ACCOUNTS
# ------------------------------------------------

accounts_response = requests.get(
    f"{GRAPH}/me/adaccounts",
    params={
        "fields": "name,account_id,currency",
        "access_token": access_token
    }
).json()

if "data" not in accounts_response:
    st.error("Unable to fetch ad accounts")
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

# ------------------------------------------------
# FILTERS
# ------------------------------------------------

date_range = st.sidebar.selectbox(
    "Date Range",
    ["today","yesterday","last_7d","last_30d"]
)

level = st.sidebar.selectbox(
    "Data Level",
    ["campaign","adset","ad"]
)

# ------------------------------------------------
# FETCH INSIGHTS
# ------------------------------------------------

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
    st.error("Insights API Error")
    st.write(insights_response)
    st.stop()

df = pd.DataFrame(insights_response["data"])

# ------------------------------------------------
# HANDLE EMPTY DATA
# ------------------------------------------------

if df.empty:
    st.warning("No campaign data found")
    st.stop()

# ------------------------------------------------
# NUMERIC CONVERSION
# ------------------------------------------------

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

# ------------------------------------------------
# KPI METRICS
# ------------------------------------------------

if "spend" not in df.columns:
    df["spend"] = 0

if "ctr" not in df.columns:
    df["ctr"] = 0

if "cpc" not in df.columns:
    df["cpc"] = 0

if "cpm" not in df.columns:
    df["cpm"] = 0

c1,c2,c3,c4 = st.columns(4)

c1.metric("Total Spend",f"{currency} {df['spend'].sum():,.0f}")
c2.metric("Average CTR",f"{df['ctr'].mean():.2f}%")
c3.metric("Average CPC",f"{currency} {df['cpc'].mean():.2f}")
c4.metric("Average CPM",f"{currency} {df['cpm'].mean():.2f}")

# ------------------------------------------------
# CHART
# ------------------------------------------------

if "campaign_name" in df.columns:

    fig = px.bar(
        df,
        x="campaign_name",
        y="spend",
        title="Campaign Spend"
    )

    st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------
# AI PERFORMANCE ANALYSIS
# ------------------------------------------------

def analyze(row):

    ctr = row["ctr"]
    cpc = row["cpc"]
    cpm = row["cpm"]

    if ctr < 1:
        return "⚠️ Creative Issue"

    if cpc > 2:
        return "⚠️ Audience Targeting Issue"

    if cpm > 20:
        return "⚠️ High CPM"

    return "✅ Healthy Campaign"

df["AI Insight"] = df.apply(analyze,axis=1)

# ------------------------------------------------
# PERFORMANCE TABLE
# ------------------------------------------------

st.subheader("Campaign Performance")

st.dataframe(df,use_container_width=True)
