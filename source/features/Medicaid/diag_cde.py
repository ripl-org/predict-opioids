import pandas as pd
import os, sys, time
from riipl import CachePopulation, Connection, SaveFeatures

population, lookback, dim_date, medicaid_diag_cde, diag_corr, icd9_file1, icd9_file2, out, manifest = sys.argv[1:]

def main():

    icd9 = pd.concat([
               pd.read_csv(icd9_file1, usecols=[0, 1], names=["DIAG_CDE", "DESC"]),
               pd.read_csv(icd9_file2)
           ]).drop_duplicates("DIAG_CDE").set_index("DIAG_CDE")

    index = ["RIIPL_ID"]
    features = CachePopulation(population, index).set_index(index)

    sql = """
          SELECT pop.riipl_id,
                 mdc.diag_cde,
                 COUNT(*) AS n
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_diag_cde} mdc
              ON pop.riipl_id = mdc.riipl_id AND
                 dd.date_dt = mdc.claim_dt
      INNER JOIN {diag_corr} dc
              ON mdc.diag_cde = dc.diag_cde AND
                 ABS(dc.corr) > 0
        GROUP BY pop.riipl_id, mdc.diag_cde
              """.format(**globals())

    with Connection() as cxn:
        values = pd.read_sql(sql, cxn._connection)

    cdes = values.DIAG_CDE.unique()

    labels = {}
    for cde in cdes:
        feature = values.loc[values.DIAG_CDE==cde, "N"]
        feature.name = "DIAG_{}".format(cde)
        features = features.join(feature)
        try:
            desc = icd9.loc[cde, "DESC"]
        except KeyError:
            desc = "unknown description"
        label = "number of diagnoses for '{}' during lookback period".format(desc)
        labels[feature.name] = label

    features = features.fillna(0)

    SaveFeatures(features, out, manifest, population, labels)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
