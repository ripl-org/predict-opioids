import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, car_crashes, out = sys.argv[1:]

def main():
    """
    """
    sql = """
          SELECT pop.riipl_id,   
                 lb.timestep,
                 cc.car_crash AS car_crashes,
                 cc.injured AS car_crash_injuries
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {car_crashes} cc
              ON lb.riipl_id = cc.riipl_id AND
                 lb.yrmo = cc.yrmo
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        crashes = pd.read_sql(sql, cxn)

    labels = {
        "CAR_CRASHES"        : "number of car crashes involved in",
        "CAR_CRASH_INJURIES" : "number of car crashes injured in"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = crashes.loc[crashes[feature] > 0, ["RIIPL_ID", "TIMESTEP", feature]].rename(columns={feature: "VALUE"})

    fill_values = dict((feature, 0) for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
