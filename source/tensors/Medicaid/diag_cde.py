import cx_Oracle
import pandas as pd
import os, sys, time
from riipl import SaveTensor, Connection

population, lookback, dim_date, medicaid_diag_cde, diag_corr, icd9file, out = sys.argv[1:]

def main():

    icd9 = pd.read_csv(icd9file, usecols=[0,1], names=["DIAG_CDE", "DESC"])

    sql = """
          SELECT pop.riipl_id,
                 lb.timestep,
                 mdc.diag_cde,
                 COUNT(*) AS value
            FROM {population} pop
       LEFT JOIN {lookback} lb
              ON pop.riipl_id = lb.riipl_id
       LEFT JOIN {dim_date} dd
              ON lb.yrmo = dd.yrmo
      INNER JOIN {medicaid_diag_cde} mdc
              ON lb.riipl_id = mdc.riipl_id AND
                 dd.date_dt = mdc.claim_dt
      INNER JOIN {diag_corr} dc
              ON mdc.diag_cde = dc.diag_cde AND
                 ABS(dc.corr) >= 0.02
        GROUP BY pop.riipl_id, lb.timestep, mdc.diag_cde
              """.format(**globals())

    with cx_Oracle.connect("/") as cxn:
        values = pd.read_sql(sql, cxn)

    features = pd.DataFrame({"DIAG_CDE": values.DIAG_CDE.unique()})
    features = features.merge(icd9, how="left", on="DIAG_CDE")
    features["FEATURE"] = "DIAG_" + features.DIAG_CDE

    labels = dict((row.FEATURE, "ICD-9 diagnosis '{}'".format(row["DESC"]))
                  for _, row in features.iterrows())

    tensor = {}
    for feature in features.DIAG_CDE:
        tensor["DIAG_" + feature] = values.loc[values.DIAG_CDE == feature, ["RIIPL_ID", "TIMESTEP", "VALUE"]]

    fill_values = dict(("DIAG_" + feature, 0) for feature in features.DIAG_CDE)

    SaveTensor(tensor, labels, fill_values, (population, "RIIPL_ID"), out)


# EXECUTE
if __name__ == "__main__":
    start = time.time()
    main()
    print("---%s seconds ---" % (time.time() - start))

# vim: expandtab sw=4 ts=4
