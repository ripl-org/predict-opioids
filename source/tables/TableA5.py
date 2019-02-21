import pandas as pd
import os
import sys

infile, outfile = sys.argv[1:]

table = pd.read_csv(infile).sort_values("odds", ascending=False)

with open(outfile, "w") as f:
    print(r"\begin{tabular}{lr}", file=f)
    print(r"\em Variable & \em Odds Ratio \\[0.5em]", file=f)
    for row in table.itertuples():
        print(r"{} & {} \\".format(row.var.replace("_", r"\_"), row.odds), file=f)
    print(r"\end{tabular}", file=f)

# vim: syntax=python expandtab sw=4 ts=4
