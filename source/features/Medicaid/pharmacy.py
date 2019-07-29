import numpy as np
import pandas as pd
import os, sys, time
from collections import defaultdict
from riipl import *

population, lookback, dim_date, medicaid_pharmacy, ashp_path, out, manifest = sys.argv[1:]

def main():
    # Read in ASHP derived table
    ashp = pd.read_csv(ashp_path)
    i = ashp.CLASS.notnull()
    ashp["FEATURE"] = np.nan
    ashp.loc[i, "FEATURE"] = ashp.loc[i, "CLASS"].apply(lambda x: "ASHP_{}".format(int(x)))
    ashp_desc = ashp.loc[i, ["FEATURE", "DESC"]].drop_duplicates("FEATURE")

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    # Load pharmacy claims
    sql = """ 
          SELECT DISTINCT
                 pop.riipl_id,
                 mp.ndc9_code
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_pharmacy} mp
              ON pop.riipl_id = mp.riipl_id AND
                 dd.date_dt = mp.dispensed_dt
          """.format(**globals())

    with Connection() as cxn:
        values = pd.read_sql(sql, cxn._connection)

    # Merge classes onto pharmacy claims
    values = values.merge(ashp, how="left", on="NDC9_CODE")

    # Missing classes should be <25%
    TestMissing(values.FEATURE, 0.25)
    values.loc[values.FEATURE.isnull(), "FEATURE"] = "ASHP_MISSING"

    # Pivot ASHP categories
    columns = ["RIIPL_ID", "FEATURE"]
    grouped = values[columns].groupby(columns).size().reset_index()
    grouped["VALUE"] = 1

    labels = {"ASHP_MISSING": "Prior prescription for unknown drug category"}
    for _, f, desc in ashp_desc.itertuples():
        if f.startswith("ASHP_99"):
            labels[f] = "Prior prescription for unknown drug category"
        else:
            labels[f] = "Prior prescription for " + desc

    for label in labels:
        feature = grouped.loc[grouped.FEATURE == label, ["RIIPL_ID", "VALUE"]].set_index(index)
        feature = feature.rename(columns={"VALUE": label})
        features = features.join(feature)

    # Drop NAICS categories that are missing for the entire population.
    features = features.dropna(axis=1, how="all").fillna(0)

    # Merge categories with the same description
    varnames = set(features.columns)
    groups = defaultdict(set)
    while(varnames):
        var1 = varnames.pop()
        for var2 in list(varnames):
            if labels[var1] == labels[var2]:
                groups[var1].add(var2)
                varnames.remove(var2)
    for k, v in groups.items():
        group = [k] + list(v)
        print("merging categories:", ", ".join(group))
        merged = "ASHP_" + "_".join(var[5:] for var in group)
        features[merged] = features[group[0]]
        for var in group:
            del features[var]
        labels[merged] = labels[k]

    # Merge perfectly correlated categories
    training = (CachePopulationSubsets(population, index).set_index(index)["SUBSET"] == "TRAINING")
    varnames = set(features.columns)
    groups = defaultdict(set)
    while(varnames):
        var1 = varnames.pop()
        for var2 in list(varnames):
            if features.loc[training, var1].equals(features.loc[training, var2]):
                groups[var1].add(var2)
                varnames.remove(var2)
    for k, v in groups.items():
        group = [k] + list(v)
        print("merging perfectly correlated categories:", ", ".join(group))
        merged = "ASHP_" + "_".join(var[5:] for var in group)
        features[merged] = features[group[0]]
        for var in group:
            del features[var]
        labels[merged] = " or ".join(map(labels.get, group))

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
