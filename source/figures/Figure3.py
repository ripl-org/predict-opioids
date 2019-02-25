import pandas as pd
import os
import sys
from bootstrap import bootstrap

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

y_pred_file, out_file = sys.argv[3:]

def cost_ratio(data):
    tp = (data.y_test == 1).sum()
    fp = (data.y_test == 0).sum()
    return tp/(fp+tp)

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)

decile = len(y) // 10

with open(out_file, "w") as f:
    print("Decile,CostRatio,CostRatioLower,CostRatioUpper", file=f)
    for i in range(1, 11):
        data = y.iloc[(i-1)*decile:i*decile]
        estimates = map("{:.3f}".format, bootstrap(data, n_bootstrap, cost_ratio, seed))
        print(i, *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
