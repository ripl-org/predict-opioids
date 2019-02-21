import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

infile, outfile = sys.argv[1:]

data = pd.read_csv(infile)

def classify(var):
    if var.startswith("MEDICAID") or var.startswith("ASHP"):
        return "Medicaid"
    elif var.startswith("DOC") or var == "CITATIONS":
        return "Criminal History"
    elif var.startswith("DHS") or var.startswith("SNAP"):
        return "Social Services"
    elif var.startswith("WAGE") or var.startswith("UI") or var == "UNEMP_RI":
        return "Labor & Training"
    else:
        return "Demographics"

data["category"] = data.var.apply(classify)

plt.figure(figsize=(6, 6))
sns.stripplot(x="odds", y="category", orient="h")
plt.tight_layout()
plt.savefig(outfile)

# vim: syntax=python expandtab sw=4 ts=4
