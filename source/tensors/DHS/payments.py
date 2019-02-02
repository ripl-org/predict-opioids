import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import *

population, lookback, mega, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 m.ccap_payments,
                 m.gpa_payments,
                 m.snap_payments,
                 m.ssi_supplement,
                 m.tanf_payments
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
        "CCAP_PAYMENTS"  : "total CCAP payments before index date",
        "GPA_PAYMENTS"   : "total GPA payments before index date",
        "SNAP_PAYMENTS"  : "total SNAP payments before index date",
        "SSI_SUPPLEMENT" : "total SSI supplement before index date",
        "TANF_PAYMENTS"  : "total TANF payments before index date",
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
