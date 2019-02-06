import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, mega, out, manifest = sys.argv[1:]

def main():
    """
    Size of DHS household and indicator for births in the DHS household from MEGA table
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 COUNT(DISTINCT m2.riipl_id) AS dhs_hh_size,
                 MAX(CASE WHEN m1.age > 1 AND m2.age < 1
                          THEN 1
                          ELSE 0 END)        AS dhs_hh_birth
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {mega} m1
              ON pop.riipl_id = m1.riipl_id AND
                 lb.yrmo = m1.month
      INNER JOIN {mega} m2
              ON m1.dhs_hh_id = m2.dhs_hh_id AND
                 m1.month = m2.month
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = features.join(pd.read_sql(sql, cxn._connection).set_index(index))

    features = features.fillna(0)

    labels = {
        "DHS_HH_SIZE"  : "count of distinct individuals in the DHS household during lookback period",
        "DHS_HH_BIRTH" : "a birth occurred in the DHS household during lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels, bool_features=["DHS_HH_BIRTH"])


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
