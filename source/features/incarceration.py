import cx_Oracle
import pandas as pd
import os, sys, time
from riipl.model import SaveFeatures

population, doc_events, outfile, manifest = sys.argv[1:]

def main():
    sql= """
         SELECT pop.riipl_id,
                SUM(CASE WHEN event_type = 'Charged' THEN 1 ELSE 0 END) AS n_charges,
                MAX(CASE WHEN event_type = 'Committed' THEN 1 ELSE 0 END) AS incarc_ever
           FROM {population} pop
      LEFT JOIN {doc_events} doc
             ON pop.riipl_id = doc.riipl_id AND
                doc.event_date < pop.initial_rx_dt AND
                pop.initial_rx_dt - doc.event_date <= 365
       GROUP BY pop.riipl_id
       ORDER BY pop.riipl_id
                """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn, index_col="RIIPL_ID")

    labels = {
        "N_CHARGES"   : "Total number of charges before first prescription",
        "INCARC_EVER" : "Ever incarcerated before first prescription"
    }

    SaveFeatures(features, outfile, manifest, population, labels, bool_features=["INCARC_EVER"])


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
