import pandas as pd
import os
import sys

manifest_file, odds_file, out_file = sys.argv[1:]

manifest = pd.read_csv(manifest_file, sep="\t", names=["var", "desc"])
odds = pd.read_csv(odds_file)

table = odds.merge(manifest, on="var", how="left").sort_values("odds", ascending=False)

def signficance(p):
    if   p < 0.001 : return "$^{***}$"
    elif p < 0.01  : return "$^{**}$"
    elif p < 0.05  : return "$^{*}$"
    else           : return ""

with open(out_file, "w") as f:
    print(r"\begin{tabular}{lcccc}", file=f)
    print(r" & \multicolumn{2}{c}{Unweighted} & \multicolumn{2}{c}{Weighted} \\", file=f)
    print(r"\em Variable & \em Odds Ratio & \em p-value & \em Odds Ratio & \em p-value\\", file=f)
    print(r" & \em (95\% C.I.) & & \em (95\% C.I.) & \\[0.5em]", file=f)
    for row in table.itertuples():
        if row.var.endswith("MISSING"):
            desc = "{} is missing".format(row.var.partition("_")[0].title())
        else:
            desc = row.desc
        print(r"{} & {:.3f} & {:.3f}{} & {:.3f} & {:.3f}{} \\".format(
                  desc, row.odds, row.p, significance(row.p), row.w_odds, row.w_p, significance(row.w_p)),
              file=f)
        print(r" & ({:.3f} - {:.3f}) &  & ({:.3f} - {:.3f}) & \\".format(
                  row.ci_lower, row.ci_upper, row.w_ci_lower, row.w_ci_upper),
              file=f)
    print(r"\end{tabular}", file=f)

# vim: syntax=python expandtab sw=4 ts=4
