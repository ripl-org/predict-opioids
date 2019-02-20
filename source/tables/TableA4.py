import pandas as pd
import os
import sys

infile, outfile = sys.argv[1:]

table = pd.read_csv(infile)
table = table[table.freq > 90]

with open(outfile, "w") as f:
    print(r"\begin{tabular}{llr}", file=f)
    print(r"\em Variable & \em Description & \em Frequency \\[0.5em]", file=f)
    for row in table.itertuples():
        print("{} & {} & {}% \\".format(row["var"], row["desc"], row["freq"]), file=f)
    print(r"\end{tabular}", file=f)

# vim: syntax=python expandtab sw=4 ts=4
