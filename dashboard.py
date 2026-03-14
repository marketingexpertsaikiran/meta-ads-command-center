import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from itertools import combinations

st.set_page_config(page_title="Meta Ads AI Command Center", layout="wide")

# ---------- UI STYLE ----------

st.markdown("""
<style>

body {background-color:#0f172a;}

.block-container {padding-top:1rem;}

.metric-card{
background:#111827;
padding:20px;
border-radius:14px;
box-shadow:0 6px 20px rgba(0,0,0,0.4);
}

.metric-title{color:#9ca3af;font-size:13px;}

.metric-value{font-size:30px;font-weight:700;color:white;}

</style>
""",unsafe_allow_html=True)

st.title("🚀 Meta Ads AI Command Center")

# ---------- MULTI ACCOUNT CONFIG ----------

accounts = [
{
"account_id":"act_830580884293323",
"access_token":"EAAV8gZAY7XdEBQ4emqP8U86yJZC0aLVWMmqmbiTbS7A0KQlRsV2lqQOxgnZBVLJmFwYFabb6wet3NPmklpmflLlqDCmS47kCCi7fA2WNvOJkqjHm6Hn4GjYaeQTjzrM9Y2OrXVgCA1c8Kpvwqx9jO5JgPZAYatrZBHd2iKyJ0nvWtARR5m9u0lX4BIjk8rDwjTEWD6ZAWqUNgNsv5J820iZCrRkiuo2xCo8MKmU"
},
{
"account_id":"act_415698175733898",
"access_token":"EAAV8gZAY7XdEBQ4emqP8U86yJZC0aLVWMmqmbiTbS7A0KQlRsV2lqQOxgnZBVLJmFwYFabb6wet3NPmklpmflLlqDCmS47kCCi7fA2WNvOJkqjHm6Hn4GjYaeQTjzrM9Y2OrXVgCA1c8Kpvwqx9jO5JgPZAYatrZBHd2iKyJ0nvWtARR5m9u0lX4BIjk8rDwjTEWD6ZAWqUNgNsv5J820iZCrRkiuo2xCo8MKmU"
}
]

# ---------- FETCH ACCOUNT NAMES ----------

account_map={}

for acc in accounts:

    url=f"https://graph.facebook.com/v19.0/{acc['account_id']}"

    params={
    "fields":"name,currency",
    "access_token":acc["access_token"]
    }

    res=requests.get(url,params=params).json()

    name=res.get("name",acc["account_id"])

    account_map[name]={
    "account_id":acc["account_id"],
    "access_token":acc["access_token"],
    "currency":res.get("currency","USD")
    }

selected_account=st.sidebar.selectbox("Ad Account",list(account_map.keys()))

ACCESS_TOKEN=account_map[selected_account]["access_token"]
AD_ACCOUNT=account_map[selected_account]["account_id"]
CURRENCY=account_map[selected_account]["currency"]

# ---------- FILTERS ----------

date_preset=st.sidebar.selectbox(
"Date Range",
["today","yesterday","last_7d","last_30d"]
)

level=st.sidebar.selectbox(
"Level",
["campaign","adset","ad"]
)

# ---------- FETCH INSIGHTS ----------

fields="campaign_name,adset_name,ad_name,spend,ctr,cpc,cpm,frequency,impressions,clicks,actions"

url=f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/insights"

params={
"level":level,
"fields":fields,
"date_preset":date_preset,
"access_token":ACCESS_TOKEN
}

data=requests.get(url,params=params).json().get("data",[])

if not data:
    st.error("No data returned from Meta API")
    st.stop()

df=pd.DataFrame(data)

# ---------- CLEAN NUMERIC DATA ----------

num_cols=["spend","ctr","cpc","cpm","frequency","impressions","clicks"]

for c in num_cols:
    if c in df.columns:
        df[c]=pd.to_numeric(df[c])

# ---------- KPI DASHBOARD ----------

c1,c2,c3,c4=st.columns(4)

with c1:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">Total Spend</div>
<div class="metric-value">{CURRENCY} {df['spend'].sum():,.0f}</div>
</div>
""",unsafe_allow_html=True)

with c2:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">Avg CTR</div>
<div class="metric-value">{df['ctr'].mean():.2f}%</div>
</div>
""",unsafe_allow_html=True)

with c3:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">Avg CPC</div>
<div class="metric-value">{CURRENCY} {df['cpc'].mean():.2f}</div>
</div>
""",unsafe_allow_html=True)

with c4:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">Avg CPM</div>
<div class="metric-value">{CURRENCY} {df['cpm'].mean():.2f}</div>
</div>
""",unsafe_allow_html=True)

st.divider()

# ---------- CAMPAIGN CHARTS ----------

if "campaign_name" in df.columns:

    col1,col2=st.columns(2)

    fig=px.bar(df,x="campaign_name",y="spend",title="Campaign Spend")
    col1.plotly_chart(fig,use_container_width=True)

    fig=px.bar(df,x="campaign_name",y="ctr",title="Campaign CTR")
    col2.plotly_chart(fig,use_container_width=True)

st.divider()

# ---------- HEALTH SCORE ----------

def health(row):

    score=100

    if row["ctr"]<1:
        score-=30

    if row["cpc"]>2:
        score-=20

    if row["cpm"]>20:
        score-=20

    if row["frequency"]>3:
        score-=10

    return score

df["health_score"]=df.apply(health,axis=1)

st.subheader("Campaign Health")

st.dataframe(df[[
"campaign_name",
"spend",
"ctr",
"cpc",
"cpm",
"frequency",
"health_score"
]])

# ---------- CREATIVE FATIGUE ----------

st.subheader("Creative Fatigue Detection")

fatigue=df[(df["frequency"]>3)&(df["ctr"]<1.5)]

for _,row in fatigue.iterrows():

    st.warning(f"{row['campaign_name']} → Creative fatigue detected")

# ---------- AI BUDGET ALLOCATOR ----------

st.subheader("AI Budget Allocator")

df["budget_action"]="Monitor"

df.loc[(df["ctr"]>2)&(df["cpc"]<1),"budget_action"]="Increase Budget 20%"
df.loc[(df["ctr"]<0.8),"budget_action"]="Reduce Budget"

st.dataframe(df[["campaign_name","budget_action"]])

# ---------- CPA ANOMALY ----------

st.subheader("CPA Anomaly Alerts")

df["CPA"]=df["spend"]/df["clicks"]

df["CPA_change"]=df["CPA"].pct_change()

alerts=df[df["CPA_change"]>0.5]

for _,row in alerts.iterrows():

    st.error(f"CPA spike detected in {row['campaign_name']}")

# ---------- CREATIVE WINNER ----------

st.subheader("Creative Winner Detection")

winners=df[(df["ctr"]>2.5)&(df["cpc"]<1)]

st.dataframe(winners)

# ---------- AUTOMATED SCALING ----------

st.subheader("Scaling Engine")

def scaling(row):

    if row["ctr"]>2 and row["cpc"]<1:
        return "Scale Budget"

    if row["ctr"]<1:
        return "Refresh Creative"

    if row["cpm"]>20:
        return "Expand Audience"

    return "Monitor"

df["AI_action"]=df.apply(scaling,axis=1)

st.dataframe(df[["campaign_name","AI_action"]])

# ---------- AUDIENCE HEATMAP ----------

st.subheader("Audience Heatmap")

break_url=f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/insights"

break_params={
"breakdowns":"age,gender",
"fields":"impressions,ctr",
"date_preset":date_preset,
"access_token":ACCESS_TOKEN
}

age_data=requests.get(break_url,params=break_params).json().get("data",[])

if age_data:

    heat_df=pd.DataFrame(age_data)

    fig=px.density_heatmap(
    heat_df,
    x="age",
    y="gender",
    z="ctr"
    )

    st.plotly_chart(fig)

# ---------- GEO ANALYZER ----------

st.subheader("Geo Performance")

geo_params={
"breakdowns":"country",
"fields":"country,ctr",
"date_preset":date_preset,
"access_token":ACCESS_TOKEN
}

geo_data=requests.get(break_url,params=geo_params).json().get("data",[])

if geo_data:

    geo_df=pd.DataFrame(geo_data)

    fig=px.bar(geo_df,x="country",y="ctr")

    st.plotly_chart(fig)

# ---------- AUDIENCE OVERLAP ----------

st.subheader("Audience Overlap Detector")

url=f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/adsets"

params={
"fields":"name,targeting",
"access_token":ACCESS_TOKEN
}

adsets=requests.get(url,params=params).json().get("data",[])

audiences={}

for ad in adsets:

    interests=ad.get("targeting",{}).get("interests",[])

    audiences[ad["name"]]=[i["name"] for i in interests]

for a,b in combinations(audiences.keys(),2):

    overlap=len(set(audiences[a])&set(audiences[b]))

    if overlap>3:

        st.warning(f"Audience overlap between {a} and {b}")

# ---------- TARGETING CHANGE TRACKER ----------

st.subheader("Targeting Change Tracker")

for ad in adsets[:10]:

    st.write(f"{ad['name']}")

# ---------- META INTEREST FINDER ----------

st.subheader("Meta Interest Finder")

keyword=st.text_input("Search Interest")

if keyword:

    url="https://graph.facebook.com/v19.0/search"

    params={
    "type":"adinterest",
    "q":keyword,
    "limit":20,
    "access_token":ACCESS_TOKEN
    }

    interests=requests.get(url,params=params).json().get("data",[])

    for i in interests:

        st.write(f"{i['name']} — Audience {i.get('audience_size','N/A')}")

# ---------- LANDING PAGE ANALYZER ----------

st.subheader("Landing Page Performance")

if "clicks" in df.columns:

    df["CVR"]=0

    df.loc[df["clicks"]>0,"CVR"]=df["clicks"]/df["impressions"]

    lp=df[(df["ctr"]>2)&(df["CVR"]<0.02)]

    for _,row in lp.iterrows():

        st.warning(f"{row['campaign_name']} → Landing page issue")
