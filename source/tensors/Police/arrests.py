import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, arrests, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,   
                 lb.timestep,
                 a.domestic,
                 a.dui
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {arrests} a
              ON lb.riipl_id = a.riipl_id AND
                 lb.yrmo = a.yrmo
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        arrests = pd.read_sql(sql, cxn)

    labels = {
        "ARRESTED"          : "arrested for any offense",
        "ARRESTED_DOMESTIC" : "arrested for a domestic offense",
        "ARRESTED_DUI"      : "arrested for a DUI offense"
    }

    tensor = {
        "ARRESTED"          : arrests.loc[:, ["RIIPL_ID", "TIMESTEP"]],
        "ARRESTED_DOMESTIC" : arrests.loc[arrests.DOMESTIC == 1, ["RIIPL_ID", "TIMESTEP"]],
        "ARRESTED_DUI"      : arrests.loc[arrests.DUI == 1, ["RIIPL_ID", "TIMESTEP"]]
    }

    fill_values = dict((feature, 0) for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
