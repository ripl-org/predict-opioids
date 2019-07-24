import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, dim_date, dlt_ui_payments, out, manifest = sys.argv[1:]

def main():
    """
    Indicator for UI exhaustion
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT DISTINCT
                 pop.riipl_id,
                 1 AS ui_exhaustion
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {dlt_ui_payments} du
              ON pop.riipl_id = du.riipl_id AND
                 dd.date_dt = du.trans_date
          WHERE  void_check_flag IS NULL AND
                 delete_flag IS NULL AND
                 opening_credits > 0 AND
                 closing_credits <= 0
          """.format(**globals())

    with Connection() as cxn:
        features = features.join(pd.read_sql(sql, cxn._connection, index_col=index)).fillna(0)

    labels = {
        "UI_EXHAUSTION" : "Exhausted UI benefits"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
