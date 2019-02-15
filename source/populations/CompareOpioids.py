import pandas as pd
import os, sys, time

ashp_path, ndc_opioids_path, ndc_ing_path, out = sys.argv[1:]

def main():
    ashp = pd.read_csv(ashp_path, usecols=["NDC9_CODE", "DESC"])
    opioids = frozenset(("Opiate Agonists", "Opiate Partial Agonists", "Opiate Antagonists"))
    ashp = ashp[ashp.DESC.isin(opioids)].drop_duplicates(["NDC9_CODE", "DESC"])

    ndc = pd.read_csv(ndc_opioids_path).rename(columns={"ndc": "NDC9_CODE"})
    ing = pd.read_csv(ndc_ing_path).rename(columns={"ndc": "NDC9_CODE"})
    ing["NDC9_CODE"] = ing.NDC9_CODE.str.extract("(\d+)")
    ing = ing[ing.NDC9_CODE.notnull()]
    ing["NDC9_CODE"] = ing.NDC9_CODE.astype(int)

    merged = ndc.merge(ashp, how="outer", on="NDC9_CODE")

    merged[(merged.opioid != 1) & (merged.recovery != 1) & merged.DESC.notnull()]\
      .merge(ing, how="left", on="NDC9_CODE")\
      .sort_values("NDC9_CODE")\
      .to_csv(out, index=False, float_format="%g")

# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
