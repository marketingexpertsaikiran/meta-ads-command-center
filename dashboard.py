import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

API = "https://graph.facebook.com/v19.0"

st.title("🚀 Meta Ads AI Command Center")

# -------------------------------
# SIDEBAR LOGIN
# -------------------------------

st.sidebar.header("Connect Meta")

token = st.sidebar.text_input("Access Token")

if not token:
    st.warning("Enter Meta Access Token")
    st.stop()

# -------------------------------
# GET AD ACCOUNTS
# -------------------------------

accounts_url = f"{API}/me/adaccounts"

accounts = requests.get(accounts_url, params={
    "fields": "name,account_id,currency",
    "access_token": token
}).json()

if "data" not in accounts:
    st.error("Invalid token or missing permissions")
    st.stop()

account_names = [a["name"] for a in accounts["data"]]

selected = st.sidebar.selectbox("Ad Account", account_names)

account_id = None
currency = "USD"

for a in accounts["data"]:
    if a["name"] == selected:
        account_id = a["account_id"]
        currency = a["currency"]

# -------------------------------
# DATE RANGE
# -------------------------------

date = st.sidebar.selectbox(
    "Date Range",
    ["today", "yesterday", "last_7d", "last_30d"]
)

# -------------------------------
# FETCH INSIGHTS
# -------------------------------

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
clicks,
unique_clicks,
inline_link_clicks,
inline_link_click_ctr,
cost_per_inline_link_click,
video_p25_watched_actions,
video_p50_watched_actions,
video_p75_watched_actions,
video_p100_watched_actions,
actions
"""

url = f"{API}/act_{account_id}/insights"

response = requests.get(url, params={
    "level": "ad",
    "fields": fields,
    "date_preset": date,
    "limit": 500,
    "access_token": token
}).json()

if "data" not in response or len(response["data"]) == 0:
    st.error("No insights data for selected range")
    st.write(response)
    st.stop()

df = pd.DataFrame(response["data"])

# -------------------------------
# CLEAN DATA
# -------------------------------

numeric_cols = [
    "spend", "ctr", "cpc", "cpm", "frequency",
    "reach", "impressions", "clicks"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col])

# -------------------------------
# KPI METRICS
# -------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("Spend", f"{currency} {df.spend.sum():,.0f}")
c2.metric("CTR", f"{df.ctr.mean():.2f}%")
c3.metric("CPC", f"{currency} {df.cpc.mean():.2f}")
c4.metric("CPM", f"{currency} {df.cpm.mean():.2f}")

# -------------------------------
# SPEND CHART
# -------------------------------

st.subheader("Campaign Spend")

fig = px.bar(df, x="campaign_name", y="spend")

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# HEALTH SCORE
# -------------------------------

def health(row):

    score = 100

    if row["ctr"] < 1:
        score -= 30

    if row["cpc"] > 2:
        score -= 20

    if row["cpm"] > 20:
        score -= 20

    if row["frequency"] > 3:
        score -= 10

    return score


df["health_score"] = df.apply(health, axis=1)

st.subheader("Campaign Health")

st.dataframe(df[
    ["campaign_name", "spend", "ctr", "cpc", "cpm", "frequency", "health_score"]
])

# -------------------------------
# AI OPTIMIZATION
# -------------------------------

def ai_action(row):

    if row["ctr"] > 2.5 and row["cpc"] < 1:
        return "Scale Budget"

    if row["ctr"] < 1:
        return "Creative Issue"

    if row["cpm"] > 20:
        return "Audience Too Narrow"

    if row["frequency"] > 3:
        return "Creative Fatigue"

    return "Monitor"


df["AI_Recommendation"] = df.apply(ai_action, axis=1)

st.subheader("AI Optimization Suggestions")

st.dataframe(df[["campaign_name", "AI_Recommendation"]])

# -------------------------------
# CREATIVE FATIGUE
# -------------------------------

st.subheader("Creative Fatigue")

fatigue = df[(df.frequency > 3) & (df.ctr < 1.5)]

st.dataframe(fatigue)

# -------------------------------
# WINNING CREATIVES
# -------------------------------

st.subheader("Winning Creatives")

winners = df[(df.ctr > 2.5) & (df.cpc < 1)]

st.dataframe(winners)

# -------------------------------
# LANDING PAGE ANALYZER
# -------------------------------

st.subheader("Landing Page Issues")

df["CVR"] = df["clicks"] / df["impressions"]

lp_issue = df[(df.ctr > 2) & (df.CVR < 0.02)]

st.dataframe(lp_issue)

# -------------------------------
# TARGETING FETCH
# -------------------------------

st.subheader("Adset Targeting")

target_url = f"{API}/act_{account_id}/adsets"

target_data = requests.get(target_url, params={
    "fields": "name,targeting",
    "limit": 200,
    "access_token": token
}).json()

if "data" in target_data:

    for ad in target_data["data"][:10]:

        st.write("###", ad["name"])

        targeting = ad.get("targeting", {})

        interests = targeting.get("interests", [])

        if interests:
            for i in interests:
                st.write("•", i["name"])

# -------------------------------
# INTEREST FINDER
# -------------------------------

st.subheader("Detailed Targeting Finder")

keyword = st.text_input("Search Interest")

if keyword:

    interest_url = f"{API}/search"

    interest_data = requests.get(
        interest_url,
        params={
            "type": "adinterest",
            "q": keyword,
            "limit": 50,
            "access_token": token
        }).json()

    if "data" in interest_data:

        for i in interest_data["data"]:

            st.write(
                i["name"],
                "- Audience Size:",
                i.get("audience_size", "N/A")
            )

# -------------------------------
# AUDIENCE OVERLAP
# -------------------------------

st.subheader("Audience Overlap Detector")

audiences = {}

if "data" in target_data:

    for ad in target_data["data"]:

        ints = ad.get("targeting", {}).get("interests", [])

        audiences[ad["name"]] = [i["name"] for i in ints]

    names = list(audiences.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):

            overlap = set(audiences[names[i]]) & set(audiences[names[j]])

            if len(overlap) > 3:

                st.warning(
                    f"Audience overlap between {names[i]} and {names[j]}"
                )
