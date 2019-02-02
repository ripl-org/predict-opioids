import cx_Oracle
import pandas as pd
import os, sys, time
from riipl.model import SaveFeatures, CachePopulation

population, medicaid_diag_cde, outfile, manifest = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,
                 SUM(CASE WHEN SUBSTR(diag_cde, 0, 2) IN ('29', '30', '31') THEN 1
                                                                            ELSE 0
                     END) AS mental_health
            FROM {population} pop
      INNER JOIN {medicaid_diag_cde} diag
              ON pop.riipl_id = diag.riipl_id AND
                 diag.claim_dt < pop.initial_rx_dt AND
                 pop.initial_rx_dt - diag.claim_dt <= 365
        GROUP BY pop.riipl_id
        ORDER BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    features = CachePopulation(population, "RIIPL_ID").set_index("RIIPL_ID").join(features).fillna(0)

    labels = {
        "MENTAL_HEALTH": "Number of mental health diagnoses in previous year"
    }

    SaveFeatures(features, outfile, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
