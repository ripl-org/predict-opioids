import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, car_crashes, out, manifest = sys.argv[1:]

def main():
    """
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,   
                 SUM(cc.car_crash) AS car_crashes,
                 SUM(cc.injured)   AS car_crash_injuries
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {car_crashes} cc
              ON pop.riipl_id = cc.riipl_id AND 
                 cc.yrmo = lb.yrmo
        GROUP BY pop.riipl_id
          """.format(**globals())

    with Connection() as cxn:
        features = features.join(pd.read_sql(sql, cxn._connection).set_index(index))

    features = features.fillna(0)

    labels = {
        "CAR_CRASHES"        : "count of car crashes involved in during lookback period",
        "CAR_CRASH_INJURIES" : "count of car crash injuries during lookback period",
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
