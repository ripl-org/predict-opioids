import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, citations, out = sys.argv[1:]

def main():
    sql = """
          SELECT pop.riipl_id,   
                 lb.timestep,
                 c.citations,
                 c.fines AS citation_fines
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
      INNER JOIN {citations} c
              ON lb.riipl_id = c.riipl_id AND
                 lb.yrmo = c.yrmo
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        citations = pd.read_sql(sql, cxn)

    labels = {
        "CITATIONS"      : "number of citations",
        "CITATION_FINES" : "total fines for citations"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = citations.loc[citations[feature] > 0, ["RIIPL_ID", "TIMESTEP", feature]].rename(columns={feature: "VALUE"})

    fill_values = dict((feature, 0) for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
