import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, mega, out, manifest = sys.argv[1:]

def main():
    """
    Home addresses from MEGA table
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT DISTINCT
                 pop.riipl_id,
                 address_trct
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {mega} m 
              ON pop.riipl_id = m.riipl_id AND
                 lb.yrmo = m.month
           WHERE m.address_trct IS NOT NULL
         """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn).set_index(index)

    labels = {}
    for trct in values.ADDRESS_TRCT.unique():
        name = "TRCT_{}".format(trct)
        feature = values[values["ADDRESS_TRCT"] == trct]
        feature[name] = 1
        features = features.join(feature[name])
        labels[name] = "lived in Census tract {} during lookback period".format(trct)

    features = features.fillna(0)

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
