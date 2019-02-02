import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

cfsfile, population, lookback, mega, out = sys.argv[1:]

def main():
    """
    """

    cfs = pd.read_csv(cfsfile, dtype={"YRMO": str, "GEOID": str})

    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 lb.yrmo,
                 (m.address_state || m.address_county || m.address_trct || m.address_blkgrp) AS geoid
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {mega} m
              ON lb.riipl_id = m.riipl_id AND
                 lb.yrmo = m.month
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn)

    features = features.merge(cfs, how="inner", on=["YRMO", "GEOID"])

    labels = dict((feature, "home blockgroup's spatial intensity of {} calls for service".format(feature[4:]))
                  for feature in cfs.columns[2:])

    tensor = {}
    for feature in labels:
        tensor[feature] = features[["RIIPL_ID", "TIMESTEP", feature]].rename(columns={feature: "VALUE"})

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
