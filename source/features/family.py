import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, relations, outfile, manifest = sys.argv[1:]

def main():

    sql = """
          SELECT pop.riipl_id, 
                 COUNT(DISTINCT hh.riipl_id) AS n_child
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {relations} rel
              ON lb.riipl_id = rel.riipl_id AND 
                 lb.yrmo = rel.yrmo
       LEFT JOIN {relations} hh
              ON rel.dhs_hh_id = hh.dhs_hh_id
           WHERE hh.relation IN ('05', '06', '07', '15', '16', '17')
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    features = CachePopulation(population, "RIIPL_ID").set_index("RIIPL_ID").join(features)

    labels = {
        "N_CHILD": "number of children in the DHS household"
    }

    SaveFeatures(features, outfile, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
