import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import sys

infile, outfile = sys.argv[1:]

table = pd.read_csv(infile)

categories = ["Medicaid", "Demographics", "Labor & Training", "Criminal History", "Social Services"]
odds = dict((c, []) for c in categories)

for row in table.itertuples():
    if row.var.startswith("MEDICAID") or row.var.starts("ASHP"):
        odds["Medicaid"].append(row.odds)
    elif row.var.startswith("DOC") or row.var == "CITATIONS":
        odds["Criminal History"].append(row.odds)
    elif row.var.startswith("DHS") or row.var.startswith("SNAP"):
        odds["Social Services"].append(row.odds)
    elif row.var.startswith("WAGE") or row.var.startswith("UI") or row.var == "UNEMP_RI":
        odds["Labor & Training"].append(row.odds)
    else:
        odds["Demographics"].append(row.odds)

sns.swarmplot(x=[odds[c] for c in categories], y=categories)
plt.savefig(outfile)

# vim: syntax=python expandtab sw=4 ts=4
