import pandas as pd

def detect_overlap(df):

    overlaps = []

    for i in range(len(df)):

        for j in range(i+1,len(df)):

            set1 = set(df.iloc[i]["Interests"].split(","))
            set2 = set(df.iloc[j]["Interests"].split(","))

            common = set1.intersection(set2)

            if len(common) > 0:

                overlaps.append({
                    "Adset A":df.iloc[i]["Adset"],
                    "Adset B":df.iloc[j]["Adset"],
                    "Overlap":",".join(common)
                })

    return pd.DataFrame(overlaps)
