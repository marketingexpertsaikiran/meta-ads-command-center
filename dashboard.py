import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta Ads Command Center", layout="wide")

st.title("🚀 Meta Ads AI Performance Command Center")

ACCESS_TOKEN = "EAAV8gZAY7XdEBQ3dfxz5UOYeQ7IB7qo1kcRFZAhE6xKVXHHlZAgowXSlUZARgQixjvdxX6uE9hSJpr76YSifh0SM7WZCkSDPsQc5XQ5ifTD0Edu4drr2rxfa7dgxdCZBWnzJ2oEWZBkZB07tYZARbkoVlFgMuHLj1lSevYD7SCpz8o8qLTdjfbJEdNCP5YUooEeYWZB7ZCiZBSXzhae54SZBTk2sZCoLfNLUnhibj0YTBUmLWQjZC0y9fLZApfDse67lYmc83rsu5ZAkvZAlnT5hRrrMV5Qb6p1HyM"
AD_ACCOUNT = "act_830580884293323"

date_preset = st.selectbox(
    "Select Date Range",
    ["today","yesterday","last_7d","last_30d"]
)

level = st.selectbox(
    "Breakdown Level",
    ["campaign","adset","ad"]
)

fields = """
campaign_name,
adset_name,
ad_name,
spend,
ctr,
cpc,
cpm,
frequency,
impressions,
clicks
"""

url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT}/insights"

params = {
    "level": level,
    "fields": fields,
    "date_preset": date_preset,
    "access_token": ACCESS_TOKEN
}

response = requests.get(url, params=params).json()
data = response.get("data", [])

if data:

    df = pd.DataFrame(data)

    numeric_cols = ["spend","ctr","cpc","cpm","frequency","impressions","clicks"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total Spend", f"${df['spend'].sum():.2f}")
    col2.metric("Average CTR", f"{df['ctr'].mean():.2f}%")
    col3.metric("Average CPC", f"${df['cpc'].mean():.2f}")
    col4.metric("Average CPM", f"${df['cpm'].mean():.2f}")

    st.divider()

    col5,col6 = st.columns(2)

    fig1 = px.bar(df, x="campaign_name", y="spend", title="Spend by Campaign")
    col5.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df, x="campaign_name", y="ctr", title="CTR by Campaign")
    col6.plotly_chart(fig2, use_container_width=True)

    st.divider()

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

    df["health_score"] = df.apply(health_score, axis=1)

    st.subheader("Campaign Health Score")

    st.dataframe(df[[
        "campaign_name",
        "adset_name",
        "ad_name",
        "spend",
        "ctr",
        "cpc",
        "cpm",
        "frequency",
        "health_score"
    ]])

    st.divider()

    def performance_issue(row):

        if row["ctr"] < 1:
            return "Creative Issue"

        if row["cpc"] > 2:
            return "Audience Targeting Issue"

        if row["cpm"] > 20:
            return "Audience Too Narrow"

        return "Healthy Campaign"

    df["performance_issue"] = df.apply(performance_issue, axis=1)

    st.subheader("Campaign Performance Analyzer")

    st.dataframe(df[[
        "campaign_name",
        "ctr",
        "cpc",
        "cpm",
        "performance_issue"
    ]])

    st.divider()

    def creative_fatigue(row):

        if row["frequency"] > 3 and row["ctr"] < 1.5:
            return "Creative Fatigue"

        return "Healthy"

    df["creative_status"] = df.apply(creative_fatigue, axis=1)

    st.subheader("Creative Fatigue Detection")

    fatigue = df[df["creative_status"] == "Creative Fatigue"]

    if len(fatigue) > 0:

        for i,row in fatigue.iterrows():

            st.warning(
                f"Creative fatigue detected in {row['campaign_name']} "
                f"(Frequency {row['frequency']})"
            )

    else:

        st.success("No creative fatigue detected")

    st.divider()

    def scaling_engine(row):

        if row["ctr"] > 2 and row["cpc"] < 1 and row["frequency"] < 3:
            return "Scale Budget"

        if row["ctr"] < 1:
            return "Test New Creatives"

        if row["cpc"] > 2:
            return "Fix Audience Targeting"

        if row["cpm"] > 20:
            return "Expand Audience"

        return "Monitor"

    df["scaling_signal"] = df.apply(scaling_engine, axis=1)

    st.subheader("Scaling Recommendations")

    for i,row in df.iterrows():

        if row["scaling_signal"] == "Scale Budget":

            st.success(
                f"{row['campaign_name']} → Scale budget by 20%"
            )

    st.divider()

    st.subheader("Pause Campaign Signals")

    pause_campaigns = df[(df["ctr"] < 0.8) & (df["cpc"] > 3)]

    if len(pause_campaigns) > 0:

        for i,row in pause_campaigns.iterrows():

            st.error(
                f"{row['campaign_name']} → Recommend pausing "
                f"(CTR {row['ctr']} CPC {row['cpc']})"
            )

    else:

        st.success("No campaigns require pausing")

    st.divider()

    st.subheader("AI Optimization Signals")

    for i,row in df.iterrows():

        signals = []

        if row["ctr"] < 1:
            signals.append("Creative Issue")

        if row["cpc"] > 2:
            signals.append("Audience Issue")

        if row["cpm"] > 20:
            signals.append("High CPM")

        if row["frequency"] > 3:
            signals.append("Creative Fatigue")

        if row["ctr"] > 2 and row["cpc"] < 1:
            signals.append("Scale Campaign")

        if signals:

            st.write(f"**{row['campaign_name']}**")

            for s in signals:
                st.write("•", s)

    st.divider()

    if level == "adset":

        st.subheader("Best Audience Detector")

        best_audience = df.sort_values("ctr", ascending=False).head(5)

        st.dataframe(best_audience[
            ["adset_name","ctr","cpc","cpm"]
        ])

    if level == "ad":

        st.subheader("Creative Performance Analyzer")

        best_ads = df.sort_values("ctr", ascending=False).head(5)

        st.dataframe(best_ads[
            ["ad_name","ctr","cpc","spend"]
        ])

    best = df.sort_values("ctr", ascending=False).iloc[0]

    st.success(
        f"Best Performer: {best['campaign_name']} "
        f"(CTR {best['ctr']}%)"
    )

else:

    st.error("No data returned from Meta API")
