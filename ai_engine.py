import numpy as np
from sklearn.linear_model import LinearRegression

def campaign_audit(df):

    results=[]

    for _,r in df.iterrows():

        if r.ctr < 1:
            results.append("Creative Problem")

        elif r.cpm > 20:
            results.append("Audience Too Narrow")

        elif r.frequency > 3:
            results.append("Creative Fatigue")

        elif r.cpc > 2:
            results.append("Low Intent Traffic")

        else:
            results.append("Healthy")

    df["AI_Audit"]=results

    return df


def predict_cpa(df):

    df["CPA"]=df.spend/df.clicks

    X=np.arange(len(df)).reshape(-1,1)
    y=df["CPA"].values

    model=LinearRegression()
    model.fit(X,y)

    pred=model.predict([[len(df)+1]])

    return pred[0]
