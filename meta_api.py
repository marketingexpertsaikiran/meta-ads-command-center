import requests
import pandas as pd

API = "https://graph.facebook.com/v19.0"


def get_account_info(account_id, token):

    url = f"{API}/{account_id}"

    params = {
        "fields": "name,currency",
        "access_token": token
    }

    return requests.get(url, params=params).json()


def get_insights(account_id, token, date):

    fields = """
campaign_name,
adset_name,
ad_name,
spend,
ctr,
cpc,
cpm,
cpp,
frequency,
reach,
impressions,
clicks,
actions,
unique_clicks,
cost_per_action_type,
video_plays,
landing_page_views,
purchase_roas
"""

    url = f"{API}/{account_id}/insights"

    params = {
        "fields": fields,
        "level": "ad",
        "date_preset": date,
        "access_token": token
    }

    data = requests.get(url, params=params).json()["data"]

    return pd.DataFrame(data)


def get_targeting(account_id, token):

    url = f"{API}/{account_id}/adsets"

    params = {
        "fields": "name,targeting",
        "limit": 200,
        "access_token": token
    }

    res = requests.get(url, params=params).json()

    return res["data"]


def search_interests(keyword, token):

    url = f"{API}/search"

    params = {
        "type": "adinterest",
        "q": keyword,
        "limit": 50,
        "access_token": token
    }

    return requests.get(url, params=params).json()["data"]
