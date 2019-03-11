import pandas as pd
import os
import sys

freq_file, odds_file, out_file = sys.argv[1:]

freq = pd.read_csv(freq_file)
freq = freq[freq.freq > 90]

odds = pd.read_csv(odds_file)

table = freq.merge(odds, on="var").sort_values("odds", ascending=False)

with open(out_file, "w") as f:
    print(r"\begin{tabular}{lcccc}", file=f)
    print(r"\em Variable & \em Odds Ratio & \em 95\% C.I. & \em p-value & \em Bootstrap Frequency\\[0.5em]", file=f)
    for row in table.itertuples():
        if row.var.endswith("MISSING"):
            desc = "{} is missing".format(row.var.partition("_")[0].title())
        else:
            desc = row.desc
        print(r"{} & {:.3f} & ({:.3f} - {:.3f}) & {:.3f} & {}\% \\".format(
                  desc, row.odds, row.ci_lower, row.ci_upper, row.p, row.freq),
              file=f)
    print(r"\end{tabular}", file=f)

# vim: syntax=python expandtab sw=4 ts=4
