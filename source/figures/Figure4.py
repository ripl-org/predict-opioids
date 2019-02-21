import pandas as pd
import os
import sys
from bootstrap import bootstrap

seed        = int(sys.argv[1])
n_bootstrap = int(sys.argv[2])

y_pred_file, demo_file, doc_file, med_file, out_file = sys.argv[3:]

def fdr(data):
    tp = (data.y_test == 1).sum()
    fp = (data.y_test == 0).sum()
    return fp/(fp+tp)

y = pd.read_csv(y_pred_file, index_col="RIIPL_ID")\
      .join(pd.read_csv(demo_file, index_col="RIIPL_ID"))\
      .join(pd.read_csv(doc_file, index_col="RIIPL_ID"))\
      .join(pd.read_csv(med_file, index_col="RIIPL_ID"))\
      .sort_values("y_pred", ascending=False)

y["RACE_WHITE"] = ((y.RACE_BLACK | y.RACE_HISPANIC | y.RACE_OTHER | y.RACE_MISSING) + 1) % 2
y["INCARCERATED"] = y.DOC_COMMITED | y.DOC_RELEASED
y["NOT_INCARCERATED"] = (y.INCARCERATED + 1) % 2
y["NOT_DISABLED"] = (y.MEDICAID_DISABLED + 1) % 2

quintile = len(y) // 5

selections = [
    ("Race", "African-American", "RACE_BLACK"),
    ("Race", "Hispanic", "RACE_HISPANIC"),
    ("Race", "White", "RACE_WHITE"),
    ("Incarcerated", "Yes", "INCARCERATED"),
    ("Incarcerated", "No", "NOT_INCARCERATED"),
    ("Disabled", "Yes", "MEDICAID_DISABLED"),
    ("Disabled", "No", "NOT_DISABLED")
]

with open(out_file, "w") as f:
    print("Quintile,Characteristic,Group,N,FDR,FDRLower,FDRUpper", file=f)
    for i in range(1, 6):
        data = y.iloc[(i-1)*quintile:i*quintile]
        for selection in selections:
            group = data[data[selection[2]] == 1]
            if len(group) >= 11:
                estimates = map("{:.3f}".format, bootstrap(group, n_bootstrap, fdr, seed))
            else:
                estimates = ["", "", ""]
            print(i, selection[0], selection[1], len(group), *estimates, sep=",", file=f)

# vim: syntax=python expandtab sw=4 ts=4
