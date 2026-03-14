import requests
import pandas as pd

API="https://graph.facebook.com/v19.0"

def get_accounts(token):

    url=f"{API}/me/adaccounts"

    r=requests.get(url,params={
        "fields":"name,account_id,currency",
        "access_token":token
    }).json()

    return r["data"]


def get_insights(token,account_id,level,date):

    fields="""
    campaign_name,
    adset_name,
    ad_name,
    spend,
    ctr,
    cpc,
    cpm,
    frequency,
    reach,
    impressions,
    clicks
    """

    url=f"{API}/act_{account_id}/insights"

    r=requests.get(url,params={
        "level":level,
        "fields":fields,
        "date_preset":date,
        "limit":500,
        "access_token":token
    }).json()

    df=pd.DataFrame(r["data"])

    for c in ["spend","ctr","cpc","cpm","frequency","clicks","impressions"]:
        df[c]=pd.to_numeric(df[c])

    return df
