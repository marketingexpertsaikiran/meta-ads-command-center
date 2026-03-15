import requests

def find_ads(keyword):

    url = "https://graph.facebook.com/v19.0/ads_archive"

    params = {
        "search_terms":keyword,
        "ad_reached_countries":["US","IN"],
        "ad_type":"ALL",
        "limit":10
    }

    res = requests.get(url,params=params).json()

    return res.get("data",[])
