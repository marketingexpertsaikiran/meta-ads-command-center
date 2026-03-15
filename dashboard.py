import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

GRAPH="https://graph.facebook.com/v19.0"

# ---------------- META STYLE UI ----------------

st.markdown("""
<style>

body {
background-color:#0e1117;
color:white;
}

[data-testid="metric-container"] {
background:#161b22;
padding:20px;
border-radius:10px;
border:1px solid #30363d;
}

</style>
""",unsafe_allow_html=True)

st.title("🚀 Meta Ads Command Center")

# ---------------- ACCESS TOKEN ----------------

token=st.text_input("Enter Meta Access Token",type="password")

if token=="":
    st.stop()

# ---------------- FETCH AD ACCOUNTS ----------------

accounts_res=requests.get(
f"{GRAPH}/me/adaccounts",
params={
"fields":"name,account_id,currency",
"access_token":token
}).json()

accounts=accounts_res.get("data",[])

if len(accounts)==0:

    st.error("No Ad Accounts Found")
    st.stop()

account_names=[a["name"] for a in accounts]

selected_account=st.sidebar.selectbox("Ad Account",account_names)

account_id=None
currency="USD"

for a in accounts:

    if a["name"]==selected_account:

        account_id=a["account_id"]
        currency=a["currency"]

# ---------------- FILTERS ----------------

date_range=st.sidebar.selectbox(
"Date Range",
["today","yesterday","last_7d","last_30d","last_90d"]
)

level=st.sidebar.selectbox(
"Data Level",
["campaign","adset","ad"]
)

# ---------------- FETCH INSIGHTS ----------------

fields="""
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

insights=requests.get(
f"{GRAPH}/act_{account_id}/insights",
params={
"fields":fields,
"level":level,
"date_preset":date_range,
"limit":500,
"access_token":token
}).json()

df=pd.DataFrame(insights.get("data",[]))

if df.empty:

    st.warning("No Data Found")
    st.stop()

# ---------------- NUMERIC CONVERSION ----------------

num_cols=[
"spend","ctr","cpc","cpm",
"frequency","impressions",
"reach","clicks"
]

for col in num_cols:

    if col in df.columns:

        df[col]=pd.to_numeric(df[col])

# ---------------- CONVERSIONS ----------------

def conversions(actions):

    if actions is None:
        return 0

    total=0

    try:

        for a in actions:

            if a["action_type"] in ["purchase","lead"]:

                total+=float(a["value"])

    except:
        return 0

    return total

df["conversions"]=df["actions"].apply(conversions)

# ---------------- REVENUE ----------------

def revenue(actions):

    if actions is None:
        return 0

    value=0

    try:

        for a in actions:

            if a["action_type"]=="purchase":

                value+=float(a["value"])

    except:
        return 0

    return value

df["revenue"]=df["actions"].apply(revenue)

# ---------------- CPA ----------------

df["CPA"]=df.apply(
lambda x:x["spend"]/x["conversions"] if x["conversions"]>0 else 0,
axis=1
)

# ---------------- ROAS ----------------

df["ROAS"]=df.apply(
lambda x:x["revenue"]/x["spend"] if x["spend"]>0 else 0,
axis=1
)

# ---------------- HEALTH SCORE ----------------

def health(row):

    score=0

    if row["ctr"]>1:
        score+=25

    if row["cpc"]<2:
        score+=25

    if row["frequency"]<3:
        score+=25

    if row["CPA"]<df["CPA"].mean():
        score+=25

    return score

df["Health Score"]=df.apply(health,axis=1)

# ---------------- KPI CARDS ----------------

c1,c2,c3,c4,c5=st.columns(5)

c1.metric("Spend",f"{currency} {df['spend'].sum():,.0f}")
c2.metric("Conversions",int(df["conversions"].sum()))
c3.metric("CTR",f"{df['ctr'].mean():.2f}%")
c4.metric("CPA",f"{currency} {df['CPA'].mean():.2f}")
c5.metric("ROAS",f"{df['ROAS'].mean():.2f}")

# ---------------- SPEND CHART ----------------

if "campaign_name" in df.columns:

    fig=px.bar(
    df,
    x="campaign_name",
    y="spend",
    title="Campaign Spend"
    )

    st.plotly_chart(fig,use_container_width=True)

# ---------------- FUNNEL ----------------

funnel=pd.DataFrame({

"Stage":[
"Impressions",
"Clicks",
"Conversions"
],

"Value":[
df["impressions"].sum(),
df["clicks"].sum(),
df["conversions"].sum()
]

})

fig=px.funnel(
funnel,
x="Value",
y="Stage",
title="Conversion Funnel"
)

st.plotly_chart(fig,use_container_width=True)

# ---------------- AI AUDIT ----------------

def audit(row):

    if row["ctr"]<1:
        return "Creative Issue"

    if row["cpc"]>2:
        return "Audience Issue"

    if row["cpm"]>20:
        return "High CPM"

    if row["frequency"]>3:
        return "Creative Fatigue"

    return "Healthy"

df["AI Audit"]=df.apply(audit,axis=1)

# ---------------- COLUMN SELECTOR ----------------

st.sidebar.subheader("Customize Columns")

columns=[
"campaign_name",
"adset_name",
"ad_name",
"spend",
"impressions",
"reach",
"clicks",
"ctr",
"cpc",
"cpm",
"frequency",
"conversions",
"CPA",
"ROAS",
"Health Score",
"AI Audit"
]

selected=st.sidebar.multiselect(
"Select Metrics",
columns,
default=[
"campaign_name",
"spend",
"impressions",
"clicks",
"ctr",
"cpc",
"cpm",
"conversions",
"CPA",
"ROAS"
]
)

st.subheader("📊 Performance Data")

st.dataframe(df[selected],use_container_width=True)

# ---------------- CREATIVE WINNERS ----------------

df["Winner Score"]=df["ctr"]*df["conversions"]

st.subheader("🏆 Creative Winners")

winner=df.sort_values(
"Winner Score",
ascending=False
).head(5)

st.dataframe(winner[selected])

# ---------------- CTR LEADERBOARD ----------------

st.subheader("🔥 Top CTR Creatives")

top_ctr=df.sort_values(
"ctr",
ascending=False
).head(10)

st.dataframe(top_ctr[selected])

# ---------------- HIGH CPA ----------------

st.subheader("🚨 High CPA")

high_cpa=df[
df["CPA"]>df["CPA"].mean()*1.5
]

st.dataframe(high_cpa[selected])

# ---------------- CREATIVE FATIGUE ----------------

st.subheader("🎨 Creative Fatigue")

fatigue=df[
df["frequency"]>3
]

st.dataframe(fatigue[selected])

# ---------------- BUDGET INSIGHTS ----------------

st.subheader("💰 Budget Insights")

total_spend=df["spend"].sum()

if total_spend>5000:

    st.warning("High Spend Alert")

if df["frequency"].mean()>3:

    st.warning("Creative Fatigue Detected")

# ---------------- TARGETING ----------------

st.subheader("🎯 Audience Targeting")

adsets=requests.get(
f"{GRAPH}/act_{account_id}/adsets",
params={
"fields":"name,targeting,optimization_goal,daily_budget",
"access_token":token
}).json()

target_list=[]

for a in adsets.get("data",[]):

    interests=[]

    targeting=a.get("targeting",{})

    if "flexible_spec" in targeting:

        for g in targeting["flexible_spec"]:

            if "interests" in g:

                for i in g["interests"]:

                    interests.append(i["name"])

    target_list.append({

    "Adset":a["name"],
    "Interests":", ".join(interests),
    "Optimization":a.get("optimization_goal"),
    "Budget":a.get("daily_budget")

    })

target_df=pd.DataFrame(target_list)

st.dataframe(target_df)

# ---------------- COMPETITOR RESEARCH ----------------

st.subheader("🔎 Competitor Ads")

brand=st.text_input("Search Brand")

if brand:

    url=f"{GRAPH}/ads_archive"

    params={

    "search_terms":brand,
    "ad_reached_countries":"IN",
    "ad_type":"ALL",
    "fields":"page_name,ad_creative_body,ad_delivery_start_time,ad_snapshot_url",
    "limit":20,
    "access_token":token

    }

    ads=requests.get(url,params=params).json()

    data=ads.get("data",[])

    if len(data)==0:

        st.warning("No ads found")

    else:

        ads_list=[]

        for ad in data:

            ads_list.append({

            "Page":ad.get("page_name"),
            "Ad Copy":ad.get("ad_creative_body"),
            "Start Date":ad.get("ad_delivery_start_time"),
            "Preview":ad.get("ad_snapshot_url")

            })

        ads_df=pd.DataFrame(ads_list)

        st.dataframe(ads_df)

        for ad in ads_list:

            if ad["Preview"]:

                st.markdown(
                f"[View Ad]({ad['Preview']})"
                )
