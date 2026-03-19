import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AI Marketing Command Center", layout="wide")

st.title("🔥 AI Marketing Command Center")

menu = st.sidebar.selectbox(
    "Select Tool",
    [
        "Competitor Ads Research",
        "Campaign Optimizer",
        "Creative Fatigue Predictor",
        "Landing Page CVR Analyzer",
        "Budget Scaling Engine",
        "Campaign Audit Report"
    ]
)

# -----------------------------
# 1 COMPETITOR ADS RESEARCH
# -----------------------------

if menu == "Competitor Ads Research":

    st.header("Competitor Ads Research")

    token = st.text_input("Enter Meta Access Token", type="password")

    brand = st.text_input("Competitor Brand")

    country = st.selectbox(
        "Country",
        ["IN","US","CA","GB","AU"]
    )

    limit = st.slider("Number of Ads",1,20,5)

    if st.button("Search Ads"):

        url = "https://graph.facebook.com/v19.0/ads_archive"

        params = {
            "search_terms": brand,
            "ad_reached_countries": [country],
            "ad_type": "ALL",
            "fields": "page_name,ad_creative_body,ad_snapshot_url,ad_delivery_start_time",
            "limit": limit,
            "access_token": token
        }

        response = requests.get(url, params=params)

        data = response.json()

        ads = data.get("data", [])

        if len(ads) == 0:
            st.warning("No ads found")

        else:

            for ad in ads:

                st.subheader(ad.get("page_name"))

                st.write(ad.get("ad_creative_body"))

                st.write("Start Date:", ad.get("ad_delivery_start_time"))

                preview = ad.get("ad_snapshot_url")

                if preview:
                    st.components.v1.iframe(preview, height=500)

                st.divider()


# -----------------------------
# 2 CAMPAIGN OPTIMIZER
# -----------------------------

elif menu == "Campaign Optimizer":

    st.header("AI Campaign Optimizer")

    ctr = st.number_input("CTR (%)",0.0,100.0)
    cvr = st.number_input("Conversion Rate (%)",0.0,100.0)
    cpa = st.number_input("CPA ($)",0.0)

    if st.button("Analyze Campaign"):

        if ctr < 1:
            st.warning("Low CTR — Improve Creatives")

        elif ctr > 3:
            st.success("CTR is strong")

        if cvr < 2:
            st.warning("Low CVR — Landing page problem")

        if cpa > 50:
            st.warning("CPA too high — refine targeting")


# -----------------------------
# 3 CREATIVE FATIGUE
# -----------------------------

elif menu == "Creative Fatigue Predictor":

    st.header("Creative Fatigue Predictor")

    frequency = st.number_input("Ad Frequency",0.0)
    ctr = st.number_input("CTR (%)",0.0)

    if st.button("Predict Fatigue"):

        if frequency > 3 and ctr < 1:
            st.error("Creative Fatigue Detected")

        else:
            st.success("Creative performing well")


# -----------------------------
# 4 LANDING PAGE ANALYZER
# -----------------------------

elif menu == "Landing Page CVR Analyzer":

    st.header("Landing Page Analyzer")

    clicks = st.number_input("Clicks",0)
    conversions = st.number_input("Conversions",0)

    if st.button("Analyze"):

        if clicks > 0:

            cvr = conversions / clicks * 100

            st.write("Conversion Rate:", round(cvr,2), "%")

            if cvr < 2:
                st.warning("Landing page needs optimization")

            else:
                st.success("Landing page performing well")


# -----------------------------
# 5 BUDGET SCALING ENGINE
# -----------------------------

elif menu == "Budget Scaling Engine":

    st.header("Meta Ads Budget Scaling Engine")

    cpa = st.number_input("Current CPA",0.0)
    target_cpa = st.number_input("Target CPA",0.0)

    if st.button("Scaling Suggestion"):

        if cpa < target_cpa:
            st.success("Increase budget by 20%")

        elif cpa > target_cpa:
            st.warning("Reduce budget or improve creatives")


# -----------------------------
# 6 CAMPAIGN AUDIT
# -----------------------------

elif menu == "Campaign Audit Report":

    st.header("Campaign Audit")

    ctr = st.number_input("CTR",0.0)
    cpc = st.number_input("CPC",0.0)
    cpa = st.number_input("CPA",0.0)

    if st.button("Generate Audit"):

        report = []

        if ctr < 1:
            report.append("Improve creatives")

        if cpc > 2:
            report.append("Audience targeting may be wrong")

        if cpa > 50:
            report.append("Optimize funnel")

        if len(report) == 0:
            st.success("Campaign healthy")

        else:

            st.subheader("Audit Findings")

            for r in report:
                st.write("-", r)
