import requests

API="https://graph.facebook.com/v19.0"

def search_ads(keyword,token):

    url=f"{API}/ads_archive"

    r=requests.get(url,params={
        "search_terms":keyword,
        "ad_reached_countries":"US",
        "access_token":token
    }).json()

    return r
