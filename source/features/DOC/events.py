import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, dim_date, doc_events, out, manifest = sys.argv[1:]

def main():
    """
    Indicators for commited, released, or charged from DOC events
    """

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 MAX(CASE WHEN de.event_type = 'Committed' THEN 1 ELSE 0 END) AS doc_commited,
                 MAX(CASE WHEN de.event_type = 'Released'  THEN 1 ELSE 0 END) AS doc_released,
                 MAX(CASE WHEN de.event_type = 'Charged'   THEN 1 ELSE 0 END) AS doc_charged
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
       LEFT JOIN {doc_events} de
              ON pop.riipl_id = de.riipl_id AND 
                 dd.date_dt = de.event_date
        GROUP BY pop.riipl_id
        """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    labels = {
        "DOC_COMMITED" : "committed to a correctional facility during the lookback period",
        "DOC_RELEASED" : "released from a correctional facility during the lookback period",
        "DOC_CHARGED"  : "charged with a crime during the lookback period"
    }

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
