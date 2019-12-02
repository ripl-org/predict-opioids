import pandas as pd
import os
import sys

manifest_file, odds_file, out_file = sys.argv[1:]

manifest = pd.read_csv(manifest_file, sep="\t", names=["var", "desc"])
odds = pd.read_csv(odds_file)

table = odds.merge(manifest, on="var", how="left").sort_values("odds", ascending=False)

def significance(p):
    if   p < 0.001 : return "$^{***}$"
    elif p < 0.01  : return "$^{**}$"
    elif p < 0.05  : return "$^{*}$"
    else           : return ""

with open(out_file, "w") as f:
    print(r"\begin{tabular}{lccc}", file=f)
    print(r"\em Variable & \em Odds Ratio & \em 95\% C.I. & \em p-value \\[0.5em]", file=f)
    for row in table.itertuples():
        if row.var.endswith("MISSING"):
            desc = "{} is missing".format(row.var.partition("_")[0].title())
        elif row.var == "(Intercept)":
            desc = "(Intercept)"
        else:
            desc = row.desc
        if row.var == "INJECTION":
            bold = r"\bf "
        else:
            bold = ""
        desc = desc[0].upper() + desc[1:]
        print(r"{}{} & {}{:.3f} & {}({:.3f} - {:.3f}) & {}{:.3f}{} \\".format(
                  bold, desc, bold, row.odds, bold, row.ci_lower, row.ci_upper, bold, row.p, significance(row.p)),
              file=f)
    print(r"\end{tabular}", file=f)

# vim: syntax=python expandtab sw=4 ts=4
