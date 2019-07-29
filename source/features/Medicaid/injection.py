import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveFeatures, CachePopulation

population, out, manifest = sys.argv[1:]

def main():

    index = ["RIIPL_ID"]

    sql = """
          SELECT pop.riipl_id,
                 pop.injection
            FROM {population} pop
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col=index)

    labels = {
        "INJECTION" : "Initial exposure was an opioid injection"
    }

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
