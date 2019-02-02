import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor

population, lookback, doc_sentences, dim_date, out = sys.argv[1:]

def main():
    sql = """
          SELECT DISTINCT
                 pop.riipl_id,
                 lb.timestep,
                 'SENTENCED_' || UPPER(ds.offense_type) AS offense
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {doc_sentences} ds
              ON lb.riipl_id = ds.riipl_id AND
                 dd.date_dt = ds.imposed_date
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = pd.read_sql(sql, cxn)

    labels = {
        "SENTENCED_ASSAULT"  : "serving sentence for assault",
        "SENTENCED_DRUG_OFF" : "serving sentence for a drug-related offense",
        "SENTENCED_HOMICIDE" : "serving sentence for homicide",
        "SENTENCED_PROP_OFF" : "serving sentence for a property-related offense",
        "SENTENCED_PUB_OFF"  : "serving sentence for a public offense",
        "SENTENCED_ROBBERY"  : "serving sentence for robbery",
        "SENTENCED_SEX_OFF"  : "serving sentence for a sex offense"
    }

    tensor = {}
    for feature in labels:
        tensor[feature] = features.loc[features.OFFENSE == feature, ["RIIPL_ID", "TIMESTEP"]]

    fill_values = dict((feature, 0) for feature in tensor)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
