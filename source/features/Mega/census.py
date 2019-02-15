import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, dim_date, address, incomepath, povertypath, outfile, manifest = sys.argv[1:]

def main():
    """
    This code generates the following features based on someone's home census block group:
    * Median income
    * Share below the federal povery line
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    income = pd.read_csv(incomepath, skiprows=1, na_values=["-", "**"],
                         usecols=["Id2", "Estimate; Median household income in the past 12 months (in 2015 Inflation-adjusted dollars)"])
    income.columns = ["GEO_ID", "BLKGRP_MEDIANINCOME"]

    fpl = pd.read_csv(povertypath, skiprows=1, na_values=["-", "**"],
                      usecols=["Id2", "Estimate; Total:", "Estimate; Income in the past 12 months below poverty level:"])
    fpl.columns = ["GEO_ID", "TOTAL", "FPL"]
    fpl["BLKGRP_BELOWFPL"] = fpl.FPL / fpl.TOTAL
    fpl = fpl[["BLKGRP_BELOWFPL"]]

    sql = """
          SELECT pop.riipl_id,
                 STATS_MODE(a.state || a.county || a.trct || a.blkgrp) AS geo_id
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {address} a
              ON pop.riipl_id = a.riipl_id AND
                 dd.date_dt = a.obs_date
        GROUP BY lb.yrmo
          """.format(**globals())

    with Connection() as cxn:
        values = pd.read_sql(sql, cxn._connection)

    values = values.merge(income, how="left", on="GEO_ID")\
                   .merge(fpl, how="left", on="GEO_ID")

    features = features.join(values.groupby(index).mean()[["BLKGRP_MEDIANINCOME", "BLKGRP_BELOWFPL"]])

    # Fill missing values with means
    missing = features.BLKGRP_MEDIANINCOME.isnull()
    assert missing.equals(features.BLKGRP_BELOWFPL.isnull())
    means = features.mean(axis=1)
    print("filling missing values with means:", means)
    features = features.fillna(means, axis=1)
    features["BLKGRP_MISSING"] = missing.astype(int)

    labels = {
        "BLKGRP_MEDIANINCOME" : "block group's median annual household income (2015 dollars)",
        "BLKGRP_BELOWFPL"     : "share of block group's residents with annual income below poverty level",
        "BLKGRP_MISSING"      : "block group is missing"
    }

    SaveFeatures(features, outfile, manifest, population, labels, bool_features=["BLKGRP_MISSING"])


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
