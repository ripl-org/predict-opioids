import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, citations, out, manifest = sys.argv[1:]

def main():
    """
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 SUM(citations) AS citations,
                 SUM(fines)     AS citation_fines
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {citations} c
              ON pop.riipl_id = c.riipl_id AND 
                 c.yrmo = lb.yrmo
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = features.join(pd.read_sql(sql, cxn._connection).set_index(index))

    features = features.fillna(0)

    labels = {
        "CITATIONS"      : "count of citations during lookback period",
        "CITATION_FINES" : "sum of citation fines during lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels)

# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
