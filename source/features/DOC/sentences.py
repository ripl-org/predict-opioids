import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import CachePopulation, SaveFeatures

population, lookback, dim_date, doc_sentences, out, manifest = sys.argv[1:]

def main():
    """
    Indicators for DOC sentences by crime type
    """

    sql = """
          SELECT DISTINCT offense_type AS offense
            FROM {doc_sentences}
           WHERE offense_type IS NOT NULL
        ORDER BY offense
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        offenses = pd.read_sql(sql, cxn)

    print(offenses)
    pivot = ",".join(["'{0}' AS doc_sentenced_{0}".format(offense) for offense in offenses["OFFENSE"]])

    index = ["RIIPL_ID"]  
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT * 
            FROM (
                  SELECT pop.riipl_id,
                         ds.offense_type AS offense,
                         1 AS sentenced
                    FROM {population} pop
               LEFT JOIN {lookback} lb
                      ON pop.riipl_id = lb.riipl_id
               LEFT JOIN {dim_date} dd
                      ON lb.yrmo = dd.yrmo
              INNER JOIN {doc_sentences} ds
                      ON pop.riipl_id = ds.riipl_id AND 
                         dd.date_dt = ds.imposed_date
                GROUP BY pop.riipl_id, ds.offense_type
                 ) 
           PIVOT (MAX(sentenced) FOR offense IN ({pivot}))
          """.format(pivot=pivot, **globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    # Drop offense types that are missing for the entire population.
    features = features.dropna(axis=1, how="all").fillna(0).astype(int)

    labels = {}
    for offense in offenses["OFFENSE"]:    
        label = "sentenced for {} during lookback period".format(offense)
        labels["DOC_SENTENCED_{}".format(offense.upper())] = label

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))

# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
