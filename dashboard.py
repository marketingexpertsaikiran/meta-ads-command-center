import streamlit as st
import plotly.express as px
from auth import login, get_accounts, save_account
from meta_api import get_insights, get_targeting, search_interests
from ai_engine import *

st.set_page_config(layout="wide")

st.title("Meta Ads AI Command Center")

login()

if "user" not in st.session_state:
    st.stop()

st.sidebar.header("Connect Ad Account")

account_id = st.sidebar.text_input("Ad Account ID")
token = st.sidebar.text_input("Access Token")

if st.sidebar.button("Save Account"):
    save_account(account_id, token)

accounts = get_accounts()

account = st.sidebar.selectbox(
    "Select Account",
    accounts
)

date = st.sidebar.selectbox(
    "Date Range",
    ["today", "yesterday", "last_7d", "last_30d"]
)

df = get_insights(account["account_id"], account["token"], date)

st.header("Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Spend", df["spend"].sum())
c2.metric("CTR", df["ctr"].mean())
c3.metric("CPC", df["cpc"].mean())
c4.metric("CPM", df["cpm"].mean())

fig = px.bar(df, x="campaign_name", y="spend")

st.plotly_chart(fig, use_container_width=True)

st.header("Campaign Health")

df["health"] = df.apply(health_score, axis=1)

st.dataframe(df)

st.header("Scaling Engine")

df["AI_action"] = df.apply(scaling_engine, axis=1)

st.dataframe(df[["campaign_name", "AI_action"]])

st.header("Creative Winners")

st.dataframe(creative_winner(df))

st.header("Creative Fatigue")

st.dataframe(creative_fatigue(df))

st.header("CPA Alerts")

st.dataframe(cpa_alert(df))

st.header("Targeting Explorer")

targeting = get_targeting(account["account_id"], account["token"])

for ad in targeting[:10]:

    interests = ad["targeting"].get("interests", [])

    if interests:

        st.write(ad["name"])

        for i in interests:

            st.write("•", i["name"])

st.header("Interest Finder")

keyword = st.text_input("Search Interest")

if keyword:

    interests = search_interests(keyword, account["token"])

    for i in interests:

        st.write(i["name"], i["audience_size"])
