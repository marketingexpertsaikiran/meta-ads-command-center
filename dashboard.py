import streamlit as st
import plotly.express as px
from auth import login
from meta_api import get_accounts,get_insights
from ai_engine import campaign_audit,predict_cpa
from competitor_ads import search_ads
from report_generator import generate_report

st.set_page_config(layout="wide")

st.title("🚀 Meta Ads AI Command Center")

if not login():
    st.stop()

token=st.sidebar.text_input("Meta Access Token")

accounts=get_accounts(token)

names=[a["name"] for a in accounts]

acc=st.sidebar.selectbox("Ad Account",names)

account_id=None

for a in accounts:
    if a["name"]==acc:
        account_id=a["account_id"]

level=st.sidebar.selectbox("Level",["campaign","adset","ad"])

date=st.sidebar.selectbox("Date",["yesterday","last_7d","last_30d"])

df=get_insights(token,account_id,level,date)

c1,c2,c3,c4=st.columns(4)

c1.metric("Spend",df.spend.sum())
c2.metric("CTR",df.ctr.mean())
c3.metric("CPC",df.cpc.mean())
c4.metric("CPM",df.cpm.mean())

tabs=st.tabs(["Performance","AI Audit","Competitor Ads","Reports"])

with tabs[0]:

    fig=px.bar(df,x="campaign_name",y="spend")

    st.plotly_chart(fig,use_container_width=True)

    st.dataframe(df)

with tabs[1]:

    df=campaign_audit(df)

    st.dataframe(df[["campaign_name","AI_Audit"]])

    pred=predict_cpa(df)

    st.metric("Predicted CPA",pred)

with tabs[2]:

    keyword=st.text_input("Search Competitor")

    if keyword:

        ads=search_ads(keyword,token)

        st.write(ads)

with tabs[3]:

    if st.button("Generate Client Report"):

        file=generate_report(
            df.spend.sum(),
            df.ctr.mean(),
            df.cpc.mean()
        )

        with open(file,"rb") as f:

            st.download_button("Download",f,"report.pdf")
