import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

infile, outfile = sys.argv[1:]

data = pd.read_csv(infile)

outliers = ["DOC_RELEASED", "MEDICAID_PAYER_RIPAE", "RACE_HISPANIC", "MEDICAID_CTG_NEEDY",
            "UNEMP_RI", "SNAP_PAYMENTS"]

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

data["category"] = data["var"].apply(classify)

categories = dict((c, i) for i, c in enumerate(data.category.unique()))

plt.figure(figsize=(8, 6))
sns.stripplot(x="odds", y="category", data=data, orient="h", jitter=0.2)
plt.title("Logit odds ratios for BOLASSO-selected predictors, by category", loc="left")
plt.xlabel("")
plt.ylabel("")
plt.grid(True, which="major", axis="x", color="k", linestyle=".")
plt.grid(True, which="minor", axis="y", color="w", linewidth=10)
plt.axvline(1.0, color="k", linewidth=1.5)

# Annotate outliers
for var in outliers:
    row = data[data["var"] == var]
    xy = (row.odds, categories[row.category])
    plt.annotate(var, xy)

plt.tight_layout()
plt.savefig(outfile)

# vim: syntax=python expandtab sw=4 ts=4
