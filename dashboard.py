import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

APP_ID = "1544270896651729"
APP_SECRET = "38bd5e7004efa0af270e773505daefd9"
REDIRECT_URI = "https://meta-ads-command-center.streamlit.app/"

GRAPH = "https://graph.facebook.com/v19.0"

st.title("🚀 Meta Ads Command Center")

# ---------------------------------
# STEP 1 : LOGIN BUTTON
# ---------------------------------

login_url = f"https://www.facebook.com/v19.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=ads_read,ads_management,business_management"

st.markdown(
    f'<a href="{login_url}" target="_self"><button style="background:#1877F2;color:white;padding:10px;border-radius:8px;">Login with Meta</button></a>',
    unsafe_allow_html=True
)

# ---------------------------------
# STEP 2 : GET CODE FROM URL
# ---------------------------------

params = st.query_params

if "code" not in params:
    st.stop()

code = params["code"]

# ---------------------------------
# STEP 3 : EXCHANGE CODE FOR TOKEN
# ---------------------------------

token_request = requests.get(
    f"{GRAPH}/oauth/access_token",
    params={
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
).json()

access_token = token_request["access_token"]

st.success("Meta Account Connected")

# ---------------------------------
# STEP 4 : FETCH AD ACCOUNTS
# ---------------------------------

accounts = requests.get(
    f"{GRAPH}/me/adaccounts",
    params={
        "fields": "name,account_id,currency",
        "access_token": access_token
    }
).json()

account_names = [a["name"] for a in accounts["data"]]

selected_account = st.sidebar.selectbox("Ad Account", account_names)

account_id = None
currency = "USD"

for a in accounts["data"]:
    if a["name"] == selected_account:
        account_id = a["account_id"]
        currency = a["currency"]

# ---------------------------------
# STEP 5 : DATE FILTER
# ---------------------------------

date = st.sidebar.selectbox(
    "Date Range",
    ["today", "yesterday", "last_7d", "last_30d"]
)

level = st.sidebar.selectbox(
    "Level",
    ["campaign", "adset", "ad"]
)

# ---------------------------------
# STEP 6 : FETCH INSIGHTS
# ---------------------------------

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

insights = requests.get(
    f"{GRAPH}/act_{account_id}/insights",
    params={
        "fields": fields,
        "level": level,
        "date_preset": date,
        "limit": 500,
        "access_token": access_token
    }
).json()

if "data" not in insights:
    st.error("No data returned")
    st.stop()

df = pd.DataFrame(insights["data"])

numeric_cols = ["spend", "ctr", "cpc", "cpm", "frequency", "impressions", "reach", "clicks"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col])

# ---------------------------------
# STEP 7 : KPI
# ---------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("Spend", f"{currency} {df.spend.sum():,.0f}")
c2.metric("CTR", f"{df.ctr.mean():.2f}%")
c3.metric("CPC", f"{currency} {df.cpc.mean():.2f}")
c4.metric("CPM", f"{currency} {df.cpm.mean():.2f}")

# ---------------------------------
# STEP 8 : PERFORMANCE CHART
# ---------------------------------

fig = px.bar(df, x="campaign_name", y="spend")

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------
# STEP 9 : DATA TABLE
# ---------------------------------

st.dataframe(df)
