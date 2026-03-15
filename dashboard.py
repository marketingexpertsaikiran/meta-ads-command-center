import streamlit as st
import pandas as pd
import plotly.express as px

from meta_api import get_ad_accounts,get_insights,get_targeting
from ai_engine import campaign_audit,scaling_signal
from targeting_engine import extract_targeting
from competitor_ads import competitor_ads

st.set_page_config(layout="wide")

st.title("🚀 Meta Ads Command Center")

token = st.text_input("EAAV8gZAY7XdEBQyFCCnJ6zjfEoWFgonqtoPjNkqRCfNAncoswVb4E4R4Nsi0IoqZBIwvYNAhu9Bb8Yh1ZCJdf39twrgW4ha6LZCx5DJA15ZCJXkonU5tZC9hcBOgVdEmZCW6MELvFaU9dy5p7qWtDZA19i0ixqFOYZANNZB2eNLggFJvaf9hErKvNW4EUDZBKJW2ncqZA9bvmpaShyN56UTrGRNr0tZBnFiS0nPfFH95L")

if token == "":
    st.stop()

accounts = get_ad_accounts(token)

account_names = [a["name"] for a in accounts]

selected = st.sidebar.selectbox("Select Ad Account",account_names)

account_id = None
currency = "USD"

for a in accounts:

    if a["name"] == selected:
        account_id = a["account_id"]
        currency = a["currency"]

date = st.sidebar.selectbox(
"Date Range",
["today","yesterday","last_7d","last_30d"]
)

level = st.sidebar.selectbox(
"Data Level",
["campaign","adset","ad"]
)

df = get_insights(account_id,token,level,date)

if df.empty:
    st.warning("No Data Found")
    st.stop()

for col in ["spend","ctr","cpc","cpm","frequency","clicks"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col])

def conversions(actions):

    if actions is None:
        return 0

    for a in actions:
        if a["action_type"] == "purchase":
            return float(a["value"])

    return 0

df["conversions"] = df["actions"].apply(conversions)

df["CPA"] = df["spend"] / df["conversions"]

df["AI Audit"] = df.apply(campaign_audit,axis=1)

df["Scaling Signal"] = df.apply(scaling_signal,axis=1)

c1,c2,c3,c4 = st.columns(4)

c1.metric("Spend",round(df["spend"].sum(),2))
c2.metric("Conversions",int(df["conversions"].sum()))
c3.metric("Avg CTR",round(df["ctr"].mean(),2))
c4.metric("Avg CPA",round(df["CPA"].mean(),2))

fig = px.bar(df,x="campaign_name",y="spend")

st.plotly_chart(fig,use_container_width=True)

st.subheader("AI Campaign Audit")

st.dataframe(df)

st.subheader("Creative Winners")

df["score"] = df["ctr"] * df["conversions"]

st.dataframe(df.sort_values("score",ascending=False).head(5))

st.subheader("Creative Fatigue")

st.dataframe(df[df["frequency"] > 3])

st.subheader("Audience Targeting")

targeting = get_targeting(account_id,token)

target_df = extract_targeting(targeting)

st.dataframe(target_df)

st.subheader("Competitor Ad Finder")

keyword = st.text_input("Competitor Brand")

if keyword:

    ads = competitor_ads(keyword)

    st.write(ads)
