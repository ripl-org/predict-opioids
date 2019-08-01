import pandas as pd
import os
import sys
from functools import partial

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

alphas = [1.0, 0.8]

y_pred_file, out_file = sys.argv[3:]

def cost_ratio(alpha, df):
    tp = alpha * (df.y_test == 1).sum()
    fp = (df.y_test == 0).sum()
    return tp/(fp+tp)

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)

decile = len(y) // 10

replicates = [y.sample(n=len(y),
                       replace=True,
                       random_state=seed+i).sort_values("y_pred", ascending=False)
              for i in range(n_bootstrap)]

with open(out_file, "w") as f:

    print("Decile", "Alpha", "CostRatio", "CostRatioLower", "CostRatioUpper", sep=",", file=f)

    for i in range(1, 11):

        yi = y.iloc[:i*decile]
        ris = [r.iloc[:i*decile] for r in replicates]

        # Recompute for each alpha
        for alpha in alphas:
            bootstraps = sorted(map(partial(cost_ratio, alpha), ris))
            estimates = map("{:.3f}".format, [cost_ratio(alpha, yi),
                                              bootstraps[int(0.025 * len(bootstraps))],
                                              bootstraps[int(0.975 * len(bootstraps))]])
            print(i, alpha, *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
