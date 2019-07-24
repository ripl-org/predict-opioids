import pandas as pd
import os
import sys

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

y_pred_file, demo_file, out_file = sys.argv[3:]

def cost_ratio(df):
    tp = (df.y_test == 1).sum()
    fp = (df.y_test == 0).sum()
    return tp/(fp+tp)

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)\
      .merge(pd.read_csv(demo_file), on="RIIPL_ID")

y["RACE_WHITE"] = ((y.RACE_BLACK | y.RACE_HISPANIC | y.RACE_OTHER | y.RACE_MISSING) + 1) % 2

decile = len(y) // 10

replicates = [y.sample(n=len(y),
                       replace=True,
                       random_state=seed+i).sort_values("y_pred", ascending=False)
              for i in range(n_bootstrap)]

with open(out_file, "w") as f:

    print("Decile", "Race", "N", "CostRatio", "CostRatioLower", "CostRatioUpper", sep=",", file=f)

    for i in range(1, 11):

        yi = y.iloc[:i*decile]
        ris = [r.iloc[:i*decile] for r in replicates]

        # Recompute for each demographic
        for race, var in zip(["All", "Black", "Hispanic", "White"],
                             ["RIIPL_ID", "RACE_BLACK", "RACE_HISPANIC", "RACE_WHITE"]):

            yd = yi[yi[var] != 0]
            if len(yd) < 11:
                estimates = ["NA", "NA", "NA"]
            else:
                bootstraps = sorted(map(cost_ratio, [ri[ri[var] != 0] for ri in ris]))
                estimates = map("{:.3f}".format, [cost_ratio(yd),
                                                  bootstraps[int(0.025 * len(bootstraps))],
                                                  bootstraps[int(0.975 * len(bootstraps))]])
            print(i, race, len(yd), *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
