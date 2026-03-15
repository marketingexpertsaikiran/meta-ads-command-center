import requests
import pandas as pd

GRAPH = "https://graph.facebook.com/v19.0"


def get_accounts(token):

    url = f"{GRAPH}/me/adaccounts"

    params = {
        "fields":"name,account_id,currency",
        "access_token":token
    }

    response = requests.get(url,params=params).json()

    return response.get("data",[])


def get_campaign_data(account_id,token,date,level):

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

    response = requests.get(url,params=params).json()

    df = pd.DataFrame(response.get("data",[]))

    return df
