import pandas as pd


def health_score(row):

    score = 100

    if row["ctr"] < 1:
        score -= 30

    if row["cpc"] > 2:
        score -= 20

    if row["cpm"] > 20:
        score -= 20

    if row["frequency"] > 3:
        score -= 10

    return score


def scaling_engine(row):

    if row["ctr"] > 2.5 and row["cpc"] < 1:
        return "Scale Budget"

    if row["ctr"] < 1:
        return "Creative Issue"

    if row["cpm"] > 20:
        return "Audience Narrow"

    if row["frequency"] > 3:
        return "Creative Fatigue"

    return "Monitor"


def creative_winner(df):

    return df[(df["ctr"] > 2.5) & (df["cpc"] < 1)]


def creative_fatigue(df):

    return df[(df["frequency"] > 3) & (df["ctr"] < 1.5)]


def cpa_alert(df):

    df["CPA"] = df["spend"] / df["clicks"]

    df["change"] = df["CPA"].pct_change()

    return df[df["change"] > 0.5]
