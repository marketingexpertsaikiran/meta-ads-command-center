import requests

def get_competitor_ads(keyword):

    url = "https://graph.facebook.com/v19.0/ads_archive"

    params = {
        "search_terms":keyword,
        "ad_reached_countries":["US","IN"],
        "ad_type":"ALL",
        "limit":10
    }

    response = requests.get(url,params=params).json()

    ads = []

    for ad in response.get("data",[]):

        ads.append({
            "Page":ad.get("page_name"),
            "Ad Text":ad.get("ad_creative_body"),
            "Start Date":ad.get("ad_delivery_start_time")
        })

    return ads
