import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveFeatures, CachePopulation

population, lookback, medicaid_enrollment, recip_demo, out, manifest = sys.argv[1:]

def main():

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 MAX(CASE WHEN rd.gender = 'M'                THEN 1 ELSE 0 END) AS sex_m,
                 MAX(CASE WHEN rd.primary_lang_cd = '01'      THEN 1 ELSE 0 END) AS lang_spanish,
                 MAX(CASE WHEN rd.primary_lang_cd = '31'      THEN 1 ELSE 0 END) AS lang_portu,
                 MAX(CASE WHEN rd.primary_lang_cd <> '00' AND
                               rd.primary_lang_cd <> '01' AND
                               rd.primary_lang_cd <> '31'     THEN 1 ELSE 0 END) AS lang_other
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {medicaid_enrollment} me
              ON pop.riipl_id = me.riipl_id AND
                 lb.yrmo = me.yrmo
       LEFT JOIN {recip_demo} rd
              ON me.re_unique_id = rd.recipient_id
        GROUP BY pop.riipl_id
          """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        features = features.join(pd.read_sql(sql, cxn).set_index(index))

    features = features.fillna(0)

    labels = {
        "SEX_M"        : "Sex is male",
        "LANG_SPANISH" : "Primary language is Spanish",
        "LANG_PORTU"   : "Primary language is Portuguese",
        "LANG_OTHER"   : "Primary language is not English, Spanish, or Portuguese",
    }

    SaveFeatures(features, out, manifest, population, labels, bool_features=list(labels))


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
