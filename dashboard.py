import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta Ads Command Center", layout="wide")

st.title("🚀 Meta Ads AI Command Center")

# -------- ADD MULTIPLE ACCOUNTS HERE --------

accounts = [
{
"account_id":"act_830580884293323",
"access_token":"EAAV8gZAY7XdEBQ7qsPauJ5ewD8NwX4HF40bqZBaYNZAQKAL0wdCgA9y1YL9jYwTZCUEpyNNU9N3zgUZBr5Ty3gcMGShxbEW8FtonsalL6pSiRZCWY6ZAlhjTnUIhpeLHHrsuXlvdRCo6ZBdu9OpE8Xf7zDs4KixzLskgntEmaIZBA3jzYO3a2idZCi5I8pusy8CX2D0TZCrQWeRaGZB3il4Wrdxp9lzxAME3NMggnZBxLZC0OQns46J7SKRhgmFYaqDc4V7ZCU62wUwikoFnZC0O5F3q3kDJUydHswZDZD"
},
{
"account_id":"act_415698175733898",
"access_token":"EAAV8gZAY7XdEBQ7qsPauJ5ewD8NwX4HF40bqZBaYNZAQKAL0wdCgA9y1YL9jYwTZCUEpyNNU9N3zgUZBr5Ty3gcMGShxbEW8FtonsalL6pSiRZCWY6ZAlhjTnUIhpeLHHrsuXlvdRCo6ZBdu9OpE8Xf7zDs4KixzLskgntEmaIZBA3jzYO3a2idZCi5I8pusy8CX2D0TZCrQWeRaGZB3il4Wrdxp9lzxAME3NMggnZBxLZC0OQns46J7SKRhgmFYaqDc4V7ZCU62wUwikoFnZC0O5F3q3kDJUydHswZDZD"
}
]

# -------- FETCH ACCOUNT NAMES --------

account_names = {}

for acc in accounts:

    url = f"https://graph.facebook.com/v19.0/{acc['account_id']}"

    params = {
        "fields":"name,currency",
        "access_token":acc["access_token"]
    }

    res = requests.get(url, params=params).json()

    name = res.get("name",acc["account_id"])

    account_names[name] = {
        "account_id":acc["account_id"],
        "access_token":acc["access_token"],
        "currency":res.get("currency","USD")
    }

selected_account = st.sidebar.selectbox(
"Select Ad Account",
list(account_names.keys())
)

ACCESS_TOKEN = account_names[selected_account]["access_token"]
AD_ACCOUNT = account_names[selected_account]["account_id"]
ACCOUNT_CURRENCY = account_names[selected_account]["currency"]

# -------- FILTERS --------

date_preset = st.sidebar.selectbox(
"Date Range",
["today","yesterday","last_7d","last_30d"]
)

level = st.sidebar.selectbox(
"Level",
["campaign","adset","ad"]
)

# -------- FETCH INSIGHTS --------

fields = "campaign_name,adset_name,ad_name,spend,ctr,cpc,cpm,frequency,impressions,clicks"

url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/insights"

params = {
"level":level,
"fields":fields,
"date_preset":date_preset,
"access_token":ACCESS_TOKEN
}

response = requests.get(url, params=params).json()

data = response.get("data",[])

if data:

    df = pd.DataFrame(data)

    numeric_cols = ["spend","ctr","cpc","cpm","frequency","impressions","clicks"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)

    # -------- KPI METRICS --------

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total Spend", f"{ACCOUNT_CURRENCY} {df['spend'].sum():.2f}")
    c2.metric("Avg CTR", f"{df['ctr'].mean():.2f}%")
    c3.metric("Avg CPC", f"{ACCOUNT_CURRENCY} {df['cpc'].mean():.2f}")
    c4.metric("Avg CPM", f"{ACCOUNT_CURRENCY} {df['cpm'].mean():.2f}")

    st.divider()

    # -------- CHARTS --------

    if "campaign_name" in df.columns:

        col1,col2 = st.columns(2)

        if "spend" in df.columns:

            fig = px.bar(df,x="campaign_name",y="spend",title="Campaign Spend")
            col1.plotly_chart(fig,use_container_width=True)

        if "ctr" in df.columns:

            fig = px.bar(df,x="campaign_name",y="ctr",title="Campaign CTR")
            col2.plotly_chart(fig,use_container_width=True)

    st.divider()

    # -------- HEALTH SCORE --------

    def health_score(row):

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

    df["health_score"] = df.apply(health_score,axis=1)

    st.subheader("Campaign Health")

    cols = [
    "campaign_name",
    "adset_name",
    "ad_name",
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "frequency",
    "health_score"
    ]

    cols = [c for c in cols if c in df.columns]

    st.dataframe(df[cols],use_container_width=True)

    st.divider()

    # -------- PERFORMANCE ANALYZER --------

    def analyze(row):

        if row["ctr"] < 1:
            return "Creative Issue"

        if row["cpc"] > 2:
            return "Audience Issue"

        if row["cpm"] > 20:
            return "High CPM"

        return "Healthy"

    df["issue"] = df.apply(analyze,axis=1)

    st.subheader("Campaign Performance Analyzer")

    cols = ["campaign_name","ctr","cpc","cpm","issue"]
    cols = [c for c in cols if c in df.columns]

    st.dataframe(df[cols],use_container_width=True)

    st.divider()

    # -------- CREATIVE FATIGUE --------

    st.subheader("Creative Fatigue Detection")

    fatigue = df[(df["frequency"] > 3) & (df["ctr"] < 1.5)]

    if len(fatigue):

        for i,row in fatigue.iterrows():

            st.warning(
            f"{row.get('campaign_name','Campaign')} → Creative fatigue detected"
            )

    else:

        st.success("No creative fatigue detected")

    st.divider()

    # -------- SCALING ENGINE --------

    def scale(row):

        if row["ctr"] > 2 and row["cpc"] < 1:
            return "Scale Budget"

        if row["ctr"] < 1:
            return "Test New Creatives"

        if row["cpc"] > 2:
            return "Improve Targeting"

        return "Monitor"

    df["scale_signal"] = df.apply(scale,axis=1)

    st.subheader("Scaling Recommendations")

    for i,row in df.iterrows():

        if row["scale_signal"] == "Scale Budget":

            st.success(
            f"{row.get('campaign_name','Campaign')} → Scale budget by 20%"
            )

    st.divider()

    # -------- PAUSE SIGNALS --------

    st.subheader("Pause Signals")

    pause = df[(df["ctr"] < 0.8) & (df["cpc"] > 3)]

    if len(pause):

        for i,row in pause.iterrows():

            st.error(
            f"{row.get('campaign_name','Campaign')} → Recommend Pausing"
            )

    else:

        st.success("No campaigns require pausing")

    st.divider()

    # -------- TARGETING CHANGE TRACKER --------

    st.subheader("Targeting Change Tracker")

    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/adsets"

    params = {
    "fields":"name,targeting,updated_time",
    "access_token":ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()

    adsets = res.get("data",[])

    for adset in adsets[:10]:

        st.write(f"""
Adset: {adset['name']}

Last Updated: {adset['updated_time']}
""")

    st.divider()

    # -------- AI TARGETING SUGGESTIONS --------

    st.subheader("AI Targeting Suggestions")

    brand = st.text_input("Enter Brand / Industry")

    def suggest_targeting(brand):

        brand = brand.lower()

        if "trading" in brand or "stock" in brand or "investment" in brand:

            return [
            "Stock Market",
            "Equity Trading",
            "Mutual Funds",
            "Personal Finance",
            "Zerodha",
            "Angel One",
            "Groww",
            "Financial Planning",
            "Investment Banking"
            ]

        if "ai" in brand or "saas" in brand:

            return [
            "Artificial Intelligence",
            "Machine Learning",
            "SaaS",
            "Startup Founders",
            "Cloud Computing",
            "Business Automation"
            ]

        if "ecommerce" in brand or "shopify" in brand:

            return [
            "Shopify",
            "Amazon Seller",
            "E-commerce",
            "Dropshipping",
            "Online Business"
            ]

        return [
        "Business",
        "Entrepreneurship",
        "Technology"
        ]

    if brand:

        interests = suggest_targeting(brand)

        for i in interests:

            st.write("•",i)

else:

    st.error("No data returned from Meta API")
