import pandas as pd
import os
import sys
from itertools import zip_longest

infile, outfile = sys.argv[1:]

table = pd.read_csv(infile)
table = table[table.DESC == "Opiate Agonists"]

opioids = frozenset(("codeine", "oxycodone", "tramadol", "opium", "opium,",
                     "hydromorphone", "fentanyl", "morphine"))

print("total:", len(table))
missing = 0

with open(outfile, "w") as f:
    print(r"\begin{tabular}{lll}", file=f)
    print(r"\em NDC Code & \em Opioid Ingredients & \em Other Ingredients \\", file=f)
    print(r"\hline", file=f)
    for ndc, group in table.groupby("NDC9_CODE"):
        ndc = "{:09d}".format(ndc)
        opioid = set()
        other = set()
        for row in group[group.ingredient.notnull()].itertuples():
            ingredient = row.ingredient.lower()
            summary = "{} ({:g}{})".format(ingredient, row.amount, row.unit.lower()).replace("%", r"\%")
            if ingredient.partition(" ")[0] in opioids:
                opioid.add(summary)
            else:
                other.add(summary)
        f.write(r"\textbf{{{}-{}}}".format(ndc[:5], ndc[5:]))
        if not (opioid or other):
            print(r"* & & \\", file=f)
            missing += 1
        else:
            for opioid, other in zip_longest(sorted(opioid), sorted(other), fillvalue=""):
                print(r" & {} & {} \\".format(opioid, other), file=f)
        print(r"\hline", file=f)
    print(r"\end{tabular}", file=f)

print("missing:", missing)

# vim: syntax=python expandtab sw=4 ts=4
