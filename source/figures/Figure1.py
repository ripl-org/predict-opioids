import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import sys

infile, outfile = sys.argv[1:]

data = pd.read_csv(infile)

outliers = ["MEDICAID_PAYER_RIPAE",
            "MEDICAID_CTG_NEEDY",
            "ASHP_12200400",
            "ASHP_28160804",
            "RACE_HISPANIC",
            "UNEMP_RI",
            "DOC_RELEASED",
            "DHS_HH_SIZE"]

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
print(data.category.value_counts())

categories = dict((c, i) for i, c in enumerate(data.category.unique()))

plt.figure(figsize=(8.5, 5))
sns.stripplot(x="odds", y="category", data=data, orient="h")
sns.despine(left=True)
plt.xlim([0, 2])
plt.title("Odds ratios for BOLASSO-selected predictors by category", loc="left", fontsize=14)
plt.xlabel("")
plt.ylabel("")
plt.grid(True, which="major", axis="y", color="lightgray", linewidth=50)
for x in [0.25, 0.5, 0.75, 1.25, 1.5, 1.75]:
    plt.axvline(x, color="w", linewidth=2, linestyle="dotted")
for x in [0, 1, 2]:
    plt.axvline(x, color="w", linewidth=2)

# Annotate outliers
for i, var in enumerate(outliers):
    row = data[data["var"] == var].iloc[0]
    xy = (row.odds, categories[row.category])
    plt.annotate(chr(97+i), xy,
                 xycoords="data",
                 xytext=(xy[0], xy[1]-0.2),
                 weight="bold",
                 arrowprops=dict(arrowstyle="->"))

plt.tight_layout()
plt.savefig(outfile)

# vim: syntax=python expandtab sw=4 ts=4
