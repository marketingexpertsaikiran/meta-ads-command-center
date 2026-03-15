import streamlit as st

APP_ID = "1544270896651729"
REDIRECT_URI = "https://meta-ads-command-center.streamlit.app/"

def login():

    login_url = f"https://www.facebook.com/v19.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=ads_read,business_management"

    st.link_button("Login with Meta",login_url)
