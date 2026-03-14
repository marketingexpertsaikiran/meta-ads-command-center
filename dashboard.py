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

fields = "campaign_name,adset_name,ad_name,spend,ctr,cpc,cpm,frequency,impressions,clicks"

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

    # KPI METRICS

    col1,col2,col3,col4 = st.columns(4)

    if "spend" in df.columns:
        col1.metric("Total Spend", f"${df['spend'].sum():.2f}")

    if "ctr" in df.columns:
        col2.metric("Average CTR", f"{df['ctr'].mean():.2f}%")

    if "cpc" in df.columns:
        col3.metric("Average CPC", f"${df['cpc'].mean():.2f}")

    if "cpm" in df.columns:
        col4.metric("Average CPM", f"${df['cpm'].mean():.2f}")

    st.divider()

    # CHARTS

    if "campaign_name" in df.columns:

        col5,col6 = st.columns(2)

        if "spend" in df.columns:

            fig1 = px.bar(df,x="campaign_name",y="spend",title="Spend by Campaign")
            col5.plotly_chart(fig1,use_container_width=True)

        if "ctr" in df.columns:

            fig2 = px.bar(df,x="campaign_name",y="ctr",title="CTR by Campaign")
            col6.plotly_chart(fig2,use_container_width=True)

    st.divider()

    # HEALTH SCORE

    def health_score(row):

        score = 100

        if "ctr" in row and row["ctr"] < 1:
            score -= 30

        if "cpc" in row and row["cpc"] > 2:
            score -= 20

        if "cpm" in row and row["cpm"] > 20:
            score -= 20

        if "frequency" in row and row["frequency"] > 3:
            score -= 10

        return score

    df["health_score"] = df.apply(health_score,axis=1)

    st.subheader("Campaign Health Score")

    available_cols = [
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

    existing_cols = [col for col in available_cols if col in df.columns]

    st.dataframe(df[existing_cols])

    st.divider()

    # PERFORMANCE ANALYZER

    def performance_issue(row):

        if "ctr" in row and row["ctr"] < 1:
            return "Creative Issue"

        if "cpc" in row and row["cpc"] > 2:
            return "Audience Targeting Issue"

        if "cpm" in row and row["cpm"] > 20:
            return "Audience Too Narrow"

        return "Healthy Campaign"

    df["performance_issue"] = df.apply(performance_issue,axis=1)

    st.subheader("Campaign Performance Analyzer")

    cols = ["campaign_name","ctr","cpc","cpm","performance_issue"]
    cols = [c for c in cols if c in df.columns]

    st.dataframe(df[cols])

    st.divider()

    # CREATIVE FATIGUE DETECTION

    st.subheader("Creative Fatigue Detection")

    if "frequency" in df.columns and "ctr" in df.columns:

        fatigue = df[(df["frequency"] > 3) & (df["ctr"] < 1.5)]

        if len(fatigue) > 0:

            for i,row in fatigue.iterrows():

                st.warning(
                    f"Creative fatigue detected in {row.get('campaign_name','Unknown')} "
                    f"(Frequency {row['frequency']})"
                )

        else:

            st.success("No creative fatigue detected")

    st.divider()

    # SCALING ENGINE

    def scaling_engine(row):

        if "ctr" in row and "cpc" in row and "frequency" in row:

            if row["ctr"] > 2 and row["cpc"] < 1 and row["frequency"] < 3:
                return "Scale Budget"

        if "ctr" in row and row["ctr"] < 1:
            return "Test New Creatives"

        if "cpc" in row and row["cpc"] > 2:
            return "Fix Audience Targeting"

        if "cpm" in row and row["cpm"] > 20:
            return "Expand Audience"

        return "Monitor"

    df["scaling_signal"] = df.apply(scaling_engine,axis=1)

    st.subheader("Scaling Recommendations")

    for i,row in df.iterrows():

        if row["scaling_signal"] == "Scale Budget":

            st.success(
                f"{row.get('campaign_name','Campaign')} → Scale budget by 20%"
            )

    st.divider()

    # PAUSE SIGNALS

    st.subheader("Pause Campaign Signals")

    if "ctr" in df.columns and "cpc" in df.columns:

        pause = df[(df["ctr"] < 0.8) & (df["cpc"] > 3)]

        if len(pause) > 0:

            for i,row in pause.iterrows():

                st.error(
                    f"{row.get('campaign_name','Campaign')} → Recommend pausing"
                )

        else:

            st.success("No campaigns require pausing")

    st.divider()

    # AI SIGNALS

    st.subheader("AI Optimization Signals")

    for i,row in df.iterrows():

        signals = []

        if "ctr" in row and row["ctr"] < 1:
            signals.append("Creative Issue")

        if "cpc" in row and row["cpc"] > 2:
            signals.append("Audience Issue")

        if "cpm" in row and row["cpm"] > 20:
            signals.append("High CPM")

        if "frequency" in row and row["frequency"] > 3:
            signals.append("Creative Fatigue")

        if "ctr" in row and "cpc" in row:
            if row["ctr"] > 2 and row["cpc"] < 1:
                signals.append("Scale Campaign")

        if signals:

            st.write(f"**{row.get('campaign_name','Campaign')}**")

            for s in signals:
                st.write("•",s)

    st.divider()

    # BEST AUDIENCE

    if level == "adset" and "ctr" in df.columns:

        st.subheader("🎯 Best Audience Segments")

        best = df.sort_values("ctr",ascending=False).head(5)

        cols = ["adset_name","ctr","cpc","cpm"]
        cols = [c for c in cols if c in df.columns]

        st.dataframe(best[cols])

    # BEST CREATIVE

    if level == "ad" and "ctr" in df.columns:

        st.subheader("🎨 Best Creatives")

        best_ads = df.sort_values("ctr",ascending=False).head(5)

        cols = ["ad_name","ctr","cpc","spend"]
        cols = [c for c in cols if c in df.columns]

        st.dataframe(best_ads[cols])

    # BEST CAMPAIGN

    if "ctr" in df.columns and "campaign_name" in df.columns:

        best = df.sort_values("ctr",ascending=False).iloc[0]

        st.success(
            f"🏆 Best Performer: {best['campaign_name']} (CTR {best['ctr']}%)"
        )

else:

    st.error("No data returned from Meta API")
