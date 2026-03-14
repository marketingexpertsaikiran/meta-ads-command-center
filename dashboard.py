import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("🚀 Meta Ads Command Center")

ACCESS_TOKEN = "PASTE_META_TOKEN"
AD_ACCOUNT_ID = "act_XXXXXXXXXXXX"

date_preset = st.selectbox(
    "Select Date Range",
    ["today","yesterday","last_7d","last_30d"]
)

url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"

params = {
    "level":"campaign",
    "fields":"campaign_name,spend,ctr,cpc,cpm,impressions,clicks",
    "date_preset":date_preset,
    "access_token":ACCESS_TOKEN
}

response = requests.get(url,params=params).json()

data = response.get("data",[])

if data:

    df = pd.DataFrame(data)

    df["spend"] = df["spend"].astype(float)
    df["ctr"] = df["ctr"].astype(float)
    df["cpc"] = df["cpc"].astype(float)
    df["cpm"] = df["cpm"].astype(float)

    st.subheader("Campaign Performance")

    st.dataframe(df)

    st.subheader("Spend by Campaign")

    fig = px.bar(df,x="campaign_name",y="spend")

    st.plotly_chart(fig)

    st.subheader("AI Campaign Insights")

    for i,row in df.iterrows():

        if row["ctr"] < 1:
            st.warning(f"{row['campaign_name']} → Low CTR. Test new creatives")

        elif row["cpc"] > 2:
            st.warning(f"{row['campaign_name']} → High CPC. Improve targeting")

        elif row["ctr"] > 2 and row["cpc"] < 1:
            st.success(f"{row['campaign_name']} → Scale this campaign 🚀")

else:

    st.error("No data returned from Meta API")
