import pandas as pd
import os
import sys

infile, outfile = sys.argv[1:]

table = pd.read_csv(infile)
opioids = frozenset(("codeine", "oxycodone", "tramadol"))

with open(outfile, "w") as f:
    print(r"\begin{tabular}{lll}", file=f)
    print(r"\em NDC Code & \em Opioid Ingredients & \em Other Ingredients\\[0.5em]", file=f)
    for ndc, group in table.groupby("NDC9_CODE"):
        ndc = "{:09d}".format(ndc)
        opioid = []
        other = []
        for row in group.itertuples():
            ingredient = row.ingredient.lower()
            summary = "{} ({}{})".format(ingredient, row.amount, row.unit.lower())
            if ingredient.partition()[0] in opioids:
                opioid.append(summary)
            else:
                other.append(summary)
        if opioid or other:
            missing = ""
        else:
            missing = "*"
        print(r"{}-{}{} & {} & {} \\".format(ndc[:5], ndc[5:], missing, "; ".join(opioid), "; ".join(other)), file=f)
    print(r"\end{tabular}", file=f)

# vim: syntax=python expandtab sw=4 ts=4
