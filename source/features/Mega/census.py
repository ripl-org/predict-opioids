import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, address, income_file, fpl_file, out, manifest = sys.argv[1:]

def main():
    """
    This code generates the following features based on someone's home census block group:
    * Median income
    * Share below the federal povery line
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    income = pd.read_csv(income_file, skiprows=1, na_values=["-", "**"],
                         usecols=["Id2", "Estimate; Median household income in the past 12 months (in 2015 Inflation-adjusted dollars)"])
    income.columns = ["GEO_ID", "BLKGRP_MEDIANINCOME"]

    fpl = pd.read_csv(fpl_file, skiprows=1, na_values=["-", "**"],
                      usecols=["Id2", "Estimate; Total:", "Estimate; Income in the past 12 months below poverty level:"])
    fpl.columns = ["GEO_ID", "TOTAL", "FPL"]
    fpl["BLKGRP_BELOWFPL"] = fpl.FPL / fpl.TOTAL
    fpl = fpl[["GEO_ID", "BLKGRP_BELOWFPL"]]

    sql = """
          SELECT pop.riipl_id,
                 STATS_MODE(TO_NUMBER(a.state || a.county || a.trct || a.blkgrp)) AS geo_id,
                 1 AS geocoded
            FROM (
                  SELECT pop.riipl_id,
                         MAX(a.obs_date) AS max_dt
                    FROM {population} pop
              INNER JOIN {address} a
                      ON pop.riipl_id = a.riipl_id AND
                         a.obs_date <= pop.initial_rx_dt
                GROUP BY pop.riipl_id
                 ) pop
      INNER JOIN {address} a
              ON pop.riipl_id = a.riipl_id AND
                 pop.max_dt = a.obs_date
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        values = pd.read_sql(sql, cxn._connection)

    values = values.merge(income, how="left", on="GEO_ID")\
                   .merge(fpl,    how="left", on="GEO_ID")

    features = features.join(values.set_index(index))
    del features["GEO_ID"]

    # Mean imputation
    features["GEOCODED"] = features.GEOCODED.fillna(0)
    features["BLKGRP_MEDIANINCOME"] = features.BLKGRP_MEDIANINCOME.fillna(features.BLKGRP_MEDIANINCOME.mean())
    features["BLKGRP_BELOWFPL"] = features.BLKGRP_BELOWFPL.fillna(features.BLKGRP_BELOWFPL.mean())

    labels = {
        "GEOCODED"            : "Has a geocoded home address",
        "BLKGRP_MEDIANINCOME" : "Block group's median annual household income (2015 dollars)",
        "BLKGRP_BELOWFPL"     : "Share of block group below poverty line"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
