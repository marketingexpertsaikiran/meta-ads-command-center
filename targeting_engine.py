import pandas as pd

def extract_targeting(adsets):

    rows = []

    for a in adsets:

        interests = []

        targeting = a.get("targeting",{})

        if "flexible_spec" in targeting:

            for g in targeting["flexible_spec"]:

                if "interests" in g:

                    for i in g["interests"]:
                        interests.append(i["name"])

        rows.append({

            "Adset":a["name"],
            "Interests":",".join(interests),
            "Optimization":a.get("optimization_goal"),
            "Budget":a.get("daily_budget")

        })

    return pd.DataFrame(rows)
