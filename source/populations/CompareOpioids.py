import pandas as pd
import os, sys, time

ashp_path, ndc_path, out = sys.argv[1:]

def main():
    ashp = pd.read_csv(ashp_path, usecols=["NDC9_CODE", "DESC"])
    opioids = frozenset(("Opiate Agonists", "Opiate Partial Agonists", "Opiate Antagonists"))
    ashp = ashp[ashp.DESC.isin(opioids)].drop_duplicates(["NDC9_CODE", "DESC"])

    ndc = pd.read_csv("ndc_path").rename(columns={"ndc": "NDC9_CODE"})

    merged = ndc.merge(ashp, how="outer", on="NDC9_CODE")

    merged[(merged.opioid != 1) & (merged.recovery != 1)].sort_values("NDC9_CODE").to_csv(out)

# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
