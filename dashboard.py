import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

GRAPH = "https://graph.facebook.com/v19.0"

# ---------- META STYLE UI ----------
st.markdown("""
<style>
body {
background-color:#0e1117;
color:white;
}

[data-testid="metric-container"] {
background-color:#161b22;
padding:20px;
border-radius:10px;
border:1px solid #30363d;
}

.sidebar .sidebar-content {
background-color:#0e1117;
}

</style>
""", unsafe_allow_html=True)

st.title("🚀 Meta Ads Command Center")

# ---------- ACCESS TOKEN ----------
token = st.text_input("Enter Meta Access Token", type="password")

if token == "":
    st.stop()

# ---------- FETCH AD ACCOUNTS ----------
accounts_res = requests.get(
f"{GRAPH}/me/adaccounts",
params={
"fields":"name,account_id,currency",
"access_token":token
}).json()

accounts = accounts_res.get("data",[])

if len(accounts)==0:
    st.error("No ad accounts found")
    st.stop()

account_names=[a["name"] for a in accounts]

selected_account=st.sidebar.selectbox("Ad Account",account_names)

account_id=None
currency="USD"

for a in accounts:
    if a["name"]==selected_account:
        account_id=a["account_id"]
        currency=a["currency"]

# ---------- FILTERS ----------
date_range=st.sidebar.selectbox(
"Date Range",
["today","yesterday","last_7d","last_30d","last_90d"]
)

level=st.sidebar.selectbox(
"Data Level",
["campaign","adset","ad"]
)

# ---------- FETCH DATA ----------
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
    st.warning("No data found")
    st.stop()

# ---------- NUMERIC ----------
for col in ["spend","ctr","cpc","cpm","frequency","impressions","reach","clicks"]:
    if col in df.columns:
        df[col]=pd.to_numeric(df[col])

# ---------- CONVERSIONS ----------
def conv(actions):

    if actions is None:
        return 0

    if isinstance(actions,float):
        return 0

    conversions=0

    try:
        for a in actions:

            if a.get("action_type")=="purchase":
                conversions+=float(a.get("value",0))

            if a.get("action_type")=="lead":
                conversions+=float(a.get("value",0))

    except:
        return 0

    return conversions

df["conversions"]=df["actions"].apply(conv)

# ---------- SAFE CPA ----------
df["CPA"]=df.apply(
lambda x: x["spend"]/x["conversions"] if x["conversions"]>0 else 0,
axis=1
)

# ---------- KPI CARDS ----------
c1,c2,c3,c4=st.columns(4)

c1.metric("Total Spend",f"{currency} {df['spend'].sum():,.0f}")
c2.metric("Conversions",int(df["conversions"].sum()))
c3.metric("Avg CTR",f"{df['ctr'].mean():.2f}%")
c4.metric("Avg CPA",f"{currency} {df['CPA'].mean():.2f}")

# ---------- CHART ----------
if "campaign_name" in df.columns:

    fig=px.bar(
    df,
    x="campaign_name",
    y="spend",
    title="Campaign Spend"
    )

    st.plotly_chart(fig,use_container_width=True)

# ---------- AI AUDIT ----------
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

# ---------- CUSTOMIZE COLUMNS ----------
st.sidebar.subheader("Customize Columns")

available_columns=[
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
"AI Audit"
]

selected_columns=st.sidebar.multiselect(
"Select Metrics",
available_columns,
default=[
"campaign_name",
"spend",
"impressions",
"clicks",
"ctr",
"cpc",
"cpm",
"conversions",
"CPA"
])

st.subheader("📊 Performance Data")

st.dataframe(df[selected_columns],use_container_width=True)

# ---------- CREATIVE WINNERS ----------
df["Winner Score"]=df["ctr"]*df["conversions"]

st.subheader("🏆 Creative Winners")

winner=df.sort_values("Winner Score",ascending=False).head(5)

st.dataframe(winner[selected_columns])

# ---------- HIGH CPA ----------
st.subheader("🚨 High CPA Campaigns")

high_cpa=df[df["CPA"]>df["CPA"].mean()*1.5]

st.dataframe(high_cpa[selected_columns])

# ---------- CREATIVE FATIGUE ----------
st.subheader("🎨 Creative Fatigue")

fatigue=df[df["frequency"]>3]

st.dataframe(fatigue[selected_columns])

# ---------- TARGETING ----------
st.subheader("🎯 Audience Targeting")

adsets=requests.get(
f"{GRAPH}/act_{account_id}/adsets",
params={
"fields":"name,targeting,optimization_goal,daily_budget",
"access_token":token
}).json()

targeting_list=[]

for a in adsets.get("data",[]):

    interests=[]

    targeting=a.get("targeting",{})

    if "flexible_spec" in targeting:

        for group in targeting["flexible_spec"]:

            if "interests" in group:

                for i in group["interests"]:
                    interests.append(i["name"])

    targeting_list.append({
    "Adset":a["name"],
    "Interests":", ".join(interests),
    "Optimization":a.get("optimization_goal"),
    "Budget":a.get("daily_budget")
    })

target_df=pd.DataFrame(targeting_list)

st.dataframe(target_df)

# ---------- COMPETITOR RESEARCH ----------
st.subheader("🔎 Competitor Research")

brand=st.text_input("Search Brand")

if brand:

    url="https://graph.facebook.com/v19.0/ads_archive"

    params={
    "search_terms":brand,
    "ad_reached_countries":"IN",
    "ad_type":"ALL",
    "fields":"page_name,ad_creative_body,ad_delivery_start_time",
    "limit":10
    }

    ads=requests.get(url,params=params).json()

    ads_data=ads.get("data",[])

    if len(ads_data)==0:

        st.warning("No ads found")

    else:

        ads_list=[]

        for ad in ads_data:

            ads_list.append({
            "Page":ad.get("page_name"),
            "Ad Copy":ad.get("ad_creative_body"),
            "Start Date":ad.get("ad_delivery_start_time")
            })

        st.dataframe(pd.DataFrame(ads_list))
