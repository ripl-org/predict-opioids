import cx_Oracle
import pandas as pd
import os, sys, time
from riipl.model import SaveFeatures

population, lookback, medicaid_enrollment, outfile, manifest = sys.argv[1:]

def main():    
    sql = """
          SELECT                                 pop.riipl_id,
                 COUNT(DISTINCT re_unique_id) AS n_id
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {medicaid_enrollment} me
              ON lb.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID").fillna(0)

    labels = {
        "N_ID": "Number of Medicaid recipient IDs before first prescription"
    }

    SaveFeatures(features, outfile, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
