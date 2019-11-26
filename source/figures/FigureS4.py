import pandas as pd
import os
import sys
from functools import partial

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

c_a = 450000
c_d = 104400

y_pred_file, out_file = sys.argv[3:]

def rho(c_d, df):
    tp = (df.y_test == 1).sum()
    fp = (df.y_test == 0).sum()
    return fp * c_d / (tp * tp * (c_a - c_d))

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)

decile = len(y) // 10

replicates = [y.sample(n=len(y),
                       replace=True,
                       random_state=seed+i).sort_values("y_pred", ascending=False)
              for i in range(n_bootstrap)]

with open(out_file, "w") as f:

    print("Decile", "DiversionCost", "Rho", "RhoLower", "RhoUpper", sep=",", file=f)

    for i in range(1, 11):

        yi = y.iloc[:i*decile]
        ris = [r.iloc[:i*decile] for r in replicates]

        # Recompute for each diversion cost
        for c in [0.5*c_d, c_d, 1.5*c_d]:
            bootstraps = sorted(map(partial(rho, c), ris))
            estimates = map("{:.3f}".format, [rho(c, yi),
                                              bootstraps[int(0.025 * len(bootstraps))],
                                              bootstraps[int(0.975 * len(bootstraps))]])
            print(i, c, *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
