import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, arrests, out, manifest = sys.argv[1:]

def main():
    """
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 MAX(NVL(domestic, 0) AS arrested_domestic,
                 MAX(NVL(juvenile, 0) AS arrested_juvenile,
                 MAX(NVL(dui, 0))     AS arrested_dui,
                 MAX(CASE WHEN domestic <> 1 AND
                               juvenile <> 1 AND
                               dui      <> 1
                          THEN 1
                          ELSE 0 END) AS arrested_other
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {arrests} a
              ON pop.riipl_id = a.riipl_id AND 
                 a.yrmo = lb.yrmo
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = features.join(pd.read_sql(sql, cxn._connection).set_index(index))

    features = features.fillna(0)

    labels = {
        "ARRESTED_DOMESTIC" : "arrested for a domestic incident during lookback period",
        "ARRESTED_JUVENILE" : "arrested as a juvenile during lookback period",
        "ARRESTED_DUI"      : "arrested for a DUI during lookback period",
        "ARRESTED_OTHER"    : "arrested for another reason during lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
