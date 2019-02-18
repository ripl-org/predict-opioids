import pandas as pd
import sys

y_pred_file, outcomes_file, outcome, out_file = sys.argv[1:]

y_pred = pd.read_csv(y_pred_file, usecols=[1], names=["pred"])
y = pd.read_csv(outcomes_file)
y = y[y.SUBSET == "TESTING"]
y["pred"] = y_pred["pred"]
y["true"] = y[outcome]
y = y[["pred", "true"]].sort_values("pred", ascending=False)
decile = len(y) // 10
print("decile,size,outcomes")
for i in range(1, 11):
    y_i = y.loc[(i-1)*decile:i*decile]
    print("{},{},{}".format(i, decile, y_i["true"].sum()))

# vim: expandtab sw=4 ts=4
