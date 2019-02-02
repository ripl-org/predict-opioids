import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, doc_events, dim_date, out = sys.argv[1:]

def main():
    sql = """
          SELECT DISTINCT
                 pop.riipl_id,
                 lb.timestep,
                 UPPER(de.event_type) AS event
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {doc_events} de
              ON lb.riipl_id = de.riipl_id AND
                 dd.date_dt = de.event_date
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn)

    labels = {
        "CHARGED"   : "criminally charged",
        "COMMITTED" : "committed to a DOC facility",
        "RELEASED"  : "released from a DOC facility"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = features.loc[features.EVENT == feature, ["RIIPL_ID", "TIMESTEP"]]

    fill_values = dict((feature, 0) for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
