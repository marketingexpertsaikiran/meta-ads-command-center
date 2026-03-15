import streamlit as st
import pandas as pd
import plotly.express as px

from oauth_login import login
from meta_api import get_accounts,get_campaign_data
from ai_engine import audit,scaling_signal
from budget_allocator import recommend_budget
from competitor_ads import find_ads

st.set_page_config(layout="wide")

st.title("🚀 Meta AI Command Center")

login()

token = st.text_input("Access Token")

if token == "":
    st.stop()

accounts = get_accounts(token)

names = [a["name"] for a in accounts]

account = st.sidebar.selectbox("Ad Account",names)

account_id = None

for a in accounts:
    if a["name"] == account:
        account_id = a["account_id"]

date = st.sidebar.selectbox(
"Date",
["today","yesterday","last_7d","last_30d"]
)

level = st.sidebar.selectbox(
"Level",
["campaign","adset","ad"]
)

df = get_campaign_data(account_id,token,date,level)

if df.empty:
    st.stop()

for col in ["spend","ctr","cpc","cpm","frequency","clicks"]:
    df[col] = pd.to_numeric(df[col])

def conv(actions):

    if actions is None:
        return 0

    for a in actions:
        if a["action_type"] == "purchase":
            return float(a["value"])

    return 0

df["conversions"] = df["actions"].apply(conv)

df["CPA"] = df["spend"] / df["conversions"]

df["Audit"] = df.apply(audit,axis=1)

df["Scaling"] = df.apply(scaling_signal,axis=1)

df["Budget Advice"] = df.apply(recommend_budget,axis=1)

c1,c2,c3,c4 = st.columns(4)

c1.metric("Spend",round(df["spend"].sum(),2))
c2.metric("Conversions",int(df["conversions"].sum()))
c3.metric("CTR",round(df["ctr"].mean(),2))
c4.metric("CPA",round(df["CPA"].mean(),2))

fig = px.bar(df,x="campaign_name",y="spend")

st.plotly_chart(fig,use_container_width=True)

st.subheader("AI Campaign Audit")

st.dataframe(df)

st.subheader("Creative Fatigue")

st.dataframe(df[df["frequency"] > 3])

st.subheader("Competitor Ad Finder")

brand = st.text_input("Competitor Brand")

if brand:

    ads = find_ads(brand)

    st.write(ads)
