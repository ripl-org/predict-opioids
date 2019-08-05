import pandas as pd
import os
import sys

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

y_pred_file, demo_file, doc_file, med_file, out_file = sys.argv[3:]

def fdr(df):
    tp = (df.y_test == 1).sum()
    fp = (df.y_test == 0).sum()
    return fp/(fp+tp)

y = pd.read_csv(y_pred_file).sort_values("y_pred", ascending=False)\
      .merge(pd.read_csv(demo_file), on="RIIPL_ID")\
      .merge(pd.read_csv(doc_file),  on="RIIPL_ID")\
      .merge(pd.read_csv(med_file),  on="RIIPL_ID")

y["RACE_WHITE"] = ((y.RACE_BLACK | y.RACE_HISPANIC | y.RACE_OTHER | y.RACE_MISSING) + 1) % 2
y["RACE_MINORITY"] = y.RACE_BLACK | y.RACE_HISPANIC | y.RACE_OTHER
y["INCARC"] = y.DOC_COMMITED | y.DOC_RELEASED
y["NINCARC"] = ~y.INCARC
y["DISABLED"] = y.MEDICAID_DISABLED
y["NDISABLED"] = ~y.DISABLED

decile = len(y) // 10

print("Incarceration for top 2 risk deciles:", y.iloc[:2*decile]["INCARC"].mean())
print("Incarceration for lower 8 risk deciles:", y.iloc[2*decile:]["INCARC"].mean())

replicates = [y.sample(n=len(y),
                       replace=True,
                       random_state=seed+i).sort_values("y_pred", ascending=False)
              for i in range(n_bootstrap)]

with open(out_file, "w") as f:

    print("Decile", "Demographic", "N", "FDR", "FDRLower", "FDRUpper", sep=",", file=f)

    for i in range(1, 11):

        yi = y.iloc[:i*decile]
        ris = [r.iloc[:i*decile] for r in replicates]

        # Recompute for each demographic
        for var in ["RIIPL_ID", "RACE_MINORITY", "RACE_WHITE", "INCARC", "NINCARC", "DISABLED", "NDISABLED"]:

            yd = yi[yi[var] != 0]
            if len(yd) < 11:
                estimates = ["NA", "NA", "NA"]
            else:
                bootstraps = sorted(map(fdr, [ri[ri[var] != 0] for ri in ris]))
                estimates = map("{:.3f}".format, [fdr(yd),
                                                  bootstraps[int(0.025 * len(bootstraps))],
                                                  bootstraps[int(0.975 * len(bootstraps))]])
            print(i, var, len(yd), *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
