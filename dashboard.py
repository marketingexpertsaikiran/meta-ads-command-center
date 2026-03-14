import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta Ads Command Center", layout="wide")

st.title("🚀 Meta Ads Performance Command Center")

ACCESS_TOKEN = "EAAV8gZAY7XdEBQ3dfxz5UOYeQ7IB7qo1kcRFZAhE6xKVXHHlZAgowXSlUZARgQixjvdxX6uE9hSJpr76YSifh0SM7WZCkSDPsQc5XQ5ifTD0Edu4drr2rxfa7dgxdCZBWnzJ2oEWZBkZB07tYZARbkoVlFgMuHLj1lSevYD7SCpz8o8qLTdjfbJEdNCP5YUooEeYWZB7ZCiZBSXzhae54SZBTk2sZCoLfNLUnhibj0YTBUmLWQjZC0y9fLZApfDse67lYmc83rsu5ZAkvZAlnT5hRrrMV5Qb6p1HyM"
AD_ACCOUNT = "act_830580884293323"

date_preset = st.selectbox(
    "Select Date Range",
    ["today","yesterday","last_7d","last_30d"]
)

url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/insights"

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

    # KPI METRICS

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Spend", f"${df['spend'].sum():.2f}")
    col2.metric("Average CTR", f"{df['ctr'].mean():.2f}%")
    col3.metric("Average CPC", f"${df['cpc'].mean():.2f}")
    col4.metric("Average CPM", f"${df['cpm'].mean():.2f}")

    st.divider()

    # CHARTS

    col5,col6 = st.columns(2)

    fig1 = px.bar(df,x="campaign_name",y="spend",title="Spend by Campaign")
    col5.plotly_chart(fig1,use_container_width=True)

    fig2 = px.bar(df,x="campaign_name",y="ctr",title="CTR by Campaign")
    col6.plotly_chart(fig2,use_container_width=True)

    st.divider()

    # HEALTH SCORE

    def health_score(row):

        score = 100

        if row["ctr"] < 1:
            score -= 30

        if row["cpc"] > 2:
            score -= 20

        if row["cpm"] > 20:
            score -= 20

        return score

    df["health_score"] = df.apply(health_score,axis=1)

    st.subheader("Campaign Health Score")

    st.dataframe(df[[
        "campaign_name",
        "spend",
        "ctr",
        "cpc",
        "cpm",
        "health_score"
    ]])

    st.divider()

    # AI INSIGHTS

    st.subheader("AI Performance Insights")

    for i,row in df.iterrows():

        if row["ctr"] < 1:

            st.warning(
                f"{row['campaign_name']} → Low CTR. Creative fatigue detected."
            )

        elif row["cpc"] > 2:

            st.warning(
                f"{row['campaign_name']} → High CPC. Audience targeting issue."
            )

        elif row["ctr"] > 2 and row["cpc"] < 1:

            st.success(
                f"{row['campaign_name']} → High performance. Scale campaign."
            )

    st.divider()

    # BEST CAMPAIGN

    best = df.sort_values("ctr",ascending=False).iloc[0]

    st.success(
        f"🏆 Best Campaign: {best['campaign_name']} with CTR {best['ctr']}%"
    )

else:

    st.error("No data returned from Meta API")
