import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("🚀 Meta Ads AI Command Center")

API="https://graph.facebook.com/v19.0"

# -------- LOGIN --------

st.sidebar.header("Connect Meta")

token=st.sidebar.text_input("Access Token")

if not token:
    st.warning("Enter Meta Access Token")
    st.stop()

# -------- FETCH AD ACCOUNTS --------

accounts_url=f"{API}/me/adaccounts"

accounts=requests.get(accounts_url,params={
"fields":"name,account_id,currency",
"access_token":token
}).json()

if "data" not in accounts:
    st.error("Token invalid or permission missing")
    st.stop()

account_names=[a["name"] for a in accounts["data"]]

selected=st.sidebar.selectbox("Ad Account",account_names)

account_id=None
currency="USD"

for a in accounts["data"]:
    if a["name"]==selected:
        account_id=a["account_id"]
        currency=a["currency"]

# -------- DATE FILTER --------

date=st.sidebar.selectbox(
"Date Range",
["today","yesterday","last_7d","last_30d"]
)

# -------- FETCH INSIGHTS --------

fields="""
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
landing_page_views,
video_plays,
actions
"""

url=f"{API}/act_{account_id}/insights"

data=requests.get(url,params={
"level":"ad",
"fields":fields,
"date_preset":date,
"access_token":token
}).json()

if "data" not in data:
    st.error("No insights data")
    st.stop()

df=pd.DataFrame(data["data"])

# -------- CLEAN DATA --------

nums=[
"spend","ctr","cpc","cpm","frequency",
"reach","impressions","clicks"
]

for n in nums:
    if n in df:
        df[n]=pd.to_numeric(df[n])

# -------- KPI --------

c1,c2,c3,c4=st.columns(4)

c1.metric("Spend",f"{currency} {df.spend.sum():.0f}")
c2.metric("CTR",f"{df.ctr.mean():.2f}%")
c3.metric("CPC",f"{currency} {df.cpc.mean():.2f}")
c4.metric("CPM",f"{currency} {df.cpm.mean():.2f}")

# -------- SPEND CHART --------

fig=px.bar(df,x="campaign_name",y="spend")

st.plotly_chart(fig,use_container_width=True)

# -------- HEALTH SCORE --------

def health(r):

    score=100

    if r["ctr"]<1:
        score-=30

    if r["cpc"]>2:
        score-=20

    if r["cpm"]>20:
        score-=20

    if r["frequency"]>3:
        score-=10

    return score

df["health"]=df.apply(health,axis=1)

st.subheader("Campaign Health")

st.dataframe(df)

# -------- AI SCALING ENGINE --------

def action(r):

    if r["ctr"]>2 and r["cpc"]<1:
        return "Scale Budget"

    if r["ctr"]<1:
        return "Creative Issue"

    if r["cpm"]>20:
        return "Audience Too Narrow"

    if r["frequency"]>3:
        return "Creative Fatigue"

    return "Monitor"

df["AI_Action"]=df.apply(action,axis=1)

st.subheader("AI Optimization")

st.dataframe(df[[
"campaign_name",
"AI_Action"
]])

# -------- CREATIVE FATIGUE --------

st.subheader("Creative Fatigue")

fatigue=df[(df.frequency>3)&(df.ctr<1.5)]

st.dataframe(fatigue)

# -------- WINNING CREATIVES --------

st.subheader("Creative Winners")

winners=df[(df.ctr>2.5)&(df.cpc<1)]

st.dataframe(winners)

# -------- LANDING PAGE ANALYZER --------

st.subheader("Landing Page Issues")

df["CVR"]=df["clicks"]/df["impressions"]

lp=df[(df.ctr>2)&(df.CVR<0.02)]

st.dataframe(lp)

# -------- TARGETING FETCH --------

st.subheader("Adset Targeting")

target_url=f"{API}/act_{account_id}/adsets"

targeting=requests.get(target_url,params={
"fields":"name,targeting",
"limit":200,
"access_token":token
}).json()

if "data" in targeting:

    for ad in targeting["data"][:10]:

        st.write("###",ad["name"])

        t=ad.get("targeting",{})

        interests=t.get("interests",[])

        for i in interests:

            st.write("•",i["name"])

# -------- INTEREST FINDER --------

st.subheader("Detailed Targeting Finder")

keyword=st.text_input("Search Interest")

if keyword:

    interest=requests.get(
    f"{API}/search",
    params={
    "type":"adinterest",
    "q":keyword,
    "limit":50,
    "access_token":token
    }).json()

    if "data" in interest:

        for i in interest["data"]:

            st.write(
            i["name"],
            "- Audience:",
            i.get("audience_size","N/A")
            )

# -------- AUDIENCE OVERLAP --------

st.subheader("Audience Overlap Detector")

aud={}

if "data" in targeting:

    for ad in targeting["data"]:

        ints=ad.get("targeting",{}).get("interests",[])

        aud[ad["name"]]=[i["name"] for i in ints]

    names=list(aud.keys())

    for i in range(len(names)):
        for j in range(i+1,len(names)):

            overlap=set(aud[names[i]]) & set(aud[names[j]])

            if len(overlap)>3:

                st.warning(
                f"Overlap between {names[i]} and {names[j]}"
                )
