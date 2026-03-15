import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(layout="wide")

APP_ID = "1544270896651729"
APP_SECRET = "38bd5e7004efa0af270e773505daefd9"
REDIRECT_URI = "https://meta-ads-command-center.streamlit.app"

GRAPH = "https://graph.facebook.com/v19.0"

# ---------- LOGIN ----------
query = st.query_params

if "code" not in query:

    auth_url = (
        "https://www.facebook.com/v19.0/dialog/oauth?"
        + urllib.parse.urlencode(
            {
                "client_id": APP_ID,
                "redirect_uri": REDIRECT_URI,
                "scope": "ads_read,ads_management,business_management",
            }
        )
    )

    st.title("Meta Ads Command Center")

    st.markdown(
        f'<a href="{auth_url}" target="_self">'
        '<button style="padding:12px 20px;font-size:18px;">Login with Meta</button>'
        "</a>",
        unsafe_allow_html=True,
    )

    st.stop()

# ---------- EXCHANGE TOKEN ----------
code = query["code"]

token_url = "https://graph.facebook.com/v19.0/oauth/access_token"

token_res = requests.get(
    token_url,
    params={
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "client_secret": APP_SECRET,
        "code": code,
    },
)

token_json = token_res.json()

access_token = token_json.get("access_token")

# ---------- GET AD ACCOUNTS ----------
accounts_res = requests.get(
    f"{GRAPH}/me/adaccounts",
    params={
        "fields": "name,account_id,currency",
        "access_token": access_token,
    },
).json()

accounts = accounts_res.get("data", [])

account_names = [a["name"] for a in accounts]

selected_account = st.sidebar.selectbox("Ad Account", account_names)

account_id = None
currency = "USD"

for a in accounts:

    if a["name"] == selected_account:

        account_id = a["account_id"]
        currency = a["currency"]

# ---------- FILTER ----------
date_range = st.sidebar.selectbox(
    "Date Range",
    ["today", "yesterday", "last_7d", "last_30d", "last_90d"],
)

level = st.sidebar.selectbox(
    "Level",
    ["campaign", "adset", "ad"],
)

# ---------- INSIGHTS ----------
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
clicks,
actions
"""

data = requests.get(
    f"{GRAPH}/act_{account_id}/insights",
    params={
        "fields": fields,
        "level": level,
        "date_preset": date_range,
        "limit": 500,
        "access_token": access_token,
    },
).json()

df = pd.DataFrame(data.get("data", []))

if df.empty:
    st.warning("No data")
    st.stop()

# ---------- NUMERIC ----------
for col in ["spend", "ctr", "cpc", "cpm", "impressions", "clicks", "frequency"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col])

# ---------- CONVERSIONS ----------
def get_conv(actions):

    if not actions:
        return 0

    for a in actions:

        if a["action_type"] == "purchase":
            return float(a["value"])

    return 0

df["conversions"] = df["actions"].apply(get_conv)

df["CPA"] = df["spend"] / df["conversions"].replace(0, 1)

# ---------- KPI ----------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Spend", f"{currency} {df['spend'].sum():,.0f}")
c2.metric("Conversions", int(df["conversions"].sum()))
c3.metric("CTR", f"{df['ctr'].mean():.2f}%")
c4.metric("CPA", f"{currency} {df['CPA'].mean():.2f}")

# ---------- CHART ----------
fig = px.bar(df, x="campaign_name", y="spend", title="Campaign Spend")

st.plotly_chart(fig, use_container_width=True)

# ---------- CUSTOM METRICS ----------
metrics = [
    "campaign_name",
    "spend",
    "impressions",
    "clicks",
    "ctr",
    "cpc",
    "cpm",
    "frequency",
    "conversions",
    "CPA",
]

selected = st.sidebar.multiselect("Columns", metrics, default=metrics)

st.dataframe(df[selected])
