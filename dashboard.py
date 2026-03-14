import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta Ads Command Center", layout="wide")

st.markdown("""
<style>
.main-title {
    font-size:40px;
    font-weight:700;
}
.card {
    padding:15px;
    border-radius:10px;
    background-color:#111827;
    color:white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🚀 Meta Ads AI Command Center</p>', unsafe_allow_html=True)

# -------- MULTI ACCOUNT CONFIG --------

accounts = {
    "Account 1": {
        "account_id": "act_830580884293323",
        "access_token": "EAAV8gZAY7XdEBQ7qsPauJ5ewD8NwX4HF40bqZBaYNZAQKAL0wdCgA9y1YL9jYwTZCUEpyNNU9N3zgUZBr5Ty3gcMGShxbEW8FtonsalL6pSiRZCWY6ZAlhjTnUIhpeLHHrsuXlvdRCo6ZBdu9OpE8Xf7zDs4KixzLskgntEmaIZBA3jzYO3a2idZCi5I8pusy8CX2D0TZCrQWeRaGZB3il4Wrdxp9lzxAME3NMggnZBxLZC0OQns46J7SKRhgmFYaqDc4V7ZCU62wUwikoFnZC0O5F3q3kDJUydHswZDZD"
    },
    "Account 2": {
        "account_id": "act_415698175733898",
        "access_token": "EAAV8gZAY7XdEBQ7qsPauJ5ewD8NwX4HF40bqZBaYNZAQKAL0wdCgA9y1YL9jYwTZCUEpyNNU9N3zgUZBr5Ty3gcMGShxbEW8FtonsalL6pSiRZCWY6ZAlhjTnUIhpeLHHrsuXlvdRCo6ZBdu9OpE8Xf7zDs4KixzLskgntEmaIZBA3jzYO3a2idZCi5I8pusy8CX2D0TZCrQWeRaGZB3il4Wrdxp9lzxAME3NMggnZBxLZC0OQns46J7SKRhgmFYaqDc4V7ZCU62wUwikoFnZC0O5F3q3kDJUydHswZDZD"
    }
}

selected_account = st.sidebar.selectbox("Select Ad Account", list(accounts.keys()))

ACCESS_TOKEN = accounts[selected_account]["access_token"]
AD_ACCOUNT = accounts[selected_account]["account_id"]

date_preset = st.sidebar.selectbox(
    "Date Range",
    ["today","yesterday","last_7d","last_30d"]
)

level = st.sidebar.selectbox(
    "Data Level",
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

    # ---------- KPI DASHBOARD ----------

    c1,c2,c3,c4 = st.columns(4)

    if "spend" in df.columns:
        c1.metric("Total Spend", f"${df['spend'].sum():.2f}")

    if "ctr" in df.columns:
        c2.metric("Avg CTR", f"{df['ctr'].mean():.2f}%")

    if "cpc" in df.columns:
        c3.metric("Avg CPC", f"${df['cpc'].mean():.2f}")

    if "cpm" in df.columns:
        c4.metric("Avg CPM", f"${df['cpm'].mean():.2f}")

    st.divider()

    # ---------- CHARTS ----------

    chart1, chart2 = st.columns(2)

    if "campaign_name" in df.columns and "spend" in df.columns:
        fig = px.bar(df, x="campaign_name", y="spend", title="Campaign Spend")
        chart1.plotly_chart(fig, use_container_width=True)

    if "campaign_name" in df.columns and "ctr" in df.columns:
        fig = px.bar(df, x="campaign_name", y="ctr", title="Campaign CTR")
        chart2.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------- HEALTH SCORE ----------

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

    df["health_score"] = df.apply(health_score, axis=1)

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

    st.dataframe(df[cols], use_container_width=True)

    st.divider()

    # ---------- PERFORMANCE ANALYZER ----------

    def analyze(row):

        if "ctr" in row and row["ctr"] < 1:
            return "Creative Problem"

        if "cpc" in row and row["cpc"] > 2:
            return "Audience Problem"

        if "cpm" in row and row["cpm"] > 20:
            return "High CPM"

        return "Healthy"

    df["issue"] = df.apply(analyze, axis=1)

    st.subheader("Performance Analyzer")

    cols = ["campaign_name","ctr","cpc","cpm","issue"]
    cols = [c for c in cols if c in df.columns]

    st.dataframe(df[cols], use_container_width=True)

    st.divider()

    # ---------- CREATIVE FATIGUE ----------

    st.subheader("Creative Fatigue Alerts")

    if "frequency" in df.columns and "ctr" in df.columns:

        fatigue = df[(df["frequency"] > 3) & (df["ctr"] < 1.5)]

        if len(fatigue):

            for i,row in fatigue.iterrows():

                st.warning(
                    f"{row.get('campaign_name','Campaign')} → Creative fatigue detected"
                )

        else:

            st.success("No fatigue detected")

    st.divider()

    # ---------- SCALING ENGINE ----------

    def scale(row):

        if "ctr" in row and "cpc" in row:

            if row["ctr"] > 2 and row["cpc"] < 1:
                return "Scale Budget"

        if "ctr" in row and row["ctr"] < 1:
            return "Test Creatives"

        if "cpc" in row and row["cpc"] > 2:
            return "Fix Targeting"

        return "Monitor"

    df["scale_signal"] = df.apply(scale, axis=1)

    st.subheader("Scaling Recommendations")

    for i,row in df.iterrows():

        if row["scale_signal"] == "Scale Budget":

            st.success(
                f"{row.get('campaign_name','Campaign')} → Scale budget 20%"
            )

    st.divider()

    # ---------- PAUSE SIGNAL ----------

    st.subheader("Pause Signals")

    if "ctr" in df.columns and "cpc" in df.columns:

        pause = df[(df["ctr"] < 0.8) & (df["cpc"] > 3)]

        if len(pause):

            for i,row in pause.iterrows():

                st.error(
                    f"{row.get('campaign_name','Campaign')} → Recommend Pause"
                )

        else:

            st.success("No campaigns require pausing")

    st.divider()

    # ---------- AI SIGNALS ----------

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
                st.write("•", s)

    st.divider()

    # ---------- BEST AUDIENCE ----------

    if level == "adset" and "ctr" in df.columns:

        st.subheader("Best Audience Segments")

        best = df.sort_values("ctr", ascending=False).head(5)

        cols = ["adset_name","ctr","cpc","cpm"]
        cols = [c for c in cols if c in df.columns]

        st.dataframe(best[cols], use_container_width=True)

    # ---------- BEST CREATIVE ----------

    if level == "ad" and "ctr" in df.columns:

        st.subheader("Top Creatives")

        best = df.sort_values("ctr", ascending=False).head(5)

        cols = ["ad_name","ctr","cpc","spend"]
        cols = [c for c in cols if c in df.columns]

        st.dataframe(best[cols], use_container_width=True)

    # ---------- BEST CAMPAIGN ----------

    if "ctr" in df.columns and "campaign_name" in df.columns:

        best = df.sort_values("ctr", ascending=False).iloc[0]

        st.success(
            f"🏆 Best Campaign → {best['campaign_name']} (CTR {best['ctr']}%)"
        )

else:

    st.error("No data returned from Meta API")
