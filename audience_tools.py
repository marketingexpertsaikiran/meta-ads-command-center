import pandas as pd

def detect_overlap(targeting_df):

    overlaps = []

    for i in range(len(targeting_df)):
        for j in range(i+1,len(targeting_df)):

            set1 = set(targeting_df.iloc[i]["Interests"].split(","))
            set2 = set(targeting_df.iloc[j]["Interests"].split(","))

            common = set1.intersection(set2)

            if len(common) > 0:

                overlaps.append({
                    "Adset A":targeting_df.iloc[i]["Adset Name"],
                    "Adset B":targeting_df.iloc[j]["Adset Name"],
                    "Common Interests":",".join(common)
                })

    return pd.DataFrame(overlaps)
