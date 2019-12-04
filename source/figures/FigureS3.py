import pandas as pd
import os
import sys
from functools import partial

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

rhos = [0, 0.5, 1.0, 4.02]

y_pred_file, out_file = sys.argv[3:]

def cost_ratio(rho, df):
    tp = (df.y_test == 1).sum() / len(df)
    tp = tp * (1 - rho * (df.y_pred.sum() / len(df)))
    fp = (df.y_test == 0).sum() / len(df)
    return tp/(fp+tp)

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)

decile = len(y) // 10

replicates = [y.sample(n=len(y),
                       replace=True,
                       random_state=seed+i).sort_values("y_pred", ascending=False)
              for i in range(n_bootstrap)]

with open(out_file, "w") as f:

    print("Decile", "Rho", "Yhat", "TPR", "CostRatio", "CostRatioLower", "CostRatioUpper", sep=",", file=f)

    for i in range(1, 11):

        yi = y.iloc[:i*decile]
        ris = [r.iloc[:i*decile] for r in replicates]

        # Recompute for each rho
        for rho in rhos:
            bootstraps = sorted(map(partial(cost_ratio, rho), ris))
            estimates = map("{:.3f}".format, [yi.y_pred.sum() / len(yi),
                                              (yi.y_test == 1).sum() / len(yi),
                                              cost_ratio(rho, yi),
                                              bootstraps[int(0.025 * len(bootstraps))],
                                              bootstraps[int(0.975 * len(bootstraps))]])
            print(i, rho, *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
