def recommend_budget(row):

    if row["CPA"] < 20 and row["ctr"] > 2:
        return "Increase Budget 20%"

    if row["CPA"] > 50:
        return "Reduce Budget"

    return "Keep Budget Same"
