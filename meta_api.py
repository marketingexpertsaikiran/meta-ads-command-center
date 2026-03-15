import requests
import pandas as pd

GRAPH = "https://graph.facebook.com/v19.0"


def get_ad_accounts(token):

    url = f"{GRAPH}/me/adaccounts"

    params = {
        "fields":"name,account_id,currency",
        "access_token":token
    }

    res = requests.get(url,params=params).json()

    return res.get("data",[])


def get_insights(account_id,token,level,date):

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
    reach,
    clicks,
    actions
    """

    url = f"{GRAPH}/act_{account_id}/insights"

    params = {
        "fields":fields,
        "level":level,
        "date_preset":date,
        "limit":500,
        "access_token":token
    }

    res = requests.get(url,params=params).json()

    df = pd.DataFrame(res.get("data",[]))

    return df


def get_targeting(account_id,token):

    url = f"{GRAPH}/act_{account_id}/adsets"

    params = {
        "fields":"name,targeting,optimization_goal,daily_budget",
        "access_token":token
    }

    res = requests.get(url,params=params).json()

    return res.get("data",[])
