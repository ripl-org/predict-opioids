import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, mega, out, manifest = sys.argv[1:]

def main():
    """
    Indicator for births in the DHS household from MEGA table
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT DISTINCT
                 pop.riipl_id,
                 1 AS dhs_hh_birth
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {mega} m1
              ON pop.riipl_id = m1.riipl_id AND
                 lb.yrmo = m1.month
      INNER JOIN {mega} m2
              ON m1.dhs_hh_id = m2.dhs_hh_id AND
                 m1.month = m2.month AND
                 m2.age < 1
           WHERE m1.dhs_hh_id IS NOT NULL AND
                 m1.age > 1
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    features = features.fillna(0)

    labels = {
        "DHS_HH_BIRTH" : "a birth occurred in the DHS household during lookback period"
        }

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
