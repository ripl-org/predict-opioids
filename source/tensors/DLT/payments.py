import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import *

population, lookback, mega, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 m.tdi_payments,
                 m.ui_payments
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {mega} m
              ON lb.riipl_id = m.riipl_id AND
                 lb.yrmo = m.month
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn)

    labels = {
        "TDI_PAYMENTS"   : "total TDI payments before index date",
        "UI_PAYMENTS"    : "total UI payments before index date"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = features.loc[features[feature].notnull(), ["RIIPL_ID", "TIMESTEP", feature]].rename(columns={feature: "VALUE"})

    fill_values = dict((feature, "mean") for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
