def audit(row):

    if row["ctr"] < 1:
        return "Creative Problem"

    if row["cpc"] > 2:
        return "Audience Problem"

    if row["cpm"] > 20:
        return "High CPM"

    if row["frequency"] > 3:
        return "Creative Fatigue"

    return "Healthy"


def scaling_signal(row):

    if row["ctr"] > 2 and row["CPA"] < 20:
        return "Scale Budget"

    if row["CPA"] > 50:
        return "Pause Campaign"

    return "Monitor"
